from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
RUNNER_DIR = LOG_DIR / ".real_web_chat_runner"
SCENARIO = os.environ.get("REAL_CHAT_SCENARIO", "phase5").strip().lower()

PHASE5_PROMPT = """Product: AI Coloring Page Niche Pack

PHASE 5 ONLY - SALES PAGE + JV MANAGER + FUNNEL

Yeu cau: xu ly nhu chat AI that, khong dung prebuilt answer, khong tra STEP_UNSUPPORTED.

25. Sales Page Strategy
26. Sales Page Copy
27. Sales Page Claim Audit
28. WarriorPlus Listing
29. JV Manager Plan
30. JV Page / JV Invite
31. Affiliate Email Swipes
32. Social Posts / Promo Assets
33. Bonus / Order Bump / OTO Map

Output phai co:
- PRODUCT USED
- PHASE USED
- Step 25 den Step 33
- SALES CLAIM SAFETY
- JV READINESS
- FUNNEL READINESS
- REQUEST DEBUG
"""

STEP35_PROMPT = """Product: AI Coloring Page Niche Pack

STEP 35 ONLY - EXPORT ZIP + MANIFEST TEST

Khong dung cau tra loi cu.
Khong dung STEP_UNSUPPORTED.
Khong dung prebuilt answer.
Khong dung san pham AI Etsy Printable Bundle Builder.

Hay xu ly bang AI API that.

Muc tieu:
Kiem tra va lap ke hoach export san pham thanh ZIP cuoi cung de giao cho buyer.
Neu chua tao ZIP that, bat buoc ghi TEXT ONLY, NOT ZIP PROOF.

Output phai co:
- PRODUCT USED
- STEP USED
- EXPORT TARGET
- ZIP CONTENT PLAN
- MANIFEST CHECK
- PLACEHOLDER CHECK
- FILES MISSING
- ZIP QUALITY GATE
- REQUEST DEBUG
"""

SCENARIOS = {
    "phase5": {
        "route": "REAL_AI_CHAT_PHASE_5",
        "prompt": PHASE5_PROMPT,
        "response_log": LOG_DIR / "real_chat_phase5_response.md",
        "debug_log": LOG_DIR / "real_chat_phase5_debug.json",
        "fail_log": LOG_DIR / "real_chat_phase5_fail.json",
        "required": ["AI Coloring Page Niche Pack", "25", "26", "27", "28", "29", "30", "31", "32", "33"],
    },
    "step35": {
        "route": "REAL_AI_CHAT_STEP_35_EXPORT_ZIP_MANIFEST_TEST",
        "prompt": STEP35_PROMPT,
        "response_log": LOG_DIR / "real_chat_step35_response.md",
        "debug_log": LOG_DIR / "real_chat_step35_debug.json",
        "fail_log": LOG_DIR / "real_chat_step35_fail.json",
        "required": ["AI Coloring Page Niche Pack", "STEP", "ZIP", "MANIFEST"],
    },
}

DEFAULT_URL = "http://127.0.0.1:18088/"

def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    RUNNER_DIR.mkdir(parents=True, exist_ok=True)
    url = os.environ.get("REAL_CHAT_URL", DEFAULT_URL)
    scenario = SCENARIOS.get(SCENARIO, SCENARIOS["phase5"])
    expected_route = scenario["route"]
    prompt = os.environ.get("REAL_CHAT_PROMPT", scenario["prompt"])
    response_log_path = scenario["response_log"]
    debug_log_path = scenario["debug_log"]
    fail_log_path = scenario["fail_log"]
    required_items = scenario["required"]
    headed = os.environ.get("HEADLESS", "0") not in {"1", "true", "TRUE"}
    timeout_ms = int(os.environ.get("REAL_CHAT_TIMEOUT_MS", "180000"))

    js = f"""
const {{ chromium }} = require('playwright');
const fs = require('fs');

const url = {json.dumps(url)};
const promptText = {json.dumps(prompt)};
const headed = {json.dumps(headed)};
const timeoutMs = {timeout_ms};
const responseLog = {json.dumps(str(response_log_path))};
const debugLog = {json.dumps(str(debug_log_path))};
const failLog = {json.dumps(str(fail_log_path))};
const expectedRoute = {json.dumps(expected_route)};
const requiredItems = {json.dumps(required_items)};

function fail(reason, extra = {{}}) {{
  const payload = {{ ok: false, fail_reason: reason, prompt_sent: promptText, ...extra }};
  fs.writeFileSync(failLog, JSON.stringify(payload, null, 2), 'utf8');
  console.error(JSON.stringify(payload, null, 2));
  process.exit(1);
}}

(async () => {{
  let browser;
  try {{
    browser = await chromium.launch({{ headless: !headed, channel: 'chrome' }}).catch(() => chromium.launch({{ headless: !headed }}));
    const page = await browser.newPage();
    page.on('dialog', async dialog => dialog.accept().catch(() => {{}}));
    await page.goto(url, {{ waitUntil: 'domcontentloaded', timeout: 30000 }});
    await page.waitForSelector('#prompt', {{ timeout: 30000 }});

    const newChat = page.locator('#newChatBtn');
    if (await newChat.count()) await newChat.click().catch(() => {{}});
    await page.locator('#prompt').fill(promptText);
    await page.locator('#sendBtn').click();

    await page.waitForFunction(() => {{
      const messages = Array.from(document.querySelectorAll('.msg.assistant'));
      const last = messages[messages.length - 1];
      const text = last ? last.innerText || '' : '';
      const debugPanel = last ? last.querySelector('.route-debug-panel') : null;
      const debugText = debugPanel ? debugPanel.innerText || '' : '';
      return text.includes(expectedRoute) || debugText.includes(expectedRoute);
    }}, null, {{ timeout: timeoutMs }});

    await page.waitForTimeout(1500);
    const data = await page.evaluate(() => {{
      const messages = Array.from(document.querySelectorAll('.msg.assistant'));
      const last = messages[messages.length - 1];
      const response_text = last ? last.innerText || '' : '';
      const debugPanel = last ? last.querySelector('.route-debug-panel') : null;
      const debug_text = debugPanel ? debugPanel.innerText || '' : '';
      return {{ response_text, debug_text }};
    }});

    fs.writeFileSync(responseLog, data.response_text, 'utf8');
    const debug = {{ ok: true, prompt_sent: promptText, ...data }};
    fs.writeFileSync(debugLog, JSON.stringify(debug, null, 2), 'utf8');

    const response = data.response_text || '';
    const debugText = data.debug_text || '';
    const missing = requiredItems.filter(item => !response.includes(item));
    const forbidden = ['STEP_UNSUPPORTED', 'STEP 5 ONLY', 'AI Etsy Printable Bundle Builder'].filter(item => response.includes(item));
    const debugFailures = [];
    if (!debugText.includes(expectedRoute) && !response.includes(expectedRoute)) debugFailures.push('selected_route missing ' + expectedRoute);
    if (!debugText.includes('API: true') && !response.includes('api_called: true')) debugFailures.push('api_called true missing');
    if (debugText.includes('Prebuilt: true') || response.includes('prebuilt_answer_used: true')) debugFailures.push('prebuilt true');
    if (missing.length || forbidden.length || debugFailures.length) {{
      fail('Real UI validation failed', {{ missing, forbidden, debugFailures, response_text: response, debug_text: debugText }});
    }}

    console.log(JSON.stringify({{ ok: true, responseLog, debugLog }}, null, 2));
    await browser.close();
  }} catch (error) {{
    if (browser) await browser.close().catch(() => {{}});
    fail(String(error && error.message ? error.message : error));
  }}
}})();
"""

    with tempfile.NamedTemporaryFile("w", suffix=".cjs", delete=False, encoding="utf-8", dir=RUNNER_DIR) as handle:
        handle.write(js)
        temp_js = handle.name
    try:
        npm = shutil.which("npm.cmd") or shutil.which("npm") or "npm"
        node = shutil.which("node.exe") or shutil.which("node") or "node"
        package_json = RUNNER_DIR / "package.json"
        if not package_json.exists():
            package_json.write_text('{"private":true,"dependencies":{"playwright":"latest"}}\n', encoding="utf-8")
        if not (RUNNER_DIR / "node_modules" / "playwright").exists():
            subprocess.run([npm, "install", "--silent"], cwd=RUNNER_DIR, check=True)
        return subprocess.run([node, temp_js], cwd=RUNNER_DIR).returncode
    finally:
        try:
            Path(temp_js).unlink()
        except OSError:
            pass


if __name__ == "__main__":
    sys.exit(main())
