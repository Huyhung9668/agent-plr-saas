from __future__ import annotations

import re
import sqlite3
from pathlib import Path

from config import DATABASE_DIR

MEMORY_DIR = Path.home() / ".codex" / "memories"
DB_PATH = MEMORY_DIR / "agent_plr_saas_launch_command_center.sqlite"


TABLE_DEFINITIONS = {
    "products": """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            niche TEXT,
            buyer TEXT,
            promise TEXT,
            format TEXT,
            price TEXT,
            status TEXT DEFAULT 'idea',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "plr_files": """
        CREATE TABLE IF NOT EXISTS plr_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            source_path TEXT,
            category TEXT,
            license_type TEXT,
            risk_level TEXT,
            rebrand_score INTEGER,
            warriorplus_fit INTEGER,
            saas_potential INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "market_research": """
        CREATE TABLE IF NOT EXISTS market_research (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            niche TEXT,
            competitor_patterns TEXT,
            market_gaps TEXT,
            pricing_notes TEXT,
            saturation_risk TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "buyer_avatars": """
        CREATE TABLE IF NOT EXISTS buyer_avatars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            avatar_name TEXT,
            stage TEXT,
            platform TEXT,
            pain TEXT,
            desired_result TEXT,
            objections TEXT,
            buying_trigger TEXT,
            message_angle TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "sales_pages": """
        CREATE TABLE IF NOT EXISTS sales_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            headline TEXT,
            offer_angle TEXT,
            sales_page_md TEXT,
            faq_md TEXT,
            compliance_notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "funnels": """
        CREATE TABLE IF NOT EXISTS funnels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            fe_offer TEXT,
            order_bump TEXT,
            oto1 TEXT,
            oto2 TEXT,
            recurring_offer TEXT,
            commission_plan TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "jv_prospects": """
        CREATE TABLE IF NOT EXISTS jv_prospects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            website_profile TEXT,
            platform TEXT,
            audience_type TEXT,
            contact TEXT,
            niche_fit TEXT,
            list_size_estimate TEXT,
            last_product_promoted TEXT,
            contacted TEXT DEFAULT 'no',
            reply TEXT,
            review_access_sent TEXT DEFAULT 'no',
            promoted TEXT DEFAULT 'no',
            follow_up_date TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "affiliate_swipes": """
        CREATE TABLE IF NOT EXISTS affiliate_swipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            asset_type TEXT,
            subject_line TEXT,
            content TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "saas_plans": """
        CREATE TABLE IF NOT EXISTS saas_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            tool_name TEXT,
            mvp_features TEXT,
            roadmap TEXT,
            pricing TEXT,
            membership_angle TEXT,
            whitelabel_notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
    "exports": """
        CREATE TABLE IF NOT EXISTS exports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            export_type TEXT,
            folder_path TEXT,
            zip_path TEXT,
            status TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """,
}

PROJECT_TASKS = {
    "offer_analyzed": "Offer analyzed",
    "buyer_avatar": "Buyer avatar created",
    "product_package": "Product package planned",
    "product_assets": "Product assets generated",
    "sales_page": "Sales page written",
    "funnel": "Funnel planned",
    "warriorplus_listing": "WarriorPlus listing created",
    "jv_pack": "JV pack created",
    "delivery_page": "Delivery page created",
    "onboarding": "Customer onboarding emails created",
    "saas_plan": "SaaS/membership plan created",
    "export_zip": "ZIP exported",
}

MODULE_TASK_MAP = {
    "idea_score": "offer_analyzed",
    "depth_check": "offer_analyzed",
    "analyze_plr": "offer_analyzed",
    "buyer_avatar": "buyer_avatar",
    "offer_angle": "product_package",
    "upgrade_kit": "product_package",
    "product_assets": "product_assets",
    "sales_page": "sales_page",
    "objections": "sales_page",
    "funnel_plan": "funnel",
    "warriorplus_listing": "warriorplus_listing",
    "jv_page": "jv_pack",
    "swipe_pack": "jv_pack",
    "outreach": "jv_pack",
    "prospects": "jv_pack",
    "tiers": "jv_pack",
    "review_access": "jv_pack",
    "saas_potential": "saas_plan",
    "mvp_plan": "saas_plan",
    "membership": "saas_plan",
    "whitelabel": "saas_plan",
    "delivery_page": "delivery_page",
    "onboarding": "onboarding",
    "export_zip": "export_zip",
    "launch_pack": "export_zip",
}

REQUIRED_ASSETS = {
    "Start Here": "product_assets",
    "Workflow / Campaign Map": "product_package",
    "Templates / Core Asset": "product_assets",
    "Customization Prompts": "product_assets",
    "Checklist": "product_assets",
    "Planner Sheet": "product_assets",
    "Example / Case Study": "product_assets",
    "License / Compliance Note": "product_assets",
    "Sales Page": "sales_page",
    "Funnel Plan": "funnel",
    "WarriorPlus Listing": "warriorplus_listing",
    "JV Page / Swipes": "jv_pack",
    "Delivery Page": "delivery_page",
    "Onboarding Emails": "onboarding",
    "ZIP Export": "export_zip",
}


def init_launch_os_database() -> Path:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=OFF")
        conn.execute("PRAGMA synchronous=OFF")
        for ddl in TABLE_DEFINITIONS.values():
            conn.execute(ddl)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS launch_os_meta (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS project_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                task_key TEXT NOT NULL,
                status TEXT DEFAULT 'missing',
                notes TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(product_id, task_key)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS project_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                note_type TEXT,
                content TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO launch_os_meta (key, value, updated_at)
            VALUES ('schema_version', '20260516_launch_os_2', CURRENT_TIMESTAMP)
            """
        )
    return DB_PATH


def launch_os_status() -> dict:
    init_launch_os_database()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=OFF")
        counts = {}
        for table in TABLE_DEFINITIONS:
            counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        active = _active_project_row(conn)
    return {"path": str(DB_PATH), "tables": list(TABLE_DEFINITIONS), "counts": counts, "activeProject": active}


def infer_product_name(text: str) -> str:
    cleaned = " ".join(str(text or "").split())
    patterns = (
        r"Product(?:\s+Name)?\s*:\s*([A-Z][A-Za-z0-9 +/&'\-]{4,80})",
        r"Sản phẩm(?:\s+nên làm)?\s*:\s*([A-Z][A-Za-z0-9 +/&'\-]{4,80})",
        r"San pham(?:\s+nen lam)?\s*:\s*([A-Z][A-Za-z0-9 +/&'\-]{4,80})",
        r"((?:AI|PLR|WarriorPlus|Email|Digital|SaaS)[A-Za-z0-9 +/&'\-]{4,80}?(?:Launch Kit|Kit|Pack|System|Builder|Engine|Club))",
    )
    for pattern in patterns:
        match = re.search(pattern, cleaned, flags=re.IGNORECASE)
        if match:
            return re.sub(r"\s+", " ", match.group(1).strip(" .,:;"))[:96]
    return ""


def ensure_project_from_text(text: str) -> dict:
    init_launch_os_database()
    product_name = infer_product_name(text)
    with sqlite3.connect(DB_PATH) as conn:
        if not product_name:
            return _active_project_row(conn) or {}
        existing = conn.execute(
            "SELECT id FROM products WHERE lower(product_name) = lower(?) ORDER BY id DESC LIMIT 1",
            (product_name,),
        ).fetchone()
        defaults = _project_defaults(product_name)
        if existing:
            product_id = int(existing[0])
            conn.execute(
                """
                UPDATE products
                SET niche = COALESCE(NULLIF(niche, ''), ?),
                    buyer = COALESCE(NULLIF(buyer, ''), ?),
                    promise = COALESCE(NULLIF(promise, ''), ?),
                    price = COALESCE(NULLIF(price, ''), ?),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (defaults["niche"], defaults["buyer"], defaults["promise"], defaults["price"], product_id),
            )
        else:
            cursor = conn.execute(
                """
                INSERT INTO products (product_name, niche, buyer, promise, format, price, status)
                VALUES (?, ?, ?, ?, ?, ?, 'research')
                """,
                (product_name, defaults["niche"], defaults["buyer"], defaults["promise"], defaults["format"], defaults["price"]),
            )
            product_id = int(cursor.lastrowid)
            for task_key in PROJECT_TASKS:
                conn.execute(
                    "INSERT OR IGNORE INTO project_tasks (product_id, task_key, status) VALUES (?, ?, 'missing')",
                    (product_id, task_key),
                )
        conn.execute(
            """
            INSERT OR REPLACE INTO launch_os_meta (key, value, updated_at)
            VALUES ('active_project_id', ?, CURRENT_TIMESTAMP)
            """,
            (str(product_id),),
        )
        return _project_snapshot(conn, product_id)


def mark_project_task_from_module(text: str, module_id: str, *, notes: str = "") -> dict:
    init_launch_os_database()
    with sqlite3.connect(DB_PATH) as conn:
        project = ensure_project_from_text(text)
        product_id = project.get("id") or (_active_project_row(conn) or {}).get("id")
        task_key = MODULE_TASK_MAP.get(module_id or "")
        if product_id and task_key:
            conn.execute(
                """
                INSERT INTO project_tasks (product_id, task_key, status, notes, updated_at)
                VALUES (?, ?, 'done', ?, CURRENT_TIMESTAMP)
                ON CONFLICT(product_id, task_key)
                DO UPDATE SET status='done', notes=excluded.notes, updated_at=CURRENT_TIMESTAMP
                """,
                (int(product_id), task_key, notes),
            )
            conn.execute("UPDATE products SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (task_key, int(product_id)))
        return _project_snapshot(conn, int(product_id)) if product_id else {}


def project_context_for_text(text: str) -> str:
    init_launch_os_database()
    with sqlite3.connect(DB_PATH) as conn:
        project = ensure_project_from_text(text)
        product_id = project.get("id") or (_active_project_row(conn) or {}).get("id")
        if not product_id:
            return "No active project memory yet."
        snapshot = _project_snapshot(conn, int(product_id))
    return _format_project_context(snapshot)


def active_project_snapshot() -> dict:
    init_launch_os_database()
    with sqlite3.connect(DB_PATH) as conn:
        active = _active_project_row(conn)
        if not active:
            return {}
        return _project_snapshot(conn, int(active["id"]))


def _project_defaults(product_name: str) -> dict:
    folded = product_name.lower()
    if "email" in folded and "campaign" in folded:
        return {
            "niche": "Email marketing / affiliate / digital product",
            "buyer": "Beginner affiliate marketer or new digital product vendor",
            "promise": "Plan, customize, and launch a simple 7-day email campaign without starting from a blank page",
            "format": "PDF/DOCX/CSV product kit",
            "price": "$17 FE",
        }
    if "plr" in folded:
        return {
            "niche": "PLR / AI / WarriorPlus product creation",
            "buyer": "Beginner WarriorPlus vendor or PLR reseller",
            "promise": "Turn raw PLR into a structured product kit with launch assets",
            "format": "PDF/DOCX/CSV/ZIP product kit",
            "price": "$17 FE",
        }
    return {"niche": "", "buyer": "", "promise": "", "format": "Digital product kit", "price": ""}


def _active_project_row(conn: sqlite3.Connection) -> dict:
    row = conn.execute(
        """
        SELECT p.id, p.product_name, p.niche, p.buyer, p.promise, p.format, p.price, p.status
        FROM launch_os_meta m
        JOIN products p ON p.id = CAST(m.value AS INTEGER)
        WHERE m.key = 'active_project_id'
        LIMIT 1
        """
    ).fetchone()
    if not row:
        return {}
    return {
        "id": row[0],
        "product_name": row[1],
        "niche": row[2],
        "buyer": row[3],
        "promise": row[4],
        "format": row[5],
        "price": row[6],
        "status": row[7],
    }


def _project_snapshot(conn: sqlite3.Connection, product_id: int) -> dict:
    product = conn.execute(
        "SELECT id, product_name, niche, buyer, promise, format, price, status FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()
    if not product:
        return {}
    task_rows = conn.execute("SELECT task_key, status, notes FROM project_tasks WHERE product_id = ?", (product_id,)).fetchall()
    task_map = {row[0]: {"status": row[1], "notes": row[2] or ""} for row in task_rows}
    for task_key in PROJECT_TASKS:
        task_map.setdefault(task_key, {"status": "missing", "notes": ""})
    assets = []
    for asset_name, task_key in REQUIRED_ASSETS.items():
        done = task_map.get(task_key, {}).get("status") == "done"
        assets.append({"name": asset_name, "status": "done" if done else "missing", "task": task_key})
    done_count = sum(1 for item in assets if item["status"] == "done")
    missing_assets = [item["name"] for item in assets if item["status"] != "done"]
    return {
        "id": product[0],
        "product_name": product[1],
        "niche": product[2] or "",
        "buyer": product[3] or "",
        "promise": product[4] or "",
        "format": product[5] or "",
        "price": product[6] or "",
        "status": product[7] or "",
        "tasks": task_map,
        "assets": assets,
        "missing_assets": missing_assets,
        "launch_readiness": round(done_count / max(1, len(assets)) * 10, 1),
        "next_actions": _next_actions(task_map),
    }


def _next_actions(task_map: dict) -> list[str]:
    order = (
        ("product_assets", "Generate Product Assets"),
        ("sales_page", "Write Sales Page"),
        ("funnel", "Create Funnel Plan"),
        ("warriorplus_listing", "Build WarriorPlus Listing"),
        ("jv_pack", "Build JV Pack"),
        ("delivery_page", "Build Delivery Page"),
        ("onboarding", "Create Customer Onboarding Emails"),
        ("export_zip", "Export Product ZIP"),
    )
    actions = [label for key, label in order if task_map.get(key, {}).get("status") != "done"]
    return actions[:3] or ["Launch readiness review", "Soft launch planner", "JV outreach tracking"]


def _format_project_context(snapshot: dict) -> str:
    if not snapshot:
        return "No active project memory yet."
    task_lines = []
    for key, label in PROJECT_TASKS.items():
        status = snapshot["tasks"].get(key, {}).get("status", "missing")
        task_lines.append(f"{'[x]' if status == 'done' else '[ ]'} {label}")
    missing = ", ".join(snapshot.get("missing_assets", [])[:8]) or "None"
    next_actions = "; ".join(snapshot.get("next_actions", [])[:3])
    return f"""Active Project Memory:
Project Name: {snapshot['product_name']}
Niche: {snapshot['niche']}
Buyer: {snapshot['buyer']}
Promise: {snapshot['promise']}
Price: {snapshot['price']}
Status: {snapshot['status']}
Launch Readiness: {snapshot['launch_readiness']}/10
Task State:
{chr(10).join(task_lines)}
Missing Assets: {missing}
Recommended Next Actions: {next_actions}
"""
