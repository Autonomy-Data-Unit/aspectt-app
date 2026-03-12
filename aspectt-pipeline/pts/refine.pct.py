# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
#|default_exp refine















# %% [markdown]
# # LLM Refinement of Translated Data
#
# The crosswalk chain (O*NET SOC -> UK SOC 2020) introduces noise in discrete
# categories: a UK occupation inherits technology skills and tasks from ALL
# contributing US occupations, many of which are irrelevant. For example,
# UK SOC 5313 (Bricklayers) inherits Jenkins CI and Salesforce from
# Hazmat Workers and Weatherization Installers.
#
# This module uses an LLM to:
# 1. **Filter irrelevant technology skills** from each occupation
# 2. **Filter irrelevant tools used** from each occupation
# 3. **Deduplicate near-identical tasks** and remove irrelevant ones
#
# Rated data (skills, abilities, knowledge, etc.) is NOT refined -- weighted
# averaging already handles the crosswalk noise smoothly for continuous scores.
#
#
# 

# %%
#|export
import asyncio
import logging
from pathlib import Path

from pydantic import BaseModel

from adulib.caching import set_default_cache_path
from adulib.llm.completions import async_single
from aspectt_pipeline.const import (
    TECH_FILTER_MODEL, TOOL_FILTER_MODEL, TASK_REFINE_MODEL,
    CONCURRENCY_LIMIT,
    TECH_CHUNK_SIZE, TOOL_CHUNK_SIZE, TASK_CHUNK_SIZE,
    JACCARD_DEDUP_THRESHOLD, VALID_TASK_TYPES,
)

logger = logging.getLogger(__name__)














# %% [markdown]
# ## Pydantic Response Models
#
# These models define the structured output format the LLM must return.
# Using `response_format=` with Pydantic models ensures type-safe, parseable
# responses and prevents the LLM from generating free-form text.
#
#
# 

# %%
#|export
class TechSkillVerdict(BaseModel):
    index: int
    relevant: bool


class TechFilterResponse(BaseModel):
    verdicts: list[TechSkillVerdict]


class TaskGroup(BaseModel):
    preferred_index: int
    duplicate_indices: list[int]


class TaskRefineResponse(BaseModel):
    kept: list[TaskGroup]
    removed_indices: list[int]














# %% [markdown]
# ## System Prompts
#
# Each refinement task has its own system prompt that frames the LLM as a
# UK occupation expert. All prompts emphasise a **conservative** stance:
# only remove items that are clearly irrelevant, keep generic items, and
# never generate new text — the LLM may only select among originals.
#
#
# 

# %%
#|export
TECH_SYSTEM_PROMPT = """\
You are an expert on UK occupations. You will receive a list of technology \
skills mapped to a UK occupation via a crosswalk from US O*NET data.

Assess whether each technology is plausibly used by workers in this occupation. \
Be CONSERVATIVE: only mark items as irrelevant if they clearly do not belong. \
Generic tools (Microsoft Office, email clients, web browsers) are relevant to \
almost all occupations.

Return a verdict for EVERY item in the list. Do not skip any."""


TOOL_SYSTEM_PROMPT = """\
You are an expert on UK occupations. You will receive a list of physical tools \
and equipment mapped to a UK occupation via a crosswalk from US O*NET data.

Assess whether each tool or piece of equipment is plausibly used by workers in \
this occupation. Be CONSERVATIVE: only mark items as irrelevant if they clearly \
do not belong. Generic items (desktop computers, laptops, telephones, and basic \
hand tools) are relevant to many occupations.

Return a verdict for EVERY item in the list. Do not skip any."""


TASK_SYSTEM_PROMPT = """\
You are an expert on UK occupations. You will receive task statements mapped \
from multiple US occupations to a single UK occupation via a crosswalk.

Your job:
1. Deduplicate near-identical tasks. Group duplicates together and pick the \
best original (preferred_index) -- the clearest and most general phrasing. \
List the other indices in duplicate_indices.
2. Mark tasks clearly irrelevant to this occupation for removal. Be \
CONSERVATIVE -- when in doubt, keep the task. Put their indices in \
removed_indices.

IMPORTANT constraints:
- Do NOT rewrite or generate any task text. You are only selecting and \
filtering original tasks.
- Only group tasks as duplicates if they say essentially the same thing. \
Do NOT group tasks just because they relate to the same broad topic.
- For occupations with many input tasks, aim to retain at least 10 distinct \
tasks in the output.

Every original task index must appear exactly once: either as a \
preferred_index, in a duplicate_indices list, or in removed_indices."""














# %% [markdown]
# ## Prompt Builders
#
# These functions construct the user-message prompt for each LLM call. Each
# prompt includes the occupation title, description, source US occupations
# (for context), and a numbered list of items. Numbering is critical — the
# LLM's structured response references items by index, so the indices must
# be stable and contiguous.
#
#
# 

# %%
#|export
def _build_tech_prompt(
    code: int,
    title: str,
    description: str,
    sources: list[dict],
    tech_skills: list[dict],
) -> str:
    """Build user prompt for technology skill filtering."""
    source_str = ", ".join(
        f"{s.get('onet_title', s.get('onet_soc', '?'))}" for s in sources
    )
    lines = [
        f"UK Occupation: {title} (SOC {code})",
        f"Description: {description}",
        f"Source US occupations: {source_str}",
        "",
        "Technologies:",
    ]
    for i, tech in enumerate(tech_skills):
        name = tech.get('name', tech.get('Example', ''))
        lines.append(f"{i}. {name}")
    return "\n".join(lines)


def _build_tool_prompt(
    code: int,
    title: str,
    description: str,
    sources: list[dict],
    tools: list[dict],
) -> str:
    """Build user prompt for tools used filtering."""
    source_str = ", ".join(
        f"{s.get('onet_title', s.get('onet_soc', '?'))}" for s in sources
    )
    lines = [
        f"UK Occupation: {title} (SOC {code})",
        f"Description: {description}",
        f"Source US occupations: {source_str}",
        "",
        "Tools and Equipment:",
    ]
    for i, tool in enumerate(tools):
        name = tool.get('name', tool.get('Example', ''))
        lines.append(f"{i}. {name}")
    return "\n".join(lines)


_TASK_TYPE_LOOKUP = {v.lower(): v for v in VALID_TASK_TYPES}


def _normalise_task_type(raw: str | None) -> str:
    """Normalise a task_type value to one of Core/Supplemental/Unclassified."""
    if raw is None:
        return 'Unclassified'
    return _TASK_TYPE_LOOKUP.get(raw.strip().lower(), 'Unclassified')


def _build_task_prompt(
    code: int,
    title: str,
    description: str,
    tasks: list[dict],
) -> str:
    """Build user prompt for task refinement."""
    lines = [
        f"UK Occupation: {title} (SOC {code})",
        f"Description: {description}",
        "",
        "Tasks:",
    ]
    for i, t in enumerate(tasks):
        task_type = _normalise_task_type(t.get('task_type'))
        task_text = t.get('task', '')
        lines.append(f"{i}. [{task_type}] {task_text}")
    return "\n".join(lines)














# %% [markdown]
# ## Chunking Helpers
#
# Some occupations inherit hundreds of items through the crosswalk. To stay
# within context-window limits, large lists are split into chunks processed
# independently. After chunked task refinement, a deterministic Jaccard
# word-overlap pass catches any cross-chunk duplicates the LLM couldn't see.
#
#
# 

# %%
#|export
def _chunk_list(items: list, chunk_size: int) -> list[list]:
    """Split a list into chunks of at most chunk_size."""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def _jaccard_word_overlap(a: str, b: str) -> float:
    """Compute Jaccard similarity on word sets."""
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0.0
    return len(words_a & words_b) / len(words_a | words_b)


def _dedup_tasks_by_jaccard(tasks: list[dict], threshold: float = JACCARD_DEDUP_THRESHOLD) -> list[dict]:
    """Deterministic post-dedup pass: merge tasks with high word overlap."""
    if not tasks:
        return tasks

    kept = []
    merged_into = {}  # index -> index it was merged into

    for i, t in enumerate(tasks):
        if i in merged_into:
            continue
        for j in range(i + 1, len(tasks)):
            if j in merged_into:
                continue
            if _jaccard_word_overlap(t['task'], tasks[j]['task']) >= threshold:
                merged_into[j] = i
        kept.append(t)

    return kept














# %% [markdown]
# ## Core Refinement Functions
#
# Each category has a `_refine_*_chunk` function (single LLM call) and a
# `_refine_*` wrapper that handles chunking. Tech and tool filtering use
# the same Pydantic model (`TechFilterResponse`) since both are simple
# relevant/irrelevant verdicts. Task refinement is more complex: the LLM
# groups near-duplicates and picks the best original phrasing from each group.
# No LLM-generated text enters the dataset — only original O*NET text is kept.
#
#
# 

# %%
#|export
async def _refine_tech_chunk(
    code: int,
    title: str,
    description: str,
    sources: list[dict],
    tech_skills: list[dict],
    model: str,
) -> list[dict]:
    """Filter a chunk of technology skills via LLM."""
    prompt = _build_tech_prompt(code, title, description, sources, tech_skills)

    response, cache_hit, call_log = await async_single(
        prompt=prompt,
        model=model,
        system=TECH_SYSTEM_PROMPT,
        response_format=TechFilterResponse,
    )

    result = TechFilterResponse.model_validate_json(response)

    # Items explicitly marked irrelevant are removed; missed indices are kept (conservative)
    irrelevant_indices = {v.index for v in result.verdicts if not v.relevant}
    kept = [tech for i, tech in enumerate(tech_skills) if i not in irrelevant_indices]

    return kept


async def _refine_tech(
    code: int,
    title: str,
    description: str,
    sources: list[dict],
    tech_skills: list[dict],
    model: str,
) -> list[dict]:
    """Filter technology skills, chunking if needed."""
    if not tech_skills:
        return tech_skills

    chunks = _chunk_list(tech_skills, TECH_CHUNK_SIZE)
    if len(chunks) == 1:
        return await _refine_tech_chunk(code, title, description, sources, tech_skills, model)

    results = []
    for chunk in chunks:
        kept = await _refine_tech_chunk(code, title, description, sources, chunk, model)
        results.extend(kept)
    return results


async def _refine_tool_chunk(
    code: int,
    title: str,
    description: str,
    sources: list[dict],
    tools: list[dict],
    model: str,
) -> list[dict]:
    """Filter a chunk of tools used via LLM."""
    prompt = _build_tool_prompt(code, title, description, sources, tools)

    response, cache_hit, call_log = await async_single(
        prompt=prompt,
        model=model,
        system=TOOL_SYSTEM_PROMPT,
        response_format=TechFilterResponse,
    )

    result = TechFilterResponse.model_validate_json(response)

    # Items explicitly marked irrelevant are removed; missed indices are kept (conservative)
    irrelevant_indices = {v.index for v in result.verdicts if not v.relevant}
    kept = [tool for i, tool in enumerate(tools) if i not in irrelevant_indices]

    return kept


async def _refine_tools(
    code: int,
    title: str,
    description: str,
    sources: list[dict],
    tools: list[dict],
    model: str,
) -> list[dict]:
    """Filter tools used, chunking if needed."""
    if not tools:
        return tools

    chunks = _chunk_list(tools, TOOL_CHUNK_SIZE)
    if len(chunks) == 1:
        return await _refine_tool_chunk(code, title, description, sources, tools, model)

    results = []
    for chunk in chunks:
        kept = await _refine_tool_chunk(code, title, description, sources, chunk, model)
        results.extend(kept)
    return results


async def _refine_task_chunk(
    code: int,
    title: str,
    description: str,
    tasks: list[dict],
    model: str,
) -> list[dict]:
    """Deduplicate and filter a chunk of tasks via LLM. Only original text is kept."""
    prompt = _build_task_prompt(code, title, description, tasks)

    response, cache_hit, call_log = await async_single(
        prompt=prompt,
        model=model,
        system=TASK_SYSTEM_PROMPT,
        response_format=TaskRefineResponse,
    )

    result = TaskRefineResponse.model_validate_json(response)

    # Keep only the preferred original task from each group, preserving all fields
    refined = []
    for group in result.kept:
        idx = group.preferred_index
        if 0 <= idx < len(tasks):
            task = dict(tasks[idx])  # shallow copy to avoid mutating input
            task['task_type'] = _normalise_task_type(task.get('task_type'))
            refined.append(task)
        else:
            logger.warning(f"SOC {code}: preferred_index {idx} out of range (0-{len(tasks)-1})")

    return refined


async def _refine_tasks(
    code: int,
    title: str,
    description: str,
    sources: list[dict],
    tasks: list[dict],
    model: str,
) -> list[dict]:
    """Refine tasks, chunking if needed, with post-dedup pass."""
    if not tasks:
        return tasks

    chunks = _chunk_list(tasks, TASK_CHUNK_SIZE)
    results = []
    for chunk in chunks:
        refined = await _refine_task_chunk(code, title, description, chunk, model)
        results.extend(refined)

    # Cross-chunk dedup via Jaccard similarity
    if len(chunks) > 1:
        results = _dedup_tasks_by_jaccard(results)

    return results














# %% [markdown]
# ## Per-Occupation Refinement
#
# Orchestrates the three refinement tasks (tech skills, tools used, tasks)
# for a single occupation. If any refinement fails, the original unrefined
# data is preserved — the pipeline never loses data due to LLM errors.
#
#
# 

# %%
#|export
async def refine_occupation(
    occ: dict,
    tech_model: str = TECH_FILTER_MODEL,
    tool_model: str = TOOL_FILTER_MODEL,
    task_model: str = TASK_REFINE_MODEL,
) -> dict:
    """Refine a single occupation's tasks, tech skills, and tools used."""
    title = occ.get('title', '')
    description = occ.get('description', '')
    code = occ.get('uk_soc_2020', 0)
    sources = occ.get('source_occupations', [])

    if occ.get('technology_skills'):
        try:
            occ['technology_skills'] = await _refine_tech(
                code, title, description, sources, occ['technology_skills'], tech_model
            )
        except Exception as e:
            logger.warning(f"Tech refinement failed for SOC {code} ({title}): {e}. Keeping original.")

    if occ.get('tools_used'):
        try:
            occ['tools_used'] = await _refine_tools(
                code, title, description, sources, occ['tools_used'], tool_model
            )
        except Exception as e:
            logger.warning(f"Tool refinement failed for SOC {code} ({title}): {e}. Keeping original.")

    if occ.get('tasks'):
        try:
            occ['tasks'] = await _refine_tasks(
                code, title, description, sources, occ['tasks'], task_model
            )
        except Exception as e:
            logger.warning(f"Task refinement failed for SOC {code} ({title}): {e}. Keeping original.")

    return occ














# %% [markdown]
# ## Dataset-Level Entry Point
#
# Processes all occupations concurrently (bounded by a semaphore) and
# prints before/after counts so you can see the impact of refinement.
# All LLM responses are cached via `adulib`, so re-runs are instant.
#
# 

# %%
#|export
def refine_dataset(
    occupations: list[dict],
    tech_model: str = TECH_FILTER_MODEL,
    tool_model: str = TOOL_FILTER_MODEL,
    task_model: str = TASK_REFINE_MODEL,
    cache_dir: Path | None = None,
    concurrency_limit: int = CONCURRENCY_LIMIT,
) -> list[dict]:
    """
    Refine all occupations' tasks, technology skills, and tools used using LLMs.

    This is the main entry point, called from build_uk_dataset().
    Runs async batch processing under the hood.

    Args:
        occupations: List of occupation dicts (mutated in place and returned).
        tech_model: Model for technology skill filtering.
        tool_model: Model for tool/equipment filtering.
        task_model: Model for task deduplication and filtering.
        cache_dir: Path for LLM response cache (default: .cache in pipeline dir).
        concurrency_limit: Max concurrent LLM calls.

    Returns:
        The refined list of occupation dicts.
    """
    if cache_dir is None:
        cache_dir = Path(__file__).parent.parent / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    set_default_cache_path(cache_dir)

    print(f"Models: tech={tech_model}, tools={tool_model}, tasks={task_model}")

    # Capture before-counts (occupations are mutated in place)
    total_tech_before = sum(len(occ.get('technology_skills', [])) for occ in occupations)
    total_tools_before = sum(len(occ.get('tools_used', [])) for occ in occupations)
    total_tasks_before = sum(len(occ.get('tasks', [])) for occ in occupations)

    async def _run():
        semaphore = asyncio.Semaphore(concurrency_limit)

        async def _bounded(occ):
            async with semaphore:
                return await refine_occupation(occ, tech_model, tool_model, task_model)

        to_refine = [
            occ for occ in occupations
            if occ.get('technology_skills') or occ.get('tools_used') or occ.get('tasks')
        ]

        if not to_refine:
            return

        from tqdm.asyncio import tqdm_asyncio
        await tqdm_asyncio.gather(
            *[_bounded(occ) for occ in to_refine],
            desc="Refining occupations",
        )

    asyncio.run(_run())

    total_tech_after = sum(len(occ.get('technology_skills', [])) for occ in occupations)
    total_tools_after = sum(len(occ.get('tools_used', [])) for occ in occupations)
    total_tasks_after = sum(len(occ.get('tasks', [])) for occ in occupations)
    print(
        f"Refinement complete: "
        f"tech {total_tech_before} -> {total_tech_after} "
        f"({total_tech_before - total_tech_after} removed), "
        f"tools {total_tools_before} -> {total_tools_after} "
        f"({total_tools_before - total_tools_after} removed), "
        f"tasks {total_tasks_before} -> {total_tasks_after} "
        f"({total_tasks_before - total_tasks_after} removed/merged)"
    )

    return occupations
