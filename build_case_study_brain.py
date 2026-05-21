from __future__ import annotations

import argparse
import json

from case_study_brain import case_study_summary, ingest_case_study_brain


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Case Study Brain from the old backup/data folder.")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild the case-study SQLite database from scratch.")
    parser.add_argument("--limit", type=int, default=300, help="Max files to scan this run. Use 0 for full scan.")
    args = parser.parse_args()

    max_files = None if args.limit == 0 else max(1, args.limit)
    result = ingest_case_study_brain(rebuild=args.rebuild, max_files=max_files)
    print(json.dumps({"ingest": result.__dict__, "summary": case_study_summary()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
