from __future__ import annotations

import json
import urllib.request

BASE = "http://127.0.0.1:18088"
CASES = [
    ("#ai-printables-kdp-prompt #market-pattern", "skills/01_market_pattern_ai_printables.md"),
    ("#ai-printables-kdp-prompt #buyer-test", "skills/07_buyer_test_ai_printables.md"),
    ("#ai-printables-kdp-prompt #export-zip", "skills/15_export_zip_ai_printables.md"),
]


def get(path: str) -> dict:
    with urllib.request.urlopen(BASE + path, timeout=15) as res:
        return json.loads(res.read().decode("utf-8"))


def post(path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.loads(res.read().decode("utf-8"))


def main() -> None:
    status = get("/api/status")
    agent = status.get("aiPrintablesKdpPromptAgent", {})
    assert status.get("ok"), "status ok failed"
    assert agent.get("brain") == "FOUND" or agent.get("brainFound") is True, f"brain not found: {agent}"
    assert agent.get("skills") == "16/16", f"skills not 16/16: {agent}"
    assert agent.get("tags") == "READY" or agent.get("tagsReady") is True, f"tags not ready: {agent}"
    assert agent.get("router") == "READY" or agent.get("routerReady") is True, f"router not ready: {agent}"
    tags = get("/api/skill_tags")
    assert tags.get("ok") and len(tags.get("tags", [])) >= 17, "skill tags incomplete"
    for message, expected in CASES:
        payload = {"message": message + " test", "tags": message.split()}
        route = post("/api/route_skill", payload)
        assert route.get("ok"), route
        assert route.get("skillFile") == expected, f"{message}: {route.get('skillFile')} != {expected}"
    print("skill routing tests PASS")


if __name__ == "__main__":
    main()

