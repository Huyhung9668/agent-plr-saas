# PERFORMANCE REPORT — Web UI v1.12-speed

## Request Tests
- `GET /api/status`: PASS, `appVersion=v1.12-speed`, `defaultMode=fast`.
- `POST /api/route_skill`: PASS, `#market-pattern` routes to `skills/01_market_pattern_ai_printables.md`.
- `python scripts/test_skill_routing.py`: PASS.
- `POST /api/chat` FAST: PASS.
- `POST /api/chat` DEEP: PASS.
- `POST /api/chat_stream`: PASS, SSE emits `meta/status` events before answer text.

## Latency Results
| Test | Mode | Result | Wall Time | Backend Timing |
|---|---|---|---:|---|
| Market pattern short | FAST | PASS | 17.37s | route 0ms, load skill/brain 1ms, model 16602ms, source RAG 358ms, total 16976ms |
| Buyer test short | DEEP | PASS | 26.94s | route 0ms, load skill/brain 2ms, model 26548ms, source RAG 380ms, total 26942ms |

## What Changed
- Added FAST/BALANCED/DEEP topK map: FAST 6, BALANCED 12, DEEP 20.
- Default mode is now FAST, not AUTO/DEEP.
- Benchmark commands are explicit only: `/run_benchmark`, `/run_compare_codex55`, `/benchmark_20_rounds`, `/public_launch_audit_deep`.
- Normal chat no longer auto-infers benchmark for generic asset/product wording.
- Router, skill markdown, and brain files are cached in RAM by mtime/size.
- Skill context uses progressive disclosure: only routed skill + listed brain files are loaded.
- Skill/brain context limits were reduced to avoid loading huge markdown into every prompt.
- `/api/chat_stream` emits status events: routing/loading, RAG, calling model, finalizing.
- Chat requests append lightweight JSONL latency logs to `reports/chat_latency.jsonl`.
- UI mode selector now shows FAST/BALANCED/DEEP and defaults to FAST.
- Added FAST quick actions for Market Pattern, Buyer Test, and Product Blueprint.

## Bottleneck
The main bottleneck is still model generation time, not local routing/cache/RAG. In the measured FAST request, local route + skill/brain load was ~1ms and source RAG was ~358ms, while model time was ~16.6s.

## Next Speed Upgrade
- Add max-output-token caps per mode in `answer_master_question`/LLM call.
- For FAST mode, optionally skip post-answer source lookup or limit displayed sources to 3.
- Add a true `/api/chat_fast` template path for very short deterministic answers.
