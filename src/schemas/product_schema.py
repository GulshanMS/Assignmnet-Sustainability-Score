from marshmallow import Schema, fields, ValidationError, validates_schema

class ProductSchema(Schema):
    product_name = fields.Str(required=True)
    materials = fields.List(fields.Str(), required=True)
    weight_grams = fields.Int(required=False)
    transport = fields.Str(required=False)
    packaging = fields.Str(required=False)
    gwp = fields.Float(required=True)
    cost = fields.Float(required=True)
    circularity = fields.Float(required=True)

    # Optional weights override
    weights = fields.Dict(keys=fields.Str(), values=fields.Float(), required=False)

    @validates_schema
    def validate_values(self, data, **kwargs):
        # Circularity should be between 0 and 100
        circ = data.get("circularity")
        if circ is not None and not (0 <= circ <= 100):
            raise ValidationError("circularity must be between 0 and 100", field_name="circularity")

        # If weights provided, must include all and sum to 1
        if "weights" in data:
            w = data["weights"]
            if not {"gwp", "circularity", "cost"}.issubset(set(w.keys())):
                raise ValidationError("weights must include gwp, circularity, and cost")
            total = sum(float(w[k]) for k in ["gwp", "circularity", "cost"])
            if abs(total - 1.0) > 1e-6:
                raise ValidationError("weights must sum to 1.0")
