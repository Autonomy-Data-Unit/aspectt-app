"""ASPECTT Backend - FastAPI server for UK O*NET equivalent data."""

import os
import time
from pathlib import Path
import json
import math
from collections import defaultdict
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

DATA_DIR = Path(os.environ.get("ASPECTT_DATA_DIR", Path(__file__).parent.parent / "aspectt-pipeline" / "data" / "uk_onet"))
STATIC_DIR = Path(os.environ.get("ASPECTT_STATIC_DIR", ""))  # Set in Docker to serve frontend

app = FastAPI(
    title="ASPECTT API",
    description="UK O*NET equivalent - Occupation data based on UK SOC 2020 codes",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Rate Limiting ---

RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))  # seconds

_rate_limit_store: dict[str, list[float]] = {}
_rate_limit_last_cleanup: float = 0.0


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple in-memory rate limiter by client IP. Only applies to /api/ routes."""
    global _rate_limit_last_cleanup

    path = request.url.path
    if not path.startswith("/api/"):
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    window_start = now - RATE_LIMIT_WINDOW

    # Periodically clean up stale IPs (every 5 minutes)
    if now - _rate_limit_last_cleanup > 300:
        stale_ips = [ip for ip, ts in _rate_limit_store.items() if not ts or ts[-1] < window_start]
        for ip in stale_ips:
            del _rate_limit_store[ip]
        _rate_limit_last_cleanup = now

    # Clean old entries and check limit
    timestamps = _rate_limit_store.get(client_ip, [])
    timestamps = [t for t in timestamps if t > window_start]
    if len(timestamps) >= RATE_LIMIT_REQUESTS:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Try again later."},
            headers={"Retry-After": str(RATE_LIMIT_WINDOW)},
        )
    timestamps.append(now)
    _rate_limit_store[client_ip] = timestamps

    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT_REQUESTS)
    response.headers["X-RateLimit-Remaining"] = str(max(0, RATE_LIMIT_REQUESTS - len(timestamps)))
    return response


# --- Data Loading & Preloading ---

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


def _load_occupation_file(soc_code: int) -> dict:
    path = DATA_DIR / "occupations" / f"{soc_code}.json"
    if not path.exists():
        return {}
    with open(path) as f:
        data = json.loads(f.read().replace(': NaN', ': null'))
    data = _clean_nans(data)
    # Normalize value fields so the frontend RatedBars component can display them uniformly.
    # Work context uses value_CX, work styles use value_DR — map both to value_IM.
    for item in data.get("work_context", []):
        if "value_IM" not in item and "value_CX" in item:
            item["value_IM"] = item["value_CX"]
    for item in data.get("work_styles", []):
        if "value_IM" not in item:
            item["value_IM"] = item.get("value_DR") or item.get("value_WI") or 0
    return data


def load_occupation_index() -> list[dict]:
    with open(DATA_DIR / "occupation_index.json") as f:
        return json.load(f)


def load_crosswalk() -> list[dict]:
    with open(DATA_DIR / "crosswalk.json") as f:
        return json.load(f)


# Preload everything into memory for fast search/browse
_occupation_index = load_occupation_index()
_soc_lookup = {o["uk_soc_2020"]: o["title"] for o in _occupation_index}
_occupations: dict[int, dict] = {}

for _occ_info in _occupation_index:
    _code = _occ_info["uk_soc_2020"]
    _data = _load_occupation_file(_code)
    if _data:
        _occupations[_code] = _data

_crosswalk = load_crosswalk()

# Load element descriptions lookup
_element_descriptions_path = DATA_DIR / "element_descriptions.json"
_element_descriptions: dict[str, str] = {}
if _element_descriptions_path.exists():
    with open(_element_descriptions_path) as f:
        _element_descriptions = json.load(f)

# Build unique O*NET occupation list for autocomplete
_onet_occupations: list[dict] = []
_onet_seen: set[str] = set()
for _xw in _crosswalk:
    _onet_code = _xw.get("onet_soc", "")
    if _onet_code and _onet_code not in _onet_seen:
        _onet_seen.add(_onet_code)
        _onet_occupations.append({"onet_soc": _onet_code, "title": _xw.get("onet_title", "")})
_onet_occupations.sort(key=lambda x: x["onet_soc"])
del _onet_seen

# Build search indices
_alt_title_index: dict[int, list[str]] = {}  # soc -> lowercase alt titles
_task_index: list[tuple[int, str, str]] = []  # (soc, task_text, task_type)
_tech_index: dict[str, list[int]] = defaultdict(list)  # tech_name_lower -> [soc_codes]
_tool_index: dict[str, list[int]] = defaultdict(list)  # tool_name_lower -> [soc_codes]
_element_index: dict[str, dict[str, list[tuple[int, float]]]] = defaultdict(lambda: defaultdict(list))
# category -> element_name -> [(soc, importance)]

for _code, _occ in _occupations.items():
    # Alt titles
    _alt_title_index[_code] = [t.lower() for t in _occ.get("alternate_titles", [])]

    # Tasks
    for _t in _occ.get("tasks", []):
        _task_index.append((_code, _t["task"], _t.get("task_type", "")))

    # Tech skills
    for _ts in _occ.get("technology_skills", []):
        _tech_index[_ts["name"].lower()].append(_code)

    # Tools used
    for _tu in _occ.get("tools_used", []):
        _tool_index[_tu["name"].lower()].append(_code)

    # Rated elements (for descriptor browsing)
    for _cat in ("skills", "abilities", "knowledge", "work_activities",
                 "work_context", "work_styles"):
        for _el in _occ.get(_cat, []):
            _name = _el.get("element_name", "")
            _im = _el.get("value_IM") or _el.get("value_DR") or _el.get("value_CX") or 0
            if _im and _name:
                _element_index[_cat][_name].append((_code, _im))

# Build unique tech skill names for browsing
_all_tech_skills = sorted(set(
    ts["name"]
    for occ in _occupations.values()
    for ts in occ.get("technology_skills", [])
))

# Build unique tool names for browsing
_all_tools = sorted(set(
    tu["name"]
    for occ in _occupations.values()
    for tu in occ.get("tools_used", [])
))

# Build RIASEC profiles for interest browsing
_interest_profiles: dict[int, dict[str, float]] = {}
_RIASEC_NAMES = ["Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional"]
for _code, _occ in _occupations.items():
    profile = {}
    for _i in _occ.get("interests", []):
        if _i["element_name"] in _RIASEC_NAMES:
            profile[_i["element_name"]] = _i.get("value_OI", 0)
    if profile:
        _interest_profiles[_code] = profile


def get_occupation(soc_code: int) -> dict:
    if soc_code not in _occupations:
        raise HTTPException(status_code=404, detail=f"Occupation {soc_code} not found")
    return _occupations[soc_code]


# --- Core Occupation Endpoints ---

@app.get("/api/occupations")
def list_occupations(
    q: str = Query(default="", description="Search query (title, alternate title, or SOC code)"),
    major_group: int | None = Query(default=None, description="Filter by major group (first digit)"),
    job_zone: int | None = Query(default=None, description="Filter by job zone (1-5)"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """List/search occupations with enhanced search across titles and alternate titles."""
    results = _occupation_index

    if q:
        q_lower = q.lower().strip()
        matched = []
        for o in results:
            code = o["uk_soc_2020"]
            if q_lower in o["title"].lower() or q_lower in str(code):
                matched.append(o)
            elif code in _alt_title_index:
                if any(q_lower in at for at in _alt_title_index[code]):
                    matched.append(o)
        results = matched

    if major_group is not None:
        results = [
            o for o in results
            if str(o["uk_soc_2020"])[0] == str(major_group)
        ]

    if job_zone is not None:
        results = [
            o for o in results
            if _occupations.get(o["uk_soc_2020"], {}).get("job_zone") == job_zone
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
def get_occupation_detail(soc_code: int):
    """Get full details for a specific occupation by UK SOC 2020 code."""
    return get_occupation(soc_code)


@app.get("/api/occupations/{soc_code}/abilities")
def get_occupation_abilities(soc_code: int):
    occ = get_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "abilities": occ.get("abilities", [])}


@app.get("/api/occupations/{soc_code}/skills")
def get_occupation_skills(soc_code: int):
    occ = get_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "skills": occ.get("skills", [])}


@app.get("/api/occupations/{soc_code}/knowledge")
def get_occupation_knowledge(soc_code: int):
    occ = get_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "knowledge": occ.get("knowledge", [])}


@app.get("/api/occupations/{soc_code}/tasks")
def get_occupation_tasks(soc_code: int):
    occ = get_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "tasks": occ.get("tasks", [])}


@app.get("/api/occupations/{soc_code}/technology-skills")
def get_occupation_tech_skills(soc_code: int):
    occ = get_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "technology_skills": occ.get("technology_skills", [])}


@app.get("/api/occupations/{soc_code}/tools-used")
def get_occupation_tools_used(soc_code: int):
    occ = get_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "tools_used": occ.get("tools_used", [])}


@app.get("/api/occupations/{soc_code}/work-activities")
def get_occupation_work_activities(soc_code: int):
    occ = get_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "work_activities": occ.get("work_activities", [])}


@app.get("/api/occupations/{soc_code}/work-context")
def get_occupation_work_context(soc_code: int):
    occ = get_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "work_context": occ.get("work_context", [])}


@app.get("/api/occupations/{soc_code}/work-styles")
def get_occupation_work_styles(soc_code: int):
    occ = get_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "work_styles": occ.get("work_styles", [])}


@app.get("/api/occupations/{soc_code}/interests")
def get_occupation_interests(soc_code: int):
    occ = get_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "interests": occ.get("interests", [])}


@app.get("/api/occupations/{soc_code}/work-values")
def get_occupation_work_values(soc_code: int):
    occ = get_occupation(soc_code)
    return {"uk_soc_2020": soc_code, "title": occ["title"], "work_values": occ.get("work_values", [])}


@app.get("/api/occupations/{soc_code}/education")
def get_occupation_education(soc_code: int):
    occ = get_occupation(soc_code)
    return {
        "uk_soc_2020": soc_code,
        "title": occ["title"],
        "education": occ.get("education", []),
        "job_zone": occ.get("job_zone"),
    }


@app.get("/api/occupations/{soc_code}/related")
def get_related_occupations(soc_code: int):
    occ = get_occupation(soc_code)
    return {
        "uk_soc_2020": soc_code,
        "title": occ["title"],
        "related_occupations": occ.get("related_occupations", []),
    }


# --- Compare Endpoint ---

@app.get("/api/compare")
def compare_occupations(
    codes: str = Query(description="Comma-separated UK SOC codes to compare (2-4)"),
):
    """Compare 2-4 occupations side-by-side."""
    try:
        code_list = [int(c.strip()) for c in codes.split(",") if c.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid SOC code format - must be integers")
    if len(code_list) < 2 or len(code_list) > 4:
        raise HTTPException(status_code=400, detail="Provide 2-4 SOC codes")

    result = []
    for code in code_list:
        occ = get_occupation(code)
        # Build summary for comparison
        top_skills = sorted(occ.get("skills", []), key=lambda x: x.get("value_IM", 0), reverse=True)[:10]
        top_abilities = sorted(occ.get("abilities", []), key=lambda x: x.get("value_IM", 0), reverse=True)[:10]
        top_knowledge = sorted(occ.get("knowledge", []), key=lambda x: x.get("value_IM", 0), reverse=True)[:10]
        top_activities = sorted(occ.get("work_activities", []), key=lambda x: x.get("value_IM", 0), reverse=True)[:10]
        top_tech = sorted(occ.get("technology_skills", []), key=lambda x: x.get("weight", 0), reverse=True)[:10]
        top_tools = sorted(occ.get("tools_used", []), key=lambda x: x.get("weight", 0), reverse=True)[:10]

        # Get RIASEC code
        interests = occ.get("interests", [])
        riasec = sorted(
            [i for i in interests if i["element_name"] in _RIASEC_NAMES],
            key=lambda x: x.get("value_OI", 0),
            reverse=True
        )
        riasec_code = "".join(i["element_name"][0] for i in riasec[:3]) if riasec else ""

        result.append({
            "uk_soc_2020": code,
            "title": occ["title"],
            "description": occ.get("description", ""),
            "job_zone": occ.get("job_zone"),
            "riasec_code": riasec_code,
            "top_skills": top_skills,
            "top_abilities": top_abilities,
            "top_knowledge": top_knowledge,
            "top_work_activities": top_activities,
            "top_technology_skills": top_tech,
            "interests": interests,
            "work_values": occ.get("work_values", []),
            "task_count": len(occ.get("tasks", [])),
            "tech_skill_count": len(occ.get("technology_skills", [])),
            "top_tools_used": top_tools,
            "tool_count": len(occ.get("tools_used", [])),
        })

    return {"occupations": result}


# --- Advanced Search Endpoints ---

@app.get("/api/search/tasks")
def search_tasks(
    q: str = Query(description="Search query for task descriptions"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Search across all occupation task statements."""
    q_lower = q.lower().strip()
    matches = []
    seen_tasks = set()
    for soc_code, task_text, task_type in _task_index:
        if q_lower in task_text.lower():
            key = (soc_code, task_text)
            if key not in seen_tasks:
                seen_tasks.add(key)
                matches.append({
                    "uk_soc_2020": soc_code,
                    "title": _soc_lookup.get(soc_code, ""),
                    "task": task_text,
                    "task_type": task_type,
                })

    total = len(matches)
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": matches[offset:offset + limit],
    }


@app.get("/api/search/technology-skills")
def search_tech_skills(
    q: str = Query(description="Search query for technology/software names"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Search occupations by technology skill name."""
    q_lower = q.lower().strip()

    # Find matching technology names
    matching_techs = [name for name in _all_tech_skills if q_lower in name.lower()]

    # Collect occupations that use matching techs
    occ_scores: dict[int, list[str]] = defaultdict(list)
    for tech_name in matching_techs:
        for soc_code in _tech_index.get(tech_name.lower(), []):
            if tech_name not in occ_scores[soc_code]:
                occ_scores[soc_code].append(tech_name)

    results = sorted(
        [
            {
                "uk_soc_2020": code,
                "title": _soc_lookup.get(code, ""),
                "matching_technologies": techs,
                "match_count": len(techs),
            }
            for code, techs in occ_scores.items()
        ],
        key=lambda x: x["match_count"],
        reverse=True,
    )

    total = len(results)
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "matching_technology_names": matching_techs[:20],
        "results": results[offset:offset + limit],
    }


@app.get("/api/search/skills")
def search_by_skill(
    q: str = Query(description="Skill name to search for"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Find occupations that require a specific skill."""
    q_lower = q.lower().strip()

    results = []
    for code, occ in _occupations.items():
        for skill in occ.get("skills", []):
            if q_lower in skill.get("element_name", "").lower():
                results.append({
                    "uk_soc_2020": code,
                    "title": occ["title"],
                    "skill_name": skill["element_name"],
                    "importance": skill.get("value_IM"),
                    "level": skill.get("value_LV"),
                })

    results.sort(key=lambda x: x.get("importance") or 0, reverse=True)
    total = len(results)
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "results": results[offset:offset + limit],
    }


@app.get("/api/search/tools-used")
def search_tools_used(
    q: str = Query(description="Search query for tool/equipment names"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Search occupations by tool/equipment name."""
    q_lower = q.lower().strip()

    # Find matching tool names
    matching_tools = [name for name in _all_tools if q_lower in name.lower()]

    # Collect occupations that use matching tools
    occ_scores: dict[int, list[str]] = defaultdict(list)
    for tool_name in matching_tools:
        for soc_code in _tool_index.get(tool_name.lower(), []):
            if tool_name not in occ_scores[soc_code]:
                occ_scores[soc_code].append(tool_name)

    results = sorted(
        [
            {
                "uk_soc_2020": code,
                "title": _soc_lookup.get(code, ""),
                "matching_tools": tools,
                "match_count": len(tools),
            }
            for code, tools in occ_scores.items()
        ],
        key=lambda x: x["match_count"],
        reverse=True,
    )

    total = len(results)
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "matching_tool_names": matching_tools[:20],
        "results": results[offset:offset + limit],
    }


# --- Browse Endpoints ---

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
    """Get occupations grouped by job zone (preparation level).
    Zones 1 and 2 are merged following O*NET Online convention."""
    zone_names = {
        2: "Little to Some Preparation Needed",
        3: "Medium Preparation Needed",
        4: "Considerable Preparation Needed",
        5: "Extensive Preparation Needed",
    }

    zones: dict[int, list[dict]] = {z: [] for z in (2, 3, 4, 5)}
    for code, occ in _occupations.items():
        jz = occ.get("job_zone")
        if jz == 1:
            jz = 2  # merge zone 1 into zone 2
        if jz and jz in zones:
            zones[jz].append({"uk_soc_2020": code, "title": occ["title"]})

    result = [
        {"zone": z, "name": zone_names[z], "label": "1–2" if z == 2 else str(z), "occupation_count": len(occs), "occupations": occs}
        for z, occs in sorted(zones.items())
    ]
    return {"job_zones": result}


@app.get("/api/browse/interests")
def browse_interests(
    code: str | None = Query(default=None, description="RIASEC letter(s) to filter, e.g. 'IR' or 'IRC'"),
    job_zone: int | None = Query(default=None, description="Filter by job zone"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Browse occupations by Holland/RIASEC interest codes."""
    # Build summary of each interest type
    interest_summary = []
    for name in _RIASEC_NAMES:
        count = sum(
            1 for profile in _interest_profiles.values()
            if profile and max(profile, key=profile.get) == name
        )
        interest_summary.append({
            "code": name[0],
            "name": name,
            "primary_count": count,
        })

    if not code:
        return {"interests": interest_summary}

    # Filter occupations by RIASEC code pattern
    code_upper = code.upper()
    target_names = [n for n in _RIASEC_NAMES if n[0] in code_upper]

    results = []
    for soc_code, profile in _interest_profiles.items():
        if not profile:
            continue
        # Sort interests by value to get the occupation's RIASEC code
        sorted_interests = sorted(profile.items(), key=lambda x: x[1], reverse=True)
        occ_code = "".join(name[0] for name, _ in sorted_interests[:len(code_upper)])

        if occ_code == code_upper:
            occ = _occupations[soc_code]
            if job_zone is not None and occ.get("job_zone") != job_zone:
                continue
            results.append({
                "uk_soc_2020": soc_code,
                "title": occ["title"],
                "riasec_code": "".join(name[0] for name, _ in sorted_interests[:3]),
                "job_zone": occ.get("job_zone"),
            })

    results.sort(key=lambda x: x["title"])
    total = len(results)

    return {
        "interests": interest_summary,
        "code_filter": code_upper,
        "total": total,
        "offset": offset,
        "limit": limit,
        "occupations": results[offset:offset + limit],
    }


@app.get("/api/browse/descriptors/{category}")
def browse_descriptors(
    category: str,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    """Browse descriptor elements for a data category (skills, abilities, knowledge, work_activities, work_context, work_styles).
    Returns all unique element names with their average importance across occupations."""
    valid = {"skills", "abilities", "knowledge", "work_activities", "work_context", "work_styles"}
    if category not in valid:
        raise HTTPException(status_code=400, detail=f"Category must be one of: {', '.join(sorted(valid))}")

    elements = _element_index.get(category, {})
    result = []
    for name, entries in elements.items():
        values = [v for _, v in entries]
        avg_val = sum(values) / len(values) if values else 0
        result.append({
            "element_name": name,
            "occupation_count": len(entries),
            "average_importance": round(avg_val, 2),
        })

    result.sort(key=lambda x: x["average_importance"], reverse=True)
    total = len(result)
    return {
        "category": category,
        "total": total,
        "offset": offset,
        "limit": limit,
        "elements": result[offset:offset + limit],
    }


@app.get("/api/browse/descriptors/{category}/{element_name}")
def browse_descriptor_occupations(
    category: str,
    element_name: str,
    job_zone: int | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Get occupations ranked by a specific descriptor element."""
    valid = {"skills", "abilities", "knowledge", "work_activities", "work_context", "work_styles"}
    if category not in valid:
        raise HTTPException(status_code=400, detail=f"Category must be one of: {', '.join(sorted(valid))}")

    entries = _element_index.get(category, {}).get(element_name, [])
    if not entries:
        raise HTTPException(status_code=404, detail=f"Element '{element_name}' not found in {category}")

    results = []
    for soc_code, importance in entries:
        occ = _occupations.get(soc_code, {})
        if job_zone is not None and occ.get("job_zone") != job_zone:
            continue
        results.append({
            "uk_soc_2020": soc_code,
            "title": occ.get("title", ""),
            "importance": round(importance, 2),
            "job_zone": occ.get("job_zone"),
        })

    results.sort(key=lambda x: x["importance"], reverse=True)
    total = len(results)
    return {
        "category": category,
        "element_name": element_name,
        "total": total,
        "offset": offset,
        "limit": limit,
        "occupations": results[offset:offset + limit],
    }


@app.get("/api/browse/technology-skills")
def browse_technology_skills(
    q: str = Query(default="", description="Filter technology names"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Browse all technology skill names across all occupations."""
    results = _all_tech_skills
    if q:
        q_lower = q.lower()
        results = [t for t in results if q_lower in t.lower()]

    total = len(results)
    items = []
    for name in results[offset:offset + limit]:
        count = len(_tech_index.get(name.lower(), []))
        items.append({"name": name, "occupation_count": count})

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "technology_skills": items,
    }


@app.get("/api/browse/tools-used")
def browse_tools_used(
    q: str = Query(default="", description="Filter tool names"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    """Browse all tool/equipment names across all occupations."""
    results = _all_tools
    if q:
        q_lower = q.lower()
        results = [t for t in results if q_lower in t.lower()]

    total = len(results)
    items = []
    for name in results[offset:offset + limit]:
        count = len(_tool_index.get(name.lower(), []))
        items.append({"name": name, "occupation_count": count})

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "tools_used": items,
    }


# --- Crosswalk ---

@app.get("/api/onet-occupations")
def search_onet_occupations(
    q: str = Query(default="", description="Search O*NET occupations by SOC code or title"),
    limit: int = Query(default=10, ge=1, le=100),
):
    """Search unique O*NET occupations from the crosswalk for autocomplete."""
    if not q.strip():
        return {"total": len(_onet_occupations), "occupations": _onet_occupations[:limit]}
    q_lower = q.lower().strip()
    matches = [o for o in _onet_occupations if q_lower in o["onet_soc"].lower() or q_lower in o["title"].lower()]
    return {"total": len(matches), "occupations": matches[:limit]}


@app.get("/api/crosswalk")
def get_crosswalk(
    uk_soc: int | None = Query(default=None, description="Filter by UK SOC code"),
    onet_soc: str | None = Query(default=None, description="Filter by O*NET SOC code"),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    """Get the US O*NET to UK SOC 2020 crosswalk."""
    xw = _crosswalk

    if uk_soc is not None:
        xw = [x for x in xw if x.get("uk_soc_2020") == uk_soc]
    if onet_soc is not None:
        xw = [x for x in xw if x.get("onet_soc") == onet_soc]

    total = len(xw)
    xw = xw[offset:offset + limit]

    return {"total": total, "offset": offset, "limit": limit, "crosswalk": xw}


# --- Stats ---

@app.get("/api/stats")
def get_stats():
    """Get dataset statistics."""
    total_tasks = sum(len(occ.get("tasks", [])) for occ in _occupations.values())
    total_tech = len(_all_tech_skills)
    total_tools = len(_all_tools)
    return {
        "total_occupations": len(_occupation_index),
        "total_tasks": total_tasks,
        "total_technology_skills": total_tech,
        "total_tools_used": total_tools,
        "soc_version": "UK SOC 2020",
        "source": "O*NET v30.2 (translated via ISCO-08 crosswalk)",
        "data_categories": [
            "abilities", "skills", "knowledge", "work_activities",
            "work_context", "work_styles", "interests", "work_values",
            "tasks", "technology_skills", "tools_used", "detailed_work_activities",
            "emerging_tasks", "reported_job_titles", "education", "related_occupations",
        ],
    }


@app.get("/api/element-descriptions")
def get_element_descriptions():
    """Get O*NET element descriptions lookup (element_id -> description)."""
    return _element_descriptions


# --- Static file serving (production) ---

if STATIC_DIR and STATIC_DIR.is_dir():
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the SvelteKit SPA. Tries the exact file first, falls back to index.html."""
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
