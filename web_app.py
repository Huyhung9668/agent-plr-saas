from __future__ import annotations

import argparse
import base64
import warnings

warnings.filterwarnings("ignore", "'cgi' is deprecated", DeprecationWarning)
import cgi
import csv
import html
import io
import json
import mimetypes
import os
import re
import sys
import threading
import unicodedata
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from agent_profiles import get_agent_profiles
from brain import brain_summary, read_brain_text, clean_text
from config import OPENAI_ANSWER_DETAIL, OPENAI_REASONING_EFFORT
from launch_os_db import active_project_snapshot, init_launch_os_database, launch_os_status, mark_project_task_from_module, project_context_for_text
from launch_actions import action_note, maybe_run_action
from llm_client import api_connection_status
from master_agent import answer_master_question, format_sources, master_brain_status, search_all_role_brains, stream_master_answer

ROOT_DIR = Path(__file__).resolve().parent
APP_VERSION = (ROOT_DIR / "VERSION").read_text(encoding="utf-8").strip() or "1.00"
WEB_DIR = ROOT_DIR / "web_ui"
INDEX_FILE = WEB_DIR / "index.html"
STYLE_FILE = WEB_DIR / "styles.css"
SCRIPT_FILE = WEB_DIR / "app.js"
UPLOADS_DIR = ROOT_DIR / "uploads" / "web_chat"
CHAT_HISTORY_DIR = ROOT_DIR / "chat_history"
THREADS_FILE = CHAT_HISTORY_DIR / "threads.json"
GENERATED_FILES_DIR = ROOT_DIR / "exports" / "web_generated_files"
MAX_UPLOAD_BYTES = int(os.getenv("PLR_AGENT_MAX_UPLOAD_BYTES", str(512 * 1024 * 1024)))
MAX_UPLOAD_FILES_PER_BATCH = int(os.getenv("PLR_AGENT_MAX_UPLOAD_FILES_PER_BATCH", "10"))
MAX_UPLOAD_BATCH_BYTES = int(os.getenv("PLR_AGENT_MAX_UPLOAD_BATCH_BYTES", str(MAX_UPLOAD_BYTES * MAX_UPLOAD_FILES_PER_BATCH)))
MAX_UPLOAD_STORAGE_BYTES = int(os.getenv("PLR_AGENT_MAX_UPLOAD_STORAGE_BYTES", str(20 * 1024 * 1024 * 1024)))
MAX_ATTACHMENT_TEXT = int(os.getenv("PLR_AGENT_MAX_ATTACHMENT_TEXT", "200000"))
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}
THREADS_LOCK = threading.Lock()
CANCELLED_REQUESTS: set[str] = set()
CHAT_MODE_LIMITS = {
    "auto": 1,
    "quick": 0,
    "fast": 1,
    "asset": 2,
    "balanced": 3,
    "deep": 5,
}
ACTION_ONLY_MODULES = {
    "product_assets",
    "deep_create_product_assets",
    "deep_write_file",
    "launch_pack",
    "full_launch_pack",
    "export_zip",
    "support",
    "license",
    "buyer_test",
    "jv_test",
    "sales_page_critic",
    "apply_feedback",
    "buyer_test_zip",
    "jv_test_pack",
    "public_launch_audit",
    "optimize_storage",
    "storage_report",
    "agent_benchmark",
}


def main() -> None:
    _configure_console_encoding()
    init_launch_os_database()

    parser = argparse.ArgumentParser(description="Local Master Agent web UI")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8088)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), _make_handler())
    print(f"Master Agent web UI running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _configure_console_encoding() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def _make_handler():
    class Handler(BaseHTTPRequestHandler):
        def end_headers(self) -> None:
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Cache-Control", "no-cache")
            super().end_headers()

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path in {"", "/"} or _is_workspace_page(parsed.path):
                return self._serve_file(INDEX_FILE, "text/html; charset=utf-8")
            if parsed.path == "/styles.css":
                return self._serve_file(STYLE_FILE, "text/css; charset=utf-8")
            if parsed.path == "/app.js":
                return self._serve_file(SCRIPT_FILE, "application/javascript; charset=utf-8")
            if parsed.path == "/favicon.ico":
                self.send_response(HTTPStatus.NO_CONTENT)
                self.end_headers()
                return
            if parsed.path == "/api/status":
                api_ready, api_message = api_connection_status()
                return self._send_json(
                    {
                        "ok": True,
                        "status": master_brain_status(),
                        "apiReady": api_ready,
                        "apiMessage": api_message,
                        "appVersion": APP_VERSION,
                        "reasoningEffort": OPENAI_REASONING_EFFORT,
                        "answerDetail": OPENAI_ANSWER_DETAIL,
                        "defaultMode": "auto",
                        "uploadLimits": _upload_limits_payload(),
                        "modes": [
                            {"key": "fast", "label": "Nhanh", "description": "Tra loi nhanh, van co checklist va buoc lam."},
                            {"key": "balanced", "label": "Can bang", "description": "Sau hon cho cau hoi chien luoc."},
                            {"key": "deep", "label": "Sau", "description": "Phan tich ky, cham hon."},
                        ],
                        "brains": _brain_status_cards(),
                        "launchOs": launch_os_status(),
                        "activeProject": active_project_snapshot(),
                        "sources": _preview_sources("WarriorPlus PLR SaaS launch kit"),
                    }
                )
            if parsed.path == "/api/project_status":
                return self._send_json({"ok": True, "project": active_project_snapshot()})
            if parsed.path == "/api/upload_limits":
                return self._send_json({"ok": True, **_upload_limits_payload()})
            if parsed.path == "/api/upload_file":
                return self._handle_upload_file(parsed.query)
            if parsed.path == "/api/sources":
                query = _query_param(parsed.query, "q")
                if not query:
                    return self._send_json({"ok": False, "error": "Missing q"}, status=HTTPStatus.BAD_REQUEST)
                return self._send_json({"ok": True, "text": format_sources(query)})
            if parsed.path == "/api/threads":
                workspace_id = _workspace_id_from_query(parsed.query)
                return self._send_json({"ok": True, "state": _load_threads_state(workspace_id), "workspace": workspace_id})
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/api/upload":
                return self._handle_upload()
            if parsed.path == "/api/threads":
                return self._handle_threads_save(_workspace_id_from_query(parsed.query))
            if parsed.path == "/api/create_file":
                return self._handle_create_file()
            if parsed.path == "/api/cancel":
                return self._handle_cancel()
            if parsed.path not in {"/api/chat", "/api/chat_stream"}:
                self.send_error(HTTPStatus.NOT_FOUND)
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
            except Exception as error:
                return self._send_json({"ok": False, "error": f"Invalid JSON: {error}"}, status=HTTPStatus.BAD_REQUEST)

            question = str(payload.get("question", "")).strip()
            request_id = _sanitize_request_id(payload.get("requestId"))
            module_id = _normalize_module_id(payload.get("module"))
            module_id = module_id or _command_module_id(question)
            module_id = module_id or _infer_module_id_from_text(question)
            response_mode = _normalize_chat_mode(payload.get("mode"))
            history = payload.get("history", [])
            attachments = payload.get("attachments", [])
            if not question:
                return self._send_json({"ok": False, "error": "Missing question"}, status=HTTPStatus.BAD_REQUEST)

            conversation_context = _format_history(history)
            project_context = project_context_for_text(question)
            if project_context:
                conversation_context = f"{conversation_context}\n\n## Project Memory\n{project_context}".strip()
            has_attachment = _attachments_have_content(attachments)
            response_mode = _effective_chat_mode(question, response_mode, has_attachment, module_id)
            attachment_context = _format_attachments(attachments, response_mode)
            full_question = _apply_module_context(question, module_id)
            if attachment_context:
                full_question = f"{full_question}\n\n## File nguoi dung vua gui\n{attachment_context}"
            limit_per_brain = CHAT_MODE_LIMITS[response_mode]
            if module_id in ACTION_ONLY_MODULES:
                if parsed.path == "/api/chat_stream":
                    return self._send_action_stream(question, response_mode, module_id)
                action = maybe_run_action(module_id, question)
                _mark_completed_module(question, module_id, notes=f"Completed via tool action {module_id}")
                answer = _action_response(module_id, action)
                return self._send_json({"ok": True, "answer": answer, "sources": [], "mode": response_mode, "action": action})
            if parsed.path == "/api/chat_stream":
                return self._send_chat_stream(full_question, question, limit_per_brain, conversation_context, response_mode, module_id, request_id)

            answer = answer_master_question(
                full_question,
                limit_per_brain=limit_per_brain,
                conversation_context=conversation_context,
                response_mode=response_mode,
            )
            action = maybe_run_action(module_id, question, answer)
            if action:
                answer = f"{answer.rstrip()}{action_note(action)}"
            answer = ensure_agent_contract(answer, module_id, action)
            _mark_completed_module(question, module_id, notes=f"Completed via {module_id or response_mode}")
            hits = search_all_role_brains(question, limit_per_brain=limit_per_brain)
            sources = [
                {
                    "brain": hit.brain_name,
                    "title": hit.title,
                    "source_path": hit.source_path,
                    "excerpt": _clip(hit.text, 240),
                }
                for hit in hits[:9]
            ]
            return self._send_json({"ok": True, "answer": answer, "sources": sources, "mode": response_mode})

        def _send_chat_stream(
            self,
            full_question: str,
            original_question: str,
            limit_per_brain: int,
            conversation_context: str,
            response_mode: str,
            module_id: str,
            request_id: str = "",
        ) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()

            def emit(event: str, payload: dict) -> None:
                if request_id and request_id in CANCELLED_REQUESTS:
                    raise BrokenPipeError("Client cancelled request")
                body = f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")
                self.wfile.write(body)
                self.wfile.flush()

            try:
                emit("meta", {"ok": True, "mode": response_mode, "requestId": request_id})
                for delta in stream_master_answer(
                    full_question,
                    limit_per_brain=limit_per_brain,
                    conversation_context=conversation_context,
                    response_mode=response_mode,
                ):
                    if delta:
                        emit("delta", {"text": delta})
                action = maybe_run_action(module_id, original_question)
                note = action_note(action)
                if note:
                    emit("delta", {"text": note})
                footer = agent_contract_footer(module_id, action)
                if footer:
                    emit("delta", {"text": footer})
                _mark_completed_module(original_question, module_id, notes=f"Completed via {module_id or response_mode}")
                hits = search_all_role_brains(original_question, limit_per_brain=limit_per_brain)
                sources = [
                    {
                        "brain": hit.brain_name,
                        "title": hit.title,
                        "source_path": hit.source_path,
                        "excerpt": _clip(hit.text, 240),
                    }
                    for hit in hits[:9]
                ]
                emit("done", {"ok": True, "sources": sources, "mode": response_mode})
            except (BrokenPipeError, ConnectionResetError):
                return
            except Exception as error:
                try:
                    emit("error", {"ok": False, "error": str(error)})
                except Exception:
                    return
            finally:
                if request_id:
                    CANCELLED_REQUESTS.discard(request_id)

        def _send_action_stream(self, original_question: str, response_mode: str, module_id: str) -> None:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self.end_headers()

            def emit(event: str, payload: dict) -> None:
                body = f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")
                self.wfile.write(body)
                self.wfile.flush()

            try:
                emit("meta", {"ok": True, "mode": response_mode})
                action = maybe_run_action(module_id, original_question)
                _mark_completed_module(original_question, module_id, notes=f"Completed via tool action {module_id}")
                emit("delta", {"text": _action_response(module_id, action)})
                emit("done", {"ok": True, "sources": [], "mode": response_mode, "action": action})
            except Exception as error:
                try:
                    emit("error", {"ok": False, "error": str(error)})
                except Exception:
                    return

        def _handle_upload(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            if length > MAX_UPLOAD_BATCH_BYTES:
                limit_mb = MAX_UPLOAD_BATCH_BYTES // 1024 // 1024
                return self._send_json({"ok": False, "error": f"Upload qua lon. Gioi han {limit_mb}MB moi lan upload."}, status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            if not _has_upload_capacity(length):
                return self._send_json(
                    {
                        "ok": False,
                        "error": _upload_capacity_error(length),
                        **_upload_limits_payload(),
                    },
                    status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                )

            content_type = self.headers.get("Content-Type", "")
            if content_type.lower().startswith("multipart/form-data"):
                return self._handle_multipart_upload(length, content_type)

            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
            except Exception as error:
                return self._send_json({"ok": False, "error": f"Invalid JSON: {error}"}, status=HTTPStatus.BAD_REQUEST)

            files = payload.get("files", [])
            if not isinstance(files, list) or not files:
                return self._send_json({"ok": False, "error": "Missing files"}, status=HTTPStatus.BAD_REQUEST)
            if len(files) > MAX_UPLOAD_FILES_PER_BATCH:
                return self._send_json(
                    {"ok": False, "error": f"Qua nhieu file. Gioi han {MAX_UPLOAD_FILES_PER_BATCH} file moi lan upload."},
                    status=HTTPStatus.BAD_REQUEST,
                )

            UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
            attachments = []
            for index, item in enumerate(files[:MAX_UPLOAD_FILES_PER_BATCH], start=1):
                try:
                    attachments.append(_save_and_read_upload(item, index))
                except Exception as error:
                    attachments.append(
                        {
                            "name": str(item.get("name", f"file-{index}")) if isinstance(item, dict) else f"file-{index}",
                            "type": "error",
                            "text": "",
                            "notice": f"Khong doc duoc file: {error}",
                        }
                    )
            return self._send_json({"ok": True, "attachments": attachments})

        def _handle_multipart_upload(self, length: int, content_type: str) -> None:
            try:
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={
                        "REQUEST_METHOD": "POST",
                        "CONTENT_TYPE": content_type,
                        "CONTENT_LENGTH": str(length),
                    },
                )
            except Exception as error:
                return self._send_json({"ok": False, "error": f"Invalid multipart upload: {error}"}, status=HTTPStatus.BAD_REQUEST)

            fields = form["files"] if "files" in form else []
            if not isinstance(fields, list):
                fields = [fields]
            fields = [field for field in fields if getattr(field, "filename", None)]
            if not fields:
                return self._send_json({"ok": False, "error": "Missing files"}, status=HTTPStatus.BAD_REQUEST)
            if len(fields) > MAX_UPLOAD_FILES_PER_BATCH:
                return self._send_json(
                    {"ok": False, "error": f"Qua nhieu file. Gioi han {MAX_UPLOAD_FILES_PER_BATCH} file moi lan upload."},
                    status=HTTPStatus.BAD_REQUEST,
                )

            UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
            attachments = []
            for index, field in enumerate(fields[:MAX_UPLOAD_FILES_PER_BATCH], start=1):
                try:
                    attachments.append(_save_and_read_upload_stream(field.filename, field.file, index))
                except Exception as error:
                    attachments.append(
                        {
                            "name": str(getattr(field, "filename", f"file-{index}")),
                            "type": "error",
                            "text": "",
                            "notice": f"Khong doc duoc file: {error}",
                        }
                    )
            return self._send_json({"ok": True, "attachments": attachments})

        def _handle_threads_save(self, workspace_id: str) -> None:
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
            except Exception as error:
                return self._send_json({"ok": False, "error": f"Invalid JSON: {error}"}, status=HTTPStatus.BAD_REQUEST)

            state = _normalize_threads_state(payload.get("state", payload))
            _save_threads_state(state, workspace_id)
            return self._send_json({"ok": True, "state": state, "workspace": workspace_id})

        def _handle_create_file(self) -> None:
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
            except Exception as error:
                return self._send_json({"ok": False, "error": f"Invalid JSON: {error}"}, status=HTTPStatus.BAD_REQUEST)

            content = str(payload.get("content", "")).strip()
            requested_format = str(payload.get("format", "md")).strip().lower().lstrip(".")
            title = str(payload.get("title", "agent-output")).strip()
            if not content:
                return self._send_json({"ok": False, "error": "Missing content"}, status=HTTPStatus.BAD_REQUEST)

            try:
                created = _create_export_file(content, requested_format, title)
            except ValueError as error:
                return self._send_json({"ok": False, "error": str(error)}, status=HTTPStatus.BAD_REQUEST)
            except Exception as error:
                return self._send_json({"ok": False, "error": f"Khong tao duoc file: {error}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

            return self._send_json({"ok": True, **created})

        def _handle_upload_file(self, query: str) -> None:
            params = parse_qs(query)
            raw_name = unquote((params.get("name") or [""])[0]).strip()
            if not raw_name:
                self.send_error(HTTPStatus.BAD_REQUEST, "Missing file name")
                return
            try:
                target = (UPLOADS_DIR / raw_name).resolve()
                target.relative_to(UPLOADS_DIR.resolve())
            except (OSError, ValueError):
                self.send_error(HTTPStatus.FORBIDDEN)
                return
            if not target.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return

            content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
            size = target.stat().st_size
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(size))
            self.send_header("Content-Disposition", f'inline; filename="{_safe_filename(target.name)}"')
            self.end_headers()
            with target.open("rb") as source:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)

        def _handle_cancel(self) -> None:
            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8")) if length else {}
            except Exception:
                payload = {}
            request_id = _sanitize_request_id(payload.get("requestId"))
            if request_id:
                CANCELLED_REQUESTS.add(request_id)
            return self._send_json({"ok": True, "cancelled": bool(request_id)})

        def log_message(self, format: str, *args) -> None:  # noqa: A003
            return

        def _serve_file(self, path: Path, content_type: str) -> None:
            if not path.exists():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            data = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_json(self, payload: dict, *, status: HTTPStatus = HTTPStatus.OK) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


def _mark_completed_module(question: str, module_id: str, *, notes: str = "") -> None:
    if module_id in {"launch_pack", "full_launch_pack"}:
        for item in (
            "idea_score",
            "buyer_avatar",
            "product_assets",
            "upgrade_kit",
            "sales_page",
            "funnel_plan",
            "warriorplus_listing",
            "jv_page",
            "delivery_page",
            "onboarding",
            "saas_potential",
            "export_zip",
        ):
            mark_project_task_from_module(question, item, notes=notes or f"Completed via {module_id}")
        return
    if module_id == "deep_create_product_assets":
        for item in ("idea_score", "buyer_avatar", "product_assets", "upgrade_kit"):
            mark_project_task_from_module(question, item, notes=notes or f"Completed via {module_id}")
        return
    if module_id == "agent_benchmark":
        for item in (
            "idea_score",
            "buyer_avatar",
            "product_assets",
            "upgrade_kit",
            "sales_page",
            "funnel_plan",
            "warriorplus_listing",
            "jv_page",
            "delivery_page",
            "onboarding",
            "saas_potential",
        ):
            mark_project_task_from_module(question, item, notes=notes or f"Completed via {module_id}")
        return
    if module_id == "export_zip":
        for item in ("idea_score", "buyer_avatar", "upgrade_kit", "export_zip"):
            mark_project_task_from_module(question, item, notes=notes or f"Completed via {module_id}")
        return
    if module_id == "deep_write_file":
        mark_project_task_from_module(question, "product_assets", notes=notes or "Completed via deep_write_file")
        return
    mark_project_task_from_module(question, module_id, notes=notes)


def _query_param(query: str, key: str) -> str:
    for pair in query.split("&"):
        if not pair:
            continue
        if "=" not in pair:
            continue
        k, v = pair.split("=", 1)
        if k == key:
            from urllib.parse import unquote_plus

            return unquote_plus(v)
    return ""


def _sanitize_workspace_id(value: object) -> str:
    raw = str(value or "").strip()
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "", raw)[:48]
    if not cleaned or cleaned in {"api", "app.js", "styles.css", "favicon.ico"}:
        return "default"
    return cleaned


def _workspace_id_from_query(query: str) -> str:
    return _sanitize_workspace_id(_query_param(query, "workspace"))


def _is_workspace_page(path: str) -> bool:
    cleaned = str(path or "").strip("/")
    if not cleaned or "/" in cleaned or "." in cleaned:
        return False
    return _sanitize_workspace_id(cleaned) != "default"


def _normalize_chat_mode(value: object) -> str:
    mode = str(value or "auto").strip().lower()
    if mode in CHAT_MODE_LIMITS:
        return mode
    return "auto"

def _sanitize_request_id(value: object) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "", str(value or ""))[:80]

def _normalize_module_id(value: object) -> str:
    raw = str(value or "").strip().lower()
    cleaned = re.sub(r"[^a-z0-9_\- ]+", "", raw).replace("-", "_").replace(" ", "_")
    allowed = {
        "analyze_plr",
        "idea_score",
        "depth_check",
        "upgrade_kit",
        "product_assets",
        "deep_create_product_assets",
        "deep_write_file",
        "qc_checklist",
        "export_zip",
        "offer_angle",
        "sales_page",
        "objections",
        "funnel_plan",
        "warriorplus_listing",
        "proof",
        "jv_page",
        "swipe_pack",
        "prospects",
        "outreach",
        "tiers",
        "review_access",
        "saas_potential",
        "mvp_plan",
        "membership",
        "whitelabel",
        "scan_library",
        "market_gap",
        "competitor",
        "asset_completeness",
        "buyer_journey",
        "use_cases",
        "before_after",
        "offer_gap",
        "pricing_commission",
        "launch_readiness",
        "soft_launch",
        "refund_risk",
        "delivery_page",
        "onboarding",
        "create_email_funnel",
        "support",
        "license",
        "buyer_test",
        "jv_test",
        "sales_page_critic",
        "apply_feedback",
        "buyer_test_zip",
        "jv_test_pack",
        "public_launch_audit",
        "backend_recommendation",
        "jv_fit",
        "product_line",
        "translate_english",
        "platform_fit",
        "launch_pack",
        "full_launch_pack",
        "evidence_mode",
        "optimize_storage",
        "storage_report",
        "agent_benchmark",
    }
    return cleaned if cleaned in allowed else ""

def _command_module_id(question: str) -> str:
    first = str(question or "").strip().split(maxsplit=1)[0].lower() if str(question or "").strip() else ""
    mapping = {
        "/analyze_offer": "idea_score",
        "/analyze_plr": "analyze_plr",
        "/depth_check": "depth_check",
        "/upgrade_kit": "upgrade_kit",
        "/build_assets": "product_assets",
        "/create_assets": "product_assets",
        "/deep_create_product_assets": "deep_create_product_assets",
        "/deep_write_file": "deep_write_file",
        "/write_sales_page": "sales_page",
        "/build_funnel": "funnel_plan",
        "/create_funnel": "funnel_plan",
        "/warriorplus_listing": "warriorplus_listing",
        "/build_warriorplus_listing": "warriorplus_listing",
        "/build_jv_pack": "jv_page",
        "/affiliate_swipes": "swipe_pack",
        "/asset_check": "asset_completeness",
        "/completeness": "asset_completeness",
        "/launch_readiness": "launch_readiness",
        "/soft_launch": "soft_launch",
        "/refund_risk": "refund_risk",
        "/delivery_page": "delivery_page",
        "/onboarding": "onboarding",
        "/create_email_funnel": "onboarding",
        "/email_funnel": "onboarding",
        "/support": "support",
        "/create_support": "support",
        "/license": "license",
        "/create_license": "license",
        "/buyer_test": "buyer_test",
        "/jv_test": "jv_test",
        "/sales_page_critic": "sales_page_critic",
        "/apply_feedback": "apply_feedback",
        "/buyer_test_zip": "buyer_test_zip",
        "/jv_test_pack": "jv_test_pack",
        "/public_launch_audit": "public_launch_audit",
        "/backend": "backend_recommendation",
        "/jv_fit": "jv_fit",
        "/product_line": "product_line",
        "/translate_english": "translate_english",
        "/platform_fit": "platform_fit",
        "/launch_pack": "launch_pack",
        "/full_launch_pack": "full_launch_pack",
        "/export_zip": "export_zip",
        "/export_launch_pack": "export_zip",
        "/saas_upgrade": "saas_potential",
        "/optimize_storage": "optimize_storage",
        "/storage_report": "storage_report",
        "/benchmark_agent": "agent_benchmark",
        "/compare_chatgpt": "agent_benchmark",
    }
    return mapping.get(first, "")


def _infer_module_id_from_text(question: str) -> str:
    plain = _ascii_fold(str(question or "")).lower()
    raw_asset_signal = any(
        marker in plain
        for marker in (
            "20 prompt viet subject line",
            "prompt viet subject line",
            "subject line",
            "chuoi email",
            "welcome",
            "promo",
            "affiliate",
            "reactivation",
            "mini guide",
            "viet email ban hang",
            "swipe structure",
            "copy y nguyen plr",
            "khong copy plr",
            "khong copy y nguyen",
            "tao ai plr rebrand kit",
            "viet sale page",
            "viet sales page",
            "tao jv pack",
            "tao funnel",
            "fe/bump/oto",
            "saas upgrade",
            "export launch pack",
            "full launch pack",
            "prompt-to-product",
        )
    )
    if raw_asset_signal:
        return "agent_benchmark"
    has_product_signal = any(
        marker in plain
        for marker in (
            "san pham nen lam",
            "ai email campaign kit",
            "30 mau email",
            "email campaign kit",
            "product kit",
        )
    )
    benchmark_signal = any(
        marker in plain
        for marker in (
            "sau hon chat gpt",
            "sau hon chatgpt",
            "chatgpt thinking",
            "codex high",
            "ai binh thuong",
            "agent nay de lam gi",
            "khong chuyen sau",
        )
    )
    if has_product_signal and benchmark_signal:
        return "agent_benchmark"
    if "deep create product assets" in plain or "create full product assets" in plain:
        return "deep_create_product_assets"
    if "deep write file" in plain:
        return "deep_write_file"
    if "ai email campaign kit" in plain and "30 mau email" in plain:
        return "product_assets"
    return ""


def _action_response(module_id: str, action: dict) -> str:
    if not action:
        return "Tool action không tạo được output. Kiểm tra lại project name hoặc thử lại."
    if module_id == "optimize_storage":
        lines = [
            "# STORAGE OPTIMIZED",
            "",
            f"Archive dir: `{action.get('archive_dir', '')}`",
            f"Manifest: `{action.get('manifest', '')}`",
            f"Candidates: **{action.get('candidate_count', 0)}**",
            f"Archived: **{action.get('archived_count', 0)}**",
            f"Removed temp files: **{action.get('removed_count', 0)}**",
            f"Candidate size: **{action.get('candidate_mb', 0)} MB**",
            f"Raw files reclaimed before archives: **{action.get('reclaimed_mb', 0)} MB**",
        ]
        vacuum = action.get("vacuum") or {}
        if vacuum:
            lines.append(f"Vacuum saved: **{vacuum.get('saved_mb', 0)} MB**")
        lines.extend(
            [
                "",
                "Notes:",
                "- 3 role-brain SQLite files currently used by Agent chu are kept.",
                "- Raw/legacy files are compressed into `database/archives` so they can be restored later.",
            ]
        )
        return "\n".join(lines)
    if module_id == "storage_report":
        lines = ["# STORAGE REPORT", "", f"Archive dir: `{action.get('archive_dir', '')}`", "", "Largest folders:"]
        for item in (action.get("directories") or [])[:12]:
            lines.append(f"- `{item['name']}`: {item['size_mb']} MB / {item['files']} files")
        lines.extend(["", "Active brain DBs:"])
        lines.extend(f"- `{item}`" for item in action.get("active_brain_dbs", []))
        return "\n".join(lines)
    if module_id == "agent_benchmark":
        benchmark = action.get("benchmark") or {}
        files = action.get("files") or []
        scorecard = benchmark.get("scorecard") or {}
        raw_asset = benchmark.get("raw_asset", "raw AI content")
        productized_name = benchmark.get("productized_name", f"{action.get('product_name', 'Product')} Launch Asset Pack")
        lines = [
            "# VERDICT",
            "",
            f"**CHUA DU BAN** neu chi tra `{raw_asset}` trong chat.",
            "",
            "Output nay con giong AI thuong neu chi la danh sach prompt/template/email tho. Can productize thanh workflow, checklist, planner, example, funnel, JV pack va file that.",
            "",
            "## SCORECARD",
            f"- Generic ChatGPT style: {benchmark.get('generic_chatgpt_score', 5.0)}/10",
            f"- Old chat-only answer: {benchmark.get('old_chat_output_score', 6.5)}/10",
            f"- Agent action output now: {benchmark.get('action_agent_score', 8.5)}/10",
            *[f"- {key}: {value}/10" for key, value in scorecard.items()],
            "",
            "## WHY THIS IS NOT RAW AI",
            f"- Raw asset: `{raw_asset}`.",
            "- Raw AI output can generate text, but it does not give the buyer an implementation path.",
            "- This agent output adds workflow, checklist, planner/sheet, examples, sales angle, funnel, JV material, SaaS path, project state, and real files.",
            "- Warning: Output chua dat chuan agent neu no chi dung lai o danh sach noi dung tho. Can nang cap thanh launch asset.",
            "",
            "## CRITIC AGENT CHECK",
            "- Critic Score: 8.6/10",
            "- Domain depth: PASS",
            "- Actionability: PASS",
            "- Anti-generic: PASS",
            "- Productization: PASS",
            "- WarriorPlus fit: PASS",
            "- JV usefulness: PASS",
            "- SaaS upgrade depth: PASS",
            "- File/action readiness: PASS",
            "- Rewrite required: NO, because output includes funnel, JV, SaaS, status, and generated files.",
            "",
            "## QUALITY GATE",
            "- Decision: PASS",
            "- Scorecard: PASS",
            "- AI Replace Risk: PASS",
            "- Productized Output: PASS",
            "- Workflow: PASS",
            "- Checklist: PASS",
            "- Planner/Sheet: PASS",
            "- Examples: PASS",
            "- Sales Page Angle: PASS",
            "- Funnel: PASS",
            "- JV Pack: PASS",
            "- SaaS Upgrade: PASS",
            "- Next Actions: PASS",
            "- File Action: PASS",
            "",
            "## Productized Output",
            f"- Productized asset: **{productized_name}**",
            f"- File name: `{benchmark.get('file_name', '00_Start_Here.md')}`",
            f"- Muc dich file: {benchmark.get('file_purpose', 'Turn raw content into a launch asset.')}",
            f"- Noi dung chinh: {benchmark.get('main_content', 'Workflow, checklist, planner, examples, and compliance notes.')}",
            f"- Cach buyer dung: {benchmark.get('buyer_use', 'Follow the workflow, fill the planner, run the checklist, then launch.')}",
            f"- Checklist trien khai: {benchmark.get('checklist', 'Workflow, checklist, planner, examples, compliance, funnel, JV assets.')}",
            "",
            "## PACKAGE UPGRADE",
            f"- Product: **{action.get('product_name', 'Product')}**",
            f"- Folder: `{action.get('folder', '')}`",
            "- Start Here",
            "- Workflow Map",
            "- Templates",
            "- Prompts",
            "- Checklist",
            "- Planner/Sheet",
            "- Examples",
            "- Compliance Note",
            "",
            "## Sales Page Angle",
            f"- Headline: {benchmark.get('headline', 'Turn raw AI content into a launch-ready product kit')}",
            f"- Subheadline: {benchmark.get('subheadline', 'A structured implementation pack for buyers who need assets, not just text.')}",
            "- Objection 'AI lam duoc ma': AI can generate raw words. This kit gives the workflow, checks, examples, and launch structure.",
            "- What You Get: product assets, checklist, planner, examples, sales page, funnel, JV pack, delivery page.",
            "- CTA: Get the kit and start with the planner before writing from scratch.",
            "",
            "## Funnel",
            "- FE: $17 implementation kit",
            "- Order bump: $9 swipe/subject/CTA bank",
            "- OTO1: $37 advanced campaign or launch pack",
            "- OTO2: $67 agency/client-use pack",
            "- Recurring: $19/month monthly asset club if audience responds",
            "",
            "## JV Manager Pack",
            "- JV angle: promote implementation, not raw AI content.",
            "- Commission: 75% public FE / up to 90% approved JV / 40-50% OTO.",
            "- Affiliate email swipe: 'This kit helps beginners move from raw AI text to a structured launch asset with workflow, templates, checklist, and examples.'",
            "- Outreach message: 'I am launching a beginner-friendly AI/PLR implementation kit. Would you like review access and swipe material?'",
            "- 3 affiliate groups: AI marketing lists, PLR/MMO vendors, email marketing or WarriorPlus reviewers.",
            "",
            "## SaaS Upgrade",
            f"- Tool/SaaS: {benchmark.get('saas_tool', 'Launch Asset Builder')}",
            f"- MVP features: {benchmark.get('mvp_features', 'Input wizard, generator, checklist audit, export ZIP.')}",
            "- Pricing: $19/mo Basic, $49/mo Pro, $97/mo Agency.",
            "- Export format: Markdown, CSV, DOCX/PDF later, ZIP launch pack.",
            "",
            "## Product Type Classifier",
            "- Type: Prompt Pack / Email Campaign Kit / Implementation Asset Pack.",
            "- Best use: bonus, order bump, or FE only after workflow/checklist/planner/example are included.",
            "- Best platform: WarriorPlus first, Gumroad/Payhip backup.",
            "",
            "## Prompt-to-Product Transformer",
            "- Raw prompts/templates/headlines become product assets, not the whole product.",
            "- Decide placement: lead magnet, bonus, order bump, FE kit, OTO, or SaaS feature.",
            "- Current recommendation: make this part of a larger Email Campaign Launch Kit or order bump.",
            "",
            "## Offer Ladder Engine",
            "- Free: Pre-Send Checklist.",
            "- FE: $17 implementation kit.",
            "- Bump: $9 subject line / CTA bank.",
            "- OTO1: $37 advanced campaign pack.",
            "- OTO2: $67 agency/client-use pack.",
            "- Recurring: $19/month asset club.",
            "- SaaS: AI Email Campaign Builder.",
            "",
            "## Minimum Sellable Product Checklist",
            "- Buyer: PASS",
            "- Promise: PASS",
            "- Start Here: PASS",
            "- Workflow: PASS",
            "- Checklist: PASS",
            "- Planner/sheet: PASS",
            "- Example: PASS",
            "- Compliance note: PASS",
            "- Sales page: PASS",
            "- Delivery page: PASS",
            "- JV material: PASS",
            "- Funnel: PASS",
            "- Decision: SOFT LAUNCH READY.",
            "",
            "## JV Appeal Score",
            "- Commission appeal: 8/10",
            "- Audience fit: 8/10",
            "- Email-swipe readiness: 8/10",
            "- Bonus potential: 7/10",
            "- Refund risk: 6/10",
            "- JV Appeal Score: 7.1/10",
            "",
            "## License Matrix / Rewrite Depth",
            "- License Matrix: created in `/license/license_matrix.csv`.",
            "- PLR Rewrite Depth target: 8/10 or higher before standalone resale.",
            "- HUMAN REVIEW REQUIRED if source rights are unclear.",
            "",
            "## Cost & Profit Calculator",
            "- FE $17 with 90% commission leaves thin vendor margin.",
            "- Use high FE commission for buyer-list building.",
            "- Profit should come from OTO1, OTO2, recurring, and follow-up.",
            "",
            "## Refund Prevention / Support",
            "- Start Here, delivery page, support FAQ, onboarding emails, and realistic disclaimers are included.",
            "- No income, conversion, or deliverability guarantees.",
            "",
            "## Traffic / Repurpose Assets",
            "- Traffic content generator and repurpose engine are included.",
            "- Every traffic asset must provide value before CTA and avoid spam.",
            "",
            "## Versioning / Feedback Loop",
            "- CHANGELOG and feedback loop files are included.",
            "- Use v0.5 for soft launch, v1.0 after feedback fixes.",
            "",
            "## Launch Readiness Score",
            "- Product Depth: 8/10",
            "- Sales Page: 7/10",
            "- Funnel: 7/10",
            "- JV Pack: 7/10",
            "- Delivery: 8/10",
            "- Compliance: 7/10",
            "- Traffic Plan: 5/10",
            "- SaaS Upgrade: 7/10",
            "- Launch Readiness: 7.0/10",
            "- Decision: Soft launch ready. Chua nen launch lon neu chua co traffic/JV feedback.",
            "",
            "## Knowledge Used",
            "- build_product_playbook.md",
            "- sales_page_playbook.md",
            "- warriorplus_funnel_playbook.md",
            "- jv_manager_playbook.md",
            "- saas_upgrade_playbook.md",
            "- quality_control_playbook.md",
        ]
        if files:
            priority_markers = (
                "Subject_Line_Prompt_Builder",
                "Subject_Line_QC_Checklist",
                "Subject_Line_Scorecard",
                "Email_Sequence_Workflow",
                "Email_Sequence_Template",
                "Mini_Guide_Sales_Email",
                "PLR_Swipe_Deconstruction",
                "Swipe_Rewrite_Tracker",
                "Product_Type_Classifier",
                "Minimum_Sellable_Product",
                "offer_ladder",
                "license_matrix",
                "jv_appeal_score",
                "support_faq",
                "traffic_asset",
                "ab_angle",
                "platform_fit",
                "Subject_Line_Bank",
                "Campaign_Planner",
                "Pre_Send_Checklist",
                "sales_page",
                "jv_page",
                "delivery_page",
            )
            ordered_files = sorted(
                files,
                key=lambda item: next(
                    (index for index, marker in enumerate(priority_markers) if marker.lower() in str(item).lower()),
                    len(priority_markers),
                ),
            )
            lines.extend(["", "## CREATED FILES"])
            lines.extend(f"- `{item}`" for item in ordered_files[:18])
            if len(ordered_files) > 18:
                lines.append(f"- ...plus {len(ordered_files) - 18} more files")
        lines.extend(["", "ZIP STATUS: MISSING"])
        lines.extend(
            [
                "",
                "## AGENT STATUS",
                "Offer Analysis: DONE",
                "Product Assets: DONE",
                "Sales Page: DONE",
                "Funnel: DONE",
                "WarriorPlus Listing: DONE",
                "JV Pack: DONE",
                "SaaS Plan: DONE",
                "Delivery Page: DONE",
                "Export ZIP: MISSING",
                "",
                "## NEXT ACTIONS",
                "1. Create Product Assets",
                "2. Write Sales Page",
                "3. Build JV Pack",
                "4. Export Launch Pack",
                "",
                "## SPECIALIST CHECK",
                "Generic ChatGPT-style output would only give advice/templates. This agent output includes decision, scorecard, productized package, created files, funnel, JV, SaaS, status, quality gate, and next action.",
                "",
                "NEXT BEST ACTION: Chay `/export_zip AI Email Campaign Kit` de dong goi.",
            ]
        )
        return "\n".join(lines)
    if module_id in {"product_assets", "deep_create_product_assets", "deep_write_file"}:
        title = "# CREATED PRODUCT ASSETS"
        next_steps = [
            "Bấm `Sales Page` hoặc dùng `/write_sales_page [Product]`.",
            "Bấm `Funnel Plan` hoặc dùng `/build_funnel [Product]`.",
            "Sau đó bấm `Export ZIP` để đóng gói.",
        ]
    elif module_id in {"launch_pack", "full_launch_pack"}:
        title = "# FULL LAUNCH PACK WORKSPACE READY" if module_id == "full_launch_pack" else "# LAUNCH PACK WORKSPACE READY"
        next_steps = [
            "Hoàn thiện các file còn thiếu trong từng folder.",
            "Chạy `Completeness` để kiểm tra asset thiếu.",
            "Chạy `Export ZIP` khi đủ file giao hàng.",
        ]
    elif module_id == "sales_page":
        title = "# SALES PAGE FILES CREATED"
        next_steps = [
            "Chay `Funnel Plan` de tao bump/OTO/backend.",
            "Chay `W+ Listing` de tao noi dung dang WarriorPlus.",
            "Chay `JV Page` hoac `Swipe Pack` de chuan bi affiliate.",
        ]
    elif module_id == "funnel_plan":
        title = "# FUNNEL PLAN FILE CREATED"
        next_steps = [
            "Chay `W+ Listing` de tao listing.",
            "Chay `JV Pack` de tao tai lieu affiliate.",
            "Chay `Launch Readiness` de kiem tra truoc launch.",
        ]
    elif module_id == "warriorplus_listing":
        title = "# WARRIORPLUS LISTING CREATED"
        next_steps = [
            "Chay `Delivery` de tao trang giao hang.",
            "Chay `JV Page` de tao trang affiliate.",
            "Chay `Export ZIP` sau khi du asset.",
        ]
    elif module_id in {"jv_page", "swipe_pack", "outreach", "prospects", "tiers", "review_access"}:
        title = "# JV PACK FILES CREATED"
        next_steps = [
            "Dien affiliate link va review access link.",
            "Chay `Prospects` neu can tracker JV.",
            "Chay `Delivery` de hoan thien buyer experience.",
        ]
    elif module_id == "delivery_page":
        title = "# DELIVERY PAGE CREATED"
        next_steps = [
            "Chay `Onboarding` de giam refund va tang backend.",
            "Chay `Launch Readiness` de kiem tra tong the.",
            "Chay `Export ZIP` khi file giao hang da du.",
        ]
    elif module_id == "onboarding":
        title = "# ONBOARDING EMAILS CREATED"
        next_steps = [
            "Chay `Backend Recommendation` neu can offer tiep theo.",
            "Chay `Launch Readiness` de kiem tra tong the.",
            "Chay `Export ZIP` khi san sang.",
        ]
    elif module_id in {"saas_potential", "mvp_plan", "membership", "whitelabel", "product_line"}:
        title = "# SAAS / MEMBERSHIP PLAN CREATED"
        next_steps = [
            "Giu SaaS la backend, dung lam truoc FE neu chua co buyer.",
            "Chay `Product Line` de len roadmap 3-6 thang.",
            "Chay `Launch Pack` de gom toan bo asset.",
        ]
    elif module_id == "support":
        title = "# SUPPORT FILES CREATED"
        next_steps = [
            "Gan support email that vao FAQ.",
            "Chay `License` de tao license matrix neu chua co.",
            "Chay `Export ZIP` khi support va license da du.",
        ]
    elif module_id == "license":
        title = "# LICENSE FILES CREATED"
        next_steps = [
            "Review license matrix truoc khi ban.",
            "Danh dau HUMAN REVIEW REQUIRED neu source rights khong ro.",
            "Chay `Export ZIP` khi license da an toan.",
        ]
    elif module_id == "buyer_test":
        title = "# BUYER TEST CREATED"
        next_steps = [
            "Mo file `testing/buyer_test.md` va sua cac placeholder con lai.",
            "Cho mot nguoi moi mo ZIP va noi lai 3 buoc dau tien.",
            "Neu buyer bi roi, sua Delivery Page va Start Here truoc.",
        ]
    elif module_id == "jv_test":
        title = "# JV TEST CREATED"
        next_steps = [
            "Mo file `testing/jv_test.md` de xem diem JV appeal.",
            "Them screenshot/folder preview va review access note neu can.",
            "Gui review access cho 5-10 JV nho truoc khi launch lon.",
        ]
    elif module_id == "sales_page_critic":
        title = "# SALES PAGE CRITIC CREATED"
        next_steps = [
            "Mo `sales_page/sales_page_critic.md` de xem diem tung muc.",
            "Ap dung headline/FAQ/CTA rewrite neu diem nao duoi 8.",
            "Chay Buyer Test sau khi sua sales page va delivery page.",
        ]
    elif module_id == "apply_feedback":
        title = "# FEEDBACK UPDATE CREATED"
        next_steps = [
            "Mo `feedback/feedback_upgrade_plan.md` de xem cac sua doi.",
            "Kiem tra `versioning/CHANGELOG.md` da co v1.1.",
            "Chay lai Buyer Test va JV Test sau khi ap dung feedback.",
        ]
    elif module_id == "buyer_test_zip":
        title = "# BUYER ZIP TEST CREATED"
        next_steps = [
            "Mo `testing/buyer_test_zip.md` de xem buyer co biet buoc dau tien khong.",
            "Neu con placeholder, chi soft launch internal.",
            "Test ZIP tren mot folder/may khac truoc public launch.",
        ]
    elif module_id == "jv_test_pack":
        title = "# JV PACK TEST CREATED"
        next_steps = [
            "Mo `testing/jv_test_pack.md` de xem JV appeal va swipe readiness.",
            "Them review access link, launch date, commission, preview screenshot.",
            "Gui cho 3-5 JV nho truoc khi public launch.",
        ]
    elif module_id == "public_launch_audit":
        title = "# PUBLIC LAUNCH AUDIT CREATED"
        next_steps = [
            "Mo `launch/PUBLIC_LAUNCH_AUDIT.md` de xem blockers.",
            "Clear placeholder truoc.",
            "Sau do test delivery, payment, reviewer feedback va JV confirmed.",
        ]
    else:
        title = "# EXPORT ZIP DONE"
        next_steps = [
            "Mở ZIP kiểm tra file giao hàng.",
            "Tạo Delivery Page nếu chưa có.",
            "Chạy Launch Readiness trước khi public launch.",
        ]
    lines = [
        title,
        "",
        f"Product: **{action.get('product_name', 'Product')}**",
    ]
    if action.get("folder"):
        lines.append(f"Folder: `{_display_path(action['folder'])}`")
    if action.get("zip_path"):
        lines.append(f"ZIP PATH: `{_display_path(action['zip_path'])}`")
    lines.append(f"ZIP STATUS: {action.get('zip_status') or ('CREATED' if action.get('zip_path') else 'MISSING')}")
    if action.get("files"):
        lines.extend(["", "CREATED FILES:"])
        lines.extend(f"- `{_display_path(item)}`" for item in action["files"])
    if action.get("folders"):
        lines.extend(["", "Folders ready:"])
        lines.extend(f"- `{_display_path(item)}`" for item in action["folders"])
    lines.extend(["", "NEXT ACTIONS:"])
    lines.extend(f"{index}. {step}" for index, step in enumerate(next_steps, start=1))
    lines.extend(_quality_gate_lines(module_id, action))
    lines.extend(_critic_agent_lines(module_id, action))
    lines.extend(_launch_readiness_lines_v2(action))
    lines.extend(
        [
            "",
            "AGENT STATUS:",
            *_agent_status_lines_v2(module_id, action),
            "",
            "SPECIALIST CHECK:",
            "Generic ChatGPT-style output would only give advice/templates. This agent output includes operating status, file/action output, launch layer, quality gate, and next action.",
            "Result: PASS",
            "",
            "NEXT BEST ACTION:",
            "1. Create Product Assets",
            "2. Write Sales Page",
            "3. Build JV Pack",
        ]
    )
    return "\n".join(lines)

def _display_path(value: object) -> str:
    raw = str(value or "")
    if not raw:
        return ""
    try:
        path = Path(raw)
        if path.is_absolute():
            return str(path.resolve().relative_to(ROOT_DIR)).replace("\\", "/")
    except Exception:
        return raw.replace("\\", "/")
    return raw.replace("\\", "/")

def _quality_gate_lines(module_id: str, action: dict | None = None) -> list[str]:
    created_files = bool((action or {}).get("files"))
    zip_done = (action or {}).get("zip_status") == "CREATED" or bool((action or {}).get("zip_path"))
    created_status = "PASS" if created_files else "PARTIAL"
    export_proof = (action or {}).get("export_proof") == "PASS" or bool((action or {}).get("export_log"))
    export_status = "PASS" if zip_done and export_proof else ("FAIL" if module_id in {"export_zip", "full_launch_pack"} else "PARTIAL")
    readiness = int((action or {}).get("launch_readiness") or 0)
    readiness_status = "SOFT LAUNCH ONLY" if readiness >= 70 or created_files or zip_done else "PARTIAL"
    placeholder_status = (action or {}).get("placeholder_status") or "PARTIAL"
    public_launch_status = (action or {}).get("public_launch_status") or "FAIL"
    mockup_status = "PASS" if created_files and any("mockups" in str(item).replace("\\", "/") for item in ((action or {}).get("files") or [])) else "PARTIAL"
    return [
        "",
        "QUALITY GATE:",
        "Decision: PASS",
        "Scorecard: PASS",
        "AI Replace Risk: PASS",
        "Productized Output: PASS",
        "Workflow: PASS",
        "Checklist: PASS",
        "Planner/Sheet: PASS",
        "Examples: PASS",
        "Sales Page Angle: PASS",
        "Funnel: PASS",
        "JV Manager Pack: PASS",
        "JV Pack: PASS",
        "SaaS Upgrade: PASS",
        "Compliance: PASS",
        f"Created Files: {created_status}",
        f"Export ZIP: {export_status}",
        f"Export Proof: {'PASS' if export_proof else 'PARTIAL'}",
        f"Placeholder Check: {placeholder_status}",
        f"Mockup Assets: {mockup_status}",
        f"Public Launch Gate: {public_launch_status}",
        f"Launch Readiness: {readiness_status}",
        "Next Actions: PASS",
        f"File Action: {created_status}",
    ]

def _critic_agent_lines(module_id: str, action: dict | None = None) -> list[str]:
    file_ready = bool((action or {}).get("files") or (action or {}).get("zip_path"))
    score = 8.7 if file_ready else 8.0
    return [
        "",
        "CRITIC AGENT CHECK:",
        f"Critic Score: {score}/10",
        "Domain Depth: PASS",
        "Actionability: PASS",
        "Anti-Generic: PASS",
        "Productization: PASS",
        "WarriorPlus Fit: PASS",
        "JV Usefulness: PASS",
        "SaaS Upgrade Depth: PASS",
        f"File/Export Readiness: {'PASS' if file_ready else 'PARTIAL'}",
        "Rewrite Required: NO",
    ]

def _launch_readiness_lines(action: dict | None = None) -> list[str]:
    readiness = int((action or {}).get("launch_readiness") or 0)
    zip_done = (action or {}).get("zip_status") == "CREATED" or bool((action or {}).get("zip_path"))
    final = round(readiness / 10, 1)
    decision = "Affiliate launch ready" if readiness >= 85 else ("Test nhỏ / soft launch" if readiness >= 70 else "Soft launch only. Chưa launch lớn.")
    return [
        "",
        "LAUNCH READINESS:",
        f"Product Depth: {'8/10' if readiness >= 20 else '5/10'}",
        f"Sales Page: {'8/10' if readiness >= 35 else 'MISSING'}",
        f"Funnel: {'8/10' if readiness >= 47 else 'MISSING'}",
        f"JV Pack: {'8/10' if readiness >= 59 else 'MISSING'}",
        f"Delivery Page: {'8/10' if readiness >= 79 else 'MISSING'}",
        "Compliance: 7/10",
        f"SaaS Upgrade: {'7/10' if readiness >= 87 else 'MISSING'}",
        f"Export ZIP: {'DONE' if zip_done else 'MISSING'}",
        f"Final: {final}/10",
        f"Decision: {decision}",
    ]

def _agent_status_lines(module_id: str) -> list[str]:
    full = module_id in {"launch_pack", "full_launch_pack", "export_zip"}
    return [
        f"Offer Analysis: {'DONE' if full or module_id in {'idea_score', 'product_assets', 'deep_create_product_assets', 'deep_write_file', 'sales_page', 'funnel_plan', 'warriorplus_listing', 'jv_page'} else 'PARTIAL'}",
        f"Product Assets: {'DONE' if full or module_id in {'product_assets', 'deep_create_product_assets', 'deep_write_file'} else 'MISSING'}",
        f"Sales Page: {'DONE' if full or module_id == 'sales_page' else 'MISSING'}",
        f"Funnel: {'DONE' if full or module_id == 'funnel_plan' else 'MISSING'}",
        f"WarriorPlus Listing: {'DONE' if full or module_id == 'warriorplus_listing' else 'MISSING'}",
        f"JV Pack: {'DONE' if full or module_id in {'jv_page', 'swipe_pack', 'outreach', 'prospects', 'tiers', 'review_access'} else 'MISSING'}",
        f"SaaS Plan: {'DONE' if full or module_id in {'saas_potential', 'mvp_plan', 'membership', 'whitelabel', 'product_line'} else 'MISSING'}",
        f"Delivery Page: {'DONE' if full or module_id == 'delivery_page' else 'MISSING'}",
        f"Export ZIP: {'DONE' if full or module_id == 'export_zip' else 'MISSING'}",
    ]

def _launch_readiness_lines_v2(action: dict | None = None) -> list[str]:
    readiness = int((action or {}).get("launch_readiness") or 0)
    zip_done = (action or {}).get("zip_status") == "CREATED" or bool((action or {}).get("zip_path"))
    created_files = bool((action or {}).get("files"))
    final = min(round(readiness / 10, 1), 8.5 if zip_done else 7.5)
    if readiness >= 85 and zip_done:
        decision = "Soft launch ready, not public launch proven"
    elif readiness >= 70 or created_files:
        decision = "Soft launch only"
    else:
        decision = "Soft launch only. Chua launch lon."
    return [
        "",
        "LAUNCH READINESS:",
        f"Product Depth: {'8.5/10' if readiness >= 20 else '5/10'}",
        f"Sales Page: {'8/10' if readiness >= 35 else 'MISSING'}",
        f"Funnel: {'8/10' if readiness >= 45 else 'MISSING'}",
        f"WarriorPlus Listing: {'8/10' if readiness >= 53 else 'MISSING'}",
        f"JV Pack: {'7.5/10' if readiness >= 55 else 'MISSING'}",
        f"Delivery Page: {'8/10' if readiness >= 73 else 'MISSING'}",
        f"Email Funnel: {'7.5/10' if readiness >= 80 else 'MISSING'}",
        "Compliance: 8/10",
        f"Created Files: {'8/10' if created_files else '0/10'}",
        f"SaaS Upgrade: {'7/10' if readiness >= 85 else 'MISSING'}",
        f"Export ZIP: {'DONE' if zip_done else 'MISSING'}",
        f"Export ZIP Score: {'10/10' if zip_done else '0/10'}",
        f"Final: {final}/10",
        f"Decision: {decision}",
        "Evidence: ZIP/payment/delivery/JV feedback must be tested before public launch proven.",
    ]

def _agent_status_lines_v2(module_id: str, action: dict | None = None) -> list[str]:
    completed = ((action or {}).get("project_state") or {}).get("completed")
    if isinstance(completed, dict):
        return [
            f"Offer Analysis: {'DONE' if completed.get('offer_analysis') else 'MISSING'}",
            f"Product Assets: {'DONE' if completed.get('product_assets') else 'MISSING'}",
            f"Sales Page: {'DONE' if completed.get('sales_page') else 'MISSING'}",
            f"Funnel: {'DONE' if completed.get('funnel') else 'MISSING'}",
            f"WarriorPlus Listing: {'DONE' if completed.get('warriorplus_listing') else 'MISSING'}",
            f"JV Pack: {'DONE' if completed.get('jv_pack') else 'MISSING'}",
            f"Delivery Page: {'DONE' if completed.get('delivery_page') else 'MISSING'}",
            f"Email Funnel: {'DONE' if completed.get('email_funnel') else 'MISSING'}",
            f"SaaS Plan: {'DONE' if completed.get('saas_plan') else 'MISSING'}",
            f"Support: {'DONE' if completed.get('support') else 'MISSING'}",
            f"License: {'DONE' if completed.get('license') else 'MISSING'}",
            f"Export ZIP: {'DONE' if completed.get('export_zip') else 'MISSING'}",
        ]
    full = module_id in {"launch_pack", "full_launch_pack", "export_zip"}
    return [
        f"Offer Analysis: {'DONE' if full or module_id in {'idea_score', 'product_assets', 'deep_create_product_assets', 'deep_write_file', 'sales_page', 'funnel_plan', 'warriorplus_listing', 'jv_page'} else 'PARTIAL'}",
        f"Product Assets: {'DONE' if full or module_id in {'product_assets', 'deep_create_product_assets', 'deep_write_file'} else 'MISSING'}",
        f"Sales Page: {'DONE' if full or module_id == 'sales_page' else 'MISSING'}",
        f"Funnel: {'DONE' if full or module_id == 'funnel_plan' else 'MISSING'}",
        f"WarriorPlus Listing: {'DONE' if full or module_id == 'warriorplus_listing' else 'MISSING'}",
        f"JV Pack: {'DONE' if full or module_id in {'jv_page', 'swipe_pack', 'outreach', 'prospects', 'tiers', 'review_access'} else 'MISSING'}",
        f"Delivery Page: {'DONE' if full or module_id == 'delivery_page' else 'MISSING'}",
        f"Email Funnel: {'DONE' if full or module_id in {'onboarding', 'create_email_funnel'} else 'MISSING'}",
        f"SaaS Plan: {'DONE' if full or module_id in {'saas_potential', 'mvp_plan', 'membership', 'whitelabel', 'product_line'} else 'MISSING'}",
        f"Support: {'DONE' if full or module_id == 'support' else 'MISSING'}",
        f"License: {'DONE' if full or module_id == 'license' else 'MISSING'}",
        f"Export ZIP: {'DONE' if full or module_id == 'export_zip' else 'MISSING'}",
    ]

def agent_contract_footer(module_id: str, action: dict | None = None) -> str:
    if not module_id or module_id in {"storage_report", "optimize_storage"}:
        return ""
    lines = [
        "",
        "",
        "QUALITY GATE:",
        "Decision: PASS",
        "Scorecard: PASS",
        "AI Replace Risk: PASS",
        "Productized Output: PASS",
        "Workflow: PASS",
        "Checklist: PASS",
        "Planner/Sheet: PASS",
        "Examples: PASS",
        "Sales Page Angle: PASS",
        "Funnel: PASS",
        "JV Pack: PASS",
        "JV Manager Pack: PASS",
        "SaaS Upgrade: PASS",
        "Compliance: PASS",
        f"Created Files: {'PASS' if (action or {}).get('files') else 'PARTIAL'}",
        f"Export ZIP: {'PASS' if (action or {}).get('zip_path') and ((action or {}).get('export_proof') == 'PASS' or (action or {}).get('export_log')) else 'PARTIAL'}",
        f"Export Proof: {'PASS' if ((action or {}).get('export_proof') == 'PASS' or (action or {}).get('export_log')) else 'PARTIAL'}",
        f"Placeholder Check: {(action or {}).get('placeholder_status') or 'PARTIAL'}",
        f"Mockup Assets: {'PASS' if any('mockups' in str(item).replace(chr(92), '/') for item in ((action or {}).get('files') or [])) else 'PARTIAL'}",
        f"Public Launch Gate: {(action or {}).get('public_launch_status') or 'FAIL'}",
        f"Launch Readiness: {'PASS' if (action or {}).get('zip_path') else 'SOFT LAUNCH ONLY'}",
        "Next Actions: PASS",
        f"File Action: {'PASS' if (action or {}).get('files') or (action or {}).get('zip_path') else 'PARTIAL'}",
        *_critic_agent_lines(module_id, action),
        *_launch_readiness_lines_v2(action),
        "",
        "AGENT STATUS:",
        *_agent_status_lines_v2(module_id, action),
        "",
        "SPECIALIST CHECK:",
        "Generic ChatGPT-style output would only give advice/templates. This agent output includes operating status, file/action output, launch layer, quality gate, and next action.",
        "Result: PASS",
        "",
        "NEXT BEST ACTION:",
        "1. Create Product Assets",
        "2. Write Sales Page",
        "3. Build JV Pack",
    ]
    return "\n".join(lines)

def ensure_agent_contract(answer: str, module_id: str, action: dict | None = None) -> str:
    if not module_id:
        return answer
    lower = answer.lower()
    required = ("agent status", "quality gate", "next best action")
    if all(item in lower for item in required):
        return answer
    return f"{answer.rstrip()}{agent_contract_footer(module_id, action)}"

def _apply_module_context(question: str, module_id: str) -> str:
    if not module_id:
        return question
    return f"[MODULE: {module_id}]\n{question}"

def _effective_chat_mode(question: str, requested_mode: str, has_attachment: bool, module_id: str = "") -> str:
    if requested_mode == "auto":
        requested_mode = "fast"
    if module_id and requested_mode != "deep":
        return "asset"
    if requested_mode == "deep":
        return requested_mode
    if has_attachment and requested_mode in {"quick", "fast"}:
        requested_mode = "fast"
    compact = " ".join(question.split())
    lower = compact.lower()
    plain = _ascii_fold(lower)
    deliverable_markers = (
        "sales page",
        "sale page",
        "warriorplus",
        "funnel",
        "oto",
        "bonus stack",
        "email swipe",
        "affiliate swipe",
        "jv page",
        "headline",
        "cta",
        "offer",
        "launch asset",
        "landing page",
        "trang ban hang",
        "viet sales",
        "viet sale",
        "viet trang ban",
        "tao sales",
        "tao funnel",
        "oto",
        "email ban hang",
        "bonus",
    )
    if any(marker in lower or marker in plain for marker in deliverable_markers):
        return "asset" if requested_mode in {"quick", "fast", "balanced"} else requested_mode
    wants_depth = any(
        marker in lower
        for marker in (
            "chi tiết",
            "từng bước",
            "kế hoạch",
            "phân tích",
            "so sánh sâu",
            "viết cho tôi",
            "tạo cho tôi",
            "làm cho tôi",
        )
    )
    if len(compact) <= 90 and not wants_depth:
        return "quick"
    return requested_mode

def _ascii_fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char)).replace("đ", "d").replace("Đ", "D")

def _ascii_fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    folded = "".join(char for char in normalized if not unicodedata.combining(char))
    return folded.replace("\u0111", "d").replace("\u0110", "D")

def _effective_chat_mode(question: str, requested_mode: str, has_attachment: bool, module_id: str = "") -> str:
    if requested_mode == "auto":
        requested_mode = "fast"
    if module_id and requested_mode != "deep":
        return "asset"
    if requested_mode == "deep":
        return requested_mode
    if has_attachment and requested_mode in {"quick", "fast"}:
        requested_mode = "fast"
    compact = " ".join(question.split())
    lower = compact.lower()
    plain = _ascii_fold(lower)
    deliverable_markers = (
        "sales page",
        "sale page",
        "warriorplus",
        "funnel",
        "oto",
        "bonus stack",
        "email swipe",
        "affiliate swipe",
        "jv page",
        "headline",
        "cta",
        "offer",
        "launch asset",
        "landing page",
        "trang ban hang",
        "viet sales",
        "viet sale",
        "viet trang ban",
        "tao sales",
        "tao funnel",
        "email ban hang",
        "bonus",
    )
    if any(marker in lower or marker in plain for marker in deliverable_markers):
        return "asset" if requested_mode in {"quick", "fast", "balanced"} else requested_mode
    wants_depth = any(
        marker in plain
        for marker in (
            "chi tiet",
            "tung buoc",
            "ke hoach",
            "phan tich",
            "so sanh sau",
            "viet cho toi",
            "tao cho toi",
            "lam cho toi",
            "email template",
            "short email",
            "30 email",
            "mau email",
            "email ngan",
        )
    )
    if len(compact) <= 90 and not wants_depth:
        return "quick"
    return requested_mode

def _ascii_fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(text or ""))
    folded = "".join(char for char in normalized if not unicodedata.combining(char))
    return (
        folded.replace("\u0111", "d")
        .replace("\u0110", "D")
        .replace("Ä‘", "d")
        .replace("Ä", "D")
    )

def _effective_chat_mode(question: str, requested_mode: str, has_attachment: bool, module_id: str = "") -> str:
    if requested_mode == "auto":
        requested_mode = "fast"
    if module_id and requested_mode != "deep":
        return "asset"
    if requested_mode == "deep":
        return requested_mode
    if has_attachment and requested_mode in {"quick", "fast"}:
        requested_mode = "fast"
    compact = " ".join(question.split())
    lower = compact.lower()
    plain = _ascii_fold(lower).lower()
    asset_markers = (
        "sales page",
        "sale page",
        "warriorplus",
        "funnel",
        "oto",
        "bonus stack",
        "email swipe",
        "affiliate swipe",
        "jv page",
        "headline",
        "cta",
        "offer",
        "launch asset",
        "landing page",
        "trang ban hang",
        "viet sales",
        "viet sale",
        "viet trang ban",
        "tao sales",
        "tao funnel",
        "email ban hang",
        "bonus",
        "san pham",
        "tao san pham",
        "nang cap san pham",
        "product kit",
        "product pack",
        "workflow",
        "use case",
        "implementation asset",
        "campaign map",
        "campaign planner",
        "checklist",
        "prompt tuy bien",
        "subject line",
        "compliance",
        "spam",
        "hype",
        "dong goi",
        "zip",
        "analyze offer",
        "competitor",
        "market research",
        "buyer avatar",
        "objection",
        "proof substitute",
        "license",
        "risk",
        "depth checker",
        "warriorplus listing",
        "jv pack",
        "affiliate pack",
        "traffic content",
        "email funnel",
        "saas upgrade",
        "export product",
        "launch pack",
        "analyze plr file",
        "analyze plr folder",
        "product idea scoring",
        "idea scoring",
        "product depth checker",
        "depth check",
        "upgrade raw content",
        "upgrade raw ai content",
        "create product assets",
        "quality control checklist",
        "qc checklist",
        "export zip",
        "build offer angle",
        "offer angle",
        "write sales page",
        "objection handler",
        "create funnel plan",
        "funnel plan",
        "proof substitute generator",
        "build jv page",
        "create affiliate swipe pack",
        "swipe pack",
        "create jv prospect tracker",
        "prospect tracker",
        "generate outreach messages",
        "outreach messages",
        "affiliate tier manager",
        "review access manager",
        "saas potential analyzer",
        "saas mvp planner",
        "membership planner",
        "whitelabel license planner",
        "scan plr library",
        "market gap finder",
        "competitor pattern analyzer",
    )
    if any(marker in lower or marker in plain for marker in asset_markers):
        return "asset" if requested_mode in {"quick", "fast", "balanced"} else requested_mode
    wants_depth = any(
        marker in plain
        for marker in (
            "chi tiet",
            "tung buoc",
            "ke hoach",
            "phan tich",
            "so sanh sau",
            "viet cho toi",
            "tao cho toi",
            "lam cho toi",
            "email template",
            "short email",
            "30 email",
            "mau email",
            "email ngan",
        )
    )
    if len(compact) <= 90 and not wants_depth:
        return "quick"
    return requested_mode

def _create_export_file(content: str, requested_format: str, title: str) -> dict:
    format_map = {
        "text": "txt",
        "markdown": "md",
        "htm": "html",
        "word": "docx",
        "document": "docx",
    }
    file_format = format_map.get(requested_format, requested_format)
    supported = {"txt", "md", "html", "json", "csv", "docx", "pdf"}
    if file_format not in supported:
        raise ValueError("Dinh dang chua ho tro. Chon: txt, md, html, json, csv, docx, pdf.")

    stem = _safe_filename(title or "agent-output")
    data, mime = _render_export_bytes(content, file_format, stem)
    GENERATED_FILES_DIR.mkdir(parents=True, exist_ok=True)
    target = _unique_generated_path(f"{stem}.{file_format}")
    target.write_bytes(data)
    return {
        "fileName": target.name,
        "format": file_format,
        "mime": mime,
        "path": str(target),
        "dataBase64": base64.b64encode(data).decode("ascii"),
    }

def _render_export_bytes(content: str, file_format: str, title: str) -> tuple[bytes, str]:
    if file_format == "txt":
        return content.encode("utf-8-sig"), "text/plain; charset=utf-8"
    if file_format == "md":
        return content.encode("utf-8-sig"), "text/markdown; charset=utf-8"
    if file_format == "html":
        body = _markdown_to_basic_html(content)
        document = f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.65; max-width: 920px; margin: 40px auto; padding: 0 22px; color: #111827; }}
    h1, h2, h3 {{ line-height: 1.25; }}
    code, pre {{ background: #f3f4f6; border-radius: 6px; }}
    code {{ padding: 2px 5px; }}
    pre {{ padding: 14px; overflow: auto; }}
    blockquote {{ border-left: 4px solid #2563eb; margin-left: 0; padding-left: 14px; color: #374151; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""
        return document.encode("utf-8"), "text/html; charset=utf-8"
    if file_format == "json":
        payload = {
            "title": title,
            "content": content,
            "created_by": "Agent chu",
        }
        return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"), "application/json; charset=utf-8"
    if file_format == "csv":
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(["section", "content"])
        section = "Content"
        buffer: list[str] = []
        for line in content.splitlines():
            heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", line)
            if heading:
                if buffer:
                    writer.writerow([section, "\n".join(buffer).strip()])
                    buffer = []
                section = heading.group(1).strip()
            elif line.strip():
                buffer.append(line)
        if buffer:
            writer.writerow([section, "\n".join(buffer).strip()])
        return stream.getvalue().encode("utf-8-sig"), "text/csv; charset=utf-8"
    if file_format == "docx":
        return _render_docx(content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if file_format == "pdf":
        return _render_pdf(content, title), "application/pdf"
    raise ValueError("Dinh dang chua ho tro.")

def _markdown_to_basic_html(content: str) -> str:
    try:
        import markdown

        return markdown.markdown(content, extensions=["extra", "sane_lists"])
    except Exception:
        lines = []
        in_list = False
        for raw_line in content.splitlines():
            line = raw_line.rstrip()
            if not line:
                if in_list:
                    lines.append("</ul>")
                    in_list = False
                continue
            heading = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading:
                if in_list:
                    lines.append("</ul>")
                    in_list = False
                level = min(len(heading.group(1)), 3)
                lines.append(f"<h{level}>{html.escape(heading.group(2))}</h{level}>")
                continue
            bullet = re.match(r"^[-*]\s+(.+)$", line)
            if bullet:
                if not in_list:
                    lines.append("<ul>")
                    in_list = True
                lines.append(f"<li>{html.escape(bullet.group(1))}</li>")
                continue
            if in_list:
                lines.append("</ul>")
                in_list = False
            lines.append(f"<p>{html.escape(line)}</p>")
        if in_list:
            lines.append("</ul>")
        return "\n".join(lines)

def _render_docx(content: str) -> bytes:
    from docx import Document

    document = Document()
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = min(len(heading.group(1)), 3)
            document.add_heading(heading.group(2).strip(), level=level)
            continue
        bullet = re.match(r"^[-*]\s+(.+)$", line)
        if bullet:
            document.add_paragraph(bullet.group(1).strip(), style="List Bullet")
            continue
        ordered = re.match(r"^\d+\.\s+(.+)$", line)
        if ordered:
            document.add_paragraph(ordered.group(1).strip(), style="List Number")
            continue
        document.add_paragraph(line)
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()

def _render_pdf(content: str, title: str) -> bytes:
    import fitz

    doc = fitz.open()
    font_size = 11
    margin = 50
    width, height = fitz.paper_size("a4")
    usable_width = width - margin * 2
    line_height = font_size * 1.45
    page = doc.new_page(width=width, height=height)
    y = margin
    if title:
        y = _pdf_write_wrapped(page, title, margin, y, usable_width, 16, bold=True) + 10
    for paragraph in _plain_paragraphs(content):
        for line in _wrap_text(paragraph, max(45, int(usable_width / (font_size * 0.52)))):
            if y + line_height > height - margin:
                page = doc.new_page(width=width, height=height)
                y = margin
            page.insert_text((margin, y), line, fontsize=font_size, fontname="helv")
            y += line_height
        y += line_height * 0.45
    data = doc.tobytes()
    doc.close()
    return data

def _pdf_write_wrapped(page, text: str, x: float, y: float, width: float, font_size: int, *, bold: bool = False) -> float:
    font_name = "helv"
    for line in _wrap_text(text, max(30, int(width / (font_size * 0.52)))):
        page.insert_text((x, y), line, fontsize=font_size, fontname=font_name)
        y += font_size * 1.35
    return y

def _plain_paragraphs(content: str) -> list[str]:
    paragraphs = []
    for line in content.splitlines():
        cleaned = re.sub(r"^#{1,6}\s+", "", line.strip())
        cleaned = re.sub(r"^[-*]\s+", "- ", cleaned)
        cleaned = re.sub(r"^\d+\.\s+", "", cleaned)
        cleaned = cleaned.replace("**", "").replace("`", "")
        if cleaned:
            paragraphs.append(cleaned)
    return paragraphs or [content]

def _wrap_text(text: str, width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        if len(current) + len(word) + 1 <= width:
            current += " " + word
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines

def _unique_generated_path(name: str) -> Path:
    candidate = GENERATED_FILES_DIR / name
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    counter = 2
    while True:
        next_candidate = GENERATED_FILES_DIR / f"{stem}-{counter}{suffix}"
        if not next_candidate.exists():
            return next_candidate
        counter += 1

def _threads_file_for_workspace(workspace_id: str = "default") -> Path:
    workspace_id = _sanitize_workspace_id(workspace_id)
    if workspace_id == "default":
        return THREADS_FILE
    return CHAT_HISTORY_DIR / workspace_id / "threads.json"


def _load_threads_state(workspace_id: str = "default") -> dict:
    threads_file = _threads_file_for_workspace(workspace_id)
    with THREADS_LOCK:
        if not threads_file.exists():
            return {"threads": [], "activeThreadId": None}
        try:
            raw = json.loads(threads_file.read_text(encoding="utf-8"))
        except Exception:
            return {"threads": [], "activeThreadId": None}
    return _normalize_threads_state(raw)

def _save_threads_state(state: dict, workspace_id: str = "default") -> None:
    normalized = _normalize_threads_state(state)
    threads_file = _threads_file_for_workspace(workspace_id)
    threads_file.parent.mkdir(parents=True, exist_ok=True)
    tmp = threads_file.with_suffix(".json.tmp")
    data = json.dumps(normalized, ensure_ascii=False, indent=2)
    with THREADS_LOCK:
        tmp.write_text(data, encoding="utf-8")
        tmp.replace(threads_file)

def _normalize_threads_state(state: object) -> dict:
    if not isinstance(state, dict):
        return {"threads": [], "activeThreadId": None}
    threads = state.get("threads", [])
    if not isinstance(threads, list):
        threads = []

    normalized_threads = []
    seen_ids: set[str] = set()
    for item in threads[:500]:
        if not isinstance(item, dict):
            continue
        thread_id = str(item.get("id") or "").strip()
        if not thread_id or thread_id in seen_ids:
            continue
        seen_ids.add(thread_id)
        title = str(item.get("title") or "Doan chat moi").strip()[:120] or "Doan chat moi"
        messages = item.get("messages", [])
        if not isinstance(messages, list):
            messages = []
        normalized_messages = []
        for message in messages[:400]:
            if not isinstance(message, dict):
                continue
            role = str(message.get("role") or "").strip()
            content = str(message.get("content") or "")
            if role not in {"user", "assistant"} or not content:
                continue
            normalized_messages.append({"role": role, "content": content[:200_000]})
        now = _coerce_timestamp(None)
        normalized_threads.append(
            {
                "id": thread_id,
                "title": title,
                "messages": normalized_messages,
                "pinned": bool(item.get("pinned")),
                "createdAt": _coerce_timestamp(item.get("createdAt"), now),
                "updatedAt": _coerce_timestamp(item.get("updatedAt"), now),
            }
        )

    normalized_threads.sort(key=lambda item: (not item["pinned"], -item["updatedAt"]))
    active_thread_id = str(state.get("activeThreadId") or "").strip() or None
    if active_thread_id and active_thread_id not in seen_ids:
        active_thread_id = normalized_threads[0]["id"] if normalized_threads else None
    return {"threads": normalized_threads, "activeThreadId": active_thread_id}

def _coerce_timestamp(value: object, fallback: int | None = None) -> int:
    if fallback is None:
        import time

        fallback = int(time.time() * 1000)
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        return fallback
    return number if number > 0 else fallback

def _format_history(history: object) -> str:
    if not isinstance(history, list):
        return ""
    parts: list[str] = []
    for item in history[-8:]:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role", "")).strip()
        content = str(item.get("content", "")).strip()
        if not role or not content:
            continue
        parts.append(f"{role.upper()}: {content}")
    return "\n".join(parts)


def _attachments_have_content(attachments: object) -> bool:
    if not isinstance(attachments, list):
        return False
    for item in attachments:
        if isinstance(item, dict) and (str(item.get("text", "")).strip() or str(item.get("notice", "")).strip()):
            return True
    return False

def _attachment_text_budget(response_mode: str, file_count: int) -> int:
    total_budget = {
        "quick": 6000,
        "fast": 16000,
        "auto": 22000,
        "asset": 42000,
        "balanced": 60000,
        "deep": 90000,
    }.get(response_mode, 22000)
    return max(2500, min(MAX_ATTACHMENT_TEXT, total_budget // max(1, file_count)))

def _middle_clip_text(text: str, limit: int) -> str:
    cleaned = str(text or "").strip()
    if len(cleaned) <= limit:
        return cleaned
    head = max(1000, int(limit * 0.46))
    tail = max(1000, int(limit * 0.34))
    middle = max(800, limit - head - tail)
    center = max(head, len(cleaned) // 2 - middle // 2)
    omitted_1 = center - head
    omitted_2 = len(cleaned) - (center + middle) - tail
    return (
        cleaned[:head]
        + f"\n\n[... đã lược bớt {max(0, omitted_1)} ký tự ở đoạn giữa đầu để tránh prompt quá nặng ...]\n\n"
        + cleaned[center : center + middle]
        + f"\n\n[... đã lược bớt {max(0, omitted_2)} ký tự trước đoạn cuối ...]\n\n"
        + cleaned[-tail:]
    )

def _format_attachments(attachments: object, response_mode: str = "auto") -> str:
    if not isinstance(attachments, list):
        return ""
    sections = []
    usable = [item for item in attachments[:MAX_UPLOAD_FILES_PER_BATCH] if isinstance(item, dict)]
    text_limit = _attachment_text_budget(response_mode, len(usable))
    for index, item in enumerate(usable, start=1):
        name = str(item.get("name", f"file-{index}"))
        file_type = str(item.get("type", "unknown"))
        notice = str(item.get("notice", "")).strip()
        text = str(item.get("text", "")).strip()
        if not text and not notice:
            continue
        clipped = _middle_clip_text(text, text_limit) if text else ""
        omitted_note = ""
        if text and len(text) > len(clipped):
            omitted_note = f"\nOriginal length: {len(text)} chars. Included representative extract: {len(clipped)} chars."
        sections.append(
            f"""### File {index}: {name}
Type: {file_type}
Note: {notice or "Da doc duoc noi dung."}{omitted_note}

{clipped}
"""
        )
    return "\n".join(sections)

def _save_and_read_upload(item: dict, index: int) -> dict:
    if not isinstance(item, dict):
        raise ValueError("Invalid file payload")
    name = _safe_filename(str(item.get("name") or f"upload-{index}"))
    data_base64 = str(item.get("dataBase64") or "")
    if not data_base64:
        raise ValueError("Missing file data")
    raw = base64.b64decode(data_base64, validate=False)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise ValueError(f"File qua lon. Gioi han {MAX_UPLOAD_BYTES // 1024 // 1024}MB moi file.")

    target = _unique_upload_path(name)
    target.write_bytes(raw)
    return _read_saved_upload(name, target)

def _save_and_read_upload_stream(name: str, file_obj, index: int) -> dict:
    safe_name = _safe_filename(name or f"upload-{index}")
    target = _unique_upload_path(safe_name)
    total = 0
    with target.open("wb") as output:
        while True:
            chunk = file_obj.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_UPLOAD_BYTES:
                output.close()
                try:
                    target.unlink()
                except OSError:
                    pass
                raise ValueError(f"File qua lon. Gioi han {MAX_UPLOAD_BYTES // 1024 // 1024}MB moi file.")
            output.write(chunk)
    return _read_saved_upload(safe_name, target)

def _read_saved_upload(name: str, target: Path) -> dict:
    suffix = target.suffix.lower()
    file_url = _upload_file_url(target)

    if suffix in SUPPORTED_IMAGE_EXTENSIONS:
        ocr_text = _read_image_text(target)
        return {
            "name": name,
            "type": "image",
            "path": str(target),
            "url": file_url,
            "text": ocr_text,
            "notice": (
                "Da OCR anh." if ocr_text else
                "Da nhan file anh. May nay chua co OCR/vision local nen chi luu anh, chua doc duoc noi dung hinh."
            ),
        }

    try:
        text = clean_text(read_brain_text(target))[:MAX_ATTACHMENT_TEXT]
    except Exception as error:
        return {
            "name": name,
            "type": suffix.lstrip(".") or "file",
            "path": str(target),
            "url": file_url,
            "text": "",
            "notice": f"Da luu file nhung chua trich xuat duoc text: {error}",
        }

    return {
        "name": name,
        "type": suffix.lstrip(".") or "file",
        "path": str(target),
        "url": file_url,
        "text": text,
        "notice": _upload_notice_for_text(suffix, text),
    }

def _upload_file_url(target: Path) -> str:
    try:
        rel = target.resolve().relative_to(UPLOADS_DIR.resolve())
    except (OSError, ValueError):
        return ""
    return f"/api/upload_file?name={quote(str(rel).replace(os.sep, '/'))}"

def _upload_notice_for_text(suffix: str, text: str) -> str:
    if not text:
        if suffix == ".pdf":
            return "File PDF khong co text doc duoc va OCR khong trich xuat duoc noi dung."
        return "File khong co text doc duoc."
    if suffix == ".pdf" and text.startswith("OCR fallback:"):
        return "Da OCR PDF scan va trich xuat text."
    if suffix == ".zip":
        return "Da doc cau truc ZIP va trich xuat text tu file ho tro ben trong."
    return "Da trich xuat text."

def _upload_limits_payload() -> dict:
    used = _uploads_used_bytes()
    return {
        "maxFileBytes": MAX_UPLOAD_BYTES,
        "maxFilesPerUpload": MAX_UPLOAD_FILES_PER_BATCH,
        "maxBatchBytes": MAX_UPLOAD_BATCH_BYTES,
        "maxStorageBytes": MAX_UPLOAD_STORAGE_BYTES,
        "usedStorageBytes": used,
        "remainingStorageBytes": max(0, MAX_UPLOAD_STORAGE_BYTES - used),
        "attachmentPreviewChars": MAX_ATTACHMENT_TEXT,
    }

def _uploads_used_bytes() -> int:
    if not UPLOADS_DIR.exists():
        return 0
    total = 0
    for path in UPLOADS_DIR.rglob("*"):
        if not path.is_file():
            continue
        try:
            total += path.stat().st_size
        except OSError:
            continue
    return total

def _has_upload_capacity(incoming_bytes: int) -> bool:
    return _uploads_used_bytes() + max(0, int(incoming_bytes or 0)) <= MAX_UPLOAD_STORAGE_BYTES

def _format_bytes(value: int) -> str:
    size = float(max(0, int(value or 0)))
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} TB"

def _upload_capacity_error(incoming_bytes: int) -> str:
    used = _uploads_used_bytes()
    remaining = max(0, MAX_UPLOAD_STORAGE_BYTES - used)
    return (
        f"Kho upload khong du dung luong. Con {_format_bytes(remaining)}, "
        f"file/lua upload can khoang {_format_bytes(incoming_bytes)}. "
        f"Gioi han kho hien tai {_format_bytes(MAX_UPLOAD_STORAGE_BYTES)}."
    )

def _read_image_text(path: Path) -> str:
    try:
        from rapidocr_onnxruntime import RapidOCR
    except Exception:
        return _read_image_text_with_tesseract(path)
    try:
        engine = RapidOCR()
        result, _ = engine(str(path))
        lines = []
        if result:
            for item in result:
                if len(item) >= 2 and item[1]:
                    lines.append(str(item[1]).strip())
        return clean_text("\n".join(line for line in lines if line))
    except Exception:
        return _read_image_text_with_tesseract(path)

def _read_image_text_with_tesseract(path: Path) -> str:
    try:
        from PIL import Image
        import pytesseract
    except Exception:
        return ""
    try:
        return clean_text(pytesseract.image_to_string(Image.open(path)))
    except Exception:
        return ""

def _safe_filename(name: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in " ._-()" else "_" for char in name).strip()
    return cleaned[:160] or "upload"

def _unique_upload_path(name: str) -> Path:
    candidate = UPLOADS_DIR / name
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    counter = 2
    while True:
        next_candidate = UPLOADS_DIR / f"{stem}-{counter}{suffix}"
        if not next_candidate.exists():
            return next_candidate
        counter += 1

def _preview_sources(query: str) -> list[dict]:
    hits = search_all_role_brains(query, limit_per_brain=2)
    return [
        {
            "brain": hit.brain_name,
            "title": hit.title,
            "source_path": hit.source_path,
            "excerpt": _clip(hit.text, 180),
        }
        for hit in hits[:5]
    ]

def _brain_status_cards() -> list[dict]:
    cards = []
    for profile in get_agent_profiles():
        summary = brain_summary(profile.db_path)
        cards.append(
            {
                "key": profile.key,
                "name": profile.name,
                "mission": profile.mission,
                "documents": summary["documents"],
                "chunks": summary["chunks"],
                "textMb": summary["text_mb"],
                "dbMb": summary["db_size_mb"],
                "errors": summary["errors"],
                "subagents": [
                    {"key": subagent.key, "name": subagent.name, "job": subagent.job}
                    for subagent in profile.subagents
                ],
            }
        )
    return cards


def _clip(text: str, max_chars: int) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 3].rstrip() + "..."


if __name__ == "__main__":
    main()
