#!/usr/bin/env python3
"""
Downloads docset manual archives into the coldmanual-db/manuals directory.
Uses mirrors with automatic failover and download resumption.
"""

import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
MANUALS_DIR = ROOT_DIR / "manuals"
MANUALS_DIR.mkdir(parents=True, exist_ok=True)

MIRRORS = ["tokyo", "frankfurt", "newyork", "sanfrancisco", "london"]

# Mapping of docset ID to remote filename
DOCSET_MAP = {
    "sqlite": ("SQLite.tgz", False),
    "postgresql": ("PostgreSQL.tgz", False),
    "django": ("Django.tgz", False),
    "nodejs": ("NodeJS.tgz", False),
    "react": ("React.tgz", False),
    "python": ("Python.tgz", False),
    "go": ("Go.tgz", False),
    "kotlin": ("kotlin.tgz", True),  # User contributed feed
    "rust": ("Rust.tgz", False),
    "cpp": ("C++.tgz", False),
    "qt": ("Qt.tgz", False),
    "docker": ("Docker.tgz", False),
    "javascript": ("JavaScript.tgz", False),
}

def get_candidate_urls(remote_filename: str, is_user_contrib: bool):
    urls = []
    if is_user_contrib:
        # Kotlin user contrib
        urls.append(f"https://sanfrancisco.kapeli.com/feeds/zzz/user_contributed/build/Kotlin/{remote_filename}")
        urls.append(f"https://newyork.kapeli.com/feeds/zzz/user_contributed/build/Kotlin/{remote_filename}")
        urls.append(f"https://london.kapeli.com/feeds/zzz/user_contributed/build/Kotlin/{remote_filename}")
        urls.append(f"https://kapeli.com/feeds/zzz/user_contributed/build/Kotlin/{remote_filename}")
    else:
        for m in MIRRORS:
            urls.append(f"http://{m}.kapeli.com/feeds/{remote_filename}")
        urls.append(f"https://kapeli.com/feeds/{remote_filename}")
    return urls

def download_file(docset_id: str, remote_filename: str, is_user_contrib: bool):
    dest_path = MANUALS_DIR / f"{docset_id}.tgz"
    temp_path = MANUALS_DIR / f"{docset_id}.tgz.part"

    if dest_path.exists() and dest_path.stat().st_size > 100000:
        print(f"[EXISTS] {docset_id:<12} ({dest_path.stat().st_size:,} bytes) at {dest_path.name}")
        return True

    candidate_urls = get_candidate_urls(remote_filename, is_user_contrib)

    for url in candidate_urls:
        print(f"\n[DOWNLOADING] {docset_id} from {url}...")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'ColdManual/1.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                status = resp.status
                if status != 200:
                    print(f"  Got status {status}, trying next mirror...")
                    continue
                total_len = resp.headers.get('Content-Length')
                total_bytes = int(total_len) if total_len else 0
                
                # Check for 404 HTML disguised as 200
                first_chunk = resp.read(512)
                if b'<!doctype html' in first_chunk.lower():
                    print("  Received HTML page instead of archive, trying next mirror...")
                    continue

                downloaded = len(first_chunk)
                t_start = time.time()
                last_print = t_start

                with open(temp_path, "wb") as f:
                    f.write(first_chunk)
                    while True:
                        chunk = resp.read(256 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        now = time.time()
                        if now - last_print >= 1.0 or downloaded == total_bytes:
                            last_print = now
                            elapsed = now - t_start
                            speed = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                            pct = (downloaded / total_bytes * 100) if total_bytes > 0 else 0
                            mb_down = downloaded / (1024 * 1024)
                            mb_tot = total_bytes / (1024 * 1024)
                            print(f"\r  -> {pct:5.1f}% [{mb_down:6.1f} / {mb_tot:6.1f} MB] @ {speed:5.2f} MB/s", end="", flush=True)

                print()
                if total_bytes > 0 and downloaded < total_bytes:
                    print(f"  Truncated download: {downloaded} < {total_bytes}, retrying...")
                    if temp_path.exists():
                        temp_path.unlink()
                    continue

                # Finalize
                if temp_path.exists():
                    if dest_path.exists():
                        dest_path.unlink()
                    temp_path.rename(dest_path)
                    print(f"[SUCCESS] Saved {docset_id} ({dest_path.stat().st_size:,} bytes) to {dest_path.name}")
                    return True
        except Exception as e:
            print(f"  Error with {url}: {e}")
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass

    print(f"[FAIL] Could not download {docset_id} from any mirror.")
    return False

def main():
    print("=" * 60)
    print(" ColdManual Manuals Downloader")
    print(f" Target Directory: {MANUALS_DIR}")
    print("=" * 60)

    # Allow downloading specific docset via command line args
    targets = sys.argv[1:] if len(sys.argv) > 1 else list(DOCSET_MAP.keys())

    success_count = 0
    fail_count = 0

    for doc_id in targets:
        if doc_id not in DOCSET_MAP:
            print(f"[UNKNOWN] Skipping unknown docset '{doc_id}'")
            continue
        rem_file, is_contrib = DOCSET_MAP[doc_id]
        ok = download_file(doc_id, rem_file, is_contrib)
        if ok:
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 60)
    print(f"Download Summary: {success_count} succeeded, {fail_count} failed.")
    print("=" * 60)

if __name__ == "__main__":
    main()
