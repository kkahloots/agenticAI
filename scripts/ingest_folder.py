#!/usr/bin/env python3
"""
Ingest all documents from DOCS_FOLDER into ChromaDB.
Tracks already-ingested files in data/ingested.json to avoid re-indexing.

Usage:
    PYTHONPATH=. python scripts/ingest_folder.py [--folder data/docs] [--reset]
"""
import argparse
import json
import pathlib
import sys
import os

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from src.tools.loader import load_file
from src.tools.knowledge import ingest_documents

MANIFEST_PATH = pathlib.Path("data/ingested.json")
SUPPORTED_EXTS = {".txt", ".md", ".pdf", ".docx", ".eml"}


def load_manifest() -> set[str]:
    if MANIFEST_PATH.exists():
        return set(json.loads(MANIFEST_PATH.read_text()))
    return set()


def save_manifest(ingested: set[str]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(sorted(ingested), indent=2))


def ingest_folder(folder: str, reset: bool = False) -> None:
    root = pathlib.Path(folder)
    if not root.exists():
        print(f"Folder not found: {root}")
        sys.exit(1)

    manifest = set() if reset else load_manifest()
    files = [p for p in root.rglob("*") if p.suffix.lower() in SUPPORTED_EXTS]

    new_files = [f for f in files if str(f) not in manifest]
    if not new_files:
        print(f"Nothing new to ingest ({len(files)} files already indexed).")
        return

    total_chunks = 0
    for path in new_files:
        chunks = load_file(path)
        if not chunks:
            print(f"  skip (no text): {path.name}")
            continue
        ingest_documents(chunks)
        manifest.add(str(path))
        total_chunks += len(chunks)
        print(f"  ingested {len(chunks):>3} chunk(s): {path.relative_to(root.parent)}")

    save_manifest(manifest)
    print(f"\nDone. {len(new_files)} files → {total_chunks} chunks ingested into ChromaDB.")
    print(f"Manifest updated: {MANIFEST_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", default="data/docs", help="Root folder to scan")
    parser.add_argument("--reset", action="store_true", help="Re-ingest all files, ignoring manifest")
    args = parser.parse_args()
    ingest_folder(args.folder, reset=args.reset)
