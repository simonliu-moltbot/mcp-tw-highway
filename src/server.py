import asyncio
import sys
import os

# Import hack to allow local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types

try:
    from logic import get_traffic_with_names, search_traffic_by_name, get_road_sections
    from config import CONGESTION_MAP
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    # Define fallbacks if needed, but here we expect the env to be correct

server = Server("mcp-tw-traffic-v2")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available traffic tools."""
    return [
        types.Tool(
            name="get_congested_sections",
            description="獲取目前國道壅塞路段 (預設顯示時速低於 80km/h 的路段)",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_level": {
                        "type": "integer",
                        "description": "最低壅塞等級 (1: 順暢, 2: 穩定, 3: 繁忙, 4: 壅塞, 5: 嚴重壅塞). 預設為 2 (時速 < 80)",
                        "default": 2
                    }
                }
            },
        ),
        types.Tool(
            name="search_traffic",
            description="按路段名稱或道路名稱（如 '國道1號', '內湖'）查詢即時路況",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "關鍵字，例如 '國道3號' 或 '汐止'"
                    }
                },
                "required": ["query"]
            },
        ),
        types.Tool(
            name="get_all_roads",
            description="列出所有可查詢的道路名稱",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""
    try:
        if name == "get_congested_sections":
            min_level = arguments.get("min_level", 2) if arguments else 2
            data = await get_traffic_with_names(min_congestion=min_level)
            
            # Sort by congestion level descending, then speed ascending
            data.sort(key=lambda x: (-x['congestion_level'], int(x['speed']) if x['speed'] else 999))
            
            if not data:
                return [types.TextContent(type="text", text="目前沒有符合條件的壅塞路段。")]
            
            lines = [f"🚦 偵測到 {len(data)} 個路段狀況較多 (Level >= {min_level}):"]
            for item in data[:20]: # Limit to top 20
                level_str = CONGESTION_MAP.get(str(item['congestion_level']), "未知")
                lines.append(f"- {item['name']}: {item['speed']} km/h ({level_str})")
            
            if len(data) > 20:
                lines.append(f"... 還有 {len(data) - 20} 個路段未列出。")
                
            return [types.TextContent(type="text", text="\n".join(lines))]

        elif name == "search_traffic":
            query = arguments.get("query")
            if not query:
                return [types.TextContent(type="text", text="請提供查詢關鍵字。")]
            
            data = await search_traffic_by_name(query)
            if not data:
                return [types.TextContent(type="text", text=f"找不到與 '{query}' 相關的路況資料。")]
            
            lines = [f"🔍 為您找到 {len(data)} 筆關於 '{query}' 的資料:"]
            for item in data[:30]:
                level_str = CONGESTION_MAP.get(str(item['congestion_level']), "未知")
                lines.append(f"- {item['name']}: {item['speed']} km/h (等級: {level_str})")
            
            return [types.TextContent(type="text", text="\n".join(lines))]

        elif name == "get_all_roads":
            sections = await get_road_sections()
            roads = sorted(list(set(s['road'] for s in sections.values() if s.get('road'))))
            return [types.TextContent(type="text", text="可用道路列表：\n" + ", ".join(roads))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        print(f"Error in tool {name}: {e}", file=sys.stderr)
        return [types.TextContent(type="text", text=f"發生錯誤: {str(e)}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-tw-traffic-v2",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
