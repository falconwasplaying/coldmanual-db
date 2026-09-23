# ColdManual Documentation Database (`coldmanual-db`)

The official centralized registry, feeds, and metadata database for [**ColdManual**](https://github.com/falconwasplaying/coldmanual) — the native, low-resource offline documentation browser and reader for programming languages and frameworks.

---

## 🚀 Overview

`coldmanual-db` separates documentation metadata from the desktop client application. Every supported language, library, and framework is declared as a JSON manifest under `docsets/`, containing:
- Upstream release lifecycles.
- **LTS (Long Term Support)** tags.
- **EOL (End of Life)** status flags.
- Direct docset archive download links and verification sizes.

All manifests are compiled into a unified, high-speed [`catalog.json`](catalog.json) feed consumed by the ColdManual desktop client.

---

## 🌐 Public Feed Endpoints

The compiled catalog can be fetched directly by clients using either the GitHub raw endpoint or the jsDelivr global CDN:

| Feed | URL | Description |
| :--- | :--- | :--- |
| **Primary (GitHub Raw)** | `https://raw.githubusercontent.com/falconwasplaying/coldmanual-db/main/catalog.json` | Direct raw file from main branch |
| **Fast CDN (jsDelivr)** | `https://cdn.jsdelivr.net/gh/falconwasplaying/coldmanual-db@main/catalog.json` | Globally cached, high-availability CDN |
| **Minified CDN** | `https://cdn.jsdelivr.net/gh/falconwasplaying/coldmanual-db@main/catalog.min.json` | Stripped whitespace for minimal bandwidth |

---

## 📂 Repository Structure

```
coldmanual-db/
├── .github/
│   └── workflows/
│       └── validate.yml         # CI verification on PRs & main push
├── docsets/                     # Individual technology manifests
│   ├── cpp.json
│   ├── django.json
│   ├── docker.json
│   ├── go.json
│   ├── javascript.json
│   ├── nodejs.json
│   ├── postgresql.json
│   ├── python.json
│   ├── qt.json
│   ├── react.json
│   ├── rust.json
│   └── sqlite.json
├── schema/
│   └── docset.schema.json       # JSON Schema definition
├── scripts/
│   └── build_catalog.py         # Catalog compiler and validator
├── catalog.json                 # Unified compiled catalog
├── catalog.min.json             # Minified compiled catalog
├── LICENSE                      # MIT License
└── README.md
```

---

## 📝 Manifest Specification

Each file in `docsets/<id>.json` must follow [`schema/docset.schema.json`](schema/docset.schema.json):

```json
{
  "id": "python",
  "name": "Python",
  "category": "Languages",
  "description": "An interpreted, high-level, general-purpose programming language emphasizing code readability.",
  "icon": "python",
  "format": "dash",
  "latest_version": "3.13",
  "latest_lts_version": "3.12",
  "versions": [
    {
      "version": "3.13",
      "display_name": "v3.13 (3.13.1)",
      "is_lts": false,
      "is_eol": false,
      "is_latest": true,
      "release_date": "2024-10-07",
      "download_url": "https://kapeli.com/feeds/Python_3.tgz",
      "size_bytes": 18450000
    },
    {
      "version": "3.8",
      "display_name": "v3.8 (3.8.20)",
      "is_lts": false,
      "is_eol": true,
      "is_latest": false,
      "release_date": "2019-10-14",
      "download_url": "https://kapeli.com/feeds/Python_3.tgz",
      "size_bytes": 16900000
    }
  ]
}
```

### Supported Categories
- `Languages`
- `Frontend`
- `Backend`
- `Databases`
- `DevOps`
- `Tools`
- `General`

---

## 🛠️ Contributing a New Docset

1. Fork and clone this repository.
2. Create a new manifest file in `docsets/<id>.json` (e.g. `docsets/kotlin.json`).
3. Compile and validate the catalog locally:
   ```bash
   python scripts/build_catalog.py
   ```
4. Ensure all schema checks pass and `catalog.json` is updated.
5. Submit a pull request. Once merged into `main`, ColdManual clients worldwide will automatically display the new docset!

---

## 📄 License

This catalog repository, schema, and compiler tooling are licensed under the [MIT License](LICENSE).

### Third-Party Trademarks & Documentation
- All product names, logos, brand names, and trademarks mentioned in this catalog (e.g., Python, Qt, Rust, React, PostgreSQL) are the property of their respective owners.
- Offline documentation sets linked in this catalog remain under the respective copyright and license terms of their original upstream authors and foundations.
