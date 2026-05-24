# Scroll Stability Hotfix v1.13-prompt-clean.5

## Fixed
- Stopped `renderActiveThread()` from scrolling to bottom by default on re-render.
- Reduced near-bottom auto-follow threshold from 120px to 24px, so reading position locks sooner.
- Reduced programmatic scroll window from 180ms to 80ms.
- Reduced textarea auto-grow max from 180px to 120px.
- Added `overflow-anchor: none`, `scroll-padding`, and extra bottom padding so content is not hidden by composer/topbar.
- Moved scroll-bottom button above composer.

## Verified
- `node --check web_ui/app.js`: PASS
- `python -m py_compile web_app.py`: PASS
- `/api/status`: PASS
