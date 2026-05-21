from __future__ import annotations

import csv
import hashlib
import json
import re
import sqlite3
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree

from config import DATABASE_DIR, PLR_INBOX_DIR, SAAS_INBOX_DIR

BRAIN_DB_PATH = DATABASE_DIR / "agent_brain.sqlite"
MEDIA_BRAIN_TEXT_DIR = DATABASE_DIR / "media_brain_text"
MEDIA_EXTRACTED_TEXT_DIR = DATABASE_DIR / "media_extracted_text"

READABLE_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
    ".docx",
    ".html",
    ".htm",
    ".csv",
    ".xlsx",
    ".json",
    ".svg",
    ".js",
    ".php",
    ".css",
    ".scss",
    ".less",
    ".xml",
    ".ini",
    ".url",
    ".rtf",
    ".pptx",
    ".zip",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".bmp",
    ".tif",
    ".tiff",
    ".map",
}

SKIP_DIR_NAMES = {
    "__macosx",
    ".git",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
}

NOISE_NAME_PARTS = {
    ".ds_store",
    "bestblackhatforum.com",
    "moneyvipprogram.com",
}

DEFAULT_CHUNK_CHARS = 3500
DEFAULT_CHUNK_OVERLAP = 350
DEFAULT_MAX_DOC_CHARS = 250_000
READ_TEXT_MAX_BYTES = 64 * 1024 * 1024
PDF_OCR_MIN_TEXT_CHARS = 80
PDF_OCR_MAX_PAGES = 80
PDF_OCR_RENDER_SCALE = 2
ZIP_MAX_MEMBERS = 1000
ZIP_MAX_MEMBER_BYTES = 512 * 1024 * 1024
ZIP_MAX_TOTAL_BYTES = 2 * 1024 * 1024 * 1024
ZIP_MAX_TEXT_CHARS = 500_000
ZIP_MAX_DEPTH = 1
ZIP_TEXT_EXTENSIONS = {".txt", ".md", ".csv", ".json", ".html", ".htm", ".xml", ".rtf", ".svg", ".ini", ".url", ".js", ".css", ".scss", ".less", ".php", ".map"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}


@dataclass
class BrainStats:
    db_path: Path
    scanned_files: int
    ingested_documents: int
    skipped_files: int
    chunks: int
    errors: int


def init_brain_database(db_path: Path = BRAIN_DB_PATH) -> Path:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT NOT NULL UNIQUE,
                root TEXT NOT NULL,
                title TEXT NOT NULL,
                extension TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                mtime REAL NOT NULL,
                sha256 TEXT NOT NULL,
                text_chars INTEGER NOT NULL,
                chunk_count INTEGER NOT NULL DEFAULT 0,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
            USING fts5(title, source_path UNINDEXED, text, chunk_id UNINDEXED, document_id UNINDEXED)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ingest_errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT NOT NULL,
                error TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_sha256 ON documents(sha256)")
    return db_path


def ingest_brain(
    roots: Iterable[Path] | None = None,
    *,
    db_path: Path = BRAIN_DB_PATH,
    rebuild: bool = False,
    chunk_chars: int = DEFAULT_CHUNK_CHARS,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    max_doc_chars: int = DEFAULT_MAX_DOC_CHARS,
    max_files: int | None = None,
) -> BrainStats:
    roots = list(roots or _default_brain_roots())
    if rebuild and db_path.exists():
        db_path.unlink()

    init_brain_database(db_path)
    scanned = ingested = skipped = chunks_created = errors = 0

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        for root in roots:
            root = root.expanduser().resolve()
            if not root.exists():
                continue
            for path in _iter_readable_files(root):
                if max_files is not None and scanned >= max_files:
                    break
                scanned += 1
                try:
                    stat = path.stat()
                    existing = conn.execute(
                        "SELECT id, mtime, size_bytes FROM documents WHERE source_path = ?",
                        (str(path),),
                    ).fetchone()
                    if existing and float(existing[1]) == stat.st_mtime and int(existing[2]) == stat.st_size:
                        skipped += 1
                        continue

                    text = read_brain_text(path)
                    text = clean_text(text)
                    if not text:
                        skipped += 1
                        continue
                    if len(text) > max_doc_chars:
                        text = text[:max_doc_chars]

                    digest = _sha256_file(path)
                    title = _title_from_path(path)
                    metadata = {
                        "relative_to_root": _safe_relative(path, root),
                        "truncated": len(text) >= max_doc_chars,
                    }

                    if existing:
                        document_id = int(existing[0])
                        conn.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
                        conn.execute("DELETE FROM chunks_fts WHERE document_id = ?", (str(document_id),))
                        conn.execute(
                            """
                            UPDATE documents
                            SET root = ?, title = ?, extension = ?, size_bytes = ?, mtime = ?,
                                sha256 = ?, text_chars = ?, metadata_json = ?,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                            """,
                            (
                                str(root),
                                title,
                                path.suffix.lower(),
                                stat.st_size,
                                stat.st_mtime,
                                digest,
                                len(text),
                                json.dumps(metadata, ensure_ascii=False),
                                document_id,
                            ),
                        )
                    else:
                        cursor = conn.execute(
                            """
                            INSERT INTO documents (
                                source_path, root, title, extension, size_bytes, mtime,
                                sha256, text_chars, metadata_json
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                str(path),
                                str(root),
                                title,
                                path.suffix.lower(),
                                stat.st_size,
                                stat.st_mtime,
                                digest,
                                len(text),
                                json.dumps(metadata, ensure_ascii=False),
                            ),
                        )
                        document_id = int(cursor.lastrowid)

                    doc_chunks = list(chunk_text(text, chunk_chars=chunk_chars, overlap=chunk_overlap))
                    for index, chunk in enumerate(doc_chunks):
                        cursor = conn.execute(
                            "INSERT INTO chunks (document_id, chunk_index, text) VALUES (?, ?, ?)",
                            (document_id, index, chunk),
                        )
                        chunk_id = int(cursor.lastrowid)
                        conn.execute(
                            """
                            INSERT INTO chunks_fts (title, source_path, text, chunk_id, document_id)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (title, str(path), chunk, str(chunk_id), str(document_id)),
                        )

                    conn.execute(
                        "UPDATE documents SET chunk_count = ? WHERE id = ?",
                        (len(doc_chunks), document_id),
                    )
                    ingested += 1
                    chunks_created += len(doc_chunks)
                    if ingested % 100 == 0:
                        conn.commit()
                        print(f"Ingested {ingested} documents / {chunks_created} chunks...")
                except Exception as error:
                    errors += 1
                    conn.execute(
                        "INSERT INTO ingest_errors (source_path, error) VALUES (?, ?)",
                        (str(path), str(error)),
                    )
            if max_files is not None and scanned >= max_files:
                break
        conn.commit()

    return BrainStats(
        db_path=db_path,
        scanned_files=scanned,
        ingested_documents=ingested,
        skipped_files=skipped,
        chunks=chunks_created,
        errors=errors,
    )


def search_brain(query: str, *, limit: int = 8, db_path: Path = BRAIN_DB_PATH) -> list[dict]:
    init_brain_database(db_path)
    query = query.strip()
    if not query:
        return []
    fts_query = _fts_query(query)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT
                chunks_fts.title,
                chunks_fts.source_path,
                chunks_fts.text,
                chunks_fts.chunk_id,
                chunks_fts.document_id,
                bm25(chunks_fts) AS rank
            FROM chunks_fts
            WHERE chunks_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts_query, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def brain_summary(db_path: Path = BRAIN_DB_PATH) -> dict:
    init_brain_database(db_path)
    with sqlite3.connect(db_path) as conn:
        doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        chunk_count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        text_chars = conn.execute("SELECT COALESCE(SUM(text_chars), 0) FROM documents").fetchone()[0]
        error_count = conn.execute("SELECT COUNT(*) FROM ingest_errors").fetchone()[0]
        by_ext = conn.execute(
            """
            SELECT extension, COUNT(*) AS count
            FROM documents
            GROUP BY extension
            ORDER BY count DESC
            """
        ).fetchall()
    size_bytes = db_path.stat().st_size if db_path.exists() else 0
    return {
        "db_path": str(db_path),
        "db_size_mb": round(size_bytes / 1024 / 1024, 2),
        "documents": doc_count,
        "chunks": chunk_count,
        "text_chars": text_chars,
        "text_mb": round(text_chars / 1024 / 1024, 2),
        "errors": error_count,
        "by_extension": [{"extension": row[0], "count": row[1]} for row in by_ext],
    }


def read_brain_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(path)
    if suffix == ".docx":
        return _read_docx(path)
    if suffix in {".html", ".htm"}:
        return _read_html(path)
    if suffix == ".csv":
        return _read_csv(path)
    if suffix == ".xlsx":
        return _read_xlsx(path)
    if suffix == ".pptx":
        return _read_pptx(path)
    if suffix == ".svg":
        return _read_svg(path)
    if suffix == ".rtf":
        return _read_rtf(path)
    if suffix == ".json":
        return _read_json(path)
    if suffix == ".zip":
        return _read_zip(path)
    if suffix in IMAGE_EXTENSIONS:
        return _read_image_text(path)
    return _read_text(path)


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, *, chunk_chars: int, overlap: int) -> Iterable[str]:
    if chunk_chars <= overlap:
        raise ValueError("chunk_chars must be larger than overlap")
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_chars, text_length)
        chunk = text[start:end].strip()
        if chunk:
            yield chunk
        if end >= text_length:
            break
        start = max(0, end - overlap)


def _iter_readable_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part.lower() in SKIP_DIR_NAMES for part in path.parts):
            continue
        lower_name = path.name.lower()
        if lower_name.startswith("~$"):
            continue
        if any(part in lower_name for part in NOISE_NAME_PARTS):
            continue
        if path.suffix.lower() in READABLE_EXTENSIONS:
            yield path

def _default_brain_roots() -> list[Path]:
    roots = [SAAS_INBOX_DIR, PLR_INBOX_DIR]
    if MEDIA_BRAIN_TEXT_DIR.exists():
        roots.append(MEDIA_BRAIN_TEXT_DIR)
    if MEDIA_EXTRACTED_TEXT_DIR.exists():
        roots.append(MEDIA_EXTRACTED_TEXT_DIR)
    return roots


def _read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            with path.open("rb") as file:
                raw = file.read(READ_TEXT_MAX_BYTES)
            text = raw.decode(encoding, errors="ignore")
            if path.stat().st_size > READ_TEXT_MAX_BYTES:
                text += f"\n\n[Stopped after first {READ_TEXT_MAX_BYTES // 1024 // 1024}MB of this text file.]"
            return text
        except UnicodeError:
            continue
    return ""


def _read_pdf(path: Path) -> str:
    import fitz

    chunks = []
    with fitz.open(path) as doc:
        for page in doc:
            chunks.append(page.get_text("text"))
        text = clean_text("\n".join(chunks))
        if len(text) >= PDF_OCR_MIN_TEXT_CHARS:
            return text
        ocr_text = _read_pdf_with_ocr(doc)
    if ocr_text:
        prefix = "OCR fallback: PDF has little/no embedded text, so text was extracted from rendered pages."
        return f"{prefix}\n\n{ocr_text}"
    return text

def _read_pdf_with_ocr(doc) -> str:
    import fitz

    lines = []
    with tempfile.TemporaryDirectory(prefix="agent_pdf_ocr_") as temp_dir:
        temp_root = Path(temp_dir)
        for page_number, page in enumerate(doc, start=1):
            if page_number > PDF_OCR_MAX_PAGES:
                lines.append(f"[OCR stopped after first {PDF_OCR_MAX_PAGES} pages.]")
                break
            pixmap = page.get_pixmap(matrix=fitz.Matrix(PDF_OCR_RENDER_SCALE, PDF_OCR_RENDER_SCALE), alpha=False)
            image_path = temp_root / f"page-{page_number:04d}.png"
            pixmap.save(str(image_path))
            page_text = _read_image_text(image_path)
            if page_text:
                lines.append(f"--- Page {page_number} OCR ---\n{page_text}")
    return clean_text("\n\n".join(lines))

def _read_image_text(path: Path) -> str:
    try:
        from rapidocr_onnxruntime import RapidOCR

        result, _ = RapidOCR()(str(path))
        lines = []
        if result:
            for item in result:
                if len(item) >= 2 and item[1]:
                    lines.append(str(item[1]).strip())
        text = "\n".join(line for line in lines if line)
        if text:
            return clean_text(text)
    except Exception:
        pass

    try:
        from PIL import Image
        import pytesseract

        return clean_text(pytesseract.image_to_string(Image.open(path)))
    except Exception:
        return ""


def _read_docx(path: Path) -> str:
    from docx import Document

    doc = Document(path)
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


def _read_html(path: Path) -> str:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(_read_text(path), "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return soup.get_text("\n")

def _read_svg(path: Path) -> str:
    text = _read_text(path)
    snippets = []
    for match in re.finditer(r">(.*?)<", text, flags=re.DOTALL):
        value = clean_text(match.group(1))
        if value and len(value) > 1:
            snippets.append(value)
    if snippets:
        return "\n".join(snippets[:1000])
    return "\n".join(
        [
            f"SVG asset: {path.stem}",
            f"File name: {path.name}",
            "No readable SVG text nodes detected. Treat as design/graphic asset.",
        ]
    )

def _read_rtf(path: Path) -> str:
    text = _read_text(path)
    text = re.sub(r"\\'[0-9a-fA-F]{2}", " ", text)
    text = re.sub(r"\\[a-zA-Z]+-?\d* ?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    return clean_text(text)


def _read_csv(path: Path) -> str:
    lines = []
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as file:
        reader = csv.reader(file)
        for row_index, row in enumerate(reader):
            if row_index >= 500:
                break
            lines.append(" | ".join(cell.strip() for cell in row if cell.strip()))
    return "\n".join(line for line in lines if line)


def _read_json(path: Path) -> str:
    text = _read_text(path)
    try:
        return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return text

def _read_zip(path: Path, *, depth: int = 0) -> str:
    lines = [f"ZIP archive: {path.name}", "Files inside:"]
    readable_count = 0
    extracted_bytes = 0
    text_chars = 0
    with zipfile.ZipFile(path) as archive:
        members = [member for member in archive.infolist() if not member.is_dir()]
        if len(members) > ZIP_MAX_MEMBERS:
            lines.append(f"[Only first {ZIP_MAX_MEMBERS} files are inspected from {len(members)} files.]")
        with tempfile.TemporaryDirectory(prefix="agent_zip_extract_") as temp_dir:
            temp_root = Path(temp_dir)
            for member in members[:ZIP_MAX_MEMBERS]:
                if text_chars >= ZIP_MAX_TEXT_CHARS:
                    lines.append(f"[Stopped ZIP text extraction after {ZIP_MAX_TEXT_CHARS} characters.]")
                    break
                if member.is_dir():
                    continue
                member_name = member.filename
                if not _safe_zip_member_name(member_name):
                    lines.append(f"- {member_name}\n  [Skipped: unsafe path inside ZIP.]")
                    continue
                suffix = Path(member_name).suffix.lower()
                lines.append(f"- {member_name}")
                if suffix not in READABLE_EXTENSIONS:
                    continue
                if member.file_size > ZIP_MAX_MEMBER_BYTES:
                    lines.append("  [Skipped: file inside ZIP is too large for inline extraction.]")
                    continue
                if extracted_bytes + member.file_size > ZIP_MAX_TOTAL_BYTES:
                    lines.append("  [Skipped: ZIP extraction byte budget reached.]")
                    continue
                if suffix == ".zip" and depth >= ZIP_MAX_DEPTH:
                    lines.append("  [Skipped: nested ZIP depth limit reached.]")
                    continue
                try:
                    extracted_path = _extract_zip_member(archive, member, temp_root)
                except (OSError, RuntimeError, zipfile.BadZipFile, KeyError):
                    lines.append("  [Skipped: could not extract this file.]")
                    continue
                extracted_bytes += member.file_size
                try:
                    if suffix == ".zip":
                        text = _read_zip(extracted_path, depth=depth + 1)
                    else:
                        text = read_brain_text(extracted_path)
                except Exception as error:
                    lines.append(f"  [Skipped: could not read text: {error}]")
                    continue
                text = clean_text(text)
                if text:
                    readable_count += 1
                    remaining = max(0, ZIP_MAX_TEXT_CHARS - text_chars)
                    snippet = text[: min(12_000, remaining)]
                    text_chars += len(snippet)
                    lines.append(f"\n--- Extracted text: {member_name} ---\n{snippet}\n")
    if readable_count == 0:
        lines.append("No readable text found in this ZIP. Supported inside ZIP: PDF, DOCX, XLSX, PPTX, images with OCR, and text-like files.")
    return "\n".join(lines)

def _safe_zip_member_name(name: str) -> bool:
    path = Path(name)
    return not path.is_absolute() and ".." not in path.parts

def _extract_zip_member(archive: zipfile.ZipFile, member: zipfile.ZipInfo, temp_root: Path) -> Path:
    target = temp_root / Path(member.filename).name
    if not target.suffix:
        target = target.with_suffix(".txt")
    with archive.open(member) as source, target.open("wb") as output:
        shutil.copyfileobj(source, output, length=1024 * 1024)
    return target


def _read_xlsx(path: Path) -> str:
    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    lines = []
    with zipfile.ZipFile(path) as archive:
        shared_strings = _xlsx_shared_strings(archive, ns)
        sheet_names = [
            name
            for name in archive.namelist()
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
        ]
        for sheet_name in sheet_names[:20]:
            try:
                root = ElementTree.fromstring(archive.read(sheet_name))
            except (KeyError, ElementTree.ParseError):
                continue
            lines.append(f"Sheet: {Path(sheet_name).stem}")
            for row_index, row in enumerate(root.findall(".//main:sheetData/main:row", ns)):
                if row_index >= 300:
                    break
                values = []
                for cell in row.findall("main:c", ns):
                    values.append(_xlsx_cell_value(cell, shared_strings, ns))
                line = " | ".join(value for value in values if value)
                if line:
                    lines.append(line)
    return "\n".join(lines)

def _read_pptx(path: Path) -> str:
    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    lines = []
    with zipfile.ZipFile(path) as archive:
        slide_names = [
            name
            for name in archive.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        ]
        for slide_name in sorted(slide_names)[:200]:
            try:
                root = ElementTree.fromstring(archive.read(slide_name))
            except (KeyError, ElementTree.ParseError):
                continue
            parts = [node.text or "" for node in root.findall(".//a:t", ns)]
            slide_text = clean_text(" ".join(parts))
            if slide_text:
                lines.append(f"{Path(slide_name).stem}: {slide_text}")
    return "\n".join(lines)

def _xlsx_shared_strings(archive: zipfile.ZipFile, ns: dict[str, str]) -> list[str]:
    try:
        root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    except (KeyError, ElementTree.ParseError):
        return []
    strings = []
    for item in root.findall("main:si", ns):
        parts = [text.text or "" for text in item.findall(".//main:t", ns)]
        strings.append("".join(parts))
    return strings

def _xlsx_cell_value(cell: ElementTree.Element, shared_strings: list[str], ns: dict[str, str]) -> str:
    value = cell.find("main:v", ns)
    if value is None or value.text is None:
        inline = cell.find(".//main:t", ns)
        return inline.text.strip() if inline is not None and inline.text else ""
    raw = value.text.strip()
    if cell.attrib.get("t") == "s":
        try:
            return shared_strings[int(raw)].strip()
        except (ValueError, IndexError):
            return raw
    return raw

def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _title_from_path(path: Path) -> str:
    return path.stem.replace("_", " ").replace("-", " ").strip()


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _fts_query(query: str) -> str:
    terms = re.findall(r"[\w]+", query, flags=re.UNICODE)
    if not terms:
        return query.replace('"', "")
    return " OR ".join(f'"{term}"' for term in terms[:12])
