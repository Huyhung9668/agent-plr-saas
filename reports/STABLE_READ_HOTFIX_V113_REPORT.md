# Stable Read Hotfix v1.13-stable-read.1

## Root causes fixed
- Disabled periodic `refreshFromServer` interval that re-rendered chat every 5 seconds while reading.
- Disabled live `MutationObserver` text repair that caused font flicker/layout shifts.
- Removed initial `focusPrompt()` on load to avoid viewport jumps.
- Added final CSS hard reset for dim/opacity/backdrop layers after real Chrome screenshot check.
- Changed reading toggle from emoji icon to text labels `Đọc` / `Viết` to avoid icon-font issues.

## Real UI check
- Chrome headless screenshot saved: `reports/stable_read_ui_check_2.png`
- Follow-up screenshot saved: `reports/stable_read_ui_check_3.png`
- Result: text is visible, no dim overlay in screenshot.

## Tests
- `node --check web_ui/app.js`: PASS
- `/api/status`: PASS, appVersion `v1.13-stable-read.1`
