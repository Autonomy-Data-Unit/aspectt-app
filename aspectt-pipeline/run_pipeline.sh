#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
uv run python -c "
from aspectt_pipeline.translate import build_uk_dataset
build_uk_dataset()
"
