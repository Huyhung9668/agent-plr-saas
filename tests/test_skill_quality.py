from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from product_pipeline import score_skill_output

REQUIRED_SECTIONS = [
    "## Purpose", "## When To Use", "## Trigger Keywords", "## Required Inputs",
    "## Optional Inputs", "## Project Context Rules", "## AI/API Rule",
    "## Tool/Fast Path Rule", "## Step-by-Step Procedure", "## Output Schema",
    "## Files To Read", "## Files To Create/Update", "## Quality Checklist",
    "## Failure Conditions", "## Test Prompts", "## Scoring Rubric /10",
    "## Repair Instructions",
]


def test_skill_quality_scores_and_outputs():
    index = json.loads((ROOT / "skills" / "_index.json").read_text(encoding="utf-8"))
    scores = {}
    failed = {}
    report = ["# Skill Audit Report", ""]
    assert len(index) == 44
    for skill in index:
        path = ROOT / skill["file_path"]
        assert path.exists(), path
        text = path.read_text(encoding="utf-8")
        missing = [section for section in REQUIRED_SECTIONS if section not in text]
        score = score_skill_output(text)
        scores[skill["skill_id"]] = {"score": score, "missing_sections": missing}
        report.append(f"- {skill['skill_id']}: {score}/10")
        if score < 10 or missing:
            failed[skill["skill_id"]] = {"score": score, "missing_sections": missing}
    out = ROOT / "skill_outputs"
    out.mkdir(exist_ok=True)
    (out / "skill_scores.json").write_text(json.dumps(scores, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "failed_skills.json").write_text(json.dumps(failed, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "skill_audit_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    assert not failed
