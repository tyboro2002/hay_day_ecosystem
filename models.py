# =====================================================================
# 1. PRODUCTION PLACES (Machines & Animal Pens)
# =====================================================================

class HayDayMachine:
    def __init__(self, name, amount_owned, max_slots=2):
        self.name = name
        self.amount_owned = amount_owned
        self.max_slots = max_slots
        self.queue = [] # List of items currently queued
        self.products = []  # Items this machine can produce, automatically filled by MachinedItems

    def __repr__(self):
        return f"Machine: {self.name}"

    def total_queued_time(self):
        return sum(item.time_to_make for item in self.queue)


class AnimalPen:
    def __init__(self, name, amount_owned, max_capacity=5, current_capacity=5):
        self.name = name
        self.current_capacity = current_capacity
        self.max_capacity = max_capacity
        self.amount_owned = amount_owned
        self.animal = None   # Holds Animal objects living here
        self.products = []  # Items this pen can produce, automatically filled by AnimalItems

    def __repr__(self):
        return f"Pen: {self.name} ({self.current_capacity}/{self.max_capacity} animals) ({self.amount_owned} owned)"


class Animal:
    def __init__(self, name, pen, item=None, required_food=None):
        self.name = name
        self.pen = pen
        self.pen.animal = self # Auto-register animal to its home pen
        self.produces_item = item
        self.required_food = required_food  # Links to a MachinedItem instance (e.g., Chicken Feed)

    def __repr__(self):
        return self.name

class PlantableStructure:
    def __init__(self, name, coin_cost, max_harvests=4):
        self.name = name
        self.coin_cost = coin_cost  # Cost to buy the tree/bush seed from the shop
        self.max_harvests = max_harvests
        self.product = None  # Will hold the PlantableItem instance it grows

    def __repr__(self):
        return f"Structure: {self.name} (Cost: {self.coin_cost} coins)"

class Field:
    def __init__(self, amount_owned):
        self.name = "Field"
        self.amount_owned = amount_owned

    def __repr__(self):
        return f"{self.amount_owned} Fields"

class SpecialStructure:
    def __init__(self, name, amount_owned=1):
        self.name = name
        self.amount_owned = amount_owned

    def __repr__(self):
        return f"{self.name}"

# =====================================================================
# 2. ITEMS (Base Class & Subclasses)
# =====================================================================

class HayDayItem:
    """The base class for everything you can hold in your barn/silo."""
    def __init__(self, name, time_to_make, sell_price, xp, ingredients=None):
        self.name = name
        self.time_to_make = time_to_make  # in minutes
        self.sell_price = sell_price
        self.xp = xp                      # XP granted upon collection
        self.ingredients = ingredients or {}  # Will hold {Item_Object: quantity}

    def __repr__(self):
        return self.name


class Crop(HayDayItem):
    """Crops grown in fields. They don't need ingredients or specific machines."""
    def __init__(self, name, time_to_make, sell_price, xp, planted_on, yield_multiplier=2):
        super().__init__(name, time_to_make, sell_price, xp)
        self.yield_multiplier = yield_multiplier
        self.planted_on = planted_on


class AnimalItem(HayDayItem):
    """Items collected from animals (Eggs, Milk, Wool, etc.). Links to a Pen."""
    def __init__(self, name, time_to_make, sell_price, xp, pen, ingredients=None):
        super().__init__(name, time_to_make, sell_price, xp, ingredients)
        self.pen = pen

        # Auto-register product to the animal pen
        if self.pen:
            self.pen.products.append(self)


class MachinedItem(HayDayItem):
    """Products made in a machine (Bread, Sugar, Feed, etc.). Links to a Machine."""
    def __init__(self, name, time_to_make, sell_price, xp, machine, ingredients=None):
        super().__init__(name, time_to_make, sell_price, xp, ingredients)
        self.machine = machine

        # Auto-register product to the production machine
        if self.machine:
            self.machine.products.append(self)


class SpecialItem(HayDayItem):
    """Items like axes, dynamite, or expansion materials that aren't produced."""
    def __init__(self, name, sell_price, xp=0):
        # Time to make is 0 because they are found/looted, not crafted
        super().__init__(name, time_to_make=0, sell_price=sell_price, xp=xp)

class PlantableItem(HayDayItem):
    """Items harvested from trees or bushes (Apples, Cherries, Blackberries, etc.)."""
    def __init__(self, name, time_to_make, sell_price, xp, structure, ingredients=None):
        super().__init__(name, time_to_make, sell_price, xp, ingredients)
        self.structure = structure

        # Auto-register product to its tree/bush structure
        if self.structure:
            self.structure.product = self