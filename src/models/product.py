from datetime import datetime
from src.app import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(256), nullable=False)
    materials = db.Column(db.String(512), nullable=False)  # JSON string
    weight_grams = db.Column(db.Integer)
    transport = db.Column(db.String(64))
    packaging = db.Column(db.String(128))
    gwp = db.Column(db.Float)
    cost = db.Column(db.Float)
    circularity = db.Column(db.Float)
    score = db.Column(db.Float)
    rating = db.Column(db.String(4))
    suggestions = db.Column(db.String(1024))  # JSON list as string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Product {self.product_name}>"
