from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    barcode = db.Column(db.String(50), unique=True)
    category = db.Column(db.String(100))
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0.0)
    brand = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "barcode": self.barcode,
            "category": self.category,
            "quantity": self.quantity,
            "price": self.price,
            "brand": self.brand
        }
    
    
   