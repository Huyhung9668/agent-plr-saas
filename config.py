import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

ROOT_DIR = Path(__file__).resolve().parent
if load_dotenv:
    load_dotenv(ROOT_DIR / ".env")

PLR_DIR = ROOT_DIR / "plr_files"
PLR_INBOX_DIR = PLR_DIR / "_INBOX_DROP_HERE"
SAAS_DIR = ROOT_DIR / "saas_files"
SAAS_INBOX_DIR = SAAS_DIR / "_INBOX_DROP_HERE"
OUTPUTS_DIR = ROOT_DIR / "outputs"
EXTRACTED_DIR = ROOT_DIR / "extracted"
REPORTS_DIR = ROOT_DIR / "reports"
EXPORTS_DIR = ROOT_DIR / "exports"
DATABASE_DIR = ROOT_DIR / "database"
DOWNLOAD_QUEUE_PATH = ROOT_DIR / "download_queue.md"
NEEDS_LICENSE_DIR = PLR_DIR / "_Needs-License-Check"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
OPENAI_API_MODE = os.getenv("OPENAI_API_MODE", "chat").lower()
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "").strip()
OPENAI_REASONING_EFFORT = os.getenv("OPENAI_REASONING_EFFORT", "low").strip().lower()
OPENAI_ANSWER_DETAIL = os.getenv("OPENAI_ANSWER_DETAIL", "high").strip().lower()

MAX_TEXT_CHARS = int(os.getenv("PLR_AGENT_MAX_TEXT_CHARS", "12000"))

SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
    ".docx",
    ".zip",
    ".rar",
    ".7z",
}
