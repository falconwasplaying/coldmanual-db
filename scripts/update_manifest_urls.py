#!/usr/bin/env python3
"""
Updates download_url and size_bytes in docsets/*.json to point to coldmanual-db.
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCSETS_DIR = ROOT_DIR / "docsets"
MANUALS_DIR = ROOT_DIR / "manuals"

for json_file in sorted(DOCSETS_DIR.glob("*.json")):
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    docset_id = data["id"]
    manual_file = MANUALS_DIR / f"{docset_id}.tgz"
    if not manual_file.exists():
        print(f"[WARN] No manual archive for {docset_id}")
        continue
    
    file_size = manual_file.stat().st_size
    repo_url = f"https://github.com/falconwasplaying/coldmanual-db/raw/main/manuals/{docset_id}.tgz"

    # Update all version entries
    for v in data.get("versions", []):
        v["download_url"] = repo_url
        v["size_bytes"] = file_size

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"[UPDATED] {json_file.name}: {repo_url} ({file_size:,} bytes)")
