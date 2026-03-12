# ---
# jupyter:
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
#|default_exp translate








# %% [markdown]
# # Translate O*NET Data to UK Context
#
# This module takes the US O*NET data and translates it into UK SOC 2020
# equivalents using the crosswalk. Each UK SOC code is a "superposition"
# of its contributing US O*NET codes - numeric values are averaged (weighted),
# and categorical/text data is combined.
# 

# %%
#|export
from pathlib import Path
import json
import pandas as pd
import numpy as np
from tqdm import tqdm

from aspectt_pipeline.crosswalk import (
    DATA_DIR, ONET_DIR,
    build_crosswalk,
    load_uk_soc_framework,
    load_onet_occupations,
)








# %%
#|export
def load_onet_table(filename: str, onet_dir: Path = ONET_DIR) -> pd.DataFrame:
    """Load an O*NET data table (tab-separated text file)."""
    return pd.read_csv(onet_dir / filename, sep='\t')








# %%
#|export
def translate_rated_data(
    onet_df: pd.DataFrame,
    crosswalk: pd.DataFrame,
    value_col: str = 'Data Value',
    group_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Translate an O*NET rated data table (Abilities, Skills, Knowledge, etc.)
    to UK SOC codes by computing weighted averages.

    These tables have Element ID, Scale ID, and Data Value columns.
    For each UK SOC code, we average the data values across all contributing
    O*NET codes, weighted by crosswalk weights.
    """
    if group_cols is None:
        group_cols = ['Element ID', 'Element Name', 'Scale ID']

    # Rename O*NET code column
    onet_col = 'O*NET-SOC Code'

    # Merge with crosswalk
    merged = onet_df.merge(
        crosswalk[['onet_soc', 'uk_soc_2020', 'uk_soc_title', 'weight']],
        left_on=onet_col,
        right_on='onet_soc',
        how='inner',
    )

    # Compute weighted average for numeric columns
    merged['weighted_value'] = merged[value_col].astype(float) * merged['weight']

    # Group by UK SOC + element + scale
    agg_cols = ['uk_soc_2020', 'uk_soc_title'] + group_cols
    result = merged.groupby(agg_cols, as_index=False).agg(
        Data_Value=('weighted_value', 'sum'),
        Weight_Sum=('weight', 'sum'),
        N_Sources=('onet_soc', 'nunique'),
    )
    result['Data Value'] = result['Data_Value'] / result['Weight_Sum']
    result = result.drop(columns=['Data_Value', 'Weight_Sum'])

    return result








# %%
#|export
def translate_task_statements(
    tasks_df: pd.DataFrame,
    crosswalk: pd.DataFrame,
    task_ratings_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """
    Translate O*NET task statements to UK SOC codes.
    Tasks are text-based, so we collect all unique tasks for each UK SOC.

    If task_ratings_df is provided, IM (importance) ratings are joined and
    weighted-averaged across contributing source occupations.
    """
    # Optionally join importance ratings onto tasks before crosswalk merge
    if task_ratings_df is not None:
        im_ratings = task_ratings_df[
            (task_ratings_df['Scale ID'] == 'IM') &
            (task_ratings_df['Recommend Suppress'] != 'Y')
        ][['O*NET-SOC Code', 'Task ID', 'Data Value']].rename(
            columns={'Data Value': 'importance_raw'}
        )
        tasks_df = tasks_df.merge(
            im_ratings, on=['O*NET-SOC Code', 'Task ID'], how='left'
        )

    merged = tasks_df.merge(
        crosswalk[['onet_soc', 'uk_soc_2020', 'uk_soc_title', 'weight']],
        left_on='O*NET-SOC Code',
        right_on='onet_soc',
        how='inner',
    )

    # For each UK SOC, collect unique tasks ordered by weight
    result = []
    for (uk_code, uk_title), group in merged.groupby(['uk_soc_2020', 'uk_soc_title']):
        # Deduplicate tasks, keeping highest weight
        agg_dict = {
            'weight': ('weight', 'max'),
            'task_type': ('Task Type', 'first'),
        }
        if task_ratings_df is not None:
            # Weighted average of importance across contributing sources
            group['weighted_importance'] = group['importance_raw'] * group['weight']
            agg_dict['wi_sum'] = ('weighted_importance', 'sum')
            agg_dict['w_sum'] = ('weight', 'sum')

        task_weights = group.groupby(['Task ID', 'Task']).agg(**agg_dict).reset_index()
        task_weights = task_weights.sort_values('weight', ascending=False)

        for _, row in task_weights.iterrows():
            rec = {
                'uk_soc_2020': uk_code,
                'uk_soc_title': uk_title,
                'task_id': row['Task ID'],
                'task': row['Task'],
                'task_type': row['task_type'] if pd.notna(row['task_type']) else 'Unclassified',
                'relevance': row['weight'],
            }
            if task_ratings_df is not None and row.get('w_sum', 0) > 0:
                imp = row['wi_sum'] / row['w_sum']
                if pd.notna(imp):
                    rec['importance'] = round(float(imp), 2)
            result.append(rec)

    return pd.DataFrame(result)








# %%
#|export
def translate_technology_skills(
    tech_df: pd.DataFrame,
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:
    """Translate O*NET technology skills to UK SOC codes."""
    merged = tech_df.merge(
        crosswalk[['onet_soc', 'uk_soc_2020', 'uk_soc_title', 'weight']],
        left_on='O*NET-SOC Code',
        right_on='onet_soc',
        how='inner',
    )

    # For each UK SOC, collect unique tech skills
    example_col = 'Example' if 'Example' in merged.columns else 'Commodity Title'
    result = merged.groupby(
        ['uk_soc_2020', 'uk_soc_title', example_col]
    ).agg(
        weight=('weight', 'sum'),
        n_sources=('onet_soc', 'nunique'),
    ).reset_index()

    result = result.sort_values(['uk_soc_2020', 'weight'], ascending=[True, False])
    return result








# %%
#|export
def translate_tools_used(
    tools_df: pd.DataFrame,
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:
    """Translate O*NET tools used to UK SOC codes."""
    merged = tools_df.merge(
        crosswalk[['onet_soc', 'uk_soc_2020', 'uk_soc_title', 'weight']],
        left_on='O*NET-SOC Code',
        right_on='onet_soc',
        how='inner',
    )

    result = merged.groupby(
        ['uk_soc_2020', 'uk_soc_title', 'Example']
    ).agg(
        weight=('weight', 'sum'),
        n_sources=('onet_soc', 'nunique'),
    ).reset_index()

    result = result.sort_values(['uk_soc_2020', 'weight'], ascending=[True, False])
    return result








# %%
#|export
def translate_detailed_work_activities(
    tasks_to_dwas_df: pd.DataFrame,
    dwa_ref_df: pd.DataFrame,
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:
    """Translate O*NET detailed work activities to UK SOC codes."""
    # Join tasks-to-DWAs with DWA reference to get titles
    dwas = tasks_to_dwas_df.merge(
        dwa_ref_df[['DWA ID', 'DWA Title', 'Element ID']],
        on='DWA ID',
        how='inner',
    )

    # Merge with crosswalk
    merged = dwas.merge(
        crosswalk[['onet_soc', 'uk_soc_2020', 'uk_soc_title', 'weight']],
        left_on='O*NET-SOC Code',
        right_on='onet_soc',
        how='inner',
    )

    # Group by UK SOC + DWA, aggregate weights
    result = merged.groupby(
        ['uk_soc_2020', 'uk_soc_title', 'DWA ID', 'DWA Title', 'Element ID']
    ).agg(
        weight=('weight', 'sum'),
        n_sources=('onet_soc', 'nunique'),
    ).reset_index()

    result = result.sort_values(['uk_soc_2020', 'weight'], ascending=[True, False])
    return result








# %%
#|export
def translate_emerging_tasks(
    emerging_df: pd.DataFrame,
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:
    """Translate O*NET emerging tasks to UK SOC codes."""
    merged = emerging_df.merge(
        crosswalk[['onet_soc', 'uk_soc_2020', 'uk_soc_title', 'weight']],
        left_on='O*NET-SOC Code',
        right_on='onet_soc',
        how='inner',
    )

    result = merged.groupby(
        ['uk_soc_2020', 'uk_soc_title', 'Task', 'Category']
    ).agg(
        weight=('weight', 'sum'),
    ).reset_index()

    result = result.sort_values(['uk_soc_2020', 'weight'], ascending=[True, False])
    return result








# %%
#|export
def translate_reported_titles(
    titles_df: pd.DataFrame,
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:
    """Translate O*NET sample of reported titles to UK SOC codes."""
    merged = titles_df.merge(
        crosswalk[['onet_soc', 'uk_soc_2020', 'uk_soc_title', 'weight']],
        left_on='O*NET-SOC Code',
        right_on='onet_soc',
        how='inner',
    )

    result = merged.groupby(
        ['uk_soc_2020', 'uk_soc_title', 'Reported Job Title']
    ).agg(
        weight=('weight', 'sum'),
    ).reset_index()

    result = result.sort_values(['uk_soc_2020', 'weight'], ascending=[True, False])
    return result








# %%
#|export
def translate_interests(
    interests_df: pd.DataFrame,
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:
    """Translate O*NET interests data to UK SOC codes."""
    return translate_rated_data(
        interests_df, crosswalk,
        value_col='Data Value',
        group_cols=['Element ID', 'Element Name', 'Scale ID'],
    )








# %%
#|export
def translate_work_values(
    values_df: pd.DataFrame,
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:
    """Translate O*NET work values to UK SOC codes."""
    return translate_rated_data(
        values_df, crosswalk,
        value_col='Data Value',
        group_cols=['Element ID', 'Element Name', 'Scale ID'],
    )








# %%
#|export
def translate_education(
    edu_df: pd.DataFrame,
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:
    """Translate O*NET education/training/experience data to UK SOC codes."""
    merged = edu_df.merge(
        crosswalk[['onet_soc', 'uk_soc_2020', 'uk_soc_title', 'weight']],
        left_on='O*NET-SOC Code',
        right_on='onet_soc',
        how='inner',
    )

    group_cols = ['Element ID', 'Element Name', 'Scale ID', 'Category']
    merged['weighted_value'] = merged['Data Value'].astype(float) * merged['weight']

    result = merged.groupby(
        ['uk_soc_2020', 'uk_soc_title'] + group_cols, as_index=False
    ).agg(
        Data_Value=('weighted_value', 'sum'),
        Weight_Sum=('weight', 'sum'),
        N_Sources=('onet_soc', 'nunique'),
    )
    result['Data Value'] = result['Data_Value'] / result['Weight_Sum']
    result = result.drop(columns=['Data_Value', 'Weight_Sum'])
    return result








# %%
#|export
def translate_job_zones(
    jz_df: pd.DataFrame,
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:
    """Translate O*NET job zone assignments to UK SOC codes."""
    merged = jz_df.merge(
        crosswalk[['onet_soc', 'uk_soc_2020', 'uk_soc_title', 'weight']],
        left_on='O*NET-SOC Code',
        right_on='onet_soc',
        how='inner',
    )

    merged['weighted_jz'] = merged['Job Zone'].astype(float) * merged['weight']

    result = merged.groupby(['uk_soc_2020', 'uk_soc_title'], as_index=False).agg(
        job_zone_raw=('weighted_jz', 'sum'),
        weight_sum=('weight', 'sum'),
        n_sources=('onet_soc', 'nunique'),
    )
    result['job_zone'] = (result['job_zone_raw'] / result['weight_sum']).round().astype(int)
    result = result.drop(columns=['job_zone_raw', 'weight_sum'])
    return result








# %%
#|export
def translate_alternate_titles(
    titles_df: pd.DataFrame,
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:
    """Translate O*NET alternate titles to UK SOC codes."""
    merged = titles_df.merge(
        crosswalk[['onet_soc', 'uk_soc_2020', 'uk_soc_title', 'weight']],
        left_on='O*NET-SOC Code',
        right_on='onet_soc',
        how='inner',
    )

    result = merged.groupby(
        ['uk_soc_2020', 'uk_soc_title', 'Alternate Title']
    ).agg(
        weight=('weight', 'sum'),
    ).reset_index()

    result = result.sort_values(['uk_soc_2020', 'weight'], ascending=[True, False])
    return result








# %%
#|export
def translate_related_occupations(
    related_df: pd.DataFrame,
    crosswalk: pd.DataFrame,
) -> pd.DataFrame:
    """Translate related occupations, mapping related O*NET codes to UK SOC codes too."""
    # First map source occupations to UK SOC
    merged = related_df.merge(
        crosswalk[['onet_soc', 'uk_soc_2020', 'uk_soc_title']],
        left_on='O*NET-SOC Code',
        right_on='onet_soc',
        how='inner',
    )

    # Then map related occupations to UK SOC
    related_uk = merged.merge(
        crosswalk[['onet_soc', 'uk_soc_2020']].rename(
            columns={'onet_soc': 'related_onet', 'uk_soc_2020': 'related_uk_soc'}
        ),
        left_on='Related O*NET-SOC Code',
        right_on='related_onet',
        how='left',
    )

    # Keep only cases where the related UK SOC is different from the source
    related_uk = related_uk[
        related_uk['related_uk_soc'].notna() &
        (related_uk['uk_soc_2020'] != related_uk['related_uk_soc'])
    ]

    result = related_uk.groupby(
        ['uk_soc_2020', 'uk_soc_title', 'related_uk_soc']
    ).size().reset_index(name='link_count')

    result['related_uk_soc'] = result['related_uk_soc'].astype(int)
    uk_groups = load_uk_soc_framework()
    result['related_uk_title'] = result['related_uk_soc'].map(uk_groups)

    result = result.sort_values(['uk_soc_2020', 'link_count'], ascending=[True, False])
    return result








# %%
#|export
def build_uk_dataset(
    data_dir: Path = DATA_DIR,
    onet_dir: Path = ONET_DIR,
    output_dir: Path | None = None,
    refine: bool = True,
    refine_model: str = "gpt-4o-mini",
) -> dict:
    """
    Build the full UK O*NET-equivalent dataset.

    Translates all major O*NET data tables to UK SOC 2020 codes and
    saves the result as a collection of JSON files.

    Returns a dict with all translated data.
    """
    if output_dir is None:
        output_dir = data_dir.parent.parent / "data" / "uk_onet"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Building crosswalk...")
    xw = build_crosswalk(data_dir, onet_dir)
    uk_groups = load_uk_soc_framework(data_dir)

    dataset = {
        'occupations': [],
        'crosswalk': xw.to_dict('records'),
    }

    # Translate rated data tables
    rated_tables = {
        'abilities': 'Abilities.txt',
        'skills': 'Skills.txt',
        'knowledge': 'Knowledge.txt',
        'work_activities': 'Work Activities.txt',
        'work_context': 'Work Context.txt',
        'work_styles': 'Work Styles.txt',
    }

    translated = {}
    for name, filename in tqdm(rated_tables.items(), desc="Translating rated data"):
        df = load_onet_table(filename, onet_dir)
        translated[name] = translate_rated_data(df, xw)

    # Translate interests and work values
    print("Translating interests...")
    interests_df = load_onet_table('Interests.txt', onet_dir)
    translated['interests'] = translate_interests(interests_df, xw)

    print("Translating work values...")
    values_df = load_onet_table('Work Values.txt', onet_dir)
    translated['work_values'] = translate_work_values(values_df, xw)

    # Translate task statements (with optional importance ratings)
    print("Translating tasks...")
    tasks_df = load_onet_table('Task Statements.txt', onet_dir)
    task_ratings_df = load_onet_table('Task Ratings.txt', onet_dir)
    translated['tasks'] = translate_task_statements(tasks_df, xw, task_ratings_df)

    # Translate technology skills
    print("Translating technology skills...")
    tech_df = load_onet_table('Technology Skills.txt', onet_dir)
    translated['technology_skills'] = translate_technology_skills(tech_df, xw)

    # Translate tools used
    print("Translating tools used...")
    tools_df = load_onet_table('Tools Used.txt', onet_dir)
    translated['tools_used'] = translate_tools_used(tools_df, xw)

    # Translate detailed work activities
    print("Translating detailed work activities...")
    tasks_to_dwas_df = load_onet_table('Tasks to DWAs.txt', onet_dir)
    dwa_ref_df = load_onet_table('DWA Reference.txt', onet_dir)
    translated['detailed_work_activities'] = translate_detailed_work_activities(
        tasks_to_dwas_df, dwa_ref_df, xw
    )

    # Translate emerging tasks
    print("Translating emerging tasks...")
    emerging_df = load_onet_table('Emerging Tasks.txt', onet_dir)
    translated['emerging_tasks'] = translate_emerging_tasks(emerging_df, xw)

    # Translate reported job titles
    print("Translating reported job titles...")
    reported_df = load_onet_table('Sample of Reported Titles.txt', onet_dir)
    translated['reported_job_titles'] = translate_reported_titles(reported_df, xw)

    # Translate education/training/experience
    print("Translating education...")
    edu_df = load_onet_table('Education, Training, and Experience.txt', onet_dir)
    translated['education'] = translate_education(edu_df, xw)

    # Translate job zones
    print("Translating job zones...")
    jz_df = load_onet_table('Job Zones.txt', onet_dir)
    translated['job_zones'] = translate_job_zones(jz_df, xw)

    # Translate alternate titles
    print("Translating alternate titles...")
    titles_df = load_onet_table('Alternate Titles.txt', onet_dir)
    translated['alternate_titles'] = translate_alternate_titles(titles_df, xw)

    # Translate related occupations
    print("Translating related occupations...")
    related_df = load_onet_table('Related Occupations.txt', onet_dir)
    translated['related_occupations'] = translate_related_occupations(related_df, xw)

    # Build per-occupation JSON
    print("Building per-occupation data...")
    onet_occ = load_onet_occupations(onet_dir)

    for uk_code, uk_title in tqdm(uk_groups.items(), desc="Building occupations"):
        occ_data = {
            'uk_soc_2020': uk_code,
            'title': uk_title,
            'description': _build_description(uk_code, xw, onet_occ),
        }

        # Add rated data
        for name in rated_tables:
            df = translated[name]
            subset = df[df['uk_soc_2020'] == uk_code]
            if len(subset) > 0:
                # Pivot: for each element, get IM and LV scale values
                occ_data[name] = _rated_to_dict(subset)

        # Add interests
        int_subset = translated['interests'][translated['interests']['uk_soc_2020'] == uk_code]
        if len(int_subset) > 0:
            occ_data['interests'] = _rated_to_dict(int_subset)

        # Add work values
        wv_subset = translated['work_values'][translated['work_values']['uk_soc_2020'] == uk_code]
        if len(wv_subset) > 0:
            occ_data['work_values'] = _rated_to_dict(wv_subset)

        # Add tasks (with importance if available)
        task_subset = translated['tasks'][translated['tasks']['uk_soc_2020'] == uk_code]
        if len(task_subset) > 0:
            task_cols = ['task', 'task_type', 'relevance']
            if 'importance' in task_subset.columns:
                task_cols.append('importance')
            occ_data['tasks'] = task_subset[task_cols].to_dict('records')

        # Add technology skills
        tech_subset = translated['technology_skills'][translated['technology_skills']['uk_soc_2020'] == uk_code]
        if len(tech_subset) > 0:
            example_col = [c for c in tech_subset.columns if c in ('Example', 'Commodity Title')][0]
            occ_data['technology_skills'] = tech_subset[[example_col, 'weight']].rename(
                columns={example_col: 'name'}
            ).to_dict('records')

        # Add tools used
        tools_subset = translated['tools_used'][translated['tools_used']['uk_soc_2020'] == uk_code]
        if len(tools_subset) > 0:
            occ_data['tools_used'] = tools_subset[['Example', 'weight']].rename(
                columns={'Example': 'name'}
            ).to_dict('records')

        # Add detailed work activities
        dwa_subset = translated['detailed_work_activities'][translated['detailed_work_activities']['uk_soc_2020'] == uk_code]
        if len(dwa_subset) > 0:
            occ_data['detailed_work_activities'] = dwa_subset[
                ['DWA ID', 'DWA Title', 'Element ID', 'weight']
            ].rename(columns={
                'DWA ID': 'dwa_id', 'DWA Title': 'title', 'Element ID': 'element_id',
            }).to_dict('records')

        # Add emerging tasks
        et_subset = translated['emerging_tasks'][translated['emerging_tasks']['uk_soc_2020'] == uk_code]
        if len(et_subset) > 0:
            occ_data['emerging_tasks'] = et_subset[['Task', 'Category']].rename(
                columns={'Task': 'task', 'Category': 'category'}
            ).to_dict('records')

        # Add reported job titles
        rjt_subset = translated['reported_job_titles'][translated['reported_job_titles']['uk_soc_2020'] == uk_code]
        if len(rjt_subset) > 0:
            occ_data['reported_job_titles'] = rjt_subset['Reported Job Title'].tolist()[:50]

        # Add education
        edu_subset = translated['education'][translated['education']['uk_soc_2020'] == uk_code]
        if len(edu_subset) > 0:
            occ_data['education'] = edu_subset[
                ['Element Name', 'Scale ID', 'Category', 'Data Value']
            ].to_dict('records')

        # Add job zone
        jz_subset = translated['job_zones'][translated['job_zones']['uk_soc_2020'] == uk_code]
        if len(jz_subset) > 0:
            occ_data['job_zone'] = int(jz_subset.iloc[0]['job_zone'])

        # Add alternate titles
        alt_subset = translated['alternate_titles'][translated['alternate_titles']['uk_soc_2020'] == uk_code]
        if len(alt_subset) > 0:
            occ_data['alternate_titles'] = alt_subset['Alternate Title'].tolist()[:50]

        # Add related occupations
        rel_subset = translated['related_occupations'][translated['related_occupations']['uk_soc_2020'] == uk_code]
        if len(rel_subset) > 0:
            occ_data['related_occupations'] = rel_subset[
                ['related_uk_soc', 'related_uk_title', 'link_count']
            ].head(20).to_dict('records')

        # Add contributing O*NET codes
        xw_subset = xw[xw['uk_soc_2020'] == uk_code]
        occ_data['source_occupations'] = xw_subset[
            ['onet_soc', 'onet_title', 'weight']
        ].to_dict('records')

        dataset['occupations'].append(occ_data)

    # Optional LLM refinement of tasks, technology skills, and tools used
    if refine:
        import copy
        from aspectt_pipeline.refine import refine_dataset
        from aspectt_pipeline.postprocess import postprocess_dataset

        # Keep unrefined copy for post-processing (tech skill whitelist restoration)
        unrefined_occupations = copy.deepcopy(dataset['occupations'])

        print("Refining tasks, technology skills, and tools used with LLM...")
        dataset['occupations'] = refine_dataset(dataset['occupations'], model=refine_model)

        print("Post-processing refined data...")
        dataset['occupations'] = postprocess_dataset(dataset['occupations'], unrefined_occupations)

        from aspectt_pipeline.postprocess import apply_manual_overrides
        dataset['occupations'] = apply_manual_overrides(dataset['occupations'])

    # Save full dataset
    print(f"Saving dataset to {output_dir}...")

    # Save occupation index
    occ_index = [{'uk_soc_2020': o['uk_soc_2020'], 'title': o['title']} for o in dataset['occupations']]
    with open(output_dir / 'occupation_index.json', 'w') as f:
        json.dump(occ_index, f, indent=2)

    # Save individual occupation files
    occ_dir = output_dir / 'occupations'
    occ_dir.mkdir(exist_ok=True)
    for occ in dataset['occupations']:
        with open(occ_dir / f"{occ['uk_soc_2020']}.json", 'w') as f:
            sanitized = _sanitize_nans(occ)
            text = json.dumps(sanitized, indent=2, default=_json_default, allow_nan=False)
            f.write(text)

    # Save crosswalk
    with open(output_dir / 'crosswalk.json', 'w') as f:
        sanitized_xw = _sanitize_nans(dataset['crosswalk'])
        text = json.dumps(sanitized_xw, indent=2, default=_json_default, allow_nan=False)
        f.write(text)

    print(f"Done! {len(dataset['occupations'])} occupations saved.")
    return dataset








# %%
#|export
def _sanitize_nans(obj):
    """Recursively replace NaN/Inf float values with None in nested structures."""
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    if isinstance(obj, (np.floating,)):
        val = float(obj)
        if np.isnan(val) or np.isinf(val):
            return None
        return val
    if isinstance(obj, dict):
        return {k: _sanitize_nans(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_nans(v) for v in obj]
    return obj


def _json_default(obj):
    """JSON serializer for numpy types, replacing NaN with None."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        val = float(obj)
        if np.isnan(val) or np.isinf(val):
            return None
        return val
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")








# %%
#|export
def _build_description(uk_code: int, crosswalk: pd.DataFrame, onet_occ: pd.DataFrame) -> str:
    """Build a combined description for a UK SOC code from contributing O*NET occupations."""
    sources = crosswalk[crosswalk['uk_soc_2020'] == uk_code]
    descs = []
    for _, row in sources.iterrows():
        occ = onet_occ[onet_occ['onet_soc'] == row['onet_soc']]
        if len(occ) > 0 and pd.notna(occ.iloc[0]['Description']):
            descs.append(occ.iloc[0]['Description'])

    if not descs:
        return ""

    # Remove duplicates while preserving order
    seen = set()
    unique_descs = []
    for d in descs:
        if d not in seen:
            seen.add(d)
            unique_descs.append(d)

    # Combine descriptions (truncate if too many)
    if len(unique_descs) <= 3:
        return " ".join(unique_descs)
    else:
        return " ".join(unique_descs[:3]) + f" (Based on {len(unique_descs)} related US occupations.)"








# %%
#|export
def _rated_to_dict(df: pd.DataFrame) -> list[dict]:
    """Convert rated data DataFrame to a list of element dicts with IM/LV values."""
    elements = {}
    for _, row in df.iterrows():
        eid = row['Element ID']
        if eid not in elements:
            elements[eid] = {
                'element_id': eid,
                'element_name': row['Element Name'],
            }
        scale = row['Scale ID']
        val = float(row['Data Value'])
        if not (np.isnan(val) or np.isinf(val)):
            elements[eid][f'value_{scale}'] = round(val, 2)

    return sorted(elements.values(), key=lambda x: x.get('value_IM', x.get('value_LV', 0)), reverse=True)
