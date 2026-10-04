from flask import Flask, Blueprint, jsonify, request
from models import db, InventoryItem
import requests

bp = Blueprint("api", __name__)


def create_app(config=None):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if config:
        app.config.update(config)

    db.init_app(app)
    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()

    return app


@bp.route("/")
def home():
    return jsonify({
        "message": "Inventory Management System API"
    })


@bp.route("/items", methods=["GET"])
def get_items():
    items = InventoryItem.query.all()

    return jsonify([
        item.to_dict() for item in items
    ])


@bp.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = db.session.get(InventoryItem, item_id)

    if not item:
        return jsonify({
            "error": "Item not found"
        }), 404

    return jsonify(item.to_dict())


@bp.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()

    if not data or not data.get("name"):
        return jsonify({
            "error": "Name is required"
        }), 400

    barcode = data.get("barcode")

    if barcode:
        existing_item = InventoryItem.query.filter_by(
            barcode=barcode
        ).first()

        if existing_item:
            return jsonify({
                "error": "An item with this barcode already exists"
            }), 409

    new_item = InventoryItem(
        name=data["name"],
        barcode=barcode,
        category=data.get("category"),
        quantity=data.get("quantity", 0),
        price=data.get("price", 0.0),
        brand=data.get("brand")
    )

    db.session.add(new_item)
    db.session.commit()

    return jsonify(new_item.to_dict()), 201


@bp.route("/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = db.session.get(InventoryItem, item_id)

    if not item:
        return jsonify({
            "error": "Item not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No data provided"
        }), 400

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


@bp.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = db.session.get(InventoryItem, item_id)

    if not item:
        return jsonify({
            "error": "Item not found"
        }), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({
        "message": "Item deleted successfully"
    })


@bp.route("/external/barcode/<barcode>", methods=["GET"])
def get_external_product(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

    headers = {
        "User-Agent": "InventoryManagementSystem/1.0 (student-project)"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

    except requests.RequestException as error:
        return jsonify({
            "error": "Could not connect to OpenFoodFacts",
            "details": str(error)
        }), 503

    if response.status_code != 200:
        return jsonify({
            "error": "OpenFoodFacts request failed",
            "status_code": response.status_code
        }), 502

    try:
        data = response.json()

    except ValueError:
        return jsonify({
            "error": "OpenFoodFacts returned invalid data"
        }), 502

    if data.get("status") != 1:
        return jsonify({
            "error": "Product not found"
        }), 404

    product = data.get("product", {})

    return jsonify({
        "name": product.get("product_name", "Unknown product"),
        "barcode": barcode,
        "brand": product.get("brands", "Unknown brand"),
        "category": product.get("categories", "Unknown category")
    })


@bp.route("/external/barcode/<barcode>/save", methods=["POST"])
def save_external_product(barcode):
    existing_item = InventoryItem.query.filter_by(barcode=barcode).first()

    if existing_item:
        return jsonify({
            "error": "Product already exists in inventory"
        }), 409

    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"

    headers = {
        "User-Agent": "InventoryManagementSystem/1.0 (student-project)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
    except requests.RequestException:
        return jsonify({
            "error": "Could not connect to OpenFoodFacts"
        }), 503

    if response.status_code != 200 or data.get("status") != 1:
        return jsonify({
            "error": "Product not found"
        }), 404

    product = data.get("product", {})

    new_item = InventoryItem(
        name=product.get("product_name", "Unknown product"),
        barcode=barcode,
        brand=product.get("brands"),
        category=product.get("categories"),
        quantity=0,
        price=0.0
    )

    db.session.add(new_item)
    db.session.commit()

    return jsonify(new_item.to_dict()), 201


if __name__ == "__main__":
    create_app().run(debug=True)
    