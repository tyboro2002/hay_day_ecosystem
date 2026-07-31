import itertools
from collections import Counter, defaultdict
from calculators.profitability import calculate_direct_ingredient_cost
from game_data.animal_feeds_data import FEEDS
from game_data.crops_data import CROPS
from game_data.fields_data import FARM_FIELDS
from game_data.game_data import MAX_LEVEL, CURRENT_LEVEL
from game_data.machined_items_data import MACHINED_ITEMS
from game_data.machines_data import MACHINES
from game_data.plants_data import PLANTS

TOTAL_FIELDS = FARM_FIELDS["fields"].amount_owned


def get_unlocked_machine_count_at_level(machine_obj, player_level):
    """Calculates how many instances of a machine are unlocked at player_level."""
    levels = getattr(machine_obj, 'unlock_schedule', None)
    if levels and isinstance(levels, list):
        count = 0
        for entry in levels:
            if isinstance(entry, (tuple, list)) and len(entry) >= 2:
                lvl, new_unlocks = entry[0], entry[1]
                if player_level >= lvl:
                    count += new_unlocks
        return count

    base_unlock = getattr(machine_obj, 'unlock_level', 1)
    return 1 if player_level >= base_unlock else 0


def calculate_strategy_for_single_level(sleep_duration_mins, player_level):
    """
    Calculates the best overnight strategy per machine for ALL valid slot counts
    (min_allowed_slots to max_allowed_slots) unlocked at player_level.
    """
    strategy = {}
    total_global_profit = 0

    # Lookup set for feed items
    feed_items_set = set(FEEDS.values())

    # 1. MACHINE STRATEGY
    for machine_name, machine_obj in MACHINES.items():
        unlocked_count = get_unlocked_machine_count_at_level(machine_obj, player_level)
        if unlocked_count == 0:
            continue

        # Safely pull candidates: if it's a Feed Mill, pull from FEEDS; otherwise pull from MACHINED_ITEMS
        if "feed mill" in machine_name.lower():
            candidates = list(FEEDS.values())
        else:
            candidates = [
                i for i in MACHINED_ITEMS.values()
                if getattr(i, 'machine', None) and i.machine.name == machine_name
            ]

        valid_items = [
            i for i in candidates
            if getattr(i, 'unlock_level', 1) <= player_level and i.time_to_make <= sleep_duration_mins
        ]

        if not valid_items:
            continue

        # Use attributes min_allowed_slots and max_allowed_slots
        min_slots = getattr(machine_obj, 'min_allowed_slots', 2) or (1 if machine_name in ["Lobster Pool", "Duck Salon"] else 2)
        max_slots_cap = getattr(machine_obj, 'max_allowed_slots', 9) or 9

        # Slot-indexed strategy array (index matches slot count 0..max_allowed_slots)
        slot_strategies = [None] * (max_slots_cap + 1)

        for num_slots in range(min_slots, max_slots_cap + 1):
            best_profit = float('-inf')
            best_combo = None

            # Test using ANY number of items up to num_slots (1 to num_slots)
            for k in range(1, num_slots + 1):
                for combo in itertools.combinations_with_replacement(valid_items, k):
                    if sum(i.time_to_make for i in combo) <= sleep_duration_mins:
                        # Feeds produce 3 units per batch slot, so ingredient cost is 3x per batch slot
                        current_profit = sum(
                            ((i.sell_price * 3 if i in feed_items_set else i.sell_price) - (calculate_direct_ingredient_cost(i) * 3 if i in feed_items_set else calculate_direct_ingredient_cost(i)))
                            for i in combo
                        )
                        if current_profit > best_profit:
                            best_profit = current_profit
                            best_combo = combo

            if best_combo is not None:
                combo_counts = dict(Counter(best_combo))
                ingredients = defaultdict(int)

                for item, count in combo_counts.items():
                    multiplier = 3 if item in feed_items_set else 1
                    if hasattr(item, 'ingredients') and item.ingredients:
                        for ing_name, ing_qty in item.ingredients.items():
                            ingredients[ing_name] += ing_qty * count * multiplier

                slot_strategies[num_slots] = {
                    "combination": combo_counts,
                    "ingredients": dict(ingredients),
                    "total_profit": best_profit
                }

        # max_slots represents current configured amount of slots
        current_slots = getattr(machine_obj, 'max_slots', min_slots) or min_slots
        default_eval = slot_strategies[current_slots] if current_slots < len(slot_strategies) else None

        strategy[machine_name] = {
            "by_slots": slot_strategies,
            "min_slots": min_slots,
            "max_slots": max_slots_cap,
            "unlocked_count": unlocked_count
        }

        if default_eval:
            total_global_profit += (default_eval["total_profit"] * unlocked_count)

    # 2. CROP STRATEGY
    valid_crops = [
        c for c in CROPS.values()
        if getattr(c, 'unlock_level', 1) <= player_level and c.time_to_make <= sleep_duration_mins
    ]
    fields_count = FARM_FIELDS["fields"].max_allowed_at_level(player_level)
    if valid_crops:
        best_crop = max(valid_crops, key=lambda c: c.sell_price * fields_count)
        profit = best_crop.sell_price * fields_count
        total_global_profit += profit

        strategy["Fields"] = {
            "combination": {best_crop: fields_count},
            "total_profit": profit,
            "unlocked_count": 1
        }

    return strategy, total_global_profit


def get_best_overnight_strategy(sleep_duration_mins=480, max_level=-1):
    if max_level == -1:
        return calculate_strategy_for_single_level(sleep_duration_mins, CURRENT_LEVEL)

    all_level_strategies = []
    for lvl in range(1, max_level + 1):
        plan, profit = calculate_strategy_for_single_level(sleep_duration_mins, lvl)
        all_level_strategies.append((plan, profit))

    return all_level_strategies