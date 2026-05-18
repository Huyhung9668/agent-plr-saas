from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from config import DATABASE_DIR


DB_PATH = DATABASE_DIR / "plr_database.sqlite"


def init_database() -> Path:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_title TEXT,
                category TEXT,
                product_type TEXT,
                license_type TEXT,
                final_score REAL,
                saas_potential_score INTEGER,
                source_path TEXT,
                payload_json TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    return DB_PATH


def save_analyses(results: list[dict]) -> Path:
    init_database()
    with sqlite3.connect(DB_PATH) as conn:
        for item in results:
            conn.execute(
                """
                INSERT INTO analyses (
                    original_title, category, product_type, license_type,
                    final_score, saas_potential_score, source_path, payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.get("original_title"),
                    item.get("category"),
                    item.get("product_type"),
                    item.get("license_type"),
                    item.get("final_score"),
                    item.get("saas_potential_score"),
                    item.get("source_path"),
                    json.dumps(item, ensure_ascii=False),
                ),
            )
    return DB_PATH
