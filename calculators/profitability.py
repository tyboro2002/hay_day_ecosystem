import os
import csv
from game_data import ITEMS, LIVESTOCK, INFRASTRUCTURE
from game_data.game_data import DIAMOND_COST


def find_animal_food_for_item(item_name):
    """Scans the LIVESTOCK registry to get the Feed item required for an animal."""
    for animal_name, animal_obj in LIVESTOCK.items():
        if animal_obj.produces_item and animal_obj.produces_item.name == item_name:
            if animal_obj.required_food:
                return animal_obj.required_food
    return None

def find_structure_for_plantable(item_name):
    """Scans INFRASTRUCTURE['plant_structures'] to match an item to its tree/bush."""
    plant_dict = INFRASTRUCTURE.get('plant_structures', INFRASTRUCTURE.get('structures', {}))
    for struct_name, struct_obj in plant_dict.items():
        # Maps 'Apple' to 'Apple Tree', 'Raspberry' to 'Raspberry Bush', etc.
        if item_name in struct_name:
            return struct_obj
    return None

def calculate_direct_ingredient_cost(item_obj):
    """Calculates immediate 1-level deep costs, incorporating custom orchard logic."""
    # 1. Check if it's an orchard plantable item (Apple, Raspberry, etc.)
    plant_struct = find_structure_for_plantable(item_obj.name)
    if plant_struct:
        struct_price = getattr(plant_struct, 'sell_price', getattr(plant_struct, 'coin_cost', 0))
        return struct_price / 12.0  # 4 harvests * 3 items = 12 total items yield

    # 2. Check if it's an animal product (requires feed)
    animal_food_obj = find_animal_food_for_item(item_obj.name)
    if animal_food_obj:
        return getattr(animal_food_obj, 'sell_price', 0)

    # 3. Standard recipe calculation
    if hasattr(item_obj, 'ingredients') and item_obj.ingredients:
        direct_cost = 0.0
        for ingredient_obj, quantity in item_obj.ingredients.items():
            ingredient_price = getattr(ingredient_obj, 'sell_price', 0)
            if ingredient_price is None:
                ingredient_price = DIAMOND_COST
            direct_cost += (ingredient_price * quantity)
        return direct_cost

    return 0.0

def print_table_header(with_time=False):
    if with_time:
        print(f"{'Item Name':<22} | {'Value Added':<12} | {'Time (Hrs)':<10} | {'Profit / Hour':<16} | {'ROI %':<8}")
    else:
        print(f"{'Item Name':<22} | {'Sell Price':<12} | {'Direct Cost':<12} | {'Value Added (Coins)':<18} | {'ROI %':<8}")
    print("-" * 84)

def print_standard_reports(reports):
    for r in reports:
        indicator = "⚠️ " if r["value_added"] < 0 else "  "
        print(f"{indicator}{r['name']:<20} | {r['final_price']:>10}c | {r['direct_cost']:>10.1f}c | {r['value_added']:>+17.1f}c | {r['roi']:>6.1f}%")

def print_time_reports(reports):
    for r in reports:
        indicator = "⚠️ " if r["value_added"] < 0 else "  "
        print(f"{indicator}{r['name']:<20} | {r['value_added']:>+10.1f}c | {r['time_hours']:>10.2f}h | {r['pph']:>+13.2f}c/h | {r['roi']:>6.1f}%")

def analyze_value_added():
    raw_reports = []

    for name, item_obj in ITEMS.items():
        class_type = type(item_obj).__name__
        has_recipe = hasattr(item_obj, 'ingredients') and item_obj.ingredients
        is_animal_product = find_animal_food_for_item(name) is not None
        is_plantable = find_structure_for_plantable(name) is not None
        is_crop = class_type == "Crop"

        # Track any item that has production inputs, including crops and orchard fruits
        if has_recipe or is_animal_product or is_plantable or is_crop:
            final_price = getattr(item_obj, 'sell_price', 0)
            direct_cost = calculate_direct_ingredient_cost(item_obj)

            value_added = final_price - direct_cost
            roi = (value_added / direct_cost) * 100 if direct_cost > 0 else 0.0

            # --- TIME RESOLVER ---
            time_minutes = getattr(item_obj, 'time_to_make', 0)

            # Fallback for Livestock
            if time_minutes == 0 and is_animal_product:
                for animal_name, animal_obj in LIVESTOCK.items():
                    if animal_obj.produces_item and animal_obj.produces_item.name == name:
                        time_minutes = getattr(animal_obj, 'time_to_make', 0)

            # Allocation math for Orchard Plantables: Divide harvest cycle time by 3 items produced
            if is_plantable:
                plant_struct = find_structure_for_plantable(name)
                struct_time = getattr(plant_struct.product, 'time_to_make', 0)
                time_minutes = struct_time / 3.0

            time_hours = time_minutes / 60.0
            pph = value_added / time_hours if time_hours > 0 else value_added

            raw_reports.append({
                "name": name,
                "final_price": final_price,
                "direct_cost": direct_cost,
                "value_added": value_added,
                "roi": roi,
                "time_hours": time_hours,
                "pph": pph
            })

    # =====================================================================
    # REPORTS PRINTING
    # =====================================================================
    print("\n=========================================================================")
    print("             HAY DAY ENGINE - SORTED BY VALUE-ADDED COINS                ")
    print("=========================================================================\n")
    by_value_added = sorted(raw_reports, key=lambda x: x["value_added"], reverse=True)
    print_table_header(with_time=False)
    print_standard_reports(by_value_added)

    print("\n" * 2)

    print("=========================================================================")
    print("                HAY DAY ENGINE - SORTED BY RETURN ON INVESTMENT          ")
    print("=========================================================================\n")
    by_roi = sorted(raw_reports, key=lambda x: x["roi"], reverse=True)
    by_roi = [x for x in by_roi if x["direct_cost"] > 0]
    print_table_header(with_time=False)
    print_standard_reports(by_roi)

    print("\n" * 2)

    print("=========================================================================")
    print("                HAY DAY ENGINE - SORTED BY PROFIT PER HOUR               ")
    print("             (The true measure of active factory efficiency)             ")
    print("=========================================================================\n")
    by_pph = sorted(raw_reports, key=lambda x: x["pph"], reverse=True)
    print_table_header(with_time=True)
    print_time_reports(by_pph)

if __name__ == "__main__":
    analyze_value_added()