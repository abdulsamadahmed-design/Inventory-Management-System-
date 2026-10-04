import requests

BASE_URL = "http://127.0.0.1:5000"


def view_items():
    try:
        response = requests.get(
            f"{BASE_URL}/items",
            timeout=10
        )

        items = response.json()

        if not items:
            print("\nNo inventory items found.")
            return

        print("\n--- Inventory ---")

        for item in items:
            print(
                f"ID: {item['id']} | "
                f"Name: {item['name']} | "
                f"Quantity: {item['quantity']} | "
                f"Price: {item['price']}"
            )

    except requests.RequestException:
        print("Could not connect to the Flask API.")


def add_item():
    name = input("Name: ").strip()
    barcode = input("Barcode: ").strip()
    category = input("Category: ").strip()
    brand = input("Brand: ").strip()

    if not name:
        print("Name is required.")
        return

    try:
        quantity = int(input("Quantity: "))
        price = float(input("Price: "))

    except ValueError:
        print("Quantity and price must be numbers.")
        return

    data = {
        "name": name,
        "barcode": barcode,
        "category": category,
        "quantity": quantity,
        "price": price,
        "brand": brand
    }

    try:
        response = requests.post(
            f"{BASE_URL}/items",
            json=data,
            timeout=10
        )

        print(response.json())

    except requests.RequestException:
        print("Could not connect to the Flask API.")


def search_barcode():
    barcode = input("Enter barcode: ").strip()

    if not barcode:
        print("Barcode is required.")
        return

    try:
        response = requests.get(
            f"{BASE_URL}/external/barcode/{barcode}",
            timeout=10
        )

        print(response.json())

    except requests.RequestException:
        print("Could not connect to the Flask API.")


def import_product():
    barcode = input("Enter barcode: ").strip()

    if not barcode:
        print("Barcode is required.")
        return

    try:
        response = requests.post(
            f"{BASE_URL}/external/barcode/{barcode}/save",
            timeout=10
        )

        print(response.json())

    except requests.RequestException:
        print("Could not connect to the Flask API.")


def update_item():
    item_id = input("Enter item ID: ").strip()

    if not item_id.isdigit():
        print("Please enter a valid item ID.")
        return

    try:
        quantity = int(input("New quantity: "))
        price = float(input("New price: "))

    except ValueError:
        print("Quantity and price must be numbers.")
        return

    data = {
        "quantity": quantity,
        "price": price
    }

    try:
        response = requests.patch(
            f"{BASE_URL}/items/{item_id}",
            json=data,
            timeout=10
        )

        print(response.json())

    except requests.RequestException:
        print("Could not connect to the Flask API.")


def delete_item():
    item_id = input("Enter item ID: ").strip()

    if not item_id.isdigit():
        print("Please enter a valid item ID.")
        return

    try:
        response = requests.delete(
            f"{BASE_URL}/items/{item_id}",
            timeout=10
        )

        print(response.json())

    except requests.RequestException:
        print("Could not connect to the Flask API.")


def main():
    while True:
        print("\n=== Inventory Management System ===")
        print("1. View inventory")
        print("2. Add item")
        print("3. Search OpenFoodFacts")
        print("4. Import OpenFoodFacts product")
        print("5. Update item")
        print("6. Delete item")
        print("7. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            view_items()

        elif choice == "2":
            add_item()

        elif choice == "3":
            search_barcode()

        elif choice == "4":
            import_product()

        elif choice == "5":
            update_item()

        elif choice == "6":
            delete_item()

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please choose 1-7.")


if __name__ == "__main__":
    main()