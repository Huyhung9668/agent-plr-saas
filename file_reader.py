from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path

from config import EXTRACTED_DIR, MAX_TEXT_CHARS, SUPPORTED_EXTENSIONS


@dataclass
class PLRFile:
    path: Path
    title: str
    file_type: str
    folder: str
    text: str
    license_hint: str


def scan_plr_folder(root: Path) -> list[Path]:
    if not root.exists():
        root.mkdir(parents=True, exist_ok=True)
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]


def read_plr_file(path: Path) -> PLRFile:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        text = _read_pdf(path)
    elif suffix == ".docx":
        text = _read_docx(path)
    elif suffix == ".zip":
        text = _read_zip(path)
    elif suffix in {".rar", ".7z"}:
        text = _read_external_archive(path)
    else:
        text = _read_text(path)

    text = text[:MAX_TEXT_CHARS]
    license_hint = _detect_license(path.name + "\n" + text)

    return PLRFile(
        path=path,
        title=path.stem.replace("_", " ").replace("-", " ").strip(),
        file_type=suffix.lstrip("."),
        folder=path.parent.name,
        text=text,
        license_hint=license_hint,
    )


def _read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return path.read_text(encoding=encoding, errors="ignore")
        except UnicodeError:
            continue
    return ""


def _read_pdf(path: Path) -> str:
    try:
        import fitz
    except ImportError:
        return "PDF reading requires PyMuPDF. Install with: pip install PyMuPDF"

    chunks = []
    with fitz.open(path) as doc:
        for page in doc:
            chunks.append(page.get_text())
            if sum(len(chunk) for chunk in chunks) >= MAX_TEXT_CHARS:
                break
    return "\n".join(chunks)


def _read_docx(path: Path) -> str:
    try:
        from docx import Document
    except ImportError:
        return "DOCX reading requires python-docx. Install with: pip install python-docx"

    doc = Document(path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


def _read_zip(path: Path) -> str:
    target_dir = EXTRACTED_DIR / path.stem
    target_dir.mkdir(parents=True, exist_ok=True)

    lines = [f"ZIP archive: {path.name}", "Files inside:"]
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            lines.append(f"- {member.filename}")
            suffix = Path(member.filename).suffix.lower()
            if suffix in {".txt", ".md"}:
                try:
                    with archive.open(member) as file:
                        content = file.read(MAX_TEXT_CHARS).decode("utf-8", errors="ignore")
                    lines.append(content[:3000])
                except (OSError, UnicodeError, zipfile.BadZipFile):
                    pass
    return "\n".join(lines)


def _read_external_archive(path: Path) -> str:
    return (
        f"Archive file: {path.name}\n"
        "RAR/7Z archive detected. Python standard library cannot inspect this archive directly.\n"
        "Extract it manually, then place the extracted PDF/DOCX/TXT/MD/ZIP files back into plr_files."
    )


def _detect_license(text: str) -> str:
    lower = text.lower()
    license_terms = {
        "PLR": ["private label rights", "plr"],
        "MRR": ["master resale rights", "mrr"],
        "RR": ["resale rights", "rr"],
        "Personal Use": ["personal use only"],
        "Unknown": [],
    }
    for label, terms in license_terms.items():
        if any(term in lower for term in terms):
            return label
    return "Unknown"
