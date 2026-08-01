from collections import Counter, defaultdict
from decimal import Decimal

# Imports from project modules
from calculators.profitability import calculate_direct_ingredient_cost
from game_data.animal_feeds_data import FEEDS
from game_data.crops_data import CROPS
from game_data.fields_data import FARM_FIELDS
from game_data.game_data import CURRENT_LEVEL
from game_data.machined_items_data import MACHINED_ITEMS
from game_data.machines_data import MACHINES

TOTAL_FIELDS = FARM_FIELDS["fields"].amount_owned


def _time_value(time_minutes):
    return Decimal(str(time_minutes))


class _IncrementalItemOptimizer:
    def __init__(self, sleep_duration_mins, max_slots_cap):
        self.max_slots_cap = max_slots_cap
        self.max_time = _time_value(sleep_duration_mins)

        self.states = [defaultdict(dict) for _ in range(max_slots_cap + 1)]
        self.states[0][_time_value(0)] = (0.0, None, None, None)
        self.parents = { (0, _time_value(0)): None }

        self.best_exact_profit = [float('-inf')] * (max_slots_cap + 1)
        self.best_exact_time = [None] * (max_slots_cap + 1)

    def add_item(self, item, item_profit, item_time_units):
        for slots_used in range(1, self.max_slots_cap + 1):
            source_states = self.states[slots_used - 1]
            target_states = self.states[slots_used]

            for source_time, (source_profit, _, _, _) in source_states.items():
                new_time = source_time + item_time_units
                if new_time > self.max_time:
                    continue

                candidate_profit = source_profit + item_profit
                current_state = target_states.get(new_time)
                if current_state is not None and candidate_profit <= current_state[0]:
                    continue

                target_states[new_time] = (candidate_profit, slots_used - 1, source_time, item)
                self.parents[(slots_used, new_time)] = (slots_used - 1, source_time, item)

                if candidate_profit > self.best_exact_profit[slots_used]:
                    self.best_exact_profit[slots_used] = candidate_profit
                    self.best_exact_time[slots_used] = new_time

            if target_states:
                self.states[slots_used] = self._prune_states(target_states)

    def _prune_states(self, states_by_time):
        pruned_states = {}
        best_profit_so_far = float('-inf')

        for total_time, state in sorted(states_by_time.items(), key=lambda item: item[0]):
            if state[0] > best_profit_so_far:
                pruned_states[total_time] = state
                best_profit_so_far = state[0]

        return pruned_states

    def best_state_for_capacity(self, num_slots):
        best_profit = float('-inf')
        best_slots = None
        best_time = None

        for slots_used in range(1, num_slots + 1):
            candidate_profit = self.best_exact_profit[slots_used]
            if candidate_profit > best_profit:
                best_profit = candidate_profit
                best_slots = slots_used
                best_time = self.best_exact_time[slots_used]

        if best_slots is None or best_time is None:
            return None

        return best_slots, best_time, best_profit

    def reconstruct_combo(self, slots_used, total_time):
        combo_counts = Counter()

        while slots_used > 0:
            parent = self.parents.get((slots_used, total_time))
            if parent is None:
                break

            next_slots, next_time, item = parent
            if item is None:
                break

            combo_counts[item] += 1

            slots_used = next_slots
            total_time = next_time

        return dict(combo_counts)


class _OvernightStrategyEngine:
    def __init__(self, sleep_duration_mins):
        self.sleep_duration_mins = sleep_duration_mins
        self.feed_items_set = set(FEEDS.values())
        self.level = 0

        self.machine_states = {}
        self.machine_item_buckets = {}
        self.crop_candidates = []
        self.crop_buckets = defaultdict(list)
        self.best_crop = None

        self._prepare_machines()
        self._prepare_crops()

    def _prepare_machines(self):
        for machine_name, machine_obj in MACHINES.items():
            min_slots = getattr(machine_obj, 'min_allowed_slots', 2)
            max_slots_cap = getattr(machine_obj, 'max_allowed_slots', 9)

            if "feed mill" in machine_name.lower():
                candidates = list(FEEDS.values())
            else:
                candidates = [
                    item for item in MACHINED_ITEMS.values()
                    if getattr(item, 'machine', None) and item.machine.name == machine_name
                ]

            candidates = [
                item for item in candidates
                if getattr(item, 'unlock_level', 1) <= 999999
            ]

            item_buckets = defaultdict(list)
            for item in candidates:
                unlock_level = getattr(item, 'unlock_level', 1)
                mult = 3 if item in self.feed_items_set else 1
                item_profit = (item.sell_price * mult) - (calculate_direct_ingredient_cost(item) * mult)
                item_buckets[unlock_level].append((item, item_profit))

            self.machine_item_buckets[machine_name] = item_buckets

            mastery_states = {}
            for star_lvl in range(0, 4):
                original_mastery = machine_obj.mastery_level
                machine_obj.mastery_level = star_lvl
                speed_mult = machine_obj.speed_multiplier
                machine_obj.mastery_level = original_mastery

                mastery_states[star_lvl] = {
                    "speed_mult": Decimal(str(speed_mult)),
                    "optimizer": _IncrementalItemOptimizer(self.sleep_duration_mins, max_slots_cap),
                }

            self.machine_states[machine_name] = {
                "machine_obj": machine_obj,
                "min_slots": min_slots,
                "max_slots": max_slots_cap,
                "mastery_states": mastery_states,
            }

    def _prepare_crops(self):
        self.crop_candidates = [
            crop for crop in CROPS.values()
            if crop.time_to_make <= self.sleep_duration_mins
        ]
        for crop in self.crop_candidates:
            self.crop_buckets[getattr(crop, 'unlock_level', 1)].append(crop)
        self.best_crop = None

    def _advance_to_level(self, target_level):
        for level in range(self.level + 1, target_level + 1):
            for machine_name, machine_state in self.machine_states.items():
                buckets = self.machine_item_buckets[machine_name]
                new_items = buckets.get(level, ())

                if not new_items:
                    continue

                for star_lvl, mastery_state in machine_state["mastery_states"].items():
                    optimizer = mastery_state["optimizer"]
                    speed_mult = mastery_state["speed_mult"]

                    for item, item_profit in new_items:
                        item_time_units = _time_value(item.time_to_make) * speed_mult
                        if item_time_units <= optimizer.max_time:
                            optimizer.add_item(item, item_profit, item_time_units)

            for crop in self.crop_buckets.get(level, ()):
                if self.best_crop is None or crop.sell_price > self.best_crop.sell_price:
                    self.best_crop = crop

        self.level = target_level

    def _build_machine_strategy(self, machine_name, player_level):
        machine_state = self.machine_states[machine_name]
        machine_obj = machine_state["machine_obj"]
        unlocked_count = machine_obj.max_allowed_at_level(player_level)

        if unlocked_count == 0:
            return None

        min_slots = machine_state["min_slots"]
        max_slots_cap = machine_state["max_slots"]
        mastery_strategies = {}

        for star_lvl, mastery_state in machine_state["mastery_states"].items():
            mastery_key = f"{star_lvl}_stars" if star_lvl != 1 else "1_star"
            optimizer = mastery_state["optimizer"]
            slot_strategies = [None] * (max_slots_cap + 1)

            if optimizer.best_exact_time[1] is not None:
                for num_slots in range(min_slots, max_slots_cap + 1):
                    best_state = optimizer.best_state_for_capacity(num_slots)
                    if best_state is None:
                        continue

                    slots_used, total_time, best_profit = best_state
                    combo_counts = optimizer.reconstruct_combo(slots_used, total_time)
                    ingredients = defaultdict(int)

                    for item, count in combo_counts.items():
                        mult = 3 if item in self.feed_items_set else 1
                        if hasattr(item, 'ingredients') and item.ingredients:
                            for ing_name, ing_qty in item.ingredients.items():
                                ingredients[ing_name] += ing_qty * count * mult

                    slot_strategies[num_slots] = {
                        "combination": combo_counts,
                        "ingredients": dict(ingredients),
                        "total_profit": best_profit,
                    }

            mastery_strategies[mastery_key] = slot_strategies

        current_slots = getattr(machine_obj, 'max_slots', min_slots)
        default_eval = (
            mastery_strategies["0_stars"][current_slots]
            if current_slots < len(mastery_strategies["0_stars"])
            else None
        )

        machine_entry = {
            "by_mastery": mastery_strategies,
            "min_slots": min_slots,
            "max_slots": max_slots_cap,
            "unlocked_count": unlocked_count,
        }

        return machine_entry, default_eval

    def calculate_level(self, player_level):
        self._advance_to_level(player_level)

        strategy = {}
        total_global_profit = 0

        for machine_name in MACHINES:
            machine_entry = self._build_machine_strategy(machine_name, player_level)
            if machine_entry is None:
                continue

            machine_strategy, default_eval = machine_entry
            strategy[machine_name] = machine_strategy

            if default_eval:
                total_global_profit += default_eval["total_profit"] * machine_strategy["unlocked_count"]

        fields_count = FARM_FIELDS["fields"].max_allowed_at_level(player_level)
        if self.best_crop is not None:
            profit = self.best_crop.sell_price * fields_count
            total_global_profit += profit

            strategy["Fields"] = {
                "combination": {self.best_crop: fields_count},
                "total_profit": profit,
                "unlocked_count": 1,
            }

        return strategy, total_global_profit


def calculate_strategy_for_single_level(sleep_duration_mins, player_level):
    """Calculate the overnight strategy for a single level."""
    engine = _OvernightStrategyEngine(sleep_duration_mins)
    return engine.calculate_level(player_level)


def calculate_overnight_strategy(sleep_duration_mins=480, max_level=CURRENT_LEVEL):
    """
    Evaluates optimal overnight production strategies from level 1 up to max_level.
    """
    print("="*30)
    print(f"calculating for {sleep_duration_mins//60}h")
    print("="*30)
    all_level_strategies = {}
    engine = _OvernightStrategyEngine(sleep_duration_mins)

    for lvl in range(1, max_level + 1):
        print(f"    - Level {lvl}")
        level_strategy, total_profit = engine.calculate_level(lvl)
        all_level_strategies[lvl] = {
            "strategy": level_strategy,
            "total_profit": total_profit
        }

    return all_level_strategies