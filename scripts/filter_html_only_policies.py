import json
from pathlib import Path

state_path = Path("/opt/icrawler/downloads/policy_updates_state.json")
data = json.loads(state_path.read_text(encoding="utf-8"))

only_html_entries = []
for entry in data.get("entries", []):
    docs = entry.get("documents") or []
    if docs and all((doc.get("type") or "").lower() == "html" for doc in docs):
        only_html_entries.append(
            {
                "serial": entry.get("serial"),
                "title": entry.get("title"),
                "remark": entry.get("remark"),
                "documents": docs,
            }
        )

print(f"共找到 {len(only_html_entries)} 条制度：")
for item in only_html_entries:
    print(item["serial"], item["title"])
