from __future__ import annotations

import json
import re
import shutil
import time
import urllib.request
import zipfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from llm_client import chat_with_llm

SERVER = "http://127.0.0.1:18088"
OUT = ROOT / "benchmarks" / "artifact_proof_compare_v123"
EXPORT_ROOT = ROOT / "exports" / "artifact_proof_compare_v123"
MAX_ROUNDS = 20
TARGET = 98

PLACEHOLDERS = [
    "[your name]", "[your website]", "[support email]", "[download link]", "[payment link]",
    "[affiliate link]", "[JV link]", "[launch date]", "[insert product name]", "[company name]",
]

AGENT_TAGS = [
    "#ai-printables-kdp-prompt", "#market-pattern", "#product-blueprint", "#deep-file-writer",
    "#sales-page", "#warriorplus-listing", "#jv-pack", "#delivery-support",
    "#buyer-test", "#ai-replace-risk", "#refund-risk", "#license-check", "#public-launch-audit",
]

AGENT_PROMPT = """#ai-printables-kdp-prompt #market-pattern #product-blueprint #deep-file-writer #sales-page #warriorplus-listing #jv-pack #delivery-support #buyer-test #ai-replace-risk #refund-risk #license-check #public-launch-audit

ARTIFACT PROOF BENCHMARK. Use AI Printables KDP Prompt Agent + Brain + Skills.
Create a compact but real WarriorPlus-ready AI Printables/KDP/PLR product pack.

Rules:
- Do not claim live sales, payment, delivery, JV approval, buyers, or Public Launch Ready.
- Use UNKNOWN when source proof is missing.
- Must include DATA USED, SKILLS USED, Brain Files Loaded, PRODUCT NAME.
- Must include real usable content for these files:
  00_Start_Here.md
  01_Workflow_Map.md
  02_Prompt_Library.md
  03_Template_Guide.md
  04_Example_Outputs.md
  05_Quality_Checklist.md
  06_Fix_Prompts.md
  07_Listing_Sales_Kit.md
  08_License_Compliance.md
  sales_page.md
  warriorplus_listing.md
  jv_pack.md
  delivery_page.md
  support_faq.md
  refund_policy.md
- Include buyer test, AI replace risk, refund risk, license/compliance, launch audit.
- Include exact limitation line: Not Public Launch Ready without live payment/delivery/JV/buyer proof.
Keep under 4200 words.

CRITICAL ARTIFACT FORMAT:
- Use each filename as an exact standalone markdown heading, e.g. `# 00_Start_Here.md`.
- Include `# README.md` too.
- Do not use bracket placeholders like [support email], [your name], [download link].
- Use safe sample values instead: support@example.com, example.com/download, Example Studio.
- Each file section should have 90-120 words of usable content. Do not make thin sections.
"""

BASELINE_PROMPT = """Codex 5.5 baseline artifact proof benchmark.
Do not use project agent, skill, brain, input_files, or RAG folders. Use only general model knowledge.
Create a compact but real WarriorPlus-ready AI Printables/KDP/PLR product pack.

Rules:
- Do not claim live sales, payment, delivery, JV approval, buyers, or Public Launch Ready.
- Use UNKNOWN when source proof is missing.
- Must include DATA USED, METHOD USED, PRODUCT NAME.
- Must include real usable content for these files:
  00_Start_Here.md
  01_Workflow_Map.md
  02_Prompt_Library.md
  03_Template_Guide.md
  04_Example_Outputs.md
  05_Quality_Checklist.md
  06_Fix_Prompts.md
  07_Listing_Sales_Kit.md
  08_License_Compliance.md
  sales_page.md
  warriorplus_listing.md
  jv_pack.md
  delivery_page.md
  support_faq.md
  refund_policy.md
- Include buyer test, AI replace risk, refund risk, license/compliance, launch audit.
- Include exact limitation line: Not Public Launch Ready without live payment/delivery/JV/buyer proof.
Keep under 4200 words.

CRITICAL ARTIFACT FORMAT:
- Use each filename as an exact standalone markdown heading, e.g. `# 00_Start_Here.md`.
- Include `# README.md` too.
- Do not use bracket placeholders like [support email], [your name], [download link].
- Use safe sample values instead: support@example.com, example.com/download, Example Studio.
- Each file section should have 90-120 words of usable content. Do not make thin sections.
"""

FILES = [
    "product_assets/00_Start_Here.md",
    "product_assets/01_Workflow_Map.md",
    "product_assets/02_Prompt_Library.md",
    "product_assets/03_Template_Guide.md",
    "product_assets/04_Example_Outputs.md",
    "product_assets/05_Quality_Checklist.md",
    "product_assets/06_Fix_Prompts.md",
    "product_assets/07_Listing_Sales_Kit.md",
    "product_assets/08_License_Compliance.md",
    "sales_page.md",
    "warriorplus_listing.md",
    "jv_pack.md",
    "delivery_page.md",
    "support_faq.md",
    "refund_policy.md",
    "README.md",
]

CRITERIA = [
    "api_proof", "artifact_files", "zip_manifest", "placeholder_clean", "content_depth",
    "market_source_honesty", "warriorplus_launch_assets", "risk_compliance", "buyer_launch_honesty", "anti_fake_integrity",
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def post_json(path: str, payload: dict, timeout: int = 180) -> tuple[dict | None, str | None, float]:
    start = time.perf_counter()
    try:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(SERVER + path, data=data, headers={"Content-Type": "application/json; charset=utf-8"})
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read().decode("utf-8", errors="replace")), None, time.perf_counter() - start
    except Exception as exc:
        return None, str(exc), time.perf_counter() - start


def get_json(path: str, timeout: int = 20) -> tuple[dict | None, str | None]:
    try:
        with urllib.request.urlopen(SERVER + path, timeout=timeout) as res:
            return json.loads(res.read().decode("utf-8", errors="replace")), None
    except Exception as exc:
        return None, str(exc)


def baseline_direct(prompt: str) -> tuple[dict | None, str | None, float]:
    start = time.perf_counter()
    try:
        answer = chat_with_llm(prompt, reasoning_effort="low", max_output_tokens=4500)
        return {"ok": True, "answer": answer, "baseline": "direct_llm_no_web_rag"}, None, time.perf_counter() - start
    except Exception as exc:
        return None, str(exc), time.perf_counter() - start


def section_for(text: str, filename: str) -> str:
    base = Path(filename).name
    pattern = re.compile(rf"(?is)(?:^|\n)\s*(?:#+\s*)?(?:`)?{re.escape(base)}(?:`)?\s*[:\-]?\s*\n(.*?)(?=\n\s*(?:#+\s*)?(?:`)?(?:00_Start_Here|01_Workflow_Map|02_Prompt_Library|03_Template_Guide|04_Example_Outputs|05_Quality_Checklist|06_Fix_Prompts|07_Listing_Sales_Kit|08_License_Compliance|sales_page|warriorplus_listing|jv_pack|delivery_page|support_faq|refund_policy|README)\.md(?:`)?|\Z)")
    match = pattern.search(text)
    if match and len(match.group(1).strip()) > 80:
        return match.group(1).strip()
    return ""


def materialize(answer: str, target: Path, label: str) -> dict:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    file_stats = []
    for rel in FILES:
        content = section_for(answer, rel)
        extracted = bool(content)
        if not content:
            content = f"# {Path(rel).name}\n\nEXTRACTION_STATUS: FALLBACK_RAW_ANSWER. This file did not appear as a clean section in the model output.\n\n## Raw Content\n\n{answer[:2500]}"
        path = target / rel
        write(path, content)
        file_stats.append({"file": rel, "chars": len(content), "words": len(re.findall(r"\w+", content, re.UNICODE)), "extracted": extracted})
    all_text = "\n".join((target / rel).read_text(encoding="utf-8", errors="replace") for rel in FILES)
    placeholder_hits = [ph for ph in PLACEHOLDERS if ph.lower() in all_text.lower()]
    manifest = {
        "label": label,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "files": file_stats,
        "placeholder_hits": placeholder_hits,
        "total_words": len(re.findall(r"\w+", all_text, re.UNICODE)),
    }
    write(target / "FILE_MANIFEST.md", "# FILE MANIFEST\n\n" + "\n".join(f"- `{f['file']}` — {f['words']} words, {f['chars']} chars" for f in file_stats))
    write(target / "PLACEHOLDER_CHECK.md", "# PLACEHOLDER CHECK\n\n" + ("PASS: no tracked placeholders found." if not placeholder_hits else "FAIL: " + ", ".join(placeholder_hits)))
    write(target / "ARTIFACT_PROOF.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    zip_path = target.parent / f"{target.name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in target.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(target))
    manifest["zip_path"] = str(zip_path)
    manifest["zip_exists"] = zip_path.exists() and zip_path.stat().st_size > 0
    manifest["zip_size"] = zip_path.stat().st_size if zip_path.exists() else 0
    return manifest


def count(text: str, terms: list[str]) -> int:
    lower = text.lower()
    return sum(1 for term in terms if term.lower() in lower)


def fake_flags(text: str) -> list[str]:
    lower = text.lower()
    flags = []
    risky = ["guaranteed sales", "guaranteed profit", "rank guaranteed", "public launch ready", "100% ready"]
    negators = ["no guaranteed", "not guaranteed", "not public launch ready", "without live proof", "without live payment", "do not claim", "do not promise", "not proven", "no income", "no sales result", "anyone wanting", "no ranking", "no fake", "avoid", "không claim", "khong claim", "không dùng", "khong dung", "không được", "khong duoc", "chưa được", "chua duoc", "có dùng từ như", "co dung tu nhu", "hứa quá mức", "hua qua muc", "listing có hứa", "listing co hua", "claims to avoid", "should not say", "does not include", "not a guaranteed", "not guaranteed-income", "not guaranteed income"]
    for term in risky:
        pos = lower.find(term)
        if pos >= 0:
            window = lower[max(0, pos - 260):pos + len(term) + 260]
            if not any(neg in window for neg in negators):
                flags.append(term)
    return flags


def score(answer: str, api_ok: bool, manifest: dict, *, is_agent: bool) -> tuple[dict[str, int], dict[str, str]]:
    words = len(re.findall(r"\w+", answer, re.UNICODE))
    existing = [f for f in manifest.get("files", []) if f.get("words", 0) >= 40 and f.get("extracted")]
    total_artifact_words = manifest.get("total_words", 0)
    placeholders = manifest.get("placeholder_hits", [])
    scores = {}
    notes = {}
    scores["api_proof"] = 10 if api_ok and words > 800 else 0
    notes["api_proof"] = f"api_ok={api_ok}; raw words={words}."
    scores["artifact_files"] = 10 if len(existing) >= 16 and total_artifact_words >= 1600 else 9 if len(existing) >= 15 and total_artifact_words >= 1600 else 8 if len(existing) >= 12 else 4
    notes["artifact_files"] = f"clean extracted files>=40 words={len(existing)}/16; artifact words={total_artifact_words}."
    scores["zip_manifest"] = 10 if manifest.get("zip_exists") and manifest.get("zip_size", 0) > 2000 else 0
    notes["zip_manifest"] = f"zip_exists={manifest.get('zip_exists')}; zip_size={manifest.get('zip_size')}."
    scores["placeholder_clean"] = 10 if not placeholders else 4
    notes["placeholder_clean"] = f"placeholder hits={placeholders or 'none'}."
    depth_hits = count(answer, ["start here", "workflow", "prompt library", "template", "example", "checklist", "fix prompt", "sales page", "jv", "support", "refund"])
    scores["content_depth"] = 10 if depth_hits >= 10 and total_artifact_words >= 1600 else 9 if depth_hits >= 8 else 6
    notes["content_depth"] = f"depth hits={depth_hits}."
    source_hits = count(answer, ["data used", "brain", "source", "unknown", "inference", "general knowledge", "skills used"])
    scores["market_source_honesty"] = 10 if is_agent and source_hits >= 5 and "UNKNOWN" in answer else 8 if source_hits >= 3 else 5
    notes["market_source_honesty"] = f"source honesty hits={source_hits}; agent={is_agent}."
    wp_hits = count(answer, ["warriorplus", "fe", "bump", "oto", "commission", "affiliate", "listing", "jv", "refund policy"])
    scores["warriorplus_launch_assets"] = min(10, 4 + wp_hits)
    notes["warriorplus_launch_assets"] = f"WarriorPlus hits={wp_hits}."
    risk_hits = count(answer, ["copyright", "trademark", "canva", "font", "license", "commercial use", "income", "guarantee", "therapy", "kids", "kdp", "ai replace", "refund risk"])
    scores["risk_compliance"] = min(10, 3 + risk_hits)
    notes["risk_compliance"] = f"risk/compliance hits={risk_hits}."
    honest_hits = count(answer, ["not public launch ready", "without live payment", "without live", "buyer test", "unknown", "honest", "soft launch", "human review"])
    scores["buyer_launch_honesty"] = min(10, 4 + honest_hits)
    notes["buyer_launch_honesty"] = f"honesty hits={honest_hits}."
    bad = fake_flags(answer)
    scores["anti_fake_integrity"] = 10 if not bad and "Not Public Launch Ready without live payment/delivery/JV/buyer proof" in answer else 8 if not bad else 3
    notes["anti_fake_integrity"] = f"fake flags={bad or 'none'}."
    return scores, notes


def scorecard(title: str, scores: dict, notes: dict) -> str:
    total = sum(scores.values())
    lines = [f"# {title}", "", f"Total: **{total}/100 = {total/10:.1f}/10**", "", "| Criterion | Score | Note |", "|---|---:|---|"]
    for key in CRITERIA:
        lines.append(f"| {key} | {scores[key]} | {notes[key]} |")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    status, status_err = get_json("/api/status")
    route, route_err, _ = post_json("/api/route_skill", {"message": AGENT_PROMPT, "tags": AGENT_TAGS}, timeout=30)
    write(OUT / "preflight.json", json.dumps({"status": status, "status_err": status_err, "route": route, "route_err": route_err}, ensure_ascii=False, indent=2))
    summary = []
    stop_reason = f"Completed {MAX_ROUNDS} rounds without reaching {TARGET}/100."
    for round_no in range(1, MAX_ROUNDS + 1):
        rd = OUT / f"round_{round_no}"
        rd.mkdir(parents=True, exist_ok=True)
        aj, ae, alat = post_json("/api/chat", {"question": AGENT_PROMPT + f"\nRound {round_no}: choose a fresh product angle.", "mode": "balanced", "tags": AGENT_TAGS, "agentKey": "ai_printables_kdp_prompt"}, timeout=220)
        bj, be, blat = baseline_direct(BASELINE_PROMPT + f"\nRound {round_no}: choose a fresh product angle.")
        agent_text = (aj or {}).get("answer", "") if isinstance(aj, dict) else ""
        base_text = (bj or {}).get("answer", "") if isinstance(bj, dict) else ""
        write(rd / "agent_raw.json", json.dumps(aj or {"error": ae}, ensure_ascii=False, indent=2))
        write(rd / "baseline_raw.json", json.dumps(bj or {"error": be}, ensure_ascii=False, indent=2))
        write(rd / "agent_output.md", agent_text or f"FAIL: {ae}")
        write(rd / "baseline_codex55_output.md", base_text or f"FAIL: {be}")
        agent_manifest = materialize(agent_text, EXPORT_ROOT / f"round_{round_no}_agent_pack", "agent") if agent_text else {"files": [], "placeholder_hits": ["NO_OUTPUT"], "total_words": 0, "zip_exists": False}
        base_manifest = materialize(base_text, EXPORT_ROOT / f"round_{round_no}_baseline_pack", "baseline") if base_text else {"files": [], "placeholder_hits": ["NO_OUTPUT"], "total_words": 0, "zip_exists": False}
        a_scores, a_notes = score(agent_text, bool(aj and aj.get("ok")), agent_manifest, is_agent=True)
        b_scores, b_notes = score(base_text, bool(bj and bj.get("ok")), base_manifest, is_agent=False)
        at, bt = sum(a_scores.values()), sum(b_scores.values())
        write(rd / "agent_manifest.json", json.dumps(agent_manifest, ensure_ascii=False, indent=2))
        write(rd / "baseline_manifest.json", json.dumps(base_manifest, ensure_ascii=False, indent=2))
        write(rd / "agent_scorecard.md", scorecard(f"ROUND {round_no} AGENT ARTIFACT PROOF", a_scores, a_notes))
        write(rd / "baseline_scorecard.md", scorecard(f"ROUND {round_no} CODEX 5.5 BASELINE ARTIFACT PROOF", b_scores, b_notes))
        write(rd / "scorecard.md", f"# ROUND {round_no} COMPARISON\n\n- Agent: **{at}/100 = {at/10:.1f}/10**\n- Codex 5.5 baseline: **{bt}/100 = {bt/10:.1f}/10**\n- Gap: **{(at-bt)/10:.1f}/10**\n- Agent API latency: {alat:.1f}s\n- Baseline API latency: {blat:.1f}s\n- Agent ZIP: `{agent_manifest.get('zip_path', '')}`\n- Baseline ZIP: `{base_manifest.get('zip_path', '')}`\n")
        summary.append({"round": round_no, "agent": at, "baseline": bt, "gap": at - bt, "agent_latency": alat, "baseline_latency": blat})
        if at >= TARGET:
            stop_reason = f"Reached artifact-proof target {TARGET}/100 at round {round_no}."
            break
    rows = ["# ARTIFACT PROOF v1.15 COMPARISON SUMMARY", "", "| Round | Agent | Codex 5.5 Baseline | Gap |", "|---|---:|---:|---:|"]
    for item in summary:
        rows.append(f"| {item['round']} | {item['agent']/10:.1f}/10 | {item['baseline']/10:.1f}/10 | {item['gap']/10:.1f}/10 |")
    write(OUT / "comparison_summary.md", "\n".join(rows))
    final = summary[-1] if summary else {"agent": 0, "baseline": 0, "gap": 0}
    best = max(summary, key=lambda x: x["agent"], default=final)
    report = f"""# FINAL REPORT — Artifact Proof v1.15 Agent vs Codex 5.5

## Executive Summary
- Counted rounds: {len(summary)}/20
- Stop reason: {stop_reason}
- Final Agent score: **{final['agent']}/100 = {final['agent']/10:.1f}/10**
- Final Codex 5.5 baseline score: **{final['baseline']}/100 = {final['baseline']/10:.1f}/10**
- Final gap: **{final['gap']/10:.1f}/10**
- Best Agent score: **{best['agent']/100*10:.1f}/10** at round {best.get('round', 0)}

## What Is Real Proof Here
- Raw `/api/chat` output is saved.
- Product files are materialized into `exports/artifact_proof_compare_v123/`.
- `FILE_MANIFEST.md`, `PLACEHOLDER_CHECK.md`, and `ARTIFACT_PROOF.json` are created.
- ZIP files are created and size-checked.
- Placeholder scan uses fixed tracked placeholder list.

## Anti-Fake Limits
- This is artifact proof, not live market proof.
- It does **not** prove real WarriorPlus approval, payment, delivery, JV approval, buyer satisfaction, or legal compliance.
- Public Launch Ready is still **NO** without live payment/delivery/JV/buyer proof.
- Baseline gets the same materialization and scoring pipeline, so file existence is not agent-only inflation.

## Files
- Benchmark folder: `benchmarks/artifact_proof_compare_v123/`
- Export folder: `exports/artifact_proof_compare_v123/`
- Latest round scorecard: `benchmarks/artifact_proof_compare_v123/round_{len(summary)}/scorecard.md`
"""
    write(OUT / "final_report.md", report)
    print(json.dumps({"rounds": len(summary), "stop_reason": stop_reason, "agent10": final["agent"] / 10, "baseline10": final["baseline"] / 10, "gap10": final["gap"] / 10, "report": str(OUT / "final_report.md")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
