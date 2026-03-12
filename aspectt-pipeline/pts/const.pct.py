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

# %%
#|export
DEFAULT_MODEL = "gpt-4o-mini"
CONCURRENCY_LIMIT = 10



# %% [markdown]
# ## Refinement tuning

# %%
#|export
TECH_CHUNK_SIZE = 400
TOOL_CHUNK_SIZE = 200
TASK_CHUNK_SIZE = 150
JACCARD_DEDUP_THRESHOLD = 0.85



# %% [markdown]
# ## Valid task types

# %%
#|export
VALID_TASK_TYPES = {'Core', 'Supplemental', 'Unclassified'}
