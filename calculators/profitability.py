import csv
from functools import lru_cache
import os

from game_data import INFRASTRUCTURE, ITEMS, LIVESTOCK
from game_data.game_data import DIAMOND_COST


def find_animal_food_for_item(item_name):
    """Scans the LIVESTOCK registry to get the Feed item required for an animal."""
    for animal_name, animal_obj in LIVESTOCK.items():
        if (
            animal_obj.produces_item
            and animal_obj.produces_item.name == item_name
        ):
            if animal_obj.required_food:
                return animal_obj.required_food
    return None


def find_structure_for_plantable(item_name):
    """Scans INFRASTRUCTURE['plant_structures'] to match an item to its tree/bush."""
    plant_dict = INFRASTRUCTURE.get(
        "plant_structures", INFRASTRUCTURE.get("structures", {})
    )
    for struct_name, struct_obj in plant_dict.items():
        if item_name in struct_name:
            return struct_obj
    return None


@lru_cache(maxsize=None)
def calculate_direct_ingredient_cost(item_obj):
    """Calculates immediate 1-level deep costs, incorporating custom orchard logic."""
    # 1. Check if it's an orchard plantable item (Apple, Raspberry, etc.)
    plant_struct = find_structure_for_plantable(item_obj.name)
    if plant_struct:
        # Total yield across all harvest stages (e.g., 2 + 3 + 4 + 4 = 13 items)
        harvest_sched = getattr(plant_struct, "harvest_schedule", [])
        total_yield = sum(harvest_sched) if harvest_sched else 1

        # Cost of the removal tool required to chop down the dead structure (Axe/Saw)
        tool_price = 0.0
        if getattr(plant_struct, "removal_tool", None):
            tool_price = getattr(
                plant_struct.removal_tool, "sell_price", 0.0
            ) or 0.0

        # Total structure expenditure = tree purchase cost + removal tool cost
        total_structure_cost = plant_struct.coin_cost + tool_price

        # Unit cost per single harvested item
        return total_structure_cost / total_yield if total_yield > 0 else 0.0

    # 2. Check if it's an animal product (requires feed)
    animal_food_obj = find_animal_food_for_item(item_obj.name)
    if animal_food_obj:
        return getattr(animal_food_obj, "sell_price", 0)

    # 3. Standard recipe calculation
    if hasattr(item_obj, "ingredients") and item_obj.ingredients:
        direct_cost = 0.0
        for ingredient_obj, quantity in item_obj.ingredients.items():
            ingredient_price = getattr(ingredient_obj, "sell_price", 0)
            if ingredient_price is None:
                ingredient_price = DIAMOND_COST
            direct_cost += ingredient_price * quantity
        return direct_cost

    return 0.0


def print_table_header(with_time=False):
    if with_time:
        print(
            f"{'Item Name':<22} | {'Value Added':<12} | {'Time (Hrs)':<10} |"
            f" {'Profit / Hour':<16} | {'ROI %':<8}"
        )
    else:
        print(
            f"{'Item Name':<22} | {'Sell Price':<12} | {'Direct Cost':<12} |"
            f" {'Value Added (Coins)':<18} | {'ROI %':<8}"
        )
    print("-" * 84)


def print_standard_reports(reports):
    for r in reports:
        indicator = "⚠️ " if r["value_added"] < 0 else "  "
        print(
            f"{indicator}{r['name']:<20} | {r['final_price']:>10}c |"
            f" {r['direct_cost']:>10.1f}c | {r['value_added']:>+17.1f}c |"
            f" {r['roi']:>6.1f}%"
        )


def print_time_reports(reports):
    for r in reports:
        indicator = "⚠️ " if r["value_added"] < 0 else "  "
        print(
            f"{indicator}{r['name']:<20} | {r['value_added']:>+10.1f}c |"
            f" {r['time_hours']:>10.2f}h | {r['pph']:>+13.2f}c/h |"
            f" {r['roi']:>6.1f}%"
        )


def analyze_value_added(silent=False):
    raw_reports = []

    for name, item_obj in ITEMS.items():
        class_type = type(item_obj).__name__
        has_recipe = hasattr(item_obj, "ingredients") and item_obj.ingredients
        unlock_level = item_obj.unlock_level
        is_animal_product = find_animal_food_for_item(name) is not None
        is_plantable = find_structure_for_plantable(name) is not None
        is_crop = class_type == "Crop"

        # Track any item that has production inputs, including crops and orchard fruits
        if has_recipe or is_animal_product or is_plantable or is_crop:
            final_price = getattr(item_obj, "sell_price", 0)
            direct_cost = calculate_direct_ingredient_cost(item_obj)

            value_added = final_price - direct_cost
            roi = (value_added / direct_cost) * 100 if direct_cost > 0 else 0.0

            # --- TIME RESOLVER ---
            time_minutes = getattr(item_obj, "time_to_make", 0)

            # Fallback for Livestock
            if time_minutes == 0 and is_animal_product:
                for animal_name, animal_obj in LIVESTOCK.items():
                    if (
                        animal_obj.produces_item
                        and animal_obj.produces_item.name == name
                    ):
                        time_minutes = getattr(animal_obj, "time_to_make", 0)

            # Allocation math for Orchard Plantables
            if is_plantable:
                plant_struct = find_structure_for_plantable(name)
                struct_time = (
                    getattr(plant_struct.product, "time_to_make", 0)
                    if plant_struct and hasattr(plant_struct, "product")
                    else time_minutes
                )
                time_minutes = struct_time

            time_hours = time_minutes / 60.0
            pph = value_added / time_hours if time_hours > 0 else value_added

            raw_reports.append({
                "name": name,
                "final_price": final_price,
                "direct_cost": direct_cost,
                "value_added": value_added,
                "roi": roi,
                "time_hours": time_hours,
                "pph": pph,
                "unlock_level": unlock_level,
            })

    if not silent:
        print(
            "\n========================================================================="
        )
        print(
            "             HAY DAY ENGINE - SORTED BY VALUE-ADDED COINS"
            "                "
        )
        print(
            "=========================================================================\n"
        )
        by_value_added = sorted(
            raw_reports, key=lambda x: x["value_added"], reverse=True
        )
        print_table_header(with_time=False)
        print_standard_reports(by_value_added)

        print("\n" * 2)

        print(
            "========================================================================="
        )
        print(
            "                HAY DAY ENGINE - SORTED BY RETURN ON INVESTMENT"
            "          "
        )
        print(
            "=========================================================================\n"
        )
        by_roi = sorted(raw_reports, key=lambda x: x["roi"], reverse=True)
        by_roi = [x for x in by_roi if x["direct_cost"] > 0]
        print_table_header(with_time=False)
        print_standard_reports(by_roi)

        print("\n" * 2)

        print(
            "========================================================================="
        )
        print(
            "                HAY DAY ENGINE - SORTED BY PROFIT PER HOUR"
            "               "
        )
        print(
            "             (The true measure of active factory efficiency)"
            "             "
        )
        print(
            "=========================================================================\n"
        )
        by_pph = sorted(raw_reports, key=lambda x: x["pph"], reverse=True)
        print_table_header(with_time=True)
        print_time_reports(by_pph)

    return raw_reports


if __name__ == "__main__":
    analyze_value_added()