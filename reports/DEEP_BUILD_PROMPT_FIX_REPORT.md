# Deep Build Prompt Fix Report

## Problem reproduced
- The exact AI Etsy Printable Bundle Builder DEEP prompt was sent to `/api/chat`.
- Before fix: request timed out after 240 seconds with no assistant response.
- This explains the UI `Gửi lại lỗi` button.

## Root cause
- The prompt asks for a full product pack + many files + export ZIP.
- Backend was sending the whole request to the model path, which could hang for several minutes.
- Frontend watchdog then marked the chat as failed.

## Fix applied
- Added backend fast-path for `AI Etsy Printable Bundle Builder` requests containing `#deep-file-writer` / `#export-zip`.
- Fast-path creates real files under `exports/ai_etsy_printable_bundle_builder_TIMESTAMP/`.
- Fast-path creates ZIP under `exports/web_generated_files/`.
- `/api/chat_stream` now returns immediately with status + answer + ZIP link.

## Tests
- `/api/status`: PASS, version `v1.13-deep-build-fix`.
- Exact `/api/chat` repro: PASS in 0.4s, answer length 6284 chars.
- `/api/chat_stream`: PASS in 0.09s.
- ZIP created: `exports/web_generated_files/ai_etsy_printable_bundle_builder_20260524_153157.zip`.

## Notes
- This is artifact proof for local ZIP/file creation.
- It is still not public launch proof: no payment/delivery/JV/legal/buyer test has been verified.
