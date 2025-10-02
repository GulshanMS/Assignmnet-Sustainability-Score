from datetime import datetime
from sqlalchemy import Integer, String, Float, DateTime
import json

from models import db   # ✅ import db from models.__init__

class Product(db.Model):
    id = db.Column(Integer, primary_key=True)
    product_name = db.Column(String(256), nullable=False)
    materials = db.Column(String(512), nullable=False)   # JSON string
    weight_grams = db.Column(Integer)
    transport = db.Column(String(64))
    packaging = db.Column(String(128))
    gwp = db.Column(Float)
    cost = db.Column(Float)
    circularity = db.Column(Float)
    score = db.Column(Float)
    rating = db.Column(String(4))
    suggestions = db.Column(String(1024))                # JSON list as string
    created_at = db.Column(DateTime, default=datetime.utcnow)

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
