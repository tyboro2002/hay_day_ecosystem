# exporters/csv_exporter.py
import os
import csv

from game_data import ITEMS, INFRASTRUCTURE, LIVESTOCK

def export_raw_structures():
    # Setup target directory
    export_dir = os.path.join("exports")
    os.makedirs(export_dir, exist_ok=True)

    print("=========================================================================")
    # =====================================================================
    # 1. EXPORT INFRASTRUCTURE (UPDATED)
    # =====================================================================
    infra_path = os.path.join(export_dir, "infrastructure.csv")
    infra_headers = ["Structure Name", "Structure Type", "Quantity Owned", "Products Made"]

    with open(infra_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(infra_headers)

        # Loop through categories: machines, pens, plant_structures, special_structures
        for cat_name, cat_dict in INFRASTRUCTURE.items():
            for struct_name, struct_obj in cat_dict.items():

                # A. Find Quantity Owned (Checking common attribute variants)
                quantity = 1
                for attr in ['amount_owned', 'amount', 'quantity', 'count', 'owned']:
                    if hasattr(struct_obj, attr):
                        quantity = getattr(struct_obj, attr)
                        break

                # B. Find everything this specific structure makes
                products = []
                for item_name, item_obj in ITEMS.items():
                    # Check standard machine links
                    if getattr(item_obj, 'machine', None) and item_obj.machine.name == struct_name:
                        products.append(item_name)
                    # Check livestock pen links
                    elif getattr(item_obj, 'pen', None) and item_obj.pen.name == struct_name:
                        products.append(item_name)

                # Fallbacks for unlinked edge cases
                if not products:
                    if struct_name == "Mine":
                        products = [n for n in ITEMS.keys() if "Ore" in n or n == "Coal"]
                    elif struct_name == "Fishing Lake":
                        products = ["Fish Filet"]

                products_str = ", ".join(products) if products else "None"

                writer.writerow([struct_name, cat_name, quantity, products_str])

    print(f" -> Exported: exports/infrastructure.csv")

    # =====================================================================
    # 2. EXPORT LIVESTOCK
    # =====================================================================
    livestock_path = os.path.join(export_dir, "livestock.csv")
    livestock_headers = ["Animal Name", "Pen", "Required Food", "Produces Item"]

    with open(livestock_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(livestock_headers)

        for name, animal_obj in LIVESTOCK.items():
            pen_name = animal_obj.pen.name if getattr(animal_obj, 'pen', None) else "None"
            food_name = animal_obj.required_food.name if getattr(animal_obj, 'required_food', None) else "None"
            produces_name = animal_obj.produces_item.name if getattr(animal_obj, 'produces_item', None) else "None"

            writer.writerow([name, pen_name, food_name, produces_name])

    print(f" -> Exported: exports/livestock.csv")

    # =====================================================================
    # 3. EXPORT ITEMS & RECIPES
    # =====================================================================
    items_path = os.path.join(export_dir, "items.csv")
    items_headers = ["Item Name", "Class Type", "Sell Price", "Time To Make (Mins)", "Source Machine/Structure", "Ingredients Needed"]

    with open(items_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(items_headers)

        for name, item_obj in ITEMS.items():
            class_type = type(item_obj).__name__
            sell_price = getattr(item_obj, 'sell_price', "N/A")
            time_to_make = getattr(item_obj, 'time_to_make', 0)

            # Resolve origin source machine
            source_machine = "None"
            if getattr(item_obj, 'machine', None):
                source_machine = item_obj.machine.name
            elif getattr(item_obj, 'pen', None):
                source_machine = item_obj.pen.name
            elif class_type == "SpecialItem" and ("Ore" in name or name == "Coal"):
                source_machine = "Mine"
            elif name in ["Fish Filet", "Fish Fillet"]:
                source_machine = "Fishing Lake"

            # Flatten ingredients dictionary {"Wheat Object": 2} -> "Wheat x2"
            ingredients_list = []
            if hasattr(item_obj, 'ingredients') and item_obj.ingredients:
                for ing_obj, qty in item_obj.ingredients.items():
                    ingredients_list.append(f"{ing_obj.name} x{qty}")
            ingredients_str = ", ".join(ingredients_list) if ingredients_list else "None"

            writer.writerow([name, class_type, sell_price, time_to_make, source_machine, ingredients_str])

    print(f" -> Exported: exports/items.csv")
    print("=========================================================================")
    print("Done! The raw blueprinted architecture of your ecosystem is exported.")

if __name__ == "__main__":
    export_raw_structures()