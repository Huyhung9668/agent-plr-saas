from __future__ import annotations


def build_license_risk_audit(results: list[dict]) -> str:
    unknown = [item for item in results if item.get("license_type") == "Unknown"]
    high_risk = [item for item in results if int(item.get("risk_score", 0) or 0) >= 7]
    top = sorted(results, key=lambda item: item.get("final_score", 0), reverse=True)[:10]

    lines = [
        "# License And Risk Audit",
        "",
        f"Total products: {len(results)}",
        f"Unknown license: {len(unknown)}",
        f"High risk: {len(high_risk)}",
        "",
        "## Top Opportunities",
        "",
    ]

    for item in top:
        lines.extend(
            [
                f"### {item.get('original_title', 'Untitled')}",
                f"- Final score: {item.get('final_score')}/10",
                f"- License: {item.get('license_type')}",
                f"- Risk score: {item.get('risk_score')}/10",
                f"- Recommended action: {item.get('recommended_action')}",
                "",
            ]
        )

    lines.extend(["## Needs License Check", ""])
    if unknown:
        for item in unknown:
            lines.append(f"- {item.get('original_title')} | {item.get('source_path', '')}")
    else:
        lines.append("- None")

    lines.extend(["", "## High Risk Items", ""])
    if high_risk:
        for item in high_risk:
            lines.append(f"- {item.get('original_title')} | Risk: {item.get('risk')} | {item.get('source_path', '')}")
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Rules Before Publishing",
            "",
            "- Do not sell unchanged PLR when the license is unclear.",
            "- Rewrite hype, income claims, health claims, and outdated tactics.",
            "- Add original templates, examples, checklists, prompts, or workflows.",
            "- Keep a copy of the license file beside each product source.",
        ]
    )
    return "\n".join(lines)
