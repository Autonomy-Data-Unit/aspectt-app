# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
#|default_exp const

# %% [markdown]
# # Pipeline constants
#
# Centralised configuration for the ASPECTT data pipeline.
# All paths, model settings, and tuning parameters live here
# so they can be changed in one place.

# %%
#|export
from pathlib import Path

# %% [markdown]
# ## Paths

# %%
#|export
DATA_DIR = Path(__file__).parent.parent / "_dev" / "00_data_download"
ONET_DIR = DATA_DIR / "onet_data" / "db_30_2_text"
OUTPUT_DIR = DATA_DIR.parent.parent / "data" / "uk_onet"

# %% [markdown]
# ## LLM settings
#
# Tech/tool filtering is a simple relevance judgement — a cheap model suffices.
# Task deduplication requires more semantic understanding, so uses a stronger model.

# %%
#|export
TECH_FILTER_MODEL = "gpt-5-mini"
TOOL_FILTER_MODEL = "gpt-5-mini"
TASK_REFINE_MODEL = "gpt-5-mini"
CONCURRENCY_LIMIT = 10

# %% [markdown]
# ## Refinement tuning
#
# Large item lists are split into chunks before being sent to the LLM.
# These sizes balance context-window utilisation against response quality.
# After chunked task refinement, a deterministic Jaccard word-overlap pass
# merges any cross-chunk duplicates that the LLM couldn't see together.

# %%
#|export
TECH_CHUNK_SIZE = 400
TOOL_CHUNK_SIZE = 200
TASK_CHUNK_SIZE = 150
JACCARD_DEDUP_THRESHOLD = 0.85

# %% [markdown]
# ## Valid task types
#
# O*NET classifies tasks as Core, Supplemental, or (rarely) leaves them
# unclassified. We normalise any missing or unexpected values to one of
# these three canonical strings throughout the pipeline.

# %%
#|export
VALID_TASK_TYPES = {'Core', 'Supplemental', 'Unclassified'}
