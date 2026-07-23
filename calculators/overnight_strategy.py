import itertools
from collections import Counter, defaultdict
from calculators.profitability import calculate_direct_ingredient_cost
from game_data.animal_feeds_data import FEEDS
from game_data.crops_data import CROPS
from game_data.fields_data import FARM_FIELDS
from game_data.machined_items_data import MACHINED_ITEMS
from game_data.machines_data import MACHINES
from game_data.plants_data import PLANTS
from visualizers.helpers.formatting import CYAN, RESET

TOTAL_FIELDS = FARM_FIELDS["fields"].amount_owned

def get_best_overnight_strategy(sleep_duration_mins=480):
    strategy = {}
    total_global_profit = 0

    # 1. MACHINE STRATEGY
    for machine_name, machine_obj in MACHINES.items():
        # print(f"Processing {machine_name}...")
        if machine_obj.amount_owned == 0 or machine_obj.max_slots == 0:
            continue

        candidates = [i for i in MACHINED_ITEMS.values() if i.machine.name == machine_name] + [i for i in FEEDS.values() if i.machine.name == machine_name]
        valid_items = [i for i in candidates if i.time_to_make <= sleep_duration_mins]
        if not valid_items:
            print(f"{CYAN}{machine_name} has no valid items in this time constraint{RESET}")
            continue

        best_profit_per_machine = 0 # Default to 0 (don't run machine if no profit)
        best_combo_per_machine = []

        # Iterate through every possible number of slots from 0 up to max_slots
        for num_slots in range(machine_obj.max_slots + 1):
            for combo in itertools.combinations_with_replacement(valid_items, num_slots):
                # Check if this specific combination finishes within sleep_duration
                if sum(i.time_to_make for i in combo) <= sleep_duration_mins:
                    current_profit = sum((i.sell_price - calculate_direct_ingredient_cost(i)) for i in combo)

                    if current_profit > best_profit_per_machine:
                        best_profit_per_machine = current_profit
                        best_combo_per_machine = combo

        if best_combo_per_machine:
            counts = Counter(best_combo_per_machine)
            total_machine_profit = best_profit_per_machine * machine_obj.amount_owned
            total_global_profit += total_machine_profit

            strategy[machine_name] = {
                "combination": {item: count * machine_obj.amount_owned for item, count in counts.items()},
                "total_profit": total_machine_profit
            }
        else:
            strategy[machine_name] = {
                "combination": {},
                "total_profit": 0
            }

    # 2. CROP STRATEGY
    valid_crops = [c for c in CROPS.values() if c.time_to_make <= sleep_duration_mins]
    if valid_crops:
        best_crop = max(valid_crops, key=lambda c: c.sell_price * TOTAL_FIELDS)
        profit = best_crop.sell_price * TOTAL_FIELDS
        total_global_profit += profit
        strategy["Fields"] = {
            "combination": {best_crop: TOTAL_FIELDS},
            "total_profit": profit
        }

    return strategy, total_global_profit

def run_report():
    plan, global_profit = get_best_overnight_strategy(480)

    # Header
    print(f"{'Machine/Source':<20} | {'Optimal Queue Strategy':<40} | {'Profit'}")
    print("-" * 85)

    global_ingredients = defaultdict(int)
    machine_requirements = {}

    # Print Strategy and collect ingredients
    for m, data in plan.items():
        combo_parts = [f"{count}x {item_obj.name}" for item_obj, count in data['combination'].items()]
        print(f"{m:<20} | {', '.join(combo_parts):<40} | {data['total_profit']:.1f}c")

        current_machine_ing = defaultdict(int)
        for item_obj, count in data['combination'].items():
            if hasattr(item_obj, 'ingredients'):
                for ing, qty in item_obj.ingredients.items():
                    total_qty = qty * count
                    current_machine_ing[ing.name] += total_qty
                    global_ingredients[ing.name] += total_qty
        machine_requirements[m] = current_machine_ing

    # Global Summary
    print("-" * 85)
    print(f"TOTAL OVERNIGHT PROFIT: {global_profit:.1f}c")

    # 1. Global Shopping List
    print("\nGLOBAL SHOPPING LIST:")
    silo_space = 0
    barn_space = 0

    # Add seeds for fields to the requirements (if applicable)
    if "Fields" in plan:
        for crop_obj in plan["Fields"]["combination"].keys():
            global_ingredients[crop_obj.name] += TOTAL_FIELDS

    for ing, qty in global_ingredients.items():
        print(f"- {qty}x {ing}")
        # Categorize storage
        if ing in CROPS or ing in PLANTS:
            silo_space += qty
        else:
            barn_space += qty

    # 2. Storage Impact
    print("\nSTORAGE IMPACT:")
    print(f"-> Silo (Crops/Seeds): {silo_space} items")
    print(f"-> Barn (Processed Goods/Animal Products): {barn_space} items")

    # 3. Per-Machine Breakdown
    print("\nPER-MACHINE INGREDIENT REQUIREMENTS:")
    for m, ingredients in machine_requirements.items():
        if ingredients:
            ing_str = ", ".join([f"{qty}x {name}" for name, qty in ingredients.items()])
            print(f"- {m}: {ing_str}")

if __name__ == "__main__":
    run_report()