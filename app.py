from flask import Flask, jsonify, request
from models import db, InventoryItem

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def home():
    return jsonify({
        "message": "Inventory Management System API"
    })

@app.route("/items", methods=["GET"])
def get_items():
    items = InventoryItem.query.all()

    return jsonify([
        item.to_dict() for item in items
    ])

@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()

    new_item = InventoryItem(
        name=data["name"],
        barcode=data.get("barcode"),
        category=data.get("category"),
        quantity=data.get("quantity", 0),
        price=data.get("price", 0.0),
        brand=data.get("brand")
    )

    db.session.add(new_item)
    db.session.commit()

    return jsonify(new_item.to_dict()), 201

@app.route("/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = db.session.get(InventoryItem, item_id)

    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()

    if "name" in data:
        item.name = data["name"]

    if "barcode" in data:
        item.barcode = data["barcode"]

    if "category" in data:
        item.category = data["category"]

    if "quantity" in data:
        item.quantity = data["quantity"]

    if "price" in data:
        item.price = data["price"]

    if "brand" in data:
        item.brand = data["brand"]

    db.session.commit()

    return jsonify(item.to_dict())

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = db.session.get(InventoryItem, item_id)

    if not item:
        return jsonify({"error": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Item deleted successfully"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
