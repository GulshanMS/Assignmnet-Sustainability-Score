from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from schemas.product_schema import ProductSchema   # <-- new import

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../products.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

@app.route("/")
def home():
    return "Database + Schema setup ready ✅"

@app.route("/validate", methods=["POST"])
def validate_product():
    schema = ProductSchema()
    try:
        data = schema.load(request.get_json())
        return jsonify({"message": "Valid data", "data": data}), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
