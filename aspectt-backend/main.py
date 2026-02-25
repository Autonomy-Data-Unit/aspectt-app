"""ASPECTT Backend - FastAPI server for UK O*NET equivalent data."""

from pathlib import Path
import json
import math
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

DATA_DIR = Path(__file__).parent.parent / "aspectt-pipeline" / "data" / "uk_onet"

app = FastAPI(
    title="ASPECTT API",
    description="UK O*NET equivalent - Occupation data based on UK SOC 2020 codes",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Data Loading ---

def load_occupation_index() -> list[dict]:
    with open(DATA_DIR / "occupation_index.json") as f:
        return json.load(f)


def _clean_nans(obj):
    """Recursively replace NaN/Inf float values with None."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _clean_nans(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean_nans(v) for v in obj]
    return obj


def load_occupation(soc_code: int) -> dict:
    path = DATA_DIR / "occupations" / f"{soc_code}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Occupation {soc_code} not found")
    with open(path) as f:
        data = json.loads(f.read().replace(': NaN', ': null'))
    return _clean_nans(data)


def load_crosswalk() -> list[dict]:
    with open(DATA_DIR / "crosswalk.json") as f:
        return json.load(f)


# Preload index for search
_occupation_index = load_occupation_index()
_soc_lookup = {o["uk_soc_2020"]: o["title"] for o in _occupation_index}


# --- API Endpoints ---

@app.get("/api/occupations")
def list_occupations(
    q: str = Query(default="", description="Search query (title or SOC code)"),
    major_group: int | None = Query(default=None, description="Filter by major group (first digit)"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """List/search occupations."""
    results = _occupation_index

    if q:
        q_lower = q.lower().strip()
        results = [
            o for o in results
            if q_lower in o["title"].lower() or q_lower in str(o["uk_soc_2020"])
        ]

    if major_group is not None:
        results = [
            o for o in results
            if str(o["uk_soc_2020"])[0] == str(major_group)
        ]

    total = len(results)
    results = results[offset:offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "occupations": results,
    }


@app.get("/api/occupations/{soc_code}")
def get_occupation(soc_code: int):
    """Get full details for a specific occupation by UK SOC 2020 code."""
    return load_occupation(soc_code)


@app.get("/api/occupations/{soc_code}/abilities")
def get_occupation_abilities(soc_code: int):
    """Get abilities data for a specific occupation."""
    occ = load_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "abilities": occ.get("abilities", [])}


@app.get("/api/occupations/{soc_code}/skills")
def get_occupation_skills(soc_code: int):
    """Get skills data for a specific occupation."""
    occ = load_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "skills": occ.get("skills", [])}


@app.get("/api/occupations/{soc_code}/knowledge")
def get_occupation_knowledge(soc_code: int):
    """Get knowledge data for a specific occupation."""
    occ = load_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "knowledge": occ.get("knowledge", [])}


@app.get("/api/occupations/{soc_code}/tasks")
def get_occupation_tasks(soc_code: int):
    """Get task statements for a specific occupation."""
    occ = load_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "tasks": occ.get("tasks", [])}


@app.get("/api/occupations/{soc_code}/technology-skills")
def get_occupation_tech_skills(soc_code: int):
    """Get technology skills for a specific occupation."""
    occ = load_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "technology_skills": occ.get("technology_skills", [])}


@app.get("/api/occupations/{soc_code}/work-activities")
def get_occupation_work_activities(soc_code: int):
    """Get work activities for a specific occupation."""
    occ = load_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "work_activities": occ.get("work_activities", [])}


@app.get("/api/occupations/{soc_code}/work-context")
def get_occupation_work_context(soc_code: int):
    """Get work context for a specific occupation."""
    occ = load_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "work_context": occ.get("work_context", [])}


@app.get("/api/occupations/{soc_code}/work-styles")
def get_occupation_work_styles(soc_code: int):
    """Get work styles for a specific occupation."""
    occ = load_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "work_styles": occ.get("work_styles", [])}


@app.get("/api/occupations/{soc_code}/interests")
def get_occupation_interests(soc_code: int):
    """Get interests data for a specific occupation."""
    occ = load_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "interests": occ.get("interests", [])}


@app.get("/api/occupations/{soc_code}/work-values")
def get_occupation_work_values(soc_code: int):
    """Get work values for a specific occupation."""
    occ = load_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "work_values": occ.get("work_values", [])}


@app.get("/api/occupations/{soc_code}/education")
def get_occupation_education(soc_code: int):
    """Get education/training data for a specific occupation."""
    occ = load_occupation(soc_code)
    return {
        "uk_soc_2020": soc_code,
        "title": occ["title"],
        "education": occ.get("education", []),
        "job_zone": occ.get("job_zone"),
    }


@app.get("/api/occupations/{soc_code}/related")
def get_related_occupations(soc_code: int):
    """Get related occupations for a specific occupation."""
    occ = load_occupation(soc_code)
    return {
        "uk_soc_2020": soc_code,
        "title": occ["title"],
        "related_occupations": occ.get("related_occupations", []),
    }


@app.get("/api/crosswalk")
def get_crosswalk(
    uk_soc: int | None = Query(default=None, description="Filter by UK SOC code"),
    onet_soc: str | None = Query(default=None, description="Filter by O*NET SOC code"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    """Get the US O*NET to UK SOC 2020 crosswalk."""
    xw = load_crosswalk()

    if uk_soc is not None:
        xw = [x for x in xw if x.get("uk_soc_2020") == uk_soc]
    if onet_soc is not None:
        xw = [x for x in xw if x.get("onet_soc") == onet_soc]

    total = len(xw)
    xw = xw[offset:offset + limit]

    return {"total": total, "offset": offset, "limit": limit, "crosswalk": xw}


# --- Browse endpoints (for finding occupations by descriptor) ---

@app.get("/api/browse/major-groups")
def browse_major_groups():
    """Get all major groups (first digit of SOC code)."""
    major_groups = {
        1: "Managers, Directors and Senior Officials",
        2: "Professional Occupations",
        3: "Associate Professional Occupations",
        4: "Administrative and Secretarial Occupations",
        5: "Skilled Trades Occupations",
        6: "Caring, Leisure and Other Service Occupations",
        7: "Sales and Customer Service Occupations",
        8: "Process, Plant and Machine Operatives",
        9: "Elementary Occupations",
    }

    result = []
    for code, title in major_groups.items():
        count = sum(1 for o in _occupation_index if str(o["uk_soc_2020"])[0] == str(code))
        result.append({"code": code, "title": title, "occupation_count": count})

    return {"major_groups": result}


@app.get("/api/browse/job-zones")
def browse_job_zones():
    """Get occupations grouped by job zone (preparation level)."""
    zone_names = {
        1: "Little or No Preparation Needed",
        2: "Some Preparation Needed",
        3: "Medium Preparation Needed",
        4: "Considerable Preparation Needed",
        5: "Extensive Preparation Needed",
    }

    zones = {z: [] for z in range(1, 6)}
    for occ_info in _occupation_index:
        occ = load_occupation(occ_info["uk_soc_2020"])
        jz = occ.get("job_zone")
        if jz and jz in zones:
            zones[jz].append({"uk_soc_2020": occ_info["uk_soc_2020"], "title": occ_info["title"]})

    result = [
        {"zone": z, "name": zone_names[z], "occupations": occs}
        for z, occs in sorted(zones.items())
    ]
    return {"job_zones": result}


@app.get("/api/stats")
def get_stats():
    """Get dataset statistics."""
    return {
        "total_occupations": len(_occupation_index),
        "soc_version": "UK SOC 2020",
        "source": "O*NET v30.2 (translated via ISCO-08 crosswalk)",
        "data_categories": [
            "abilities", "skills", "knowledge", "work_activities",
            "work_context", "work_styles", "interests", "work_values",
            "tasks", "technology_skills", "education", "related_occupations",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
