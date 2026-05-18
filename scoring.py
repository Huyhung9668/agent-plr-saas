KEYWORDS = {
    "AI / Make Money": ["chatgpt", "ai", "prompt", "automation", "make money", "income"],
    "Marketing": ["marketing", "affiliate", "email", "traffic", "funnel", "sales page"],
    "Planner": ["planner", "journal", "tracker", "checklist", "printable"],
    "Etsy": ["etsy", "printable", "digital download", "template"],
    "Self Help": ["self help", "mindset", "confidence", "habits", "productivity"],
    "Health": ["health", "fitness", "weight loss", "diet", "wellness"],
    "Kids Story": ["kids", "children", "story", "coloring", "activity book"],
    "Business": ["business", "startup", "entrepreneur", "clients", "agency"],
}


def heuristic_analysis(product) -> dict:
    combined = f"{product.title} {product.folder} {product.text}".lower()
    category = _detect_category(combined)
    product_type = _detect_product_type(product.file_type, combined)

    demand = _score_by_terms(combined, ["ai", "chatgpt", "marketing", "affiliate", "etsy", "template"])
    warriorplus_fit = _score_by_terms(combined, ["ai", "make money", "affiliate", "traffic", "funnel", "marketing"])
    rebrand = _score_by_terms(combined, ["template", "checklist", "guide", "prompt", "planner", "bundle"])
    saas = _score_by_terms(combined, ["generator", "template", "prompt", "automation", "calendar", "planner", "content", "email", "sales page"])
    ease = 8 if product.file_type in {"txt", "md", "docx", "pdf"} else 6
    backend = _score_by_terms(combined, ["course", "bundle", "agency", "license", "templates", "software"])
    risk = _risk_score(combined, product.license_hint)
    freshness = _freshness_score(combined)

    final_score = (
        demand * 0.25
        + warriorplus_fit * 0.25
        + rebrand * 0.20
        + saas * 0.15
        + ease * 0.10
        - risk * 0.05
    )

    new_name = _suggest_name(category)

    return {
        "original_title": product.title,
        "category": category,
        "product_type": product_type,
        "license_type": product.license_hint,
        "freshness_score": freshness,
        "demand_score": demand,
        "warriorplus_fit_score": warriorplus_fit,
        "rebrand_potential_score": rebrand,
        "saas_potential_score": saas,
        "ease_of_creation_score": ease,
        "backend_potential_score": backend,
        "risk_score": risk,
        "final_score": round(final_score, 2),
        "best_angle": _best_angle(category),
        "buyer_avatar": _buyer_avatar(category),
        "promise": _promise(category),
        "recommended_action": f"Rebrand thanh {new_name}",
        "risk": _risk_note(risk, product.license_hint),
        "bonus_ideas": ["7-day checklist", "headline templates", "email swipe pack"],
        "oto_ideas": ["Done-for-you bundle builder", "Agency license pack"],
        "sales_page_angle": _sales_angle(category),
        "saas_angle": _saas_angle(category),
        "traffic_angle": "Affiliate launch, short-form content, email list, and WarriorPlus marketplace.",
        "notes": "Khong ban nguyen ban. Dung PLR lam nen, viet lai angle va bo sung tai nguyen moi.",
    }


def _detect_category(text: str) -> str:
    scores = {
        category: sum(1 for keyword in keywords if keyword in text)
        for category, keywords in KEYWORDS.items()
    }
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "General Digital Product"


def _detect_product_type(file_type: str, text: str) -> str:
    if "prompt" in text:
        return "prompt pack"
    if "planner" in text or "journal" in text:
        return "planner"
    if "checklist" in text:
        return "checklist"
    if "video" in text or "module" in text:
        return "video course"
    if file_type == "zip":
        return "bundle"
    if file_type in {"pdf", "docx", "txt", "md"}:
        return "ebook"
    return "digital asset"


def _score_by_terms(text: str, terms: list[str]) -> int:
    matches = sum(1 for term in terms if term in text)
    return max(3, min(10, 4 + matches))


def _risk_score(text: str, license_hint: str) -> int:
    risk = 3
    risky_terms = ["guaranteed income", "instant profits", "blackhat", "hack", "spam"]
    risk += sum(2 for term in risky_terms if term in text)
    if license_hint == "Unknown":
        risk += 2
    if "health" in text or "weight loss" in text:
        risk += 1
    return min(10, risk)


def _freshness_score(text: str) -> int:
    if any(term in text for term in ["chatgpt", "ai", "automation", "2025", "2026"]):
        return 8
    if any(term in text for term in ["facebook ads", "seo", "email marketing", "etsy"]):
        return 6
    return 5


def _suggest_name(category: str) -> str:
    names = {
        "AI / Make Money": "AI Product Sprint Kit",
        "Marketing": "Affiliate Offer Launch Kit",
        "Planner": "Digital Planner Profit Pack",
        "Etsy": "Etsy Digital Product Starter Kit",
        "Self Help": "7-Day Productivity Reset Kit",
        "Health": "Wellness Content Starter Pack",
        "Kids Story": "Kids Storybook Creator Kit",
        "Business": "Micro Business Launch Kit",
    }
    return names.get(category, "Digital Product Starter Kit")


def _best_angle(category: str) -> str:
    return {
        "AI / Make Money": "AI side-product guide for beginners",
        "Marketing": "simple launch assets for affiliate marketers",
        "Planner": "printable and digital planner bundle for niche sellers",
        "Etsy": "ready-to-customize digital download starter system",
    }.get(category, "turn existing PLR into a focused 7-day digital product offer")


def _buyer_avatar(category: str) -> str:
    if category == "AI / Make Money":
        return "Nguoi moi muon dung AI de tao san pham so nho."
    if category == "Marketing":
        return "Affiliate marketer can tai nguyen launch nhanh."
    return "Nguoi ban san pham so muon co offer gon, de lam, de ban."


def _promise(category: str) -> str:
    if category == "AI / Make Money":
        return "Tao san pham so dau tien trong 7 ngay bang AI, khong can code."
    return "Bien tai nguyen PLR thanh offer moi co the ban trong 7 ngay."


def _sales_angle(category: str) -> str:
    if category == "AI / Make Money":
        return "Stop guessing what to sell. Use AI to turn simple assets into a sellable product in 7 days."
    return "Turn dusty PLR into a focused digital product offer with assets, bonuses, and a launch plan."


def _saas_angle(category: str) -> str:
    if category == "AI / Make Money":
        return "PLR Rebrand Engine: upload PLR, generate a new offer, sales page, bonuses, and launch emails."
    if category == "Marketing":
        return "Campaign Builder: generate funnels, email swipes, and affiliate assets from a niche and offer."
    if category == "Planner":
        return "Planner Generator: create printable planner packs, prompts, covers, and listing copy."
    if category == "Etsy":
        return "Etsy Digital Download Builder: generate product ideas, listing copy, tags, and bundle plans."
    return "Digital Product Builder: turn content assets into offer packs, launch assets, and exportable reports."


def _risk_note(risk: int, license_hint: str) -> str:
    if license_hint == "Unknown":
        return "License chua ro, can kiem tra file rights truoc khi ban."
    if risk >= 7:
        return "Can viet lai de tranh claim qua da hoac noi dung nhay cam."
    return "Rui ro thap neu rebrand va bo sung gia tri moi."
