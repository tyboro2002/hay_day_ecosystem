# =====================================================================
# 1. PRODUCTION PLACES (Machines & Animal Pens)
# =====================================================================

class HayDayMachine:
    """
    unlock_schedule: List of tuples -> [(level, amount_extra_unlocked)]
    Example for Feed Mill: [(3, 1), (12, 1)]
    -> 1 mill unlocked at lvl 3, +1 extra unlocked at lvl 12.

    Example for Sugar Mill: [(7, 1), (76, 1)]
    """
    def __init__(self, name, amount_owned, min_allowed_slots = 2, max_allowed_slots = 9, max_slots=2,
                 unlock_schedule=None, mastery_level=0, mastery=None, costs=None):
        self.name = name
        self.amount_owned = amount_owned
        self.max_slots = max_slots
        self.min_allowed_slots = min_allowed_slots
        self.max_allowed_slots = max_allowed_slots
        self.unlock_schedule = unlock_schedule or [(1, 1)] # Default: 1 unlocked at level 1
        self.costs = costs or []                             # [cost_1st, cost_2nd, ...]
        self.mastery_level = min(max(mastery_level, 0), 3)  # Active star level (0..3)
        self.mastery_config = mastery or {}          # Raw incremental YAML block
        self.queue = [] # List of items currently queued
        self.products = []  # Items this machine can produce, automatically filled by MachinedItems

    def __repr__(self):
        return f"Machine: {self.name}"

    @property
    def full_unlock_schedule(self):
        """
        Returns a list of tuples formatted as:
        [(level, count, unit_costs_list), ...]
        Example: [(24, 5, [100, 200, 300, 400, 500])]
        """
        detailed_schedule = []
        cost_cursor = 0

        for lvl, count in self.unlock_schedule:
            # Grab the slice of costs corresponding to the machines unlocked at this level
            tier_costs = self.costs[cost_cursor : cost_cursor + count]
            cost_cursor += count

            detailed_schedule.append((lvl, count, tier_costs))

        return detailed_schedule

    def get_star_info(self, star_number):
        """Returns the incremental data for a specific star from YAML."""
        return self.mastery_config.get(f"star_{star_number}", {})

    def get_total_hours_for_star(self, star_number):
        """
        Calculates cumulative hours required from 0 to target star level.
        Example for Bakery Star 3: 35 + 140 + 560 = 735 total hours.
        """
        return sum(
            self.get_star_info(s).get("hours_required", 0)
            for s in range(1, star_number + 1)
        )

    @property
    def total_mastery_hours(self):
        """Returns total hours to fully 3-star (master) this machine."""
        return self.get_total_hours_for_star(3)

    @property
    def cumulative_bonuses(self):
        """Accumulates all active incremental bonuses up to current mastery_level."""
        bonuses = {"coin_bonus": 0.0, "xp_bonus": 0.0, "speed_bonus": 0.0}

        for star in range(1, self.mastery_level + 1):
            info = self.get_star_info(star)
            bonuses["coin_bonus"] += info.get("coin_bonus", 0.0)
            bonuses["xp_bonus"] += info.get("xp_bonus", 0.0)
            bonuses["speed_bonus"] += info.get("speed_bonus", 0.0)

        return bonuses

    @property
    def speed_multiplier(self):
        """Crafting time multiplier used for RSS optimization."""
        return 1.0 - self.cumulative_bonuses["speed_bonus"]

    @property
    def coin_multiplier(self):
        return 1.0 + self.cumulative_bonuses["coin_bonus"]

    @property
    def xp_multiplier(self):
        return 1.0 + self.cumulative_bonuses["xp_bonus"]

    @property
    def unlock_level(self):
        """Returns the minimum player level required to unlock the first machine."""
        if not self.unlock_schedule:
            return 1
        return min(lvl for lvl, _ in self.unlock_schedule)

    def total_queued_time(self):
        return sum(item.time_to_make for item in self.queue)

    def is_unlocked(self, player_level):
        """Returns True if at least 1 machine is unlocked at the given player level."""
        return player_level >= self.unlock_level

    def max_allowed_at_level(self, player_level):
        """
        Sums up all 'amount_extra' unlocked up to the player's level.
        """
        return sum(extra for lvl, extra in self.unlock_schedule if player_level >= lvl)


class AnimalPen:
    def __init__(self, name, amount_owned, max_capacity=5, current_capacity=5, unlock_schedule=None, costs=None):
        self.name = name
        self.current_capacity = current_capacity
        self.max_capacity = max_capacity
        self.amount_owned = amount_owned
        self.unlock_schedule = unlock_schedule or [(1, 1)]
        self.costs = costs or []                             # [cost_1st, cost_2nd, ...]
        self.animal = None   # Holds Animal objects living here
        self.products = []  # Items this pen can produce, automatically filled by AnimalItems

    def __repr__(self):
        return f"Pen: {self.name} ({self.current_capacity}/{self.max_capacity} animals) ({self.amount_owned} owned)"

    @property
    def full_unlock_schedule(self):
        """
        Returns a list of tuples formatted as:
        [(level, count, unit_costs_list), ...]
        Example: [(24, 5, [100, 200, 300, 400, 500])]
        """
        detailed_schedule = []
        cost_cursor = 0

        for lvl, count in self.unlock_schedule:
            # Grab the slice of costs corresponding to the machines unlocked at this level
            tier_costs = self.costs[cost_cursor : cost_cursor + count]
            cost_cursor += count

            detailed_schedule.append((lvl, count, tier_costs))

        return detailed_schedule

    @property
    def unlock_level(self):
        """Returns the minimum level required to unlock the first pen."""
        if not self.unlock_schedule:
            return 1
        return min(lvl for lvl, _ in self.unlock_schedule)

    def is_unlocked(self, player_level):
        """Returns True if the player level meets or exceeds the minimum unlock level."""
        return player_level >= self.unlock_level

    def max_pens_at_level(self, player_level):
        """Calculates total pens unlocked at level."""
        return sum(extra for lvl, extra in self.unlock_schedule if player_level >= lvl)

    def max_animal_capacity_at_level(self, player_level):
        """Max potential animals allowed based on level."""
        return self.max_pens_at_level(player_level) * self.max_capacity


class Animal:
    def __init__(self, name, pen, item=None, required_food=None):
        self.name = name
        self.pen = pen
        self.pen.animal = self # Auto-register animal to its home pen
        self.produces_item = item
        self.required_food = required_food  # Links to a MachinedItem instance (e.g., Chicken Feed)

    def __repr__(self):
        return self.name

    @property
    def unlock_level(self):
        """Returns the level at which the animal's pen first unlocks."""
        return self.pen.unlock_level if self.pen else 1

    def is_unlocked(self, player_level):
        """Returns True if the animal's home pen is unlocked at the given player level."""
        return player_level >= self.unlock_level

    def max_allowed(self, player_level):
        """Upper cap on how many animals the player could own at their level."""
        return self.pen.max_animal_capacity_at_level(player_level)

class PlantableStructure:
    def __init__(self, name, coin_cost, unlock_level=1, harvest_schedule=None, removal_tool=None,):
        self.name = name
        self.coin_cost = coin_cost  # Cost to buy the tree/bush seed from the shop
        self.unlock_level = unlock_level
        # Default Hay Day harvest schedule (2, 3, 4, 4 items per harvest)
        self.harvest_schedule = (
            list(harvest_schedule)
            if harvest_schedule is not None
            else [2, 3, 4, 4]
        )
        self.max_harvests = len(self.harvest_schedule)
        self.product = None  # Will hold the PlantableItem instance it grows
        self.removal_tool = (
            removal_tool  # Matches key in SPECIAL_ITEMS (e.g., "Axe" or "Saw")
        )

    def is_unlocked(self, player_level):
        return player_level >= self.unlock_level

    def __repr__(self):
        return f"Structure: {self.name} (Cost: {self.coin_cost} coins)"

class Field:
    def __init__(self, amount_owned):
        self.name = "Field"
        self.amount_owned = amount_owned

    @staticmethod
    def max_allowed_at_level(player_level):
        """
        Calculates max fields unlocked in Hay Day:
        - Starts at Level 1 with 6 fields
        - Unlocks occur on ODD levels (3, 5, 7, ..., 49) giving +3 fields
        - Unlocks on ODD levels (51, 53, ..., 99) give +2 fields
        - Unlocks on ODD levels (101+) give +1 field
        """
        if player_level < 1:
            return 0

        total_fields = 6  # Level 1 starting fields

        for lvl in range(3, player_level + 1):
            if lvl % 2 != 0:  # Odd levels only (3, 5, 7, etc.)
                if lvl <= 49:
                    total_fields += 3
                elif lvl <= 99:
                    total_fields += 2
                else:
                    total_fields += 1

        return total_fields

    def is_unlocked(self, player_level):
        """Fields are unlocked right from level 1."""
        return player_level >= 1

    def __repr__(self):
        return f"{self.amount_owned} Fields"

class SpecialStructure:
    """
    For unique buildings unlocked at a specific single level (Mine, Fishing Dock, Town Hall, etc.).
    """
    def __init__(self, name, amount_owned=1, unlock_level=1):
        self.name = name
        self.amount_owned = amount_owned
        self.unlock_level = unlock_level

    def is_unlocked(self, player_level):
        """Returns True if the player's level is high enough for this structure."""
        return player_level >= self.unlock_level

    def __repr__(self):
        return f"{self.name} (Unlocks at Lvl {self.unlock_level})"

# =====================================================================
# 2. ITEMS (Base Class & Subclasses)
# =====================================================================

class HayDayItem:
    """The base class for everything you can hold in your barn/silo."""
    def __init__(self, name, time_to_make, sell_price, xp, unlock_level=1, ingredients=None):
        self.name = name
        self.time_to_make = time_to_make  # in minutes
        self.sell_price = sell_price
        self.xp = xp                      # XP granted upon collection
        self.unlock_level = unlock_level  # Single integer level requirement
        self.ingredients = ingredients or {}  # Will hold {Item_Object: quantity}

    def is_unlocked(self, player_level):
        """Returns True if the player's level is high enough to produce/collect this item."""
        return player_level >= self.unlock_level

    def __repr__(self):
        return self.name

class Crop(HayDayItem):
    """Crops grown in fields. They don't need ingredients or specific machines."""
    def __init__(self, name, time_to_make, sell_price, xp, planted_on, unlock_level=1, yield_multiplier=2):
        super().__init__(name, time_to_make, sell_price, xp, unlock_level=unlock_level)
        self.yield_multiplier = yield_multiplier
        self.planted_on = planted_on

class AnimalItem(HayDayItem):
    """Items collected from animals (Eggs, Milk, Wool, etc.). Links to a Pen."""
    def __init__(self, name, time_to_make, sell_price, xp, pen, unlock_level=1, ingredients=None):
        super().__init__(name, time_to_make, sell_price, xp, unlock_level, ingredients)
        self.pen = pen

        # Auto-register product to the animal pen
        if self.pen:
            self.pen.products.append(self)

    def is_unlocked(self, player_level):
        """
        An animal item is unlocked if the player's level meets its requirement
        AND at least 1 pen for this animal is unlocked.
        """
        pen_unlocked = self.pen.is_unlocked(player_level) if self.pen else True
        return (player_level >= self.unlock_level) and pen_unlocked

class MachinedItem(HayDayItem):
    """Products made in a machine (Bread, Sugar, Feed, etc.). Links to a Machine."""
    def __init__(self, name, time_to_make, sell_price, xp, machine, unlock_level=1, ingredients=None):
        super().__init__(name, time_to_make, sell_price, xp, unlock_level, ingredients)
        self.machine = machine

        # Auto-register product to the production machine
        if self.machine:
            self.machine.products.append(self)

class SpecialItem(HayDayItem):
    """Items like axes, dynamite, or expansion materials that aren't produced."""
    def __init__(self, name, sell_price, xp=0, unlock_level=1):
        # Time to make is 0 because they are found/looted, not crafted
        super().__init__(name, time_to_make=0, sell_price=sell_price, xp=xp, unlock_level=unlock_level)

class PlantableItem(HayDayItem):
    """Items harvested from trees or bushes (Apples, Cherries, Blackberries, etc.)."""
    def __init__(self, name, time_to_make, sell_price, xp, structure, ingredients=None):
        super().__init__(name, time_to_make, sell_price, xp, ingredients)
        self.structure = structure

        # Auto-register product to its tree/bush structure
        if self.structure:
            self.structure.product = self

    @property
    def unlock_level(self):
        """Dynamically fetches unlock_level from the associated structure."""
        if self.structure:
            return getattr(self.structure, "unlock_level", 1)
        return 1

    @unlock_level.setter
    def unlock_level(self, value):
        """
        Dummy setter so HayDayItem.__init__ setting self.unlock_level=1
        doesn't crash with AttributeError.
        """
        pass

    def is_unlocked(self, player_level):
        """Delegates directly to the structure's unlock requirement."""
        if self.structure:
            return self.structure.is_unlocked(player_level)
        return True