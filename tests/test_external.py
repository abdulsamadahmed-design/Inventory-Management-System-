import requests

from models import db, InventoryItem

GOOD_PAYLOAD = {
    "status": 1,
    "product": {
        "product_name": "Test Cola",
        "brands": "Acme",
        "categories": "Drinks",
    },
}


class FakeResponse:
    """Stands in for the object requests.get() returns."""

    def __init__(self, status_code=200, payload=None, bad_json=False):
        self.status_code = status_code
        self.payload = payload
        self.bad_json = bad_json

    def json(self):
        if self.bad_json:
            raise ValueError("not valid JSON")
        return self.payload


def fake_get(response=None, error=None):
    """Build a replacement for requests.get that returns or raises on demand."""

    def _get(*args, **kwargs):
        if error:
            raise error
        return response

    return _get


# ---------- GET /external/barcode/<barcode> ----------

def test_lookup_success(client, monkeypatch):
    monkeypatch.setattr(
        "app.requests.get",
        fake_get(FakeResponse(200, GOOD_PAYLOAD)),
    )

    response = client.get("/external/barcode/12345")

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Test Cola"
    assert data["brand"] == "Acme"
    assert data["barcode"] == "12345"


def test_lookup_product_not_found(client, monkeypatch):
    monkeypatch.setattr(
        "app.requests.get",
        fake_get(FakeResponse(200, {"status": 0})),
    )

    response = client.get("/external/barcode/00000")

    assert response.status_code == 404


def test_lookup_connection_failure(client, monkeypatch):
    monkeypatch.setattr(
        "app.requests.get",
        fake_get(error=requests.ConnectionError("network down")),
    )

    response = client.get("/external/barcode/12345")

    assert response.status_code == 503


def test_lookup_upstream_error_status(client, monkeypatch):
    monkeypatch.setattr(
        "app.requests.get",
        fake_get(FakeResponse(500, {})),
    )

    response = client.get("/external/barcode/12345")

    assert response.status_code == 502


def test_lookup_invalid_json(client, monkeypatch):
    monkeypatch.setattr(
        "app.requests.get",
        fake_get(FakeResponse(200, bad_json=True)),
    )

    response = client.get("/external/barcode/12345")

    assert response.status_code == 502


# ---------- POST /external/barcode/<barcode>/save ----------

def test_save_success(client, app, monkeypatch):
    monkeypatch.setattr(
        "app.requests.get",
        fake_get(FakeResponse(200, GOOD_PAYLOAD)),
    )

    response = client.post("/external/barcode/12345/save")

    assert response.status_code == 201
    assert response.get_json()["name"] == "Test Cola"

    with app.app_context():
        saved = InventoryItem.query.filter_by(barcode="12345").first()
        assert saved is not None
        assert saved.brand == "Acme"


def test_save_duplicate_barcode(client, monkeypatch):
    monkeypatch.setattr(
        "app.requests.get",
        fake_get(FakeResponse(200, GOOD_PAYLOAD)),
    )

    client.post("/items", json={"name": "Existing", "barcode": "12345"})
    response = client.post("/external/barcode/12345/save")

    assert response.status_code == 409


def test_save_product_not_found(client, monkeypatch):
    monkeypatch.setattr(
        "app.requests.get",
        fake_get(FakeResponse(200, {"status": 0})),
    )

    response = client.post("/external/barcode/00000/save")

    assert response.status_code == 404


def test_save_connection_failure(client, monkeypatch):
    monkeypatch.setattr(
        "app.requests.get",
        fake_get(error=requests.ConnectionError("network down")),
    )

    response = client.post("/external/barcode/12345/save")

    assert response.status_code == 503