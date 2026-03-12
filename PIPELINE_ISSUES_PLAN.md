# Pipeline Issues Fix Plan

197 of 412 occupations have issues identified during systematic review. Most can be fixed through automated post-processing without re-running LLM calls.

## Phase 1 — Automated Post-Processing (no LLM re-run)

Fixes ~159/197 issues. Add a `postprocess_dataset()` function in a new `pts/postprocess.pct.py` module that runs after refinement in `build_uk_dataset()`.

### 1.1 Fix "nan" task_type (69 occupations)

In `translate_task_statements()`, default null task types to `"Unclassified"` before serialisation. Also in `postprocess_dataset()`, replace any `"nan"` string task_type with `"Unclassified"`.

### 1.2 Remove LLM artifacts from task text (13 occupations)

Delete any task where:
- `task` text contains "Remove irrelevant", "[REMOVED]", "[REDACTED]", or starts with "Remove tasks"
- `task_type` is `"Irrelevant"`
- `task` text is empty or equals "Not relevant."
- `task` text starts with literal `[nan]`

### 1.3 Add generic tech skill whitelist (12 occupations)

After LLM refinement, re-add items from the unrefined data that match a whitelist of generic software if they were removed:
- Microsoft Office, Microsoft Excel, Microsoft Word, Microsoft Outlook, Microsoft PowerPoint
- Web browser software, Electronic mail software

Only re-add if they existed in the unrefined data for that occupation.

### 1.4 US→UK terminology substitution (65 occupations)

Deterministic find-and-replace on task text and tech skill names:

| US term | UK replacement |
|---------|---------------|
| `federal and state` | `central and devolved government` |
| `state and federal` | `central and devolved government` |
| `federal` (standalone in context) | `central government` |
| `Medicare` / `Medicaid` | `NHS` |
| `OSHA` | `HSE` |

Remove US-specific tech skill entries entirely:
- Items containing "FRESA", "SEVIS", "USDA" in the name

### 1.5 Remove wrong-domain tasks by keyword (20 occupations)

For non-gambling occupations (title doesn't contain "gambling", "betting", "casino"), remove tasks containing gambling/casino/jackpot/slot machine keywords.

For non-fire occupations (title doesn't contain "fire", "rescue"), remove tasks containing "fire suppression", "arson investigation", "fire crew" keywords.

### 1.6 Wire into pipeline

Call `postprocess_dataset(occupations, unrefined_occupations)` after `refine_dataset()` in `build_uk_dataset()`. The function needs both refined and unrefined data (for the tech skill whitelist re-add).

Export via nblite: `cd aspectt-pipeline && nbl export --reverse && nbl export`

## Phase 2 — Prompt Improvements + Selective LLM Re-Run

Fixes remaining ~38 issues (mega-tasks, tools unchanged, task over-filtering). Requires clearing cached LLM responses for affected occupations and re-running.

### 2.1 Fix task mega-merging (66 occupations)

Update `TASK_SYSTEM_PROMPT` in `pts/refine.pct.py`:

Add these constraints:
- "Each merged task MUST be a single, clear sentence — never a paragraph."
- "A merged task should combine at most 3 very similar original tasks."
- "Do NOT merge tasks just because they relate to the same broad topic."
- "No task in your output should exceed 200 characters."

Add post-processing in `_refine_task_chunk()`: if any returned task exceeds 300 chars, log a warning and split it or keep original individual tasks instead.

### 2.2 Fix tools refinement for unchanged occupations (18 occupations)

Reduce `TOOL_CHUNK_SIZE` from 400 to 200 in `pts/refine.pct.py` to avoid output token limit truncation.

### 2.3 Fix task over-filtering (8 occupations)

Add to `TASK_SYSTEM_PROMPT`:
- "For occupations with many input tasks, aim to retain at least 10 distinct tasks in the output."

The mega-merge fix (2.1) will also help since over-filtering and mega-merging are intertwined — the LLM collapses many tasks into one blob, which counts as "1 task retained" despite being unusable.

### 2.4 Selective re-run

After prompt changes:
1. Delete cached responses for the ~80 affected occupations (union of mega-task + tools-unchanged + over-filtered)
2. Re-run `build_uk_dataset(refine=True)` — only uncached occupations will make API calls
3. Re-run `postprocess_dataset()` on the full output

## Phase 3 — Manual Overrides (edge cases)

For issues that no automated fix can handle.

### 3.1 Create `manual_overrides.json`

A JSON file of manual edits applied as the final pipeline step:

```json
{
  "overrides": [
    {
      "uk_soc_2020": 5311,
      "action": "remove_tasks_containing",
      "pattern": "hydraulic analysis|water supply systems|environmental impact"
    },
    {
      "uk_soc_2020": 5311,
      "action": "remove_tech_skills",
      "names": ["AutoCAD Civil 3D", "HydroCAD", "HEC-RAS", "StormCAD", "Bentley InRoads"]
    },
    {
      "uk_soc_2020": 1161,
      "action": "set_flag",
      "flag": "insufficient_source_data",
      "reason": "US O*NET military codes (55-xxxx) contain no data"
    },
    {
      "uk_soc_2020": 9222,
      "action": "set_flag",
      "flag": "insufficient_source_data",
      "reason": "Single source is 'All Other' residual O*NET code with no data"
    }
  ]
}
```

### 3.2 Apply overrides function

Add `apply_manual_overrides(occupations, overrides_path)` that processes the JSON and applies edits. Called as the very last step in `build_uk_dataset()`.

## Execution Order

1. **Phase 1** — implement `postprocess_dataset()`, wire in, re-run pipeline, verify fixes
2. **Phase 2** — update prompts, clear affected caches, re-run pipeline with refinement, verify
3. **Phase 3** — build manual overrides for remaining edge cases
4. **Verify** — re-run the automated review checks from MANUAL_CHECK_TODO.md and confirm issue counts drop

## Expected Outcome

| Phase | Issues fixed | Remaining |
|-------|-------------|-----------|
| Phase 1 | ~159 | ~38 |
| Phase 2 | ~35 | ~3 |
| Phase 3 | ~3 | 0 |
