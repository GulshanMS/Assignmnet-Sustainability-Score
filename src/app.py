# src/app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from datetime import datetime
import os, json
from schemas.product_schema import ProductSchema
from services.scoring import compute_score, rating_from_score, suggestions_for_product

# Absolute static path so running from src/ serves ../static correctly
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../products.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(256), nullable=False)
    materials = db.Column(db.String(512), nullable=False)
    weight_grams = db.Column(db.Integer)
    transport = db.Column(db.String(64))
    packaging = db.Column(db.String(128))
    gwp = db.Column(db.Float)
    cost = db.Column(db.Float)
    circularity = db.Column(db.Float)
    score = db.Column(db.Float)
    rating = db.Column(db.String(4))
    suggestions = db.Column(db.String(1024))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "product_name": self.product_name,
            "materials": json.loads(self.materials),
            "weight_grams": self.weight_grams,
            "transport": self.transport,
            "packaging": self.packaging,
            "gwp": self.gwp,
            "cost": self.cost,
            "circularity": self.circularity,
            "score": self.score,
            "rating": self.rating,
            "suggestions": json.loads(self.suggestions) if self.suggestions else [],
            "created_at": self.created_at.isoformat(),
        }

@app.route("/")
def index():
    # Serve the dashboard HTML
    return send_from_directory(STATIC_DIR, "index.html")

# API: validation
@app.route("/validate", methods=["POST"])
def validate_product():
    schema = ProductSchema()
    try:
        data = schema.load(request.get_json())
        return jsonify({"message": "Valid data", "data": data}), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

# API: score + persist
@app.route("/score", methods=["POST"])
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
        score=s, rating=r,
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

# API: history
@app.route("/history", methods=["GET"])
def history():
    try:
        limit = int(request.args.get("limit", 20))
    except Exception:
        limit = 20
    rows = Product.query.order_by(Product.created_at.desc()).limit(limit).all()
    return jsonify([r.to_dict() for r in rows]), 200

# API: summary
@app.route("/score-summary", methods=["GET"])
def score_summary():
    from collections import Counter
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
    trans_counts = Counter([(r.transport or "").strip().lower() for r in rows if r.transport])
    if trans_counts.get("air", 0) > 0:
        top_issues.append("Air transport")
    pack_counts = Counter([(r.packaging or "").strip().lower() for r in rows if r.packaging])
    if pack_counts:
        common_pack, _ = pack_counts.most_common(1)[0]
        if ("recycl" not in common_pack) and ("biodegrad" not in common_pack):
            top_issues.append("Non-recyclable packaging")

    return jsonify({
        "total_products": total,
        "average_score": round(avg, 2),
        "ratings": ratings,
        "top_issues": top_issues
    }), 200

if __name__ == "__main__":
    print("Serving static from:", STATIC_DIR)
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
