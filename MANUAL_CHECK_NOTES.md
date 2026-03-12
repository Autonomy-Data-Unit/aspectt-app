# MANUAL_CHECK_NOTES

Notes from systematic review of the ASPECTT pipeline output. Identifies issues, patterns, and potential pipeline improvements.

## Summary Statistics

**215 occupations OK, 197 occupations with issues** (out of 412 total)

| Issue | Count | Description |
|-------|-------|-------------|
| NAN-TYPE | 69 | Tasks with task_type="nan" instead of Core/Supplemental |
| MEGA-TASK | 66 | Contains a task >1000 chars (improper LLM merging) |
| US-TERMS | 50 | Tasks containing US-specific terms ("federal", OSHA, etc.) |
| TOOLS-UNCHANGED | 18 | Tools not refined at all (>50 tools, 0 change) |
| US-TECH | 15 | Tech skills contain US-specific tool names |
| LLM-ARTIFACT-IN-TASK | 13 | LLM refinement instructions leaked into task text |
| ESSENTIAL-TECH-REMOVED | 12 | 3+ essential generic tools (MS Office, etc.) wrongly removed |
| TASK-OVERFILTER | 8 | Tasks reduced by >95% during LLM refinement |
| EMPTY-TASK | 4 | Contains a blank or placeholder task |
| WRONG-DOMAIN-FIRE-TASK | 12 | Contains firefighting tasks in non-fire occupation |
| GAMBLING-TASK | 8 | Contains gambling/casino tasks in non-gambling occupation |
| NO-DATA | 2 | No discrete data in source O*NET occupations |
| TECH-OVERFILTER | 2 | Tech skills reduced by >95% during LLM refinement |
| NAN-PREFIX-IN-TASK | 1 | Task text starts with literal [nan] prefix |

---

## Issue 1: Task mega-merging (66 occupations)

**Problem:** The LLM merges dozens of distinct tasks into single enormous blobs rather than keeping them as separate items. 154 occupations have at least one task >500 characters; 66 have tasks >1000 characters.

**Worst examples:**
- 3582 Health and safety managers and officers: 5,473 chars in one task
- 5311 Steel erectors: 5,172 chars in one task
- 2419 Legal professionals n.e.c.: 4,903 chars in one task
- 9132 Packers, bottlers, canners and fillers: 3,838 chars
- 6116 Nannies and au pairs: 1,842 chars
- 7211 Call and contact centre occupations: 1,796 chars

**Root cause:** The task system prompt says "Merge near-duplicate tasks into a single clear statement" but the LLM interprets "near-duplicate" too broadly, concatenating all tasks about a general topic (e.g., "patient care") into one run-on paragraph.

**Suggested fix:** Add constraints to the task refinement prompt:
- "Each merged task should combine at most 3-5 very similar original tasks"
- "A merged task should be a single, clear sentence — not a paragraph"
- "Do NOT merge tasks just because they relate to the same topic area"
- Add a post-processing step that splits any task >300 chars back into separate tasks (or flags for review)

---

## Issue 2: Over-aggressive task filtering (11 occupations)

**Problem:** Some occupations lost >95% of their tasks, leaving only 1-4 tasks (often mega-merged blobs).

| SOC | Title | Before | After |
|-----|-------|--------|-------|
| 2254 | Medical radiographers | 141 | 1 |
| 7211 | Call and contact centre occupations | 124 | 1 |
| 6137 | Care escorts | 201 | 2 |
| 6116 | Nannies and au pairs | 98 | 1 |
| 9131 | Industrial cleaning process occupations | 336 | 4 |
| 5311 | Steel erectors | 119 | 3 |
| 9132 | Packers, bottlers, canners and fillers | 61 | 2 |
| 5224 | Precision instrument makers and repairers | 72 | 3 |
| 9232 | School midday and crossing patrol occupations | 225 | 8 |
| 1223 | Publicans and managers of licensed premises | 299 | 12 |
| 4134 | Transport and distribution clerks and assistants | 145 | 7 |

**Detailed findings:**

**2254 Medical radiographers:** Source occupations include Photographers (correctly irrelevant), but also Radiation Therapists, MRI Technologists, Radiologic Technicians — all clearly relevant. The LLM merged everything into one 757-char blob and removed all individual radiology tasks like "Operate MRI scanners", "Position patients", "Inspect images for quality".

**7211 Call and contact centre:** 7 sources including Customer Service Reps (w=0.50), Switchboard Operators, Telephone Operators. Nearly all are directly relevant. All merged into one 1,796-char blob.

**6116 Nannies and au pairs:** Sources are Childcare Workers and Nannies — almost entirely relevant. Core tasks like "Transport children", "Dress children and change diapers", "Maintain safe play environment" were all merged into one blob.

**5311 Steel erectors:** The LLM kept civil engineering tasks (hydraulic analysis, transportation planning) but merged all actual steel erection tasks into one 5,172-char blob. This is incorrect prioritisation — the civil engineering tasks should have been removed, not the steel erection tasks.

**Suggested fix:**
- Add minimum task count guard: "The final output should contain at least 10 tasks for any occupation that had 50+ input tasks"
- Improve the prompt to distinguish between "tasks from a relevant source occupation" vs "tasks from an irrelevant source occupation"
- Consider a two-phase approach: first classify source occupations as relevant/irrelevant to the UK title, then filter tasks

---

## Issue 3: Over-aggressive tech skill filtering (7 occupations)

| SOC | Title | Before | After |
|-----|-------|--------|-------|
| 9121 | Groundworkers | 62 | 1 |
| 7112 | Retail cashiers | 53 | 2 |
| 2161 | R&D managers | 794 | 37 |
| 4152 | Data entry administrators | 865 | 39 |
| 6240 | Cleaning and housekeeping managers | 386 | 19 |
| 8112 | Textile process operatives | 245 | 10 |
| 9129 | Elementary construction occupations n.e.c. | 348 | 16 |

**9121 Groundworkers:** Only "Web browser software" survives from 62 items. Microsoft Office, Microsoft Excel, cost estimating software were all removed despite the system prompt explicitly saying "Generic tools (Microsoft Office, email clients, web browsers) are relevant to almost all occupations."

**7112 Retail cashiers:** Only POS software and Barcode software remain from 53. Microsoft Office, spreadsheet software, and inventory management systems were removed.

**Root cause:** gpt-4o-mini does not reliably follow the "be conservative / keep generic tools" instruction.

**Suggested fix:**
- Add a post-processing safeguard: always keep items matching a whitelist of generic software (Microsoft Office, Excel, Word, Outlook, email clients, web browsers) regardless of LLM verdict
- Consider using a larger model (gpt-4o) for occupations with >200 tech skills

---

## Issue 4: Tools not refined for 39 occupations (TOOLS-UNCHANGED)

**Problem:** 39 occupations with >10 tools show zero change between unrefined and refined data. This includes:
- 5449 Other skilled trades n.e.c.: 3,312 tools (unchanged)
- 2127 Engineering project managers: 1,083 tools (unchanged)
- 8133 Energy plant operatives: 803 tools (unchanged)
- 8114 Plastics process operatives: 474 tools (unchanged)
- 9111 Farm workers: 362 tools (unchanged)
- 9261 Bar and catering supervisors: 323 tools (unchanged)
- 6231 Housekeepers and related: 279 tools (unchanged)
- 2126 Aerospace engineers: 250 tools (unchanged)
- 1122 Production managers in construction: 247 tools (unchanged)
- 2322 Education managers: 217 tools (unchanged)

**Root cause:** The refinement log showed SOC 5449 failed due to JSON response truncation (1,738 tools exceeded output token limit). The `refine_occupation()` function catches all exceptions and keeps original data. The same likely applies to other occupations with large tool lists, or the LLM returned all-relevant verdicts.

**Suggested fix:**
- Reduce `TOOL_CHUNK_SIZE` from 400 to ~200 to avoid output token limits
- Log which occupations had refinement failures (currently silently kept)
- Re-run refinement for these occupations after fixing chunking

---

## Issue 5: "nan" task_type in 65 occupations

**Problem:** 65 occupations have tasks where `task_type` is the string `"nan"` instead of `"Core"` or `"Supplemental"`.

**Root cause:** 845 tasks in the raw O*NET data (`Task Statements.txt`) have `NULL` task_type across 86 O*NET occupations. In the translation pipeline, these become `None` in the unrefined JSON. When the LLM refinement processes them, it sees the string `[nan]` in the input prompt and outputs `"nan"` as the task_type string.

**Suggested fix:**
- In `translate_task_statements()`, replace `None`/`NaN` task_type with a default value (e.g., `"Core"` or `"Unclassified"`)
- In the refinement output processing, map `"nan"` back to `"Unclassified"` as a safety net
- The 845 source tasks are from newer O*NET updates (O*NET-SOC codes like 15-1255, 13-2054) where task type classification may not yet be complete

---

## Issue 6: US-specific terminology surviving refinement

**Problem:** Refined tasks contain US-specific terms that don't apply to UK occupations.

**Examples:**
- "Apply for **federal** funding for emergency-management-related needs" (1111)
- "Train local groups in preparing long-term plans compatible with **federal and state** plans" (1111)
- "Seek **federal** funding for local projects and programs" (1112)
- "Meet with **federal, state, and local agencies**" (2311)
- "Advise clients or community groups on... **Medicaid**" (3219)
- **SEVIS** (Student and Exchange Visitor Information System) in tech skills for 2311

Total: 69 tasks contain "federal", plus scattered references to US-specific agencies and programs.

**Suggested fix:**
- Add to the LLM task refinement prompt: "Replace US-specific terminology with UK equivalents where possible (e.g., 'federal/state' → 'central/local government', 'OSHA' → 'HSE')"
- Or add a deterministic post-processing step with common US→UK term substitutions
- Consider an additional post-processing pass: a simpler find-and-replace for known US→UK terminology

---

## Issue 7: Questionable crosswalk mappings

Some UK SOC codes receive source occupations that are clearly inappropriate. This is a crosswalk-level issue (not refinement), but the refinement step should ideally handle it.

**Examples:**
- **5241 Electricians:** Sources include Disc Jockeys (w=0.10), Costume Attendants (w=0.10), Artists (w=0.10), Entertainers (w=0.10)
- **1111 Chief executives:** Emergency Management Directors (w=0.25) is the highest-weighted source, causing emergency/disaster management tasks to dominate
- **5313 Bricklayers:** Sources include Solar PV Installers, Hazmat Workers, Weatherization Installers
- **7111 Sales and retail assistants:** Sources include Fast Food Workers, Baristas, Motion Picture Projectionists
- **5311 Steel erectors:** Sources include 3 Civil Engineer variants (w=0.11 each) that dominate the profile

**Note:** These are upstream crosswalk artifacts from the 4-step mapping chain. The LLM refinement partially handles them (removing irrelevant tech/tools), but sometimes keeps the wrong items (see Steel erectors keeping civil engineering content).

**Suggested fix:**
- Consider a manual crosswalk override table for the worst mappings
- Could add a pipeline step where the LLM first classifies source occupations as relevant/irrelevant to the UK title, then only includes data from relevant sources

---

## Issue 8: No data for 2 occupations

- **1161 Officers in armed forces:** 8 source O*NET codes are all military (55-xxxx). The US O*NET database has zero data for military occupations — they are placeholder codes with no content.
- **9222 Street cleaners:** Single source is `37-3019.00` (Grounds Maintenance Workers, All Other), an "All Other" residual code with no data.

**Suggested fix:** These are limitations of the source data. Could add manual data for these occupations in a post-processing step, or flag them as "insufficient data" in the output.

---

## Issue 9: Near-duplicate tasks surviving refinement

Some occupations have clearly duplicate tasks that survived both LLM merging and Jaccard dedup.

**Example from 2311 (Higher education teaching):**
- "Plan, evaluate, and revise curricula, course content, course materials, and methods of instruction."
- "Plan, evaluate, and revise curricula, course content, and course materials and methods of instruction."

These differ by a single comma and conjunction but were not caught because they come from different chunks.

**Suggested fix:**
- Lower the Jaccard dedup threshold from 0.85 to ~0.75
- Or add a fuzzy string matching pass (e.g., Levenshtein ratio >0.90) in addition to Jaccard

---

## Issue 10: Wrong items kept during refinement (5311 Steel erectors)

**Problem:** The LLM kept items from the wrong source occupations. For SOC 5311 (Steel erectors):
- **Kept:** Civil engineering CAD software (AutoCAD Civil 3D, Bentley InRoads, HydroCAD, HEC-RAS, StormCAD), hydraulic analysis tasks, environmental impact assessment tasks
- **Removed:** Steel/rebar-specific software (aSa Rebar, RebarWin), individual steel erection tasks

The LLM appears to have been confused about which source occupations were relevant, favouring the higher-prestige Civil Engineering content over the actual steel erection content.

**Suggested fix:** This is partially addressed by the "two-phase refinement" suggestion in Issue 2 — first classify source occupations as relevant, then filter items.

---

## Issue 11: LLM refinement instructions leaked into task text (13 occupations)

**Problem:** The LLM's own reasoning or instructions appear verbatim in the final task text. Instead of filtering tasks, it wrote its reasoning as the task content.

**Examples:**
- 3572 Careers advisers: task starts with "Remove irrelevant tasks. [Task removed: ..."
- 3549 Business associate professionals: 5 tasks prefixed with "[Removed]"
- 3555 Estate agents and auctioneers: "Remove irrelevant tasks regarding project management..."
- 3417 Photographers/broadcasting: "Remove tasks not relevant to photographic, audio-visual..."
- 9132 Packers: task with task_type "Irrelevant" still in output
- 9226 Parking: "Remove irrelevant tasks related to machine operations..."
- 2440 Business/financial project management: "[REDACTED]", "[REMOVED]" markup in task text

**Root cause:** gpt-4o-mini occasionally outputs its reasoning or removal annotations as part of the structured JSON response, and the pipeline doesn't filter these out.

**Suggested fix:**
- Add post-processing to detect and remove tasks containing "Remove irrelevant", "[REMOVED]", "[REDACTED]", or task_type="Irrelevant"
- Consider adding a validation step that checks task text doesn't contain LLM meta-language

---

## Issue 12: Wrong-domain tasks surviving refinement (20+ occupations)

**Problem:** Tasks from clearly irrelevant source occupations survive the LLM refinement step.

**Gambling tasks in non-gambling occupations (8 occupations):**
- 1223 Publicans: gambling table monitoring tasks
- 4129 Financial admin: gambling/gaming tasks
- 4131 Records clerks: gambling + slaughterhouse tasks
- 7112 Retail cashiers: gambling tasks retained
- 7115 Pharmacy assistants: gambling tasks
- 6211 Sports and leisure assistants: gambling tasks

**Firefighting tasks in non-fire occupations (12 occupations):**
- 3114 Building/civil engineering technicians: arson investigation, fire suppression tasks
- 3312 Police officers: photonics/laser tasks from wrong source
- 5112 Horticultural trades: fire crew tasks
- 2452-2454 Librarians/archivists: fire service tasks
- Plus several others

**Other wrong-domain examples:**
- 3214 Complementary health: farm animal genetics, agricultural research tasks
- 3415 Musicians: film editing tasks
- 4111 National government admin: slaughterhouse monitoring
- 5224 Precision instruments: "Install medical equipment"

**Root cause:** The LLM refinement sometimes keeps tasks that are vaguely related but from clearly wrong source occupations. The one-phase approach (filter individual tasks without considering source occupation relevance) is insufficient.

**Suggested fix:** Two-phase refinement (P7) would address this. Alternatively, add source occupation context to each task in the refinement prompt so the LLM can see where each task comes from.

---

## Proposed Pipeline Improvements (Priority Order)

### P1 — Fix task mega-merging
Constrain the task prompt to prevent mega-merges. Add max merge size (3-5 tasks) and max task length (~200 chars). Add post-processing to split oversized tasks.

### P2 — Fix "nan" task_type
Default null task types to "Unclassified" during translation. Clean up "nan" strings in refinement output.

### P3 — Fix tools refinement for 39 unchanged occupations
Reduce TOOL_CHUNK_SIZE to ~200. Add explicit logging for refinement failures. Re-run.

### P4 — Add generic software whitelist
Always keep Microsoft Office, email clients, web browsers regardless of LLM verdict. Prevents the Groundworkers/Retail cashiers problem.

### P5 — US→UK terminology post-processing
Add deterministic text substitutions: federal→central government, state→devolved government, OSHA→HSE, etc.

### P6 — Lower Jaccard dedup threshold
Reduce from 0.85 to 0.75 and/or add fuzzy string matching.

### P7 — Consider two-phase refinement
First classify source occupations as relevant/irrelevant, then only filter items from relevant sources. This would fix the Steel erectors problem.

### P8 — Remove LLM artifacts from task text
Post-processing pass to remove tasks containing "Remove irrelevant", "[REMOVED]", "[REDACTED]", or task_type="Irrelevant". 13 occupations affected.

### P9 — Wrong-domain task filtering
Add source occupation info to the task refinement prompt so the LLM can identify which tasks come from which source, improving domain filtering. 20+ occupations affected by gambling, firefighting, or other wrong-domain tasks.

### P10 — Manual overrides system
Add a JSON file of manual edits (add task X to occupation Y, remove item Z from occupation W, override crosswalk for occupation V). Apply as a final pipeline step.

---

## Per-Occupation Notes

Automated notes for all 197 occupations with issues. Sorted by SOC code.

### 1111 Chief executives and senior officials
- US-specific terms in tasks: federal.

### 1112 Elected officers and representatives
- US-specific terms in tasks: federal.

### 1122 Production managers and directors in construction
- 1 mega-merged task(s), longest 1362 chars.
- 247 tools unchanged after refinement (likely failed or all-relevant).

### 1123 Production managers and directors in mining and energy
- 8 tasks with nan/missing task_type.

### 1131 Financial managers and directors
- US-specific terms in tasks: federal.

### 1132 Marketing, sales and advertising directors
- LLM instruction leaked into task: "Remove tasks that are irrelevant or not applicable to the marketing, sales and a..."

### 1135 Charitable organisation managers and directors
- 1 mega-merged task(s), longest 1362 chars.
- US-specific terms in tasks: federal.

### 1137 Information technology directors
- 2 tasks with nan/missing task_type.

### 1139 Functional managers and directors n.e.c.
- US-specific terms in tasks: federal.

### 1140 Directors in logistics, warehousing and transport
- 3 tasks with nan/missing task_type.

### 1161 Officers in armed forces
- No data in source O*NET occupations.

### 1172 Social services managers and directors
- US-specific terms in tasks: federal.

### 1211 Managers and proprietors in agriculture and horticulture
- US-specific terms in tasks: federal.

### 1212 Managers and proprietors in forestry, fishing and related services
- 8 tasks with nan/missing task_type.
- US-specific terms in tasks: federal.

### 1223 Publicans and managers of licensed premises
- 1 mega-merged task(s), longest 1740 chars.
- Contains gambling/casino tasks from wrong source occupation.

### 1224 Leisure and sports managers and proprietors
- US-specific terms in tasks: federal.

### 1225 Travel agency managers and proprietors
- 1 tasks with nan/missing task_type.

### 1242 Managers in storage and warehousing
- 1 tasks with nan/missing task_type.

### 1251 Property, housing and estate managers
- 1 tasks with nan/missing task_type.

### 1254 Waste disposal and environmental services managers
- 5 tasks with nan/missing task_type.
- 168 tools unchanged after refinement (likely failed or all-relevant).

### 1255 Managers and directors in the creative industries
- Contains gambling/casino tasks from wrong source occupation.

### 1257 Hire services managers and proprietors
- Contains gambling/casino tasks from wrong source occupation.

### 1258 Directors in consultancy services
- 1 tasks with nan/missing task_type.

### 1259 Managers and proprietors in other services n.e.c.
- 1 tasks with nan/missing task_type.
- US-specific terms in tasks: federal.

### 2113 Biochemists and biomedical scientists
- 1 mega-merged task(s), longest 1440 chars.

### 2114 Physical scientists
- US-specific terms in tasks: state government.

### 2121 Civil engineers
- US-specific tech: EPA Storm Water Management Model SWMM.

### 2122 Mechanical engineers (professional)
- US-specific tech: Federal Renewable Energy Screening Assistant FRESA.

### 2124 Electronics engineers (professional)
- 1 mega-merged task(s), longest 1017 chars.
- 63 tools unchanged after refinement (likely failed or all-relevant).

### 2125 Production and process engineers
- 1 mega-merged task(s), longest 1123 chars.
- LLM instruction leaked into task: "Remove tasks clearly irrelevant to this occupation...."

### 2126 Aerospace engineers
- 250 tools unchanged after refinement (likely failed or all-relevant).

### 2127 Engineering project managers and project engineers
- US-specific tech: Federal Renewable Energy Screening Assistant FRESA.
- 1083 tools unchanged after refinement (likely failed or all-relevant).

### 2129 Engineering professionals n.e.c.
- 6 mega-merged task(s), longest 4757 chars.
- 3 tasks with nan/missing task_type.
- LLM instruction leaked into task: "Remove irrelevant tasks: Collaborate with search engine shopping specialists to ..."
- US-specific terms in tasks: federal.

### 2131 IT project managers
- 9 tasks with nan/missing task_type.
- Contains empty or placeholder task.

### 2133 IT business analysts, architects and systems designers
- 4 tasks with nan/missing task_type.

### 2134 Programmers and software development professionals
- 1 mega-merged task(s), longest 1062 chars.
- 5 tasks with nan/missing task_type.

### 2135 Cyber security professionals
- 1 mega-merged task(s), longest 1684 chars.
- 2 tasks with nan/missing task_type.

### 2139 Information technology professionals n.e.c.
- 21 tasks with nan/missing task_type.

### 2141 Web design professionals
- 1 mega-merged task(s), longest 1053 chars.
- 4 tasks with nan/missing task_type.

### 2142 Graphic and multimedia designers
- 1 mega-merged task(s), longest 1021 chars.
- 1 tasks with nan/missing task_type.

### 2151 Conservation professionals
- 1 mega-merged task(s), longest 1092 chars.
- US-specific terms in tasks: federal.
- US-specific tech: U.S. Department of Agriculture USDA WinSRM, USDA NRCS Soil Data Viewer.

### 2152 Environment professionals
- US-specific terms in tasks: federal.

### 2161 Research and development (R&D) managers
- 2 tasks with nan/missing task_type.

### 2162 Other researchers, unspecified discipline
- US-specific tech: U.S. Department of Agriculture USDA National Nutrient Database.

### 2223 Speech and language therapists
- 73 tools unchanged after refinement (likely failed or all-relevant).

### 2229 Therapy professionals n.e.c.
- US-specific terms in tasks: federal.
- US-specific tech: USDA Child Nutrition Database, U.S. Department of Agriculture USDA National Nutrient Database.

### 2237 Other registered nursing professionals
- 1 tasks with nan/missing task_type.

### 2254 Medical radiographers
- Severe task over-filtering: 141 -> 1 tasks.

### 2256 Podiatrists
- 1 mega-merged task(s), longest 1145 chars.

### 2259 Other health professionals n.e.c.
- US-specific tech: U.S. Department of Agriculture USDA National Nutrient Database.

### 2311 Higher education teaching professionals
- US-specific tech: Student and Exchange Visitor Information System SEVIS.

### 2315 Nursery education teaching professionals
- 1 tasks with nan/missing task_type.
- US-specific terms in tasks: federal.

### 2316 Special and additional needs education teaching professionals
- 139 tools unchanged after refinement (likely failed or all-relevant).

### 2319 Teaching professionals n.e.c.
- US-specific terms in tasks: federal.

### 2321 Head teachers and principals
- US-specific terms in tasks: federal.

### 2322 Education managers
- 1 mega-merged task(s), longest 1017 chars.
- 217 tools unchanged after refinement (likely failed or all-relevant).

### 2323 Education advisers and school inspectors
- 7 tasks with nan/missing task_type.
- US-specific terms in tasks: federal.

### 2324 Early education and childcare services managers
- 2 tasks with nan/missing task_type.
- LLM instruction leaked into task: "Remove irrelevant or duplicate tasks related to other occupations and maintain o..."
- US-specific terms in tasks: federal.

### 2329 Other educational professionals n.e.c
- US-specific terms in tasks: federal.

### 2412 Solicitors and lawyers
- US-specific terms in tasks: federal.

### 2419 Legal professionals n.e.c.
- 2 mega-merged task(s), longest 4903 chars.

### 2421 Chartered and certified accountants
- US-specific terms in tasks: federal.

### 2422 Finance and investment analysts and advisers
- US-specific terms in tasks: federal.

### 2433 Actuaries, economists and statisticians
- 13 tasks with nan/missing task_type.
- US-specific terms in tasks: federal.

### 2434 Business and related research professionals
- 3 mega-merged task(s), longest 2520 chars.
- 2 tasks with nan/missing task_type.

### 2435 Professional/Chartered company secretaries
- US-specific terms in tasks: federal.

### 2439 Business, research and administrative professionals n.e.c.
- 1 mega-merged task(s), longest 1133 chars.
- 7 tasks with nan/missing task_type.

### 2440 Business and financial project management professionals
- 1 mega-merged task(s), longest 1098 chars.
- 1 tasks with nan/missing task_type.
- LLM instruction leaked into task: "Remove irrelevant core tasks related to delivering death certificates, preparing..."

### 2452 Chartered architectural technologists, planning officers and consultants
- 1 mega-merged task(s), longest 1281 chars.
- Contains firefighting tasks from wrong source occupation.

### 2453 Quantity surveyors
- 7 tasks with nan/missing task_type.
- US-specific tech: Federal Renewable Energy Screening Assistant FRESA.
- Contains firefighting tasks from wrong source occupation.

### 2454 Chartered surveyors
- Contains firefighting tasks from wrong source occupation.

### 2455 Construction project managers and related professionals
- US-specific tech: EPA Storm Water Management Model SWMM, Federal Renewable Energy Screening Assistant FRESA.

### 2481 Quality control and planning engineers
- Contains firefighting tasks from wrong source occupation.

### 2482 Quality assurance and regulatory professionals
- US-specific terms in tasks: federal.

### 3111 Laboratory technicians
- 3 tasks with nan/missing task_type.
- Contains firefighting tasks from wrong source occupation.

### 3114 Building and civil engineering technicians
- 1 tasks with nan/missing task_type.
- Contains firefighting tasks from wrong source occupation.

### 3115 Quality assurance technicians
- 1 mega-merged task(s), longest 1068 chars.
- 4 tasks with nan/missing task_type.

### 3119 Science, engineering and production technicians n.e.c.
- Contains firefighting tasks from wrong source occupation.

### 3120 CAD, drawing and architectural technicians
- Contains firefighting tasks from wrong source occupation.

### 3132 IT user support technicians
- 67 tools unchanged after refinement (likely failed or all-relevant).

### 3133 Database administrators and web content technicians
- 3 tasks with nan/missing task_type.

### 3213 Medical and dental technicians
- 3 mega-merged task(s), longest 1107 chars.
- 2 tasks with nan/missing task_type.

### 3214 Complementary health associate professionals
- 1 mega-merged task(s), longest 1092 chars.
- US-specific tech: U.S. Department of Agriculture USDA National Nutrient Database.

### 3219 Health associate professionals n.e.c.
- US-specific terms in tasks: Medicaid.

### 3222 Child and early years officers
- 1 mega-merged task(s), longest 1245 chars.
- 55 tools unchanged after refinement (likely failed or all-relevant).

### 3312 Police officers (sergeant and below)
- 1 mega-merged task(s), longest 1342 chars.

### 3319 Protective service associate professionals n.e.c.
- 1 mega-merged task(s), longest 1267 chars.
- US-specific terms in tasks: federal.
- Contains gambling/casino tasks from wrong source occupation.

### 3412 Authors, writers and translators
- LLM instruction leaked into task: "Remove tasks related to audio-visual production, such as setting up audio-visual..."

### 3415 Musicians
- 157 tools unchanged after refinement (likely failed or all-relevant).

### 3416 Arts officers, producers and directors
- 3 tasks with nan/missing task_type.

### 3417 Photographers, audio-visual and broadcasting equipment operators
- 2 mega-merged task(s), longest 1308 chars.
- LLM instruction leaked into task: "Remove tasks not relevant to photographic, audio-visual, or broadcasting equipme..."

### 3429 Design occupations n.e.c.
- 2 tasks with nan/missing task_type.

### 3431 Sports players
- Essential tech removed: Microsoft Excel, Microsoft PowerPoint, Microsoft Word.

### 3511 Aircraft pilots and air traffic controllers
- US-specific terms in tasks: federal.

### 3512 Ship and hovercraft officers
- 1 tasks with nan/missing task_type.
- US-specific terms in tasks: federal.

### 3520 Legal associate professionals
- US-specific terms in tasks: federal.

### 3533 Financial and accounting technicians
- 1 mega-merged task(s), longest 1011 chars.
- US-specific terms in tasks: federal.

### 3534 Financial accounts managers
- US-specific terms in tasks: federal.

### 3544 Data analysts
- US-specific terms in tasks: federal.

### 3549 Business associate professionals n.e.c.
- 4 mega-merged task(s), longest 1215 chars.
- 6 tasks with nan/missing task_type.

### 3554 Advertising and marketing associate professionals
- 1 mega-merged task(s), longest 1068 chars.
- 3 tasks with nan/missing task_type.

### 3555 Estate agents and auctioneers
- 1 tasks with nan/missing task_type.
- LLM instruction leaked into task: "Remove irrelevant tasks regarding project management and sustainability project ..."
- US-specific terms in tasks: federal.

### 3556 Sales accounts and business development managers
- US-specific terms in tasks: federal.

### 3557 Events managers and organisers
- US-specific terms in tasks: federal.

### 3560 Public services associate professionals
- 4 mega-merged task(s), longest 1326 chars.
- 6 tasks with nan/missing task_type.
- US-specific terms in tasks: federal.

### 3571 Human resources and industrial relations officers
- US-specific terms in tasks: federal.

### 3572 Careers advisers and vocational guidance specialists
- 2 mega-merged task(s), longest 1345 chars.
- LLM instruction leaked into task: "Remove irrelevant tasks. [Task removed: Provide food, drinking water, and field ..."

### 3581 Inspectors of standards and regulations
- 1 tasks with nan/missing task_type.
- Contains firefighting tasks from wrong source occupation.

### 3582 Health and safety managers and officers
- 2 mega-merged task(s), longest 5473 chars.
- Contains firefighting tasks from wrong source occupation.

### 4111 National government administrative occupations
- US-specific terms in tasks: federal.

### 4121 Credit controllers
- 1 tasks with nan/missing task_type.
- Contains empty or placeholder task.

### 4123 Bank and post office clerks
- 2 tasks with nan/missing task_type.

### 4129 Financial administrative occupations n.e.c.
- 2 mega-merged task(s), longest 2509 chars.
- LLM instruction leaked into task: "Remove irrelevant tasks related to customer service in retail environments, stoc..."
- Contains gambling/casino tasks from wrong source occupation.

### 4131 Records clerks and assistants
- 2 tasks with nan/missing task_type.
- Contains gambling/casino tasks from wrong source occupation.
- Contains firefighting tasks from wrong source occupation.

### 4134 Transport and distribution clerks and assistants
- 5 mega-merged task(s), longest 1438 chars.

### 4141 Office managers
- 1 tasks with nan/missing task_type.
- US-specific terms in tasks: federal.

### 4152 Data entry administrators
- 1 mega-merged task(s), longest 1672 chars.

### 4159 Other administrative occupations n.e.c.
- 3 mega-merged task(s), longest 1473 chars.

### 4212 Legal secretaries
- 1 mega-merged task(s), longest 1116 chars.

### 5111 Farmers
- 1 mega-merged task(s), longest 1283 chars.
- Contains empty or placeholder task.

### 5112 Horticultural trades
- Contains firefighting tasks from wrong source occupation.

### 5119 Agricultural and fishing trades n.e.c.
- US-specific terms in tasks: federal.
- US-specific tech: USDA Forest Vegetation Simulator FVS.

### 5211 Sheet metal workers
- 1 mega-merged task(s), longest 1513 chars.

### 5213 Welding trades
- Contains firefighting tasks from wrong source occupation.

### 5223 Metal working production and maintenance fitters and technicians
- 4 mega-merged task(s), longest 1747 chars.
- 1 tasks with nan/missing task_type.
- US-specific terms in tasks: federal.

### 5224 Precision instrument makers and repairers
- 3 mega-merged task(s), longest 3330 chars.
- Severe task over-filtering: 72 -> 3 tasks.

### 5225 Air-conditioning and refrigeration installers and repairers
- 1 tasks with nan/missing task_type.

### 5236 Rail and rolling stock builders and repairers
- 1 mega-merged task(s), longest 1350 chars.

### 5241 Electricians and electrical fitters
- 2 mega-merged task(s), longest 1190 chars.

### 5242 Telecoms and related network installers and repairers
- 1 mega-merged task(s), longest 1003 chars.

### 5311 Steel erectors
- 3 mega-merged task(s), longest 5172 chars.
- Severe task over-filtering: 119 -> 3 tasks.
- US-specific tech: EPA Storm Water Management Model SWMM.

### 5319 Construction and building trades n.e.c.
- US-specific tech: EPA Storm Water Management Model SWMM.

### 5321 Plasterers
- 2 mega-merged task(s), longest 1434 chars.

### 5323 Painters and decorators
- 5 tasks with nan/missing task_type.

### 5412 Footwear and leather working trades
- 1 mega-merged task(s), longest 1966 chars.

### 5442 Furniture makers and other craft woodworkers
- US-specific terms in tasks: federal.

### 5449 Other skilled trades n.e.c.
- 8 tasks with nan/missing task_type.
- 3312 tools unchanged after refinement (likely failed or all-relevant).

### 6111 Early education and childcare assistants
- 1 tasks with nan/missing task_type.

### 6116 Nannies and au pairs
- 1 mega-merged task(s), longest 1842 chars.
- Severe task over-filtering: 98 -> 1 tasks.

### 6132 Ambulance staff (excluding paramedics)
- 4 tasks with nan/missing task_type.

### 6137 Care escorts
- Severe task over-filtering: 201 -> 2 tasks.

### 6211 Sports and leisure assistants
- Contains gambling/casino tasks from wrong source occupation.

### 6213 Air travel assistants
- US-specific terms in tasks: federal.

### 6214 Rail travel assistants
- 1 tasks with nan/missing task_type.

### 6219 Leisure and travel service occupations n.e.c.
- 3 mega-merged task(s), longest 2215 chars.

### 6221 Hairdressers and barbers
- 61 tools unchanged after refinement (likely failed or all-relevant).

### 6222 Beauticians and related occupations
- 2 tasks with nan/missing task_type.

### 6231 Housekeepers and related occupations
- 279 tools unchanged after refinement (likely failed or all-relevant).

### 7111 Sales and retail assistants
- Essential tech removed: Microsoft Excel, Microsoft PowerPoint, Microsoft Word.

### 7112 Retail cashiers and check-out operators
- Severe tech skill over-filtering: 53 -> 2.
- Essential tech removed: Microsoft Excel, Microsoft Outlook, Microsoft PowerPoint, Microsoft Word, Web browser software.
- Contains gambling/casino tasks from wrong source occupation.

### 7115 Vehicle and parts salespersons and advisers
- Contains gambling/casino tasks from wrong source occupation.

### 7123 Roundspersons and van salespersons
- Essential tech removed: Microsoft Excel, Microsoft Outlook, Microsoft Word.

### 7131 Shopkeepers and owners - retail and wholesale
- 1 tasks with nan/missing task_type.

### 7211 Call and contact centre occupations
- 1 mega-merged task(s), longest 1796 chars.
- Severe task over-filtering: 124 -> 1 tasks.

### 7219 Customer service occupations n.e.c.
- 5 tasks with nan/missing task_type.
- US-specific terms in tasks: federal.

### 8113 Chemical and related process operatives
- 7 tasks with nan/missing task_type.

### 8114 Plastics process operatives
- 474 tools unchanged after refinement (likely failed or all-relevant).

### 8115 Metal making and treating process operatives
- 2 tasks with nan/missing task_type.

### 8119 Process operatives n.e.c.
- 6 mega-merged task(s), longest 2482 chars.

### 8120 Metal working machine operatives
- 2 mega-merged task(s), longest 1283 chars.

### 8131 Paper and wood machine operatives
- 1 mega-merged task(s), longest 1762 chars.

### 8132 Mining and quarry workers and related operatives
- Contains empty or placeholder task.

### 8133 Energy plant operatives
- 4 tasks with nan/missing task_type.
- 803 tools unchanged after refinement (likely failed or all-relevant).

### 8139 Plant and machine operatives n.e.c.
- 3 mega-merged task(s), longest 1528 chars.
- 3 tasks with nan/missing task_type.

### 8144 Weighers, graders and sorters
- 2 mega-merged task(s), longest 1154 chars.
- 3 tasks with nan/missing task_type.

### 8145 Tyre, exhaust and windscreen fitters
- Essential tech removed: Microsoft Excel, Microsoft Outlook, Microsoft PowerPoint, Microsoft Word, Web browser software.

### 8149 Assemblers and routine operatives n.e.c.
- Contains firefighting tasks from wrong source occupation.

### 8151 Scaffolders, stagers and riggers
- US-specific terms in tasks: federal.

### 8153 Rail construction and maintenance operatives
- 3 mega-merged task(s), longest 1210 chars.
- US-specific tech: EPA Storm Water Management Model SWMM.

### 8159 Construction operatives n.e.c.
- 1 mega-merged task(s), longest 1217 chars.

### 8211 Heavy and large goods vehicle drivers
- US-specific terms in tasks: federal.

### 8214 Delivery drivers and couriers
- 1 tasks with nan/missing task_type.
- Task text starts with literal [nan] prefix.

### 8221 Crane drivers
- 5 tasks with nan/missing task_type.
- Essential tech removed: Microsoft Excel, Microsoft Outlook, Microsoft PowerPoint, Microsoft Word, Web browser software.

### 8231 Train and tram drivers
- 1 tasks with nan/missing task_type.

### 8232 Marine and waterways transport operatives
- 1 mega-merged task(s), longest 1018 chars.

### 8233 Air transport operatives
- 1 mega-merged task(s), longest 1039 chars.

### 8239 Other drivers and transport operatives n.e.c.
- 3 mega-merged task(s), longest 1447 chars.

### 9111 Farm workers
- 362 tools unchanged after refinement (likely failed or all-relevant).

### 9112 Forestry and related workers
- LLM instruction leaked into task: "Remove irrelevant content related to security personnel tasks that do not align ..."

### 9121 Groundworkers
- Severe tech skill over-filtering: 62 -> 1.
- Essential tech removed: Microsoft Excel, Microsoft Outlook, Microsoft PowerPoint, Microsoft Word.

### 9129 Elementary construction occupations n.e.c.
- 2 mega-merged task(s), longest 1316 chars.
- US-specific terms in tasks: federal.

### 9131 Industrial cleaning process occupations
- Severe task over-filtering: 336 -> 4 tasks.

### 9132 Packers, bottlers, canners and fillers
- 1 mega-merged task(s), longest 3838 chars.
- 1 tasks with nan/missing task_type.
- Severe task over-filtering: 61 -> 2 tasks.
- LLM instruction leaked into task: "Remove tasks related to athletic events and sports performance that are irreleva..."

### 9211 Postal workers, mail sorters and messengers
- 1 mega-merged task(s), longest 1233 chars.
- 1 tasks with nan/missing task_type.

### 9219 Elementary administration occupations n.e.c.
- 1 mega-merged task(s), longest 2040 chars.

### 9221 Window cleaners
- Essential tech removed: Microsoft Excel, Microsoft Outlook, Microsoft Word.

### 9222 Street cleaners
- No data in source O*NET occupations.

### 9226 Vehicle valeters and cleaners
- 1 tasks with nan/missing task_type.
- LLM instruction leaked into task: "Remove irrelevant tasks related to machine operations, programming, and technica..."

### 9231 Security guards and related occupations
- Contains firefighting tasks from wrong source occupation.

### 9232 School midday and crossing patrol occupations
- 1 mega-merged task(s), longest 1388 chars.

### 9249 Elementary sales occupations n.e.c.
- 4 mega-merged task(s), longest 1516 chars.
- Essential tech removed: Microsoft Excel, Microsoft PowerPoint, Microsoft Word.

### 9261 Bar and catering supervisors
- 323 tools unchanged after refinement (likely failed or all-relevant).

### 9263 Kitchen and catering assistants
- Essential tech removed: Microsoft Excel, Microsoft Outlook, Microsoft Word, Web browser software.

### 9264 Waiters and waitresses
- 2 tasks with nan/missing task_type.

### 9266 Coffee shop workers
- Essential tech removed: Microsoft Excel, Microsoft Outlook, Microsoft Word, Web browser software.

### 9267 Leisure and theme park attendants
- 2 tasks with nan/missing task_type.
- Essential tech removed: Microsoft Excel, Microsoft Outlook, Microsoft PowerPoint, Microsoft Word.

### 9269 Other elementary services occupations n.e.c.
- 1 tasks with nan/missing task_type.

