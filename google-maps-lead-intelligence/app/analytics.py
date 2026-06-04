from collections import Counter

NEGATIVE_KEYWORDS = [
    # French
    "nul", "mauvais", "horrible", "décevant", "déçu", "sale", "lent",
    "incompétent", "arnaque", "escroquerie", "fermé", "indisponible",
    "impoli", "désagréable", "attente", "problème", "panne",
    "qualité médiocre", "pas professionnel", "cher pour rien",
    "pas recommandé", "à éviter", "très mauvais", "catastrophique",
    # English
    "terrible", "awful", "bad", "worst", "dirty", "slow", "rude",
    "scam", "fraud", "closed", "unavailable", "unprofessional",
    "disappointing", "poor quality", "overpriced", "broken",
    "long wait", "never again", "not recommended", "avoid",
    "waste of money", "horrible service", "do not go",
]


def detect_negative_keywords(text: str) -> list:
    text_lower = text.lower()
    found = []
    for kw in NEGATIVE_KEYWORDS:
        if kw in text_lower and kw not in found:
            found.append(kw)
    return found


def score_place(place: dict) -> dict:
    score = 0
    rating = place.get("rating")
    review_count = place.get("review_count") or 0
    neg_keywords = place.get("negative_keywords") or []

    if rating is not None and float(rating) < 3.8:
        score += 30
    if int(review_count) > 100:
        score += 20
    if neg_keywords:
        score += 25
    if place.get("phone"):
        score += 10
    if place.get("website"):
        score += 10

    if score >= 70:
        label = "High"
    elif score >= 40:
        label = "Medium"
    else:
        label = "Low"

    place["priority_score"] = score
    place["priority_label"] = label
    return place


def build_recommended_angle(keywords: list) -> str:
    if not keywords:
        return "Proposer un audit gratuit de réputation en ligne"

    kw_lower = [k.lower() for k in keywords]

    if any(k in kw_lower for k in ["lent", "attente", "slow", "long wait"]):
        return "Angle : Réduire les temps d'attente et améliorer la réactivité client"
    if any(k in kw_lower for k in ["sale", "dirty"]):
        return "Angle : Améliorer les standards d'hygiène et de propreté"
    if any(k in kw_lower for k in ["impoli", "rude", "désagréable"]):
        return "Angle : Formation au service client et à la relation client"
    if any(k in kw_lower for k in ["cher", "overpriced", "arnaque", "scam"]):
        return "Angle : Retravailler l'offre tarifaire et la communication de valeur"
    if any(k in kw_lower for k in ["qualité", "quality", "poor", "mauvais"]):
        return "Angle : Mettre en avant les garanties qualité et certifications"
    if any(k in kw_lower for k in ["incompétent", "unprofessional"]):
        return "Angle : Valoriser les compétences et parcours de l'équipe"

    return "Angle : Proposer une stratégie de gestion des avis négatifs"


def compute_analytics(places: list) -> dict:
    if not places:
        return {
            "total": 0,
            "high_priority": 0,
            "avg_rating": 0,
            "top_keywords": [],
            "by_industry": {},
        }

    high_priority = sum(1 for p in places if p.get("priority_label") == "High")

    ratings = [float(p["rating"]) for p in places if p.get("rating") is not None]
    avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0

    all_keywords = []
    for p in places:
        all_keywords.extend(p.get("negative_keywords") or [])
    top_keywords = [kw for kw, _ in Counter(all_keywords).most_common(10)]

    by_industry: dict = {}
    for p in places:
        ind = p.get("industry") or "Unknown"
        if ind not in by_industry:
            by_industry[ind] = {"count": 0, "high": 0, "medium": 0, "low": 0}
        by_industry[ind]["count"] += 1
        label = (p.get("priority_label") or "low").lower()
        if label in by_industry[ind]:
            by_industry[ind][label] += 1

    return {
        "total": len(places),
        "high_priority": high_priority,
        "avg_rating": avg_rating,
        "top_keywords": top_keywords,
        "by_industry": by_industry,
    }
