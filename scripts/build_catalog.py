#!/usr/bin/env python3
"""
ColdManual Catalog Compiler & Schema Validator
Scans docsets/*.json, validates structure and tags, and compiles unified catalog.json.
"""

import json
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DOCSETS_DIR = ROOT_DIR / "docsets"
CATALOG_PATH = ROOT_DIR / "catalog.json"
CATALOG_MIN_PATH = ROOT_DIR / "catalog.min.json"
SCHEMA_PATH = ROOT_DIR / "schema" / "docset.schema.json"

REQUIRED_FIELDS = ["id", "name", "category", "description", "icon", "format", "latest_version", "versions"]
ALLOWED_CATEGORIES = {"Languages", "Frontend", "Backend", "Databases", "DevOps", "Tools", "General"}
ALLOWED_FORMATS = {"dash", "devdocs", "html"}

def validate_docset(manifest: dict, filename: str) -> list[str]:
    errors = []
    
    # Check top-level required fields
    for field in REQUIRED_FIELDS:
        if field not in manifest or manifest[field] is None:
            errors.append(f"Missing required field: '{field}'")
            
    if "id" in manifest and not manifest["id"].replace("-", "").replace("_", "").isalnum():
        errors.append(f"Invalid id '{manifest['id']}': must be lowercase alphanumeric with hyphens/underscores")

    if "category" in manifest and manifest["category"] not in ALLOWED_CATEGORIES:
        errors.append(f"Invalid category '{manifest['category']}': must be one of {sorted(ALLOWED_CATEGORIES)}")

    if "format" in manifest and manifest["format"] not in ALLOWED_FORMATS:
        errors.append(f"Invalid format '{manifest['format']}': must be one of {sorted(ALLOWED_FORMATS)}")

    versions = manifest.get("versions", [])
    if not isinstance(versions, list) or len(versions) == 0:
        errors.append("Field 'versions' must be a non-empty array")
    else:
        seen_versions = set()
        for idx, v in enumerate(versions):
            if not isinstance(v, dict):
                errors.append(f"Version #{idx} is not an object")
                continue
            ver_id = v.get("version")
            if not ver_id or not isinstance(ver_id, str):
                errors.append(f"Version #{idx} missing string 'version'")
                continue
            if ver_id in seen_versions:
                errors.append(f"Duplicate version '{ver_id}' found in manifest")
            seen_versions.add(ver_id)

            # Type checking on optional fields
            if "is_lts" in v and not isinstance(v["is_lts"], bool):
                errors.append(f"Version '{ver_id}' 'is_lts' must be a boolean")
            if "is_eol" in v and not isinstance(v["is_eol"], bool):
                errors.append(f"Version '{ver_id}' 'is_eol' must be a boolean")
            if "size_bytes" in v and not isinstance(v["size_bytes"], int):
                errors.append(f"Version '{ver_id}' 'size_bytes' must be an integer")

    return errors


def build_catalog():
    print("=" * 60)
    print(" ColdManual Catalog Compiler")
    print("=" * 60)

    if not DOCSETS_DIR.exists():
        print(f"Error: Docsets directory not found at {DOCSETS_DIR}")
        sys.exit(1)

    json_files = sorted(DOCSETS_DIR.glob("*.json"))
    if not json_files:
        print(f"Error: No JSON files found in {DOCSETS_DIR}")
        sys.exit(1)

    compiled_docsets = []
    total_versions = 0
    total_lts = 0
    total_eol = 0
    has_errors = False

    for file_path in json_files:
        rel_name = file_path.name
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[FAIL] {rel_name}: JSON Parse Error - {e}")
            has_errors = True
            continue

        errors = validate_docset(data, rel_name)
        if errors:
            print(f"[FAIL] {rel_name}:")
            for err in errors:
                print(f"       - {err}")
            has_errors = True
            continue

        # Normalization
        versions = data.get("versions", [])
        for v in versions:
            total_versions += 1
            if v.get("is_lts"):
                total_lts += 1
            if v.get("is_eol"):
                total_eol += 1
            if "display_name" not in v or not v["display_name"]:
                v["display_name"] = f"v{v['version']}"
            if "is_lts" not in v:
                v["is_lts"] = False
            if "is_eol" not in v:
                v["is_eol"] = False
            if "is_latest" not in v:
                v["is_latest"] = (v["version"] == data["latest_version"])

        # Auto-compute latest_lts_version if missing
        if "latest_lts_version" not in data or not data["latest_lts_version"]:
            for v in versions:
                if v.get("is_lts") and not v.get("is_eol"):
                    data["latest_lts_version"] = v["version"]
                    break

        icon_name = data.get("icon", data.get("id"))
        has_logo = (ROOT_DIR / "logos" / f"{icon_name}.svg").exists()
        logo_tag = "SVG: OK" if has_logo else "NO SVG"
        print(f"[OK]   {data['id']:<15} -> {data['name']:<18} ({len(versions)} versions) [{logo_tag}]")
        compiled_docsets.append(data)

    if has_errors:
        print("\n[ERROR] Validation failed. Fix errors above before compiling.")
        sys.exit(1)

    # Sort catalog by name
    compiled_docsets.sort(key=lambda d: d.get("name", "").lower())

    # Write formatted catalog.json
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(compiled_docsets, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # Write minified catalog.min.json
    with open(CATALOG_MIN_PATH, "w", encoding="utf-8") as f:
        json.dump(compiled_docsets, f, separators=(",", ":"), ensure_ascii=False)

    print("-" * 60)
    print(f"Successfully compiled {len(compiled_docsets)} docsets to:")
    print(f"  -> {CATALOG_PATH.name} ({CATALOG_PATH.stat().st_size:,} bytes)")
    print(f"  -> {CATALOG_MIN_PATH.name} ({CATALOG_MIN_PATH.stat().st_size:,} bytes)")
    print(f"Total Versions: {total_versions} | Active/Past LTS: {total_lts} | EOL: {total_eol}")
    print("=" * 60)


if __name__ == "__main__":
    build_catalog()
