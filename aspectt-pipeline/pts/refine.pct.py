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
# 2. **Merge near-duplicate tasks** and remove irrelevant ones
#
# Rated data (skills, abilities, knowledge, etc.) is NOT refined -- weighted
# averaging already handles the crosswalk noise smoothly for continuous scores.

# %%
#|export
import asyncio
import logging
from pathlib import Path

from pydantic import BaseModel

from adulib.caching import set_default_cache_path
from adulib.llm.completions import async_single

logger = logging.getLogger(__name__)






# %% [markdown]
# ## Pydantic Response Models

# %%
#|export
class TechSkillVerdict(BaseModel):
    index: int
    relevant: bool


class TechFilterResponse(BaseModel):
    verdicts: list[TechSkillVerdict]


class MergedTask(BaseModel):
    task: str
    task_type: str
    source_indices: list[int]


class TaskRefineResponse(BaseModel):
    tasks: list[MergedTask]
    removed_indices: list[int]






# %% [markdown]
# ## System Prompts

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


TASK_SYSTEM_PROMPT = """\
You are an expert on UK occupations. You will receive task statements mapped \
from multiple US occupations to a single UK occupation via a crosswalk.

Your job:
1. Merge near-duplicate tasks into a single clear statement. Keep wording \
close to the originals. Prefer the clearer/more general phrasing.
2. Mark tasks clearly irrelevant to this occupation for removal. Be \
CONSERVATIVE -- when in doubt, keep the task.

Every original task index must appear in exactly one merged task's \
source_indices OR in removed_indices. Do not leave any index unaccounted for."""






# %% [markdown]
# ## Prompt Builders

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
        task_type = t.get('task_type', 'Core')
        task_text = t.get('task', '')
        lines.append(f"{i}. [{task_type}] {task_text}")
    return "\n".join(lines)






# %% [markdown]
# ## Chunking Helpers

# %%
#|export
TECH_CHUNK_SIZE = 400
TASK_CHUNK_SIZE = 150
JACCARD_DEDUP_THRESHOLD = 0.85


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

    # Build set of relevant indices
    relevant_indices = {v.index for v in result.verdicts if v.relevant}

    # Keep items marked as relevant; if the LLM missed an index, keep it (conservative)
    kept = []
    for i, tech in enumerate(tech_skills):
        if i in relevant_indices or not any(v.index == i for v in result.verdicts):
            kept.append(tech)

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


async def _refine_task_chunk(
    code: int,
    title: str,
    description: str,
    tasks: list[dict],
    model: str,
) -> list[dict]:
    """Refine a chunk of tasks via LLM (merge duplicates + filter irrelevant)."""
    prompt = _build_task_prompt(code, title, description, tasks)

    response, cache_hit, call_log = await async_single(
        prompt=prompt,
        model=model,
        system=TASK_SYSTEM_PROMPT,
        response_format=TaskRefineResponse,
    )

    result = TaskRefineResponse.model_validate_json(response)

    # Build refined task list
    refined = []
    for mt in result.tasks:
        refined.append({
            'task': mt.task,
            'task_type': mt.task_type,
        })

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

# %%
#|export
async def refine_occupation(occ: dict, model: str) -> dict:
    """Refine a single occupation's tasks and tech skills."""
    title = occ.get('title', '')
    description = occ.get('description', '')
    code = occ.get('uk_soc_2020', 0)
    sources = occ.get('source_occupations', [])

    try:
        if occ.get('technology_skills'):
            occ['technology_skills'] = await _refine_tech(
                code, title, description, sources, occ['technology_skills'], model
            )

        if occ.get('tasks'):
            occ['tasks'] = await _refine_tasks(
                code, title, description, sources, occ['tasks'], model
            )
    except Exception as e:
        logger.warning(f"Refinement failed for SOC {code} ({title}): {e}. Keeping original data.")

    return occ






# %% [markdown]
# ## Dataset-Level Entry Point

# %%
#|export
DEFAULT_MODEL = "gpt-4o-mini"
CONCURRENCY_LIMIT = 10


def refine_dataset(
    occupations: list[dict],
    model: str = DEFAULT_MODEL,
    cache_dir: Path | None = None,
    concurrency_limit: int = CONCURRENCY_LIMIT,
) -> list[dict]:
    """
    Refine all occupations' tasks and technology skills using an LLM.

    This is the main entry point, called from build_uk_dataset().
    Runs async batch processing under the hood.

    Args:
        occupations: List of occupation dicts (mutated in place and returned).
        model: LLM model identifier (default: gpt-4o-mini).
        cache_dir: Path for LLM response cache (default: .cache in pipeline dir).
        concurrency_limit: Max concurrent LLM calls.

    Returns:
        The refined list of occupation dicts.
    """
    if cache_dir is None:
        cache_dir = Path(__file__).parent.parent / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    set_default_cache_path(cache_dir)

    # Capture before-counts (occupations are mutated in place)
    total_tech_before = sum(len(occ.get('technology_skills', [])) for occ in occupations)
    total_tasks_before = sum(len(occ.get('tasks', [])) for occ in occupations)

    async def _run():
        semaphore = asyncio.Semaphore(concurrency_limit)

        async def _bounded(occ):
            async with semaphore:
                return await refine_occupation(occ, model)

        to_refine = [
            occ for occ in occupations
            if occ.get('technology_skills') or occ.get('tasks')
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
    total_tasks_after = sum(len(occ.get('tasks', [])) for occ in occupations)
    print(
        f"Refinement complete: "
        f"tech {total_tech_before} -> {total_tech_after} "
        f"({total_tech_before - total_tech_after} removed), "
        f"tasks {total_tasks_before} -> {total_tasks_after} "
        f"({total_tasks_before - total_tasks_after} removed/merged)"
    )

    return occupations
