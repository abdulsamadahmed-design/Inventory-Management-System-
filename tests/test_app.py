from models import db, InventoryItem


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["message"] == \
        "Inventory Management System API"


def test_get_empty_inventory(client):
    response = client.get("/items")

    assert response.status_code == 200
    assert response.get_json() == []


def test_create_item(client):
    data = {
        "name": "Sugar",
        "barcode": "123456",
        "category": "Food",
        "quantity": 5,
        "price": 100,
        "brand": "Test Brand"
    }

    response = client.post("/items", json=data)

    assert response.status_code == 201

    item = response.get_json()

    assert item["name"] == "Sugar"
    assert item["quantity"] == 5
    assert item["price"] == 100


def test_get_item(client, app):
    item = InventoryItem(
        name="Salt",
        barcode="111111",
        quantity=3,
        price=50
    )

    with app.app_context():
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    response = client.get(f"/items/{item_id}")

    assert response.status_code == 200
    assert response.get_json()["name"] == "Salt"


def test_update_item(client, app):
    item = InventoryItem(
        name="Milk",
        barcode="222222",
        quantity=2,
        price=80
    )

    with app.app_context():
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    response = client.patch(
        f"/items/{item_id}",
        json={
            "quantity": 10,
            "price": 120
        }
    )

    assert response.status_code == 200

    updated_item = response.get_json()

    assert updated_item["quantity"] == 10
    assert updated_item["price"] == 120


def test_delete_item(client, app):
    item = InventoryItem(
        name="Bread",
        barcode="333333",
        quantity=4,
        price=60
    )

    with app.app_context():
        db.session.add(item)
        db.session.commit()
        item_id = item.id

    response = client.delete(f"/items/{item_id}")

    assert response.status_code == 200
    assert response.get_json()["message"] == \
        "Item deleted successfully"


def test_missing_item(client):
    response = client.get("/items/999")

    assert response.status_code == 404


def test_create_item_without_name(client):
    response = client.post(
        "/items",
        json={
            "quantity": 5,
            "price": 100
        }
    )

    assert response.status_code == 400


def test_duplicate_barcode(client):
    data = {
        "name": "Product One",
        "barcode": "999999",
        "quantity": 1,
        "price": 50
    }

    first_response = client.post("/items", json=data)
    second_response = client.post("/items", json=data)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    