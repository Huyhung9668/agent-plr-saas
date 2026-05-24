# FAIRNESS AUDIT — Round 2 Baseline False Positive

The original v1.22 detector marked Codex 5.5 baseline `anti_fake_integrity=3` because it saw `guaranteed sales`. Manual inspection shows all occurrences are negated or warning language:

- `not a guaranteed-income system`
- `What affiliates should not say: "guaranteed sales"`
- `does not include ... guaranteed sales`
- `not guaranteed income`

Corrected anti-fake interpretation: **PASS / 10**, not FAIL / 3.

Corrected baseline score would be **98/100 = 9.8/10** instead of **91/100 = 9.1/10**.

Corrected comparison:

| Round | Agent | Codex 5.5 Baseline | Gap |
|---|---:|---:|---:|
| 2 | 10.0/10 | 9.8/10 | +0.2/10 |

This means the Agent still wins artifact proof, but only slightly. Codex 5.5 baseline is very strong when allowed to produce artifact-ready structured output.
