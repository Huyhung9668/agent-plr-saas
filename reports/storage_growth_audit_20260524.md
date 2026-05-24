# Storage Growth Audit — 2026-05-24

## Finding
Project size looks ~12GB mainly because `input_files` contains both the original compressed ZIP and the extracted copy.

## Main Size Sources
| Path | Size | Note |
|---|---:|---|
| `input_files/AI Printables KDP Promt Skill.zip` | ~5.23 GB | Original archive kept in project |
| `input_files/AI Printables KDP Promt Skill/` | ~5.24 GB | Extracted copy of same archive |
| `input_files/AI Printables KDP Promt Skill/_RECOVERED_3500_20260522/First_Class_Travel_Secrets_SLENDERMAN_BBHF.zip` | ~4.42 GB | Largest recovered ZIP inside extracted folder |
| `input_files/AI Printables KDP Promt Skill/_RECOVERED_3500_20260522/BowesPublishing_Content_Creation_Tools_For_KDP_Printables_POD_Etsy_Creators_SM_BBHF.zip` | ~562 MB | Recovered ZIP |
| `database/` | ~1.18 GB | Brain sqlite/db archives |
| `agents/` | ~0.14 MB | Agent/brain/skills are tiny |
| `benchmarks/` | ~0.40 MB | Benchmark logs tiny |
| `exports/` | ~0.29 MB | Export artifacts tiny |
| `chat_history/` | ~0.47 MB | Chat history tiny |

## Conclusion
The Agent system did not grow to 12GB. The size is from input archives and extracted recovered files.

## Why It Doubled
`AI Printables KDP Promt Skill.zip` (~5.23GB) and its extracted folder (~5.24GB) are both present. That alone is ~10.47GB.

## Safe Cleanup Options
1. Keep extracted folder, move original ZIP outside project to backup drive.
2. Keep original ZIP, delete extracted folder only after brain/source map has been verified and backup exists.
3. Move the giant unrelated recovered ZIP `First_Class_Travel_Secrets_SLENDERMAN_BBHF.zip` out of this AI Printables folder if it is not needed for this agent.

## Do Not Delete Automatically
No files were deleted by this audit.
