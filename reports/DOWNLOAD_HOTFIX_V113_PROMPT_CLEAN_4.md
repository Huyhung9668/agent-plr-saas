# Download Hotfix v1.13-prompt-clean.4

## Fixed
- Choosing a format from the assistant message `⇩` menu now creates the file and immediately triggers browser download.
- Added fallback URL download if base64 payload is unavailable.
- Clarified button tooltip from `Tạo file từ trả lời này` to `Tạo và tải file từ trả lời này`.
- Made generated file download icons visibly clickable.
- Updated cache/version to `v1.13-prompt-clean.4`.

## Verified
- `node --check web_ui/app.js`: PASS
- `python -m py_compile web_app.py`: PASS
- `POST /api/create_file`: PASS, created `download-test.txt`
- `GET /api/generated_file?name=download-test.txt`: PASS via `curl.exe`, downloaded 16 bytes
- `/api/status`: PASS, appVersion `v1.13-prompt-clean.4`
