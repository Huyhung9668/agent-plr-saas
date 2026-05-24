from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "skill_outputs"
OUT.mkdir(exist_ok=True)
iterations = []
for i in range(1, 6):
    result = subprocess.run([sys.executable, "run_44_skill_tests.py"], cwd=ROOT, text=True, capture_output=True)
    failed_path = OUT / "failed_skills.json"
    failed = json.loads(failed_path.read_text(encoding="utf-8")) if failed_path.exists() else {}
    iterations.append({"iteration": i, "returncode": result.returncode, "failed_skills": failed, "stdout_tail": result.stdout[-4000:], "stderr_tail": result.stderr[-2000:]})
    if result.returncode == 0 and not failed:
        break
(OUT / "upgrade_iterations.json").write_text(json.dumps(iterations, ensure_ascii=False, indent=2), encoding="utf-8")
scores_path = OUT / "skill_scores.json"
if scores_path.exists():
    scores = json.loads(scores_path.read_text(encoding="utf-8"))
    lines = ["# Final 44 Skill Scorecard", ""] + [f"- {k}: {v['score']}/10" for k, v in scores.items()]
    (OUT / "final_44_skill_scorecard.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps(iterations[-1], ensure_ascii=False, indent=2))
sys.exit(iterations[-1]["returncode"])
