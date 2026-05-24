# Reading Mode v1.13-reading-mode

## Added
- Floating eye button `👁` to hide topbar/composer while reading.
- In reading mode, the chat area uses almost full height and extra padding.
- Button changes to `✎` while reading; click again to show input/topbar.
- `Esc` exits reading mode.
- Reading mode state is saved in localStorage.

## Verified
- `node --check web_ui/app.js`: PASS
- `python -m py_compile web_app.py`: PASS
- `/api/status`: PASS
