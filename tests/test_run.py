import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from logic import get_traffic_with_names, get_road_sections

async def test():
    print("Testing Road Sections fetching...", file=sys.stderr)
    sections = await get_road_sections()
    print(f"Found {len(sections)} road sections.", file=sys.stderr)
    
    # Print a few samples
    sample_ids = list(sections.keys())[:3]
    for sid in sample_ids:
        print(f"Sample Section {sid}: {sections[sid]['name']}", file=sys.stderr)

    print("\nTesting Live Traffic fetching...", file=sys.stderr)
    traffic = await get_traffic_with_names(min_congestion=1)
    print(f"Found {len(traffic)} live traffic records.", file=sys.stderr)
    
    congested = [t for t in traffic if t['congestion_level'] >= 3]
    print(f"Found {len(congested)} congested sections (Level >= 3).", file=sys.stderr)
    
    for c in congested[:5]:
        print(f"- {c['name']}: {c['speed']} km/h", file=sys.stderr)

    print("\nTest completed successfully.", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(test())
