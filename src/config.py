# Configuration and Constants
LIVE_TRAFFIC_URL = "https://tisvcloud.freeway.gov.tw/history/motc20/LiveTraffic.xml"
ROAD_SECTION_URL = "https://tisvcloud.freeway.gov.tw/history/motc20/Section.xml"

# Congestion levels mapping based on XML (CongestionLevel tag)
# 1: Green (>80 km/h)
# 2: Orange (60-80 km/h)
# 3: Red (40-60 km/h)
# 4: Dark Red (20-40 km/h)
# 5: Purple (<20 km/h)
# Note: Exact thresholds might vary by road type, but these are general indicators.
CONGESTION_MAP = {
    "1": "順暢 (Speed > 80)",
    "2": "穩定 (Speed 60-80)",
    "3": "繁忙 (Speed 40-60)",
    "4": "壅塞 (Speed 20-40)",
    "5": "嚴重壅塞 (Speed < 20)"
}
