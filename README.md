# Inventory Management System

A Flask REST API and command-line application for managing a retail inventory. Employees can add, view, edit and delete items, and look up product details from the OpenFoodFacts API by barcode.

Built as a Python REST API summative project.

## Features

- Full CRUD for inventory items (create, read, update, delete)
- Look up a product by barcode on OpenFoodFacts
- Import an OpenFoodFacts product straight into the inventory
- Menu-driven command-line interface that talks to the API
- Automated tests with pytest (external API calls are mocked, so tests never use the internet)

## Technologies

- Python 3
- Flask and Flask-SQLAlchemy
- SQLite (the database file is created automatically)
- Requests
- Pytest
- OpenFoodFacts API

## Project structure

```
app.py             Flask app factory and API routes
models.py          InventoryItem database model
cli.py             Command-line interface
tests/
  conftest.py      Shared test fixtures (in-memory database)
  test_app.py      Tests for the CRUD routes
  test_external.py Tests for the OpenFoodFacts routes (mocked)
requirements.txt   Python dependencies
```

## Installation

1. Clone the repository and move into it:

   ```bash
   git clone https://github.com/abdulsamadahmed-design/Inventory-Management-System-.git
   cd Inventory-Management-System-
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the API

```bash
python app.py
```

The API runs at `http://127.0.0.1:5000`. The SQLite database (`instance/inventory.db`) is created on first start. Leave this terminal running.

## Using the CLI

The CLI sends requests to the API, so **the API must already be running**. Open a second terminal, activate the virtual environment, then run:

```bash
python cli.py
```

Menu options:

| Option | Action |
|---|---|
| 1 | View inventory |
| 2 | Add item |
| 3 | Search OpenFoodFacts by barcode |
| 4 | Import an OpenFoodFacts product into the inventory |
| 5 | Update an item's quantity and price |
| 6 | Delete an item |
| 7 | Exit |

## API endpoints

| Method | URL | What it does |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/items` | List all items |
| GET | `/items/<id>` | Get one item (404 if not found) |
| POST | `/items` | Create an item (`name` required; 409 if the barcode already exists) |
| PATCH | `/items/<id>` | Update any of the item's fields |
| DELETE | `/items/<id>` | Delete an item |
| GET | `/external/barcode/<barcode>` | Look up a product on OpenFoodFacts (does not save it) |
| POST | `/external/barcode/<barcode>/save` | Fetch a product from OpenFoodFacts and add it to the inventory |

An item has these fields: `id`, `name`, `barcode`, `category`, `quantity`, `price`, `brand`.

Example: create an item.

```bash
curl -X POST http://127.0.0.1:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Sugar", "barcode": "123456", "quantity": 5, "price": 100}'
```

Imported OpenFoodFacts products are saved with a quantity of 0 and a price of 0.0, because OpenFoodFacts does not provide stock or price. Update them afterwards with `PATCH /items/<id>` or CLI option 5.

## Running the tests

```bash
pytest
```

Tests run against an in-memory database, so they never touch your real inventory. The OpenFoodFacts calls are replaced with fakes, so no internet connection is needed.

## Known limitations

- Product lookup works by barcode only (not by product name).
- The CLI has no automated tests.
- Input validation is minimal: quantity and price are not checked for sensible values.
- Adding several items with a blank barcode through the API or CLI can fail, because barcodes must be unique.