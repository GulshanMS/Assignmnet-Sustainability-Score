from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from collections import Counter
import json

from schemas.product_schema import ProductSchema
from services.scoring import compute_score, rating_from_score, suggestions_for_product
from models.product import db, Product

api = Blueprint("api", __name__)

@api.route("/validate", methods=["POST"])
def validate_product():
    schema = ProductSchema()
    try:
        data = schema.load(request.get_json())
        return jsonify({"message": "Valid data", "data": data}), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400


@api.route("/score", methods=["POST"])
def score():
    schema = ProductSchema()
    try:
        payload = schema.load(request.get_json(force=True))
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    weights = payload.get("weights")
    s = compute_score(payload, weights)
    r = rating_from_score(s)
    sugg = suggestions_for_product(payload)

    row = Product(
        product_name=payload["product_name"],
        materials=json.dumps(payload.get("materials", [])),
        weight_grams=payload.get("weight_grams"),
        transport=payload.get("transport"),
        packaging=payload.get("packaging"),
        gwp=float(payload.get("gwp")),
        cost=float(payload.get("cost")),
        circularity=float(payload.get("circularity")),
        score=s,
        rating=r,
        suggestions=json.dumps(sugg),
    )
    db.session.add(row)
    db.session.commit()

    return jsonify({
        "product_name": payload["product_name"],
        "sustainability_score": s,
        "rating": r,
        "suggestions": sugg
    }), 201


@api.route("/history", methods=["GET"])
def history():
    try:
        limit = int(request.args.get("limit", 20))
    except Exception:
        limit = 20
    rows = Product.query.order_by(Product.created_at.desc()).limit(limit).all()
    return jsonify([r.to_dict() for r in rows]), 200


@api.route("/score-summary", methods=["GET"])
def score_summary():
    rows = Product.query.all()
    total = len(rows)
    if total == 0:
        return jsonify({
            "total_products": 0,
            "average_score": 0.0,
            "ratings": {"A": 0, "B": 0, "C": 0, "D": 0},
            "top_issues": [],
        }), 200

    avg = sum(r.score for r in rows) / total
    ratings = {"A": 0, "B": 0, "C": 0, "D": 0}
    for r in rows:
        ratings[r.rating] = ratings.get(r.rating, 0) + 1

    mat_counter = Counter()
    for r in rows:
        try:
            for m in json.loads(r.materials):
                mat_counter[m.strip().lower()] += 1
        except Exception:
            pass

    top_issues = []
    for mat, _ in mat_counter.most_common(3):
        if "plastic" in mat:
            top_issues.append("Plastic used")
            break

    return jsonify({
        "total_products": total,
        "average_score": round(avg, 2),
        "ratings": ratings,
        "top_issues": top_issues
    }), 200
