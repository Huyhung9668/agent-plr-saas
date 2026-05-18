from __future__ import annotations

import json
from pathlib import Path

from config import PLR_DIR
from file_reader import PLRFile, read_plr_file, scan_plr_folder
from llm_client import analyze_with_llm, has_api_key
from scoring import heuristic_analysis


def scan_library(root: Path = PLR_DIR) -> list[Path]:
    return scan_plr_folder(root)


def analyze_product(path: Path, use_ai: bool = True) -> dict:
    product = read_plr_file(path)
    if use_ai and has_api_key():
        try:
            return analyze_with_llm(_product_context(product))
        except Exception as error:
            print(f"AI analysis failed for {path.name}. Falling back to heuristic. Error: {error}")
    return heuristic_analysis(product)


def analyze_library(root: Path = PLR_DIR, use_ai: bool = True) -> list[dict]:
    paths = scan_library(root)
    results = []
    for index, path in enumerate(paths, start=1):
        print(f"[{index}/{len(paths)}] Analyzing {path.name}")
        result = analyze_product(path, use_ai=use_ai)
        result["source_path"] = str(path)
        results.append(result)
    return sorted(results, key=lambda item: item.get("final_score", 0), reverse=True)


def analysis_to_json(results: list[dict]) -> str:
    return json.dumps(results, ensure_ascii=False, indent=2)


def _product_context(product: PLRFile) -> str:
    return f"""
Title: {product.title}
File type: {product.file_type}
Folder: {product.folder}
License hint: {product.license_hint}
Path: {product.path}

Content excerpt:
{product.text}
"""
