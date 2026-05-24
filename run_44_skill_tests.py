from pathlib import Path
import importlib.util
import sys
import traceback

ROOT = Path(__file__).resolve().parent
TESTS = [
    "tests/test_product_routes.py",
    "tests/test_skill_router.py",
    "tests/test_skill_quality.py",
    "tests/test_product_isolation.py",
    "tests/test_ai_api_required.py",
    "tests/test_44_skill_prompts.py",
]

def load_module(path: Path):
    name = path.stem + "_standalone"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

failures = []
for rel in TESTS:
    path = ROOT / rel
    module = load_module(path)
    for name in sorted(dir(module)):
        if not name.startswith("test_"):
            continue
        fn = getattr(module, name)
        if not callable(fn):
            continue
        try:
            fn()
            print(f"PASS {rel}::{name}")
        except Exception as exc:
            failures.append(f"{rel}::{name}: {exc}")
            print(f"FAIL {rel}::{name}")
            traceback.print_exc()
if failures:
    print("\nFAILURES:")
    for failure in failures:
        print("-", failure)
    sys.exit(1)
print("\nALL TESTS PASSED")
