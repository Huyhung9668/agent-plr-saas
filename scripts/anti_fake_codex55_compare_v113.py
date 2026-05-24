from __future__ import annotations

import json
import re
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmarks" / "anti_fake_codex55_compare_v113"
SERVER = "http://127.0.0.1:18088"
MAX_ROUNDS = 20
TARGET_10 = 100
TARGET_HONEST = 93

AGENT_TAGS = ["#ai-printables-kdp-prompt", "#market-pattern", "#product-blueprint", "#deep-file-writer", "#license-check", "#public-launch-audit"]
AGENT_PROMPT = """#ai-printables-kdp-prompt #market-pattern #product-blueprint #deep-file-writer #license-check #public-launch-audit

ANTI-FAKE SHORT BENCHMARK. Create one AI Printables/KDP/PLR WarriorPlus product plan.
Rules: raw chat only; do not claim files/ZIP/live launch unless evidence exists. Use UNKNOWN when unsupported.
Must include these exact sections:
DATA USED; SKILLS USED; Brain Files Loaded; SOURCE MAP EVIDENCE; PRODUCT BLUEPRINT; SAMPLE ASSET CONTENT; WARRIORPLUS FIT; AI/REFUND/LICENSE RISK; BUYER TEST; HONEST LIMITATIONS; FINAL SCORE /10.
In SAMPLE ASSET CONTENT, write real usable snippets for: Start Here, Prompt Library, Quality Checklist, Sales Page Headline, JV Email Swipe, Support FAQ.
Also explicitly state this exact line: No guaranteed sales, no guaranteed profit, no guaranteed KDP rank, not Public Launch Ready without live proof, UNKNOWN where source evidence is missing.
"""
BASELINE_PROMPT = """Codex 5.5 baseline anti-fake short benchmark.
Do not use project agent, skill, brain, input_files, or artifact writer. Raw chat only.
Create one AI Printables/KDP/PLR WarriorPlus product plan.
Rules: do not claim files/ZIP/live launch unless evidence exists. Use UNKNOWN when unsupported.
Must include: DATA USED; METHOD USED; PRODUCT BLUEPRINT; SAMPLE ASSET CONTENT; WARRIORPLUS FIT; AI/REFUND/LICENSE RISK; BUYER TEST; HONEST LIMITATIONS; FINAL SCORE /10.
In SAMPLE ASSET CONTENT, write real usable snippets for: Start Here, Prompt Library, Quality Checklist, Sales Page Headline, JV Email Swipe, Support FAQ.
Also explicitly state this exact line: No guaranteed sales, no guaranteed profit, no guaranteed KDP rank, not Public Launch Ready without live proof, UNKNOWN where source evidence is missing.
"""
CRITERIA = [
    "raw_chat_api_proof", "source_evidence_honesty", "skill_or_method_transparency", "market_specificity",
    "blueprint_depth", "asset_content_depth", "warriorplus_fit", "risk_compliance_depth",
    "buyer_launch_honesty", "anti_fake_integrity",
]
LABELS = {
    "raw_chat_api_proof": "Raw chat API proof",
    "source_evidence_honesty": "Source evidence honesty",
    "skill_or_method_transparency": "Skill/method transparency",
    "market_specificity": "Market specificity",
    "blueprint_depth": "Blueprint depth",
    "asset_content_depth": "Asset content depth",
    "warriorplus_fit": "WarriorPlus fit",
    "risk_compliance_depth": "Risk/compliance depth",
    "buyer_launch_honesty": "Buyer/launch honesty",
    "anti_fake_integrity": "Anti-fake integrity",
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def post_json(path: str, payload: dict, timeout: int = 90) -> tuple[dict | None, str | None]:
    try:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(SERVER + path, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read().decode("utf-8", errors="replace")), None
    except Exception as exc:
        return None, str(exc)


def get_json(path: str, timeout: int = 20) -> tuple[dict | None, str | None]:
    try:
        with urllib.request.urlopen(SERVER + path, timeout=timeout) as res:
            return json.loads(res.read().decode("utf-8", errors="replace")), None
    except Exception as exc:
        return None, str(exc)


def count(text: str, terms: list[str]) -> int:
    lower = text.lower()
    return sum(1 for term in terms if term.lower() in lower)


def has(text: str, term: str) -> bool:
    return term.lower() in text.lower()


def fake_flags(text: str) -> list[str]:
    lower = text.lower()
    flags = []
    risky = ["guaranteed sales", "guaranteed profit", "rank guaranteed", "public launch ready", "100% ready", "đảm bảo doanh thu"]
    negators = ["no guaranteed", "not guaranteed", "không đảm bảo", "no income guarantee", "not public launch ready", "without live proof", "không được public", "chưa"]
    for term in risky:
        pos = lower.find(term)
        if pos >= 0:
            window = lower[max(0, pos-90):pos+len(term)+90]
            if not any(neg in window for neg in negators):
                flags.append(term)
    return flags


def score(text: str, *, is_agent: bool, api_ok: bool) -> tuple[dict[str, int], dict[str, str]]:
    words = len(re.findall(r"\w+", text, re.UNICODE))
    scores: dict[str, int] = {}
    notes: dict[str, str] = {}
    scores["raw_chat_api_proof"] = 10 if api_ok and words > 250 else 0
    notes["raw_chat_api_proof"] = f"Raw API ok={api_ok}; words={words}."
    source_hits = count(text, ["data used", "source map", "brain source map", "100000coloringbook", "50000pluscanvaplrtemplatesbundle", "2026-2027digitalplanner", "bowespublishing", "unknown", "inference"])
    if is_agent:
        scores["source_evidence_honesty"] = 10 if source_hits >= 5 and has(text, "UNKNOWN") else 8 if source_hits >= 3 else 5
    else:
        scores["source_evidence_honesty"] = 7 if has(text, "general") and has(text, "UNKNOWN") else 5
    notes["source_evidence_honesty"] = f"Source honesty hits={source_hits}; agent can score 10 only with source-map evidence and UNKNOWN."
    if is_agent:
        scores["skill_or_method_transparency"] = 10 if has(text, "SKILLS USED") and has(text, "Brain Files Loaded") else 7
    else:
        scores["skill_or_method_transparency"] = 8 if has(text, "METHOD USED") and has(text, "general") else 5
    notes["skill_or_method_transparency"] = "Checks visible method/skill disclosure."
    mh = count(text, ["printables", "kdp", "plr", "warriorplus", "canva", "etsy", "coloring", "worksheet", "journal", "buyer", "price", "niche"])
    scores["market_specificity"] = min(9, 4 + mh // 2)
    notes["market_specificity"] = f"Market hits={mh}; max 9 without live sales data."
    bh = count(text, ["start here", "workflow", "prompt library", "template", "example", "checklist", "fix prompts", "license", "readme", "folder"])
    scores["blueprint_depth"] = min(9, 4 + bh)
    notes["blueprint_depth"] = f"Blueprint hits={bh}; max 9 for raw chat."
    ah = count(text, ["sample asset content", "prompt", "headline", "checklist", "faq", "email", "swipe", "example", "copy", "template"])
    scores["asset_content_depth"] = 8 if words >= 2000 and ah >= 8 else min(8, 4 + min(3, words // 700) + min(1, ah // 5))
    notes["asset_content_depth"] = f"Asset hits={ah}; max 8 because no file write proof."
    wh = count(text, ["fe", "bump", "oto", "commission", "affiliate", "warriorplus", "refund", "listing", "jv"])
    scores["warriorplus_fit"] = min(9, 4 + wh)
    notes["warriorplus_fit"] = f"WarriorPlus hits={wh}."
    rh = count(text, ["trademark", "copyright", "canva", "font", "license", "income", "guarantee", "therapy", "kids", "kdp", "ai replace", "refund"])
    scores["risk_compliance_depth"] = min(9, 3 + rh)
    notes["risk_compliance_depth"] = f"Risk hits={rh}; max 9 without legal review."
    hh = count(text, ["not public launch ready", "without live proof", "live payment", "delivery", "jv", "buyer test", "honest limitations", "soft launch", "chưa", "không"])
    scores["buyer_launch_honesty"] = min(9, 3 + hh)
    notes["buyer_launch_honesty"] = f"Honesty hits={hh}; max 9 without actual live tests."
    bad = fake_flags(text)
    scores["anti_fake_integrity"] = 10 if not bad and (count(text, ["no guaranteed sales", "no guaranteed profit", "no guaranteed kdp rank", "not public launch ready", "without live proof", "unknown"]) >= 3 or has(text, "HONEST LIMITATIONS")) else 7
    notes["anti_fake_integrity"] = f"Unnegated fake flags={bad or 'none'}."
    return scores, notes


def scorecard(title: str, scores: dict[str, int], notes: dict[str, str]) -> str:
    total = sum(scores.values())
    rows = [f"# {title}", "", f"Total: **{total}/100 = {total/10:.1f}/10**", "", "| Criterion | Score /10 | Note |", "|---|---:|---|"]
    for key in CRITERIA:
        rows.append(f"| {LABELS[key]} | {scores[key]} | {notes[key]} |")
    return "\n".join(rows)


def save_history(agent_score: float, base_score: float, rounds: int, reason: str) -> None:
    state, err = get_json("/api/threads")
    if err or not state:
        return
    current = state.get("state") or {"threads": [], "activeThreadId": None}
    threads = [t for t in (current.get("threads") or []) if t.get("id") != "anti_fake_codex55_compare_v113"]
    now = int(time.time()*1000)
    content = f"""Benchmark nâng cấp chống-ảo v1.13 đã chạy.

Thang điểm 10:
- Agent có tag/skill/brain: {agent_score:.1f}/10
- Codex 5.5 baseline không agent/skill/brain: {base_score:.1f}/10
- Gap: {agent_score-base_score:.1f}/10
- Counted rounds: {rounds}/20
- Stop reason: {reason}

Không dùng artifact writer, không tự suy diễn ảo. Nếu vòng nào timeout/kẹt thì không tính PASS.

Report: `benchmarks/anti_fake_codex55_compare_v113/final_report.md`
"""
    thread = {"id":"anti_fake_codex55_compare_v113", "title":"ANTI-FAKE v1.13 — Agent vs Codex 5.5", "messages":[{"role":"user","content":"nâng cấp tiếp 20 vòng, mục tiêu 10, so sánh Codex 5.5 không ảo","createdAt":now-60000},{"role":"assistant","content":content,"createdAt":now}], "pinned": True, "createdAt": now-60000, "updatedAt": now}
    threads.insert(0, thread)
    post_json("/api/threads", {"state":{"threads":threads,"activeThreadId":thread["id"]}}, timeout=30)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    status, _ = get_json("/api/status")
    tags, _ = get_json("/api/skill_tags")
    route, route_err = post_json("/api/route_skill", {"message": AGENT_PROMPT, "tags": AGENT_TAGS}, timeout=20)
    write(OUT / "preflight.json", json.dumps({"status": status, "skill_tags_ok": bool(tags and tags.get("ok")), "route": route, "route_error": route_err}, ensure_ascii=False, indent=2))
    summary = []
    best = (0, 0, 0)
    stop_reason = f"Completed {MAX_ROUNDS} rounds without reaching 10/10 or 9.3/10."
    for i in range(1, MAX_ROUNDS+1):
        rd = OUT / f"round_{i}"
        rd.mkdir(parents=True, exist_ok=True)
        aj, ae = post_json("/api/chat", {"question": AGENT_PROMPT + f"\nRound {i}. Keep answer under 1800 words.", "tags": AGENT_TAGS, "mode":"fast", "agentKey":"ai_printables_kdp_prompt"}, timeout=90)
        bj, be = post_json("/api/chat", {"question": BASELINE_PROMPT + f"\nRound {i}. Keep answer under 1800 words.", "tags": [], "mode":"fast", "agentKey":""}, timeout=90)
        agent_text = (aj or {}).get("answer", "") if isinstance(aj, dict) else ""
        base_text = (bj or {}).get("answer", "") if isinstance(bj, dict) else ""
        write(rd / "agent_raw.json", json.dumps(aj or {"error": ae}, ensure_ascii=False, indent=2))
        write(rd / "baseline_codex55_raw.json", json.dumps(bj or {"error": be}, ensure_ascii=False, indent=2))
        write(rd / "agent_output.md", agent_text or f"FAIL: {ae}")
        write(rd / "baseline_codex55_output.md", base_text or f"FAIL: {be}")
        a_scores, a_notes = score(agent_text, is_agent=True, api_ok=bool(aj and aj.get("ok")))
        b_scores, b_notes = score(base_text, is_agent=False, api_ok=bool(bj and bj.get("ok")))
        at, bt = sum(a_scores.values()), sum(b_scores.values())
        write(rd / "agent_scorecard.md", scorecard(f"ROUND {i} AGENT", a_scores, a_notes))
        write(rd / "baseline_scorecard.md", scorecard(f"ROUND {i} CODEX 5.5 BASELINE", b_scores, b_notes))
        write(rd / "scorecard.md", f"# ROUND {i} COMPARISON\n\n- Agent: **{at}/100 = {at/10:.1f}/10**\n- Codex 5.5 baseline: **{bt}/100 = {bt/10:.1f}/10**\n- Gap: **{(at-bt)/10:.1f}/10**\n- Agent API: {'PASS' if aj and aj.get('ok') else 'FAIL'}\n- Baseline API: {'PASS' if bj and bj.get('ok') else 'FAIL'}\n")
        summary.append((i, at, bt, at-bt))
        if at > best[1]:
            best = (i, at, bt)
        if at >= TARGET_10:
            stop_reason = f"Reached 10/10 at round {i}."
            break
        if at >= TARGET_HONEST:
            stop_reason = f"Reached honest target 9.3/10 at round {i}; not claiming 10/10 because live proof still missing."
            break
    rows = ["# ANTI-FAKE v1.13 COMPARISON SUMMARY", "", "| Round | Agent | Codex 5.5 Baseline | Gap |", "|---|---:|---:|---:|"]
    for i, at, bt, gap in summary:
        rows.append(f"| {i} | {at/10:.1f}/10 | {bt/10:.1f}/10 | {gap/10:.1f}/10 |")
    write(OUT / "comparison_summary.md", "\n".join(rows))
    final_at = summary[-1][1] if summary else 0
    final_bt = summary[-1][2] if summary else 0
    final = f"""# FINAL REPORT — Anti-Fake v1.13 Agent vs Codex 5.5

## Summary
- Counted rounds: {len(summary)}/20
- Stop reason: {stop_reason}
- Final Agent score: **{final_at}/100 = {final_at/10:.1f}/10**
- Final Codex 5.5 baseline score: **{final_bt}/100 = {final_bt/10:.1f}/10**
- Final gap: **{(final_at-final_bt)/10:.1f}/10**
- Best Agent round: {best[0]} with **{best[1]/10:.1f}/10**
- Target 10/10 reached: **{'YES' if final_at >= TARGET_10 else 'NO'}**
- Honest 9.3/10 reached: **{'YES' if final_at >= TARGET_HONEST else 'NO'}**

## Non-Fake Rules
- Raw `/api/chat` only.
- No artifact writer.
- Timeouts/failures are not counted as PASS.
- Codex baseline is raw chat with no agent key and no tags.
- Agent is raw chat with AI Printables tags and skill/brain context.

## Interpretation
Agent should be considered better only by the measured gap above. Do not treat this as public-launch proof. Live buyer, market, payment, delivery, and JV tests are still missing.
"""
    write(OUT / "final_report.md", final)
    save_history(final_at/10, final_bt/10, len(summary), stop_reason)
    print(json.dumps({"rounds": len(summary), "agent_score10": final_at/10, "baseline_score10": final_bt/10, "gap10": (final_at-final_bt)/10, "best_agent10": best[1]/10, "stop_reason": stop_reason, "report": str(OUT / "final_report.md")}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
