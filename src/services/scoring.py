# src/services/scoring.py

def _clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))

def _normalize_cost(cost, max_cost=100.0):
    # Lower cost → higher score (0–100)
    if max_cost <= 0:
        return 0.0
    return _clamp(100.0 * max(0.0, 1.0 - float(cost) / float(max_cost)))

def _normalize_gwp(gwp, max_gwp=50.0):
    # Lower GWP → higher score (0–100)
    if max_gwp <= 0:
        return 0.0
    return _clamp(100.0 * max(0.0, 1.0 - float(gwp) / float(max_gwp)))

def _normalize_circularity(circ):
    # Already a 0–100 style metric
    return _clamp(float(circ))

def compute_score(data, weights=None, gwp_max=50.0, cost_max=100.0):
    weights = weights or {"gwp": 0.5, "circularity": 0.3, "cost": 0.2}
    w_gwp = float(weights.get("gwp", 0.5))
    w_circ = float(weights.get("circularity", 0.3))
    w_cost = float(weights.get("cost", 0.2))
    w_sum = w_gwp + w_circ + w_cost
    if w_sum <= 0:
        w_gwp, w_circ, w_cost, w_sum = 1.0, 1.0, 1.0, 3.0

    s_gwp = _normalize_gwp(data.get("gwp", 0.0), gwp_max)
    s_circ = _normalize_circularity(data.get("circularity", 0.0))
    s_cost = _normalize_cost(data.get("cost", 0.0), cost_max)

    score = (w_gwp * s_gwp + w_circ * s_circ + w_cost * s_cost) / w_sum
    return round(score, 1)

def rating_from_score(score):
    s = float(score)
    if s >= 85.0:
        return "A"
    if s >= 70.0:
        return "B"
    if s >= 55.0:
        return "C"
    return "D"

def suggestions_for_product(data):
    tips = []
    transport = (data.get("transport") or "").strip().lower()
    packaging = (data.get("packaging") or "").strip().lower()
    materials = [m.strip().lower() for m in data.get("materials", [])]
    gwp = float(data.get("gwp", 0.0))
    circ = float(data.get("circularity", 0.0))

    if transport == "air":
        tips.append("Avoid air transport; prefer sea/rail/optimized road")
    if "plastic" in materials:
        tips.append("Reduce plastic; increase recycled or bio-based content")
    if packaging and ("recycl" not in packaging and "biodegrad" not in packaging):
        tips.append("Switch to recyclable or biodegradable packaging")
    if gwp > 10.0:
        tips.append("Reduce embodied carbon via material or process changes")
    if circ < 60.0:
        tips.append("Improve circularity via design for repair/reuse/recycling")

    # Deduplicate and cap to keep responses concise
    dedup = []
    for t in tips:
        if t not in dedup:
            dedup.append(t)
    return dedup[:5]
