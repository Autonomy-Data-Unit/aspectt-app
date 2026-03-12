# ASPECTT

**The UK's multidimensional occupations database.**

ASPECTT provides detailed skills, tasks, abilities, knowledge, technology and work characteristics for 412 UK occupations, classified under SOC 2020. It fills the gap left by the absence of a UK equivalent to the US [O\*NET](https://www.onetonline.org/) system, adapting O\*NET data for a UK context through a chain of standard occupation code crosswalks.

**Live site:** https://aspectt.apps.autonomy.work

Built by the [Autonomy Data Unit](https://autonomy.work/adu/) at the [Autonomy Institute](https://autonomy.work/). Source code on [GitHub](https://github.com/Autonomy-Data-Unit/aspectt-app).

## Project structure

```
├── aspectt-pipeline/        # Data pipeline (nblite literate programming)
│   ├── pts/                 # Source notebooks (.pct.py) — edit these
│   ├── nbs/                 # Jupyter notebooks (auto-generated)
│   ├── aspectt_pipeline/    # Python module (auto-generated, do not edit)
│   ├── _dev/                # Raw source data files
│   │   └── 00_data_download/
│   └── data/uk_onet/        # Pipeline output (per-occupation JSON)
├── aspectt-backend/         # FastAPI backend (single-file API server)
├── aspectt-frontend/        # SvelteKit frontend (static site)
├── Dockerfile               # Multi-stage production build
├── appgarden.toml           # AppGarden deployment config
├── run.sh                   # Start full local dev stack
└── pyproject.toml           # Root workspace (uv)
```

## Tech stack

| Component | Technologies |
|-----------|-------------|
| **Frontend** | SvelteKit, Svelte 5, TypeScript, Vite, adapter-static |
| **Backend** | FastAPI, Uvicorn, Python 3.12 |
| **Pipeline** | nblite, pandas, Pydantic, adulib (LLM caching) |
| **Deployment** | Docker (multi-stage), AppGarden |
| **Package management** | uv (Python), npm (frontend) |

## Getting started

### Prerequisites

- Python 3.10+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/) package manager

### Quick start

```bash
# Install dependencies for both backend and frontend
cd aspectt-backend && uv sync && cd ..
cd aspectt-frontend && npm install && cd ..

# Start the full stack
./run.sh
```

This starts:
- **Frontend** at http://localhost:5173
- **Backend** at http://localhost:8000
- **API docs** at http://localhost:8000/docs

### Running components individually

**Backend:**

```bash
cd aspectt-backend
uv sync
uv run uvicorn main:app --reload --port 8000
```

**Frontend:**

```bash
cd aspectt-frontend
npm install
npm run dev
```

**Pipeline:**

```bash
cd aspectt-pipeline
uv sync
nbl export           # Generate Python module from notebooks
```

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ASPECTT_DATA_DIR` | `../aspectt-pipeline/data/uk_onet` | Path to pipeline output data |
| `ASPECTT_STATIC_DIR` | (none) | Path to built frontend static files (production) |
| `RATE_LIMIT_REQUESTS` | `60` | API requests per window per client IP |
| `RATE_LIMIT_WINDOW` | `60` | Rate limit window in seconds |

## Data pipeline

The pipeline transforms US O\*NET occupational data into UK SOC 2020-classified occupations through five notebooks in `aspectt-pipeline/pts/`:

| Notebook | Purpose |
|----------|---------|
| `const.pct.py` | Constants and configuration |
| `crosswalk.pct.py` | Build the four-step crosswalk chain |
| `translate.pct.py` | Combine source data into UK occupations |
| `refine.pct.py` | LLM-based filtering and deduplication |
| `postprocess.pct.py` | Final output formatting |

### Crosswalk chain

```
US O*NET SOC → US SOC 2018 → US SOC 2010 → ISCO-08 → UK SOC 2020
```

Each UK SOC code maps to one or more US O\*NET occupations. Rated data (skills, abilities, knowledge, etc.) is averaged across sources using uniform weights. Discrete data (tasks, technologies, tools) is collected and deduplicated.

### LLM refinement

An optional refinement step uses an LLM to:
- Filter irrelevant technology skills and tools inherited through the crosswalk
- Deduplicate overlapping task statements
- Remove clearly US-specific items

All LLM responses are cached to disk via adulib, so reruns are fast and deterministic.

### Source data

| Source | Description |
|--------|-------------|
| [US O\*NET v30.2](https://www.onetcenter.org/database.html) | 923 occupations with full occupational profiles |
| [UK SOC 2020 coding index](https://www.ons.gov.uk/methodology/classificationsandstandards/standardoccupationalclassificationsoc/soc2020) | 412 unit groups with embedded ISCO-08 codes |
| [BLS ISCO-08 ↔ SOC 2010 crosswalk](https://www.bls.gov/soc/) | International to US classification mapping |
| [BLS SOC 2010 → 2018 crosswalk](https://www.bls.gov/soc/) | US SOC edition mapping |

### Data categories

Each occupation includes:

- **Skills** — developed capacities that facilitate learning or performance
- **Abilities** — enduring attributes that influence performance
- **Knowledge** — organised sets of principles and facts
- **Tasks** — specific work activities (core, supplemental, emerging)
- **Technology skills** — software and technologies used
- **Tools used** — physical tools and equipment
- **Work activities** — general types of job behaviour
- **Work context** — physical and social conditions of work
- **Work styles** — personal characteristics relevant to performance
- **Interests** — Holland (RIASEC) interest profiles
- **Work values** — what workers in the occupation tend to value
- **Education** — typical preparation level required
- **Related occupations** — links to similar UK SOC codes

## API

The backend exposes a REST API. Full interactive documentation is available at `/docs` (Swagger UI) when running the backend.

Key endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /api/occupations` | List/search occupations (title, SOC code, filters) |
| `GET /api/occupations/{soc_code}` | Full occupation profile |
| `GET /api/browse/major-groups` | 9 SOC 2020 major groups |
| `GET /api/browse/job-zones` | Occupations by preparation level |
| `GET /api/browse/interests` | RIASEC interest profiles |
| `GET /api/browse/descriptors/{category}` | Browse skills, abilities, knowledge, etc. |
| `GET /api/browse/technology-skills` | All technology skills |
| `GET /api/browse/tools-used` | All tools and equipment |
| `GET /api/search/tasks` | Full-text task search |
| `GET /api/search/skills` | Search by skill name |
| `GET /api/search/technology-skills` | Search by technology |
| `GET /api/search/tools-used` | Search by tool/equipment |
| `GET /api/compare?codes=X,Y,Z` | Compare 2–4 occupations |
| `GET /api/crosswalk` | View/filter crosswalk mappings |
| `GET /api/stats` | Dataset statistics |

## Deployment

ASPECTT is deployed via [AppGarden](https://github.com/AutonomyInstitute/appgarden) using a multi-stage Dockerfile that builds the frontend and backend into a single container serving on port 8000.

```bash
# Build the frontend first
cd aspectt-frontend && npm run build && cd ..

# Deploy to production
appgarden deploy production
```

The Docker build:
1. **Stage 1** (Node 20): builds the SvelteKit frontend to static files
2. **Stage 2** (Python 3.12): runs FastAPI with Uvicorn, serving the frontend as static assets and the API under `/api`

## nblite workflow

The pipeline uses [nblite](https://github.com/AnswerDotAI/nblite) for literate programming. Source code lives in `.pct.py` files (percent-format notebooks) in `pts/`.

```bash
cd aspectt-pipeline

# After editing .pct.py files:
nbl export --reverse   # Sync to .ipynb
nbl export             # Generate Python module

# Never edit files in aspectt_pipeline/ directly
```

Key directives in `.pct.py` files:
- `#|default_exp module_name` — set the export target module
- `#|export` — include cell in the generated module
- `#|hide` — exclude from documentation
- `#|eval: false` — skip execution

## Known limitations

- **US-source bias** — all data originates from US O\*NET and may not fully reflect UK labour market conditions
- **Crosswalk noise** — the four-step mapping can assign tangentially related data to UK occupations
- **ISCO-08 granularity** — ISCO-08 is coarser than either US SOC or UK SOC, limiting mapping precision
- **Uniform weighting** — source occupations are combined with equal weights regardless of similarity
- **Work styles and interests** — sourced from interviews with US workers, not UK workers

## Licence

This work is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

## Contact

For inquiries or to commission bespoke occupational analysis using ASPECTT data: [aspectt@autonomy.work](mailto:aspectt@autonomy.work)
