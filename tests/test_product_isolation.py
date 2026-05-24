from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from product_pipeline import resolve_skill_route, slugify_project_name


def test_project_slug_isolation_names():
    product_a = slugify_project_name("AI Etsy Printable Bundle Builder")
    product_b = slugify_project_name("AI Coloring Page Niche Pack")
    assert product_a != product_b
    route = resolve_skill_route("Product: AI Coloring Page Niche Pack\n\nStep 17 Buyer Simulation Test")
    assert route["selected_skill"] == "17_buyer_simulation_test"
    assert "AI Etsy Printable Bundle Builder" not in str(route)
