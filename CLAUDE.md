# ASPECTT - UK O*NET Equivalent

## Project Structure

```
├── aspectt-pipeline/     # Data pipeline (nblite project)
│   ├── pts/              # Percent notebooks (edit these)
│   ├── nbs/              # Jupyter notebooks (auto-generated from pts)
│   ├── aspectt_pipeline/ # Auto-generated Python module (DO NOT EDIT)
│   ├── _dev/             # Development/intermediary work
│   │   └── 00_data_download/  # Raw data files
│   ├── nblite.toml
│   └── pyproject.toml
├── aspectt-backend/      # FastAPI backend
├── aspectt-frontend/     # Svelte frontend
└── pyproject.toml        # Root project (uv workspace)
```

## Environment Management

**Always use `uv` to manage virtual environments and dependencies.**
- Each sub-project (`aspectt-pipeline`, `aspectt-backend`) has its own `.venv`
- `cd` into the sub-project directory and use `uv sync` / `uv run` / `uv pip install` there
- Do NOT manually create venvs with `python -m venv`
- Do NOT share a single venv across sub-projects

## Pipeline (nblite)

The `aspectt-pipeline` package uses nblite for literate programming:
- Edit `.pct.py` files in `pts/`, then run `nbl export --reverse && nbl export`
- Never edit files in `aspectt_pipeline/` directly (auto-generated)
- See `NBLITE_INSTRUCTIONS.md` for full nblite documentation

## Key Data Files

- `_dev/00_data_download/onet_data/db_30_2_text/` - US O*NET v30.2 database
- `_dev/00_data_download/soc2020volume2thecodingindexexcel03122025.xlsx` - UK SOC 2020 coding index
- `_dev/00_data_download/ISCO_SOC_Crosswalk.xls` - BLS ISCO-08 ↔ US SOC 2010
- `_dev/00_data_download/soc_2010_to_2018_crosswalk.xlsx` - BLS SOC 2010 → 2018

## Crosswalk Chain

US O*NET SOC → US SOC 2018 → US SOC 2010 → ISCO-08 → UK SOC 2020

Each UK SOC code is a "superposition" of contributing US O*NET codes, with data averaged/combined using uniform weights.

## Deployment

The app is deployed via **AppGarden** using a Dockerfile. Config is in `appgarden.toml`.

- **Production URL:** https://aspectt.apps.autonomy.work
- **Server:** `adu-apps`
- **Deploy command:** `appgarden deploy production`
- **Method:** Dockerfile (builds backend + frontend into a single container on port 8000)

After making frontend or backend changes, rebuild the frontend (`cd aspectt-frontend && npm run build`) then deploy.

## Retrieving GitHub Issue Images

GitHub issue images (user-attachments URLs) require authentication. To download and view them:

```bash
# Download image via authenticated gh API
gh api -H "Accept: application/octet-stream" "https://github.com/user-attachments/assets/<asset-id>" > /tmp/image.png

# Then use the Read tool to view the image
```
