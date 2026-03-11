# ASPECTT Pipeline Methodology

ASPECTT (A System for Profiling Employment Characteristics and Transferable Traits) translates the US O\*NET occupational database into a UK-contextualised equivalent, mapped to the UK Standard Occupational Classification (SOC) 2020 framework.

## 1. Data Sources

| Source | Version | Description |
|--------|---------|-------------|
| US O\*NET | v30.2 | 923 occupation profiles with skills, abilities, knowledge, tasks, technology skills, interests, work values, education requirements, and more |
| BLS SOC 2010 ↔ 2018 crosswalk | 2018 | Maps between the 2010 and 2018 editions of the US Standard Occupational Classification |
| BLS ISCO-08 ↔ SOC 2010 crosswalk | — | Maps between the International Standard Classification of Occupations (ISCO-08) and US SOC 2010 |
| ONS SOC 2020 coding index | 2025-03-12 | UK SOC 2020 framework (412 unit groups) with embedded ISCO-08 codes |

## 2. Crosswalk Construction

The pipeline builds a four-step crosswalk chain to bridge US and UK classification systems:

```
O*NET SOC  →  US SOC 2018  →  US SOC 2010  →  ISCO-08  →  UK SOC 2020
```

**Step 1 — O\*NET SOC → US SOC 2018:** O\*NET codes (e.g. `15-1252.00`) are truncated to their 6-digit base SOC code (`15-1252`), which maps directly to the US SOC 2018 system.

**Step 2 — US SOC 2018 → US SOC 2010:** The BLS provides a crosswalk between the 2018 and 2010 editions. This is a many-to-many mapping (occupations were split and merged between editions).

**Step 3 — US SOC 2010 → ISCO-08:** The BLS provides a crosswalk between US SOC 2010 and ISCO-08, the international standard used as the bridge to UK classifications.

**Step 4 — ISCO-08 → UK SOC 2020:** The ONS SOC 2020 coding index includes ISCO-08 codes for each entry. We extract unique ISCO-08 → UK SOC 2020 pairs from this index.

### Weighting Scheme

Each O\*NET occupation may map to multiple UK SOC codes. The contribution weight is uniform: if an O\*NET code maps to N distinct UK SOC codes, each receives weight 1/N. This ensures every O\*NET occupation's total contribution sums to 1.0 across all UK SOC codes it feeds into.

The result is a crosswalk table with columns: `onet_soc`, `onet_title`, `uk_soc_2020`, `uk_soc_title`, `weight`.

## 3. Data Translation

Each UK SOC 2020 unit group becomes a "superposition" of its contributing US O\*NET occupations. The translation method depends on data type:

### Rated (Continuous) Data

For data with numeric scores — abilities, skills, knowledge, work activities, work context, work styles, interests, work values — we compute **weighted averages**:

```
UK_value(element, scale) = Σ (weight_i × ONET_value_i) / Σ weight_i
```

where the sum is over all contributing O\*NET occupations. This produces smooth, reasonable values even when many sources contribute. For example, a UK programming occupation that draws from 15 O\*NET software roles will have its "Programming" skill score dominated by the high-scoring sources.

Education and job zone data are also averaged using the same weighted scheme.

### Discrete (Categorical/Text) Data

For data that cannot be meaningfully averaged — tasks, technology skills, alternate titles — we **collect all unique items** from all contributing O\*NET occupations. Items are sorted by their contribution weight (sum of source weights).

This is where the many-to-one mapping introduces noise: a UK occupation inherits *everything* from all its source occupations. For example, UK SOC 5313 (Bricklayers) maps from 10 US occupations including Hazardous Materials Removal Workers, Solar Photovoltaic Installers, and Weatherization Installers, inheriting their technology skills and task statements even when they are clearly irrelevant to bricklaying.

### Related Occupations

Related occupations from O\*NET are re-mapped through the crosswalk to produce UK SOC-to-UK SOC relationships. Self-references (where a related occupation maps to the same UK SOC code) are removed.

## 4. LLM Refinement

To address the crosswalk noise in discrete data, an optional LLM refinement step filters and deduplicates technology skills and tasks.

### What Gets Refined

| Category | Operation | Rationale |
|----------|-----------|-----------|
| Technology skills | Filter irrelevant items | Crosswalk noise is most visible here (e.g. Jenkins CI, Salesforce for Bricklayers) |
| Tasks | Merge near-duplicates + filter irrelevant | Multiple O\*NET sources contribute overlapping or unrelated task statements |

**Rated data is NOT refined.** Weighted averaging already handles crosswalk noise smoothly for continuous numeric scores — the irrelevant sources are naturally diluted by the relevant ones.

### Conservative Philosophy

The LLM is instructed to be **conservative**: only remove items that are *clearly* irrelevant. Generic tools (Microsoft Office, email, web browsers) are kept for almost all occupations. When in doubt, items are preserved. This prevents the LLM from over-filtering legitimate but uncommon technology associations.

### Technology Skill Filtering

The LLM receives the occupation title, description, source US occupations, and a numbered list of technology skills. It returns a verdict (relevant/irrelevant) for each item. Items with no verdict are kept (fail-safe conservative default).

### Task Refinement

The LLM receives task statements (with Core/Supplemental type labels) and is asked to:
1. **Merge near-duplicate tasks** into single clear statements, keeping wording close to originals
2. **Remove clearly irrelevant tasks** that do not belong to this occupation

Every original task must appear in exactly one merged group or in the removal list — no task is silently dropped.

### Chunking and Deduplication

For occupations with very large item lists (>400 tech skills or >150 tasks), input is split into chunks processed independently. After task chunking, a deterministic post-processing pass merges any cross-chunk duplicates using Jaccard word-overlap (threshold: 0.85).

### Model and Cost

The default model is `gpt-4o-mini`. At ~1,500 API calls across 343 occupations with data (~5M input tokens, ~2.5M output tokens), a full run costs approximately $2.25. All responses are cached with `adulib`, so re-runs are free.

## 5. Output Format

The pipeline produces per-occupation JSON files in `data/uk_onet/occupations/{soc_code}.json`, plus an `occupation_index.json` and `crosswalk.json`.

### Per-Occupation JSON Schema

```json
{
  "uk_soc_2020": 2134,
  "title": "Programmers and software development professionals",
  "description": "Combined description from source O*NET occupations...",
  "abilities": [
    {"element_id": "1.A.1.a.1", "element_name": "Oral Comprehension", "value_IM": 3.8, "value_LV": 4.1}
  ],
  "skills": [...],
  "knowledge": [...],
  "work_activities": [...],
  "work_context": [...],
  "work_styles": [...],
  "interests": [...],
  "work_values": [...],
  "tasks": [
    {"task": "Write, analyse, review, and rewrite programs...", "task_type": "Core"}
  ],
  "technology_skills": [
    {"name": "Python", "weight": 2.5}
  ],
  "education": [...],
  "job_zone": 4,
  "alternate_titles": ["Software Developer", "Systems Programmer", ...],
  "related_occupations": [
    {"related_uk_soc": 2135, "related_uk_title": "...", "link_count": 12}
  ],
  "source_occupations": [
    {"onet_soc": "15-1252.00", "onet_title": "Software Developers", "weight": 0.1}
  ]
}
```

### Data Categories

| Category | Type | Scales | Description |
|----------|------|--------|-------------|
| Abilities | Rated | IM (importance), LV (level) | Enduring attributes relevant to work performance |
| Skills | Rated | IM, LV | Developed capacities for performing work activities |
| Knowledge | Rated | IM, LV | Sets of principles and facts relevant to work |
| Work Activities | Rated | IM, LV | General types of job behaviours |
| Work Context | Rated | Various | Physical and social factors of the work environment |
| Work Styles | Rated | IM | Personal characteristics for job performance |
| Interests | Rated | OI (occupational interest) | Holland/RIASEC interest profiles |
| Work Values | Rated | EX (extent) | Work aspects valued by workers |
| Tasks | Discrete | — | Specific work activities performed |
| Technology Skills | Discrete | weight | Software, tools, and technologies used |
| Education | Rated | — | Education, training, and experience requirements |
| Job Zone | Numeric | 1–5 | Preparation level (1=little, 5=extensive) |

## 6. Limitations

**Crosswalk chain noise.** The four-step crosswalk introduces many-to-many mappings. Some UK SOC codes inherit data from tangentially related US occupations. LLM refinement mitigates the worst of this for discrete data, but the underlying crosswalk is imperfect.

**US-source bias.** All data originates from the US O\*NET programme. Occupation structures, skill requirements, and technology usage may differ in the UK labour market. The pipeline translates occupation *classifications* but cannot adapt the underlying occupational data to UK-specific realities.

**ISCO-08 as bridge.** ISCO-08 is coarser than both US SOC and UK SOC, so the bridge step necessarily groups occupations that may be distinct in either national system.

**LLM judgement boundaries.** The refinement step relies on an LLM's assessment of item relevance. While conservative prompting reduces false removals, the model may occasionally keep irrelevant items or remove marginally relevant ones. All LLM responses are cached and deterministic for a given model version.

**Uniform weighting.** All contributing O\*NET codes receive equal weight (1/N). A more sophisticated approach might weight by occupational similarity, but no suitable similarity metric exists across classification systems.

## 7. Reproducibility

**Caching.** All LLM API calls are cached to disk via `adulib`'s diskcache backend (`.cache/` directory). Once a response is cached, re-running the pipeline produces identical output at zero API cost.

**Deterministic thresholds.** The Jaccard deduplication threshold (0.85) is fixed and applied deterministically after LLM processing.

**Data versioning.** The pipeline is pinned to O\*NET v30.2 and the March 2025 edition of the ONS SOC 2020 coding index. Source data files are stored in `_dev/00_data_download/`.

**Running the pipeline:**

```bash
cd aspectt-pipeline
uv sync
uv run python -c "
from aspectt_pipeline.translate import build_uk_dataset
dataset = build_uk_dataset(refine=True)
"
```

Set `refine=False` (the default) to skip the LLM refinement step and produce raw translated data.
