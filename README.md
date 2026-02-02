# Taiwan Highway Traffic MCP Server v2

基於交通部高速公路局公開資料的 MCP 伺服器，提供即時國道路況查詢。

## 功能
- `get_congested_sections`: 獲取目前全台國道壅塞路段。
- `search_traffic`: 按關鍵字（如「國道1號」、「內湖」）查詢特定路段。
- `get_all_roads`: 列出所有可查詢的道路。

## 資料來源
- [交通部高速公路局 - 路段即時路況動態資訊(v2.0)](https://data.gov.tw/dataset/37658)
- [交通部高速公路局 - 路段基本資訊(v2.0)](https://data.gov.tw/dataset/37652)

## 🛠 Dive 設定指南
若要在 Dive 中使用此伺服器，請新增一個 `stdio` 類型的伺服器：

- **Command**: `/Applications/Dive.app/Contents/Resources/python/bin/python3`
- **Args**: `{{PWD}}/src/server.py`
- **Env**:
    - `PYTHONPATH`: `{{PWD}}/src`

*(請將 `{{PWD}}` 替換為此專案的絕對路徑)*

## 安裝依賴
本專案建議使用 Dive 內建的 Python 環境以確保 MCP 支援：
```bash
/Applications/Dive.app/Contents/Resources/python/bin/pip install -r requirements.txt --break-system-packages
```
