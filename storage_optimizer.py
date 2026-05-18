from __future__ import annotations

import json
import shutil
import sqlite3
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from agent_profiles import get_agent_profiles
from config import DATABASE_DIR, ROOT_DIR

ARCHIVE_DIR = DATABASE_DIR / "archives"


@dataclass
class OptimizeCandidate:
    path: Path
    reason: str
    action: str = "archive"


def optimize_storage(*, apply: bool = False, include_legacy_db: bool = True) -> dict:
    """Archive raw/legacy knowledge files that are not required by the 8088 role-brain runtime."""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    candidates = _storage_candidates(include_legacy_db=include_legacy_db)
    before = _total_size(c.path for c in candidates)
    manifest = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "apply": apply,
        "include_legacy_db": include_legacy_db,
        "candidates": [],
    }
    archived = []
    removed = []
    skipped = []
    reclaimed = 0

    for candidate in candidates:
        path = candidate.path
        if not path.exists():
            skipped.append({"path": str(path), "reason": "missing"})
            continue
        size = _path_size(path)
        item = {
            "path": str(path),
            "size_bytes": size,
            "reason": candidate.reason,
            "action": candidate.action,
        }
        manifest["candidates"].append(item)
        if not apply:
            skipped.append({**item, "reason": "dry_run"})
            continue
        if candidate.action == "delete":
            _remove_path(path)
            removed.append(item)
            reclaimed += size
            continue
        archive_path = _archive_path_for(path)
        _archive_path(path, archive_path)
        if _verify_archive(archive_path):
            _remove_path(path)
            archived.append({**item, "archive": str(archive_path)})
            reclaimed += size
        else:
            skipped.append({**item, "reason": "archive_verify_failed"})

    manifest["archived"] = archived
    manifest["removed"] = removed
    manifest["skipped"] = skipped
    manifest["before_bytes"] = before
    manifest["reclaimed_bytes"] = reclaimed
    manifest_path = ARCHIVE_DIR / f"storage_optimize_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "apply": apply,
        "archive_dir": str(ARCHIVE_DIR),
        "manifest": str(manifest_path),
        "candidate_count": len(candidates),
        "archived_count": len(archived),
        "removed_count": len(removed),
        "skipped_count": len(skipped),
        "candidate_mb": round(before / 1024 / 1024, 2),
        "reclaimed_mb": round(reclaimed / 1024 / 1024, 2),
        "archived": archived,
        "removed": removed,
        "skipped": skipped,
    }


def vacuum_active_brains() -> dict:
    results = []
    for db_path in _active_db_paths():
        if not db_path.exists():
            continue
        before = db_path.stat().st_size
        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA optimize")
            conn.execute("VACUUM")
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        after = db_path.stat().st_size
        results.append(
            {
                "path": str(db_path),
                "before_mb": round(before / 1024 / 1024, 2),
                "after_mb": round(after / 1024 / 1024, 2),
                "saved_mb": round((before - after) / 1024 / 1024, 2),
            }
        )
    return {"databases": results, "saved_mb": round(sum(item["saved_mb"] for item in results), 2)}


def storage_report() -> dict:
    directories = []
    for path in sorted(ROOT_DIR.iterdir()):
        if not path.is_dir():
            continue
        directories.append({"name": path.name, "size_mb": round(_path_size(path) / 1024 / 1024, 2), "files": _file_count(path)})
    directories.sort(key=lambda item: item["size_mb"], reverse=True)
    active = [str(path) for path in _active_db_paths() if path.exists()]
    return {"directories": directories, "active_brain_dbs": active, "archive_dir": str(ARCHIVE_DIR)}


def _storage_candidates(*, include_legacy_db: bool) -> list[OptimizeCandidate]:
    active_paths = {path.resolve() for path in _active_db_paths() if path.exists()}
    candidates: list[OptimizeCandidate] = []
    if include_legacy_db:
        legacy = DATABASE_DIR / "agent_brain.sqlite"
        if legacy.exists() and legacy.resolve() not in active_paths:
            candidates.append(OptimizeCandidate(legacy, "Legacy monolithic brain DB; web_app.py uses role brain DBs."))
    for name in ("media_extracted_text", "media_brain_text"):
        path = DATABASE_DIR / name
        if path.exists():
            candidates.append(OptimizeCandidate(path, "Raw extracted/media text already ingested into role brain SQLite."))
    for profile in get_agent_profiles():
        for name in ("media_extracted_text", "media_brain_text", "backup_media_extracted_text", "backup_media_brain_text"):
            path = profile.brain_dir / name
            if path.exists():
                candidates.append(OptimizeCandidate(path, f"Raw/backup media text for {profile.key}; SQLite brain remains active."))
    for pattern in ("*.sqlite-journal", "test_*.sqlite", "test_write.tmp", "launch_os.sqlite", "launch_os_sandbox.sqlite"):
        for path in DATABASE_DIR.glob(pattern):
            if path.exists() and path.resolve() not in active_paths:
                candidates.append(OptimizeCandidate(path, "Temporary/test database artifact.", action="delete"))
    return _dedupe_candidates(candidates)


def _active_db_paths() -> list[Path]:
    return [profile.db_path for profile in get_agent_profiles()]


def _dedupe_candidates(candidates: list[OptimizeCandidate]) -> list[OptimizeCandidate]:
    seen = set()
    unique = []
    for item in candidates:
        key = str(item.path.resolve())
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _archive_path_for(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "_".join(path.relative_to(ROOT_DIR).parts).replace(":", "").replace(" ", "_")
    return ARCHIVE_DIR / f"{safe}_{stamp}.zip"


def _archive_path(path: Path, archive_path: Path) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        if path.is_file():
            archive.write(path, path.relative_to(ROOT_DIR))
            return
        for child in path.rglob("*"):
            if child.is_file():
                archive.write(child, child.relative_to(ROOT_DIR))


def _verify_archive(archive_path: Path) -> bool:
    try:
        with zipfile.ZipFile(archive_path, "r") as archive:
            if archive.testzip() is not None:
                return False
            return bool(archive.namelist())
    except Exception:
        return False


def _remove_path(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def _path_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    if not path.exists():
        return 0
    return sum(child.stat().st_size for child in path.rglob("*") if child.is_file())


def _total_size(paths) -> int:
    return sum(_path_size(Path(path)) for path in paths)


def _file_count(path: Path) -> int:
    if path.is_file():
        return 1
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compact local Agent PLR SaaS storage.")
    parser.add_argument("--apply", action="store_true", help="Archive/delete candidates. Without this, only dry-runs.")
    parser.add_argument("--no-legacy-db", action="store_true", help="Do not archive database/agent_brain.sqlite.")
    parser.add_argument("--vacuum", action="store_true", help="Run VACUUM on active role brain databases.")
    args = parser.parse_args()
    result = optimize_storage(apply=args.apply, include_legacy_db=not args.no_legacy_db)
    if args.vacuum:
        result["vacuum"] = vacuum_active_brains()
    print(json.dumps(result, ensure_ascii=False, indent=2))
