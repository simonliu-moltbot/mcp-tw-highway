import httpx
import xmltodict
import sys
from typing import Dict, List, Optional
from config import LIVE_TRAFFIC_URL, ROAD_SECTION_URL

# Cache for road sections to avoid repeated fetching
_road_sections_cache: Dict[str, dict] = {}

async def fetch_xml_as_dict(url: str) -> dict:
    """Fetch XML from URL and convert to dictionary."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            # freeway XML might have encoding issues, httpx usually handles it
            return xmltodict.parse(response.text)
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        raise

async def get_road_sections() -> Dict[str, dict]:
    """Fetch and cache road section definitions."""
    global _road_sections_cache
    if _road_sections_cache:
        return _road_sections_cache
    
    data = await fetch_xml_as_dict(ROAD_SECTION_URL)
    sections = data.get("SectionList", {}).get("Sections", {}).get("Section", [])
    
    if isinstance(sections, dict):
        sections = [sections]
        
    for sec in sections:
        sid = sec.get("SectionID")
        if sid:
            _road_sections_cache[sid] = {
                "name": sec.get("SectionName"),
                "road": sec.get("RoadName"),
                "direction": sec.get("RoadDirection"),
                "start": sec.get("RoadSection", {}).get("Start"),
                "end": sec.get("RoadSection", {}).get("End"),
                "length": sec.get("SectionLength"),
                "speed_limit": sec.get("SpeedLimit")
            }
    return _road_sections_cache

async def get_live_traffic() -> List[dict]:
    """Fetch live traffic data."""
    data = await fetch_xml_as_dict(LIVE_TRAFFIC_URL)
    traffics = data.get("LiveTrafficList", {}).get("LiveTraffics", {}).get("LiveTraffic", [])
    if isinstance(traffics, dict):
        traffics = [traffics]
    return traffics

async def get_traffic_with_names(min_congestion: int = 1) -> List[dict]:
    """Get traffic data merged with road names."""
    sections = await get_road_sections()
    live_data = await get_live_traffic()
    
    results = []
    for entry in live_data:
        sid = entry.get("SectionID")
        congestion = int(entry.get("CongestionLevel", 1))
        
        if congestion >= min_congestion:
            info = sections.get(sid, {"name": f"Unknown Section ({sid})"})
            results.append({
                "section_id": sid,
                "name": info.get("name"),
                "speed": entry.get("TravelSpeed"),
                "travel_time": entry.get("TravelTime"),
                "congestion_level": congestion,
                "road": info.get("road"),
                "direction": info.get("direction")
            })
    return results

async def search_traffic_by_name(query: str) -> List[dict]:
    """Search for traffic info by road or section name."""
    all_traffic = await get_traffic_with_names()
    query = query.lower()
    return [t for t in all_traffic if t["name"] and query in t["name"].lower()]
