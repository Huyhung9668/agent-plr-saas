import os
import shlex
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

ROOT_DIR = Path(__file__).resolve().parent
if load_dotenv:
    load_dotenv(ROOT_DIR / ".env")

def _shell_export_value(name: str) -> str:
    for path in (Path.home() / ".bashrc", Path.home() / ".profile", Path.home() / ".bash_profile"):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if stripped.startswith("export "):
                stripped = stripped.removeprefix("export ").strip()
            if not stripped.startswith(f"{name}="):
                continue
            value = stripped.split("=", 1)[1].strip()
            try:
                return shlex.split(value)[0]
            except ValueError:
                return value.strip("\"'")
    return ""

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
FILE_BACKUP_DIR = Path(os.getenv("PLR_AGENT_FILE_BACKUP_DIR", "G:/file_backup"))

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "cx/gpt-5.5")
OPENAI_API_MODE = os.getenv("OPENAI_API_MODE", "chat").lower()
OPENAI_API_BASE = (
    os.getenv("OPENAI_API_BASE")
    or os.getenv("OPENAI_BASE_URL")
    or "http://103.82.26.216:20128/v1"
).strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or _shell_export_value("OPENAI_API_KEY") or ("local-ai-key" if OPENAI_API_BASE else "")
OPENAI_REASONING_EFFORT = os.getenv("OPENAI_REASONING_EFFORT", "low").strip().lower()
OPENAI_ANSWER_DETAIL = os.getenv("OPENAI_ANSWER_DETAIL", "high").strip().lower()

MAX_TEXT_CHARS = int(os.getenv("PLR_AGENT_MAX_TEXT_CHARS", "12000"))

SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
    ".docx",
    ".xlsx",
    ".pptx",
    ".html",
    ".htm",
    ".csv",
    ".json",
    ".rtf",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",
    ".zip",
    ".rar",
    ".7z",
}
