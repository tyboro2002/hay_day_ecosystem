# 1. Import all the individual Item collections
from .crops_data import CROPS
from .plants_data import PLANTS
from .animal_items_data import ANIMAL_ITEMS
from .animal_feeds_data import FEEDS
from .machined_items_data import MACHINED_ITEMS
from .special_items_data import SPECIAL_ITEMS

# 2. Import all Infrastructure & Entity collections
from .machines_data import MACHINES
from .animal_pens_data import PENS
from .plant_structures_data import STRUCTURES
from .special_structures_data import SPECIAL_STRUCTURES
from .animals_data import ANIMALS
from .fields_data import FARM_FIELDS

# =====================================================================
# GLOBAL CENTRAL REGISTRIES
# =====================================================================

DIAMOND_COST = 10000.0

# Combine all inventory-holding items together using the dictionary update operator (|)
ITEMS = {}
ITEMS |= CROPS
ITEMS |= PLANTS
ITEMS |= ANIMAL_ITEMS
ITEMS |= FEEDS
ITEMS |= MACHINED_ITEMS
ITEMS |= SPECIAL_ITEMS

# Group your world infrastructure together for easy simulator access
INFRASTRUCTURE = {
    "machines": MACHINES,
    "pens": PENS,
    "plant_structures": STRUCTURES,
    "special_structures": SPECIAL_STRUCTURES,
    "fields": FARM_FIELDS
}

# Group biological entities
LIVESTOCK = ANIMALS

# =====================================================================
# THE INGREDIENT RECIPE LINKER
# =====================================================================
# This loops through every item in our master registry. If it has an
# 'ingredients' attribute, it swaps the string keys for real object pointers.

for item_name, item_obj in ITEMS.items():
    if hasattr(item_obj, 'ingredients') and item_obj.ingredients:
        linked_ingredients = {}

        for ingredient_name, quantity in item_obj.ingredients.items():
            resolved_item_obj = ITEMS.get(ingredient_name)

            if resolved_item_obj:
                linked_ingredients[resolved_item_obj] = quantity
            else:
                print(f"[Warning] Could not resolve ingredient '{ingredient_name}' for item '{item_name}'")

        # Overwrite the old string-based dictionary with our object-based dictionary
        item_obj.ingredients = linked_ingredients

# =====================================================================
# DIAGNOSTIC CHECK
# =====================================================================
if __name__ == "__main__":
    print("==================================================")
    print("      HAY DAY ENGINE - CENTRAL REGISTRY          ")
    print("==================================================")

    print(f"\n[ITEMS LOADED: {len(ITEMS)} total]")
    for name, item_obj in ITEMS.items():
        print(f"  ↳ {name:<20} | Subclass: {type(item_obj).__name__}")

    print(f"\n[INFRASTRUCTURE LAUNCHED]")
    print(f"  ↳ Machines: {list(MACHINES.keys())}")
    print(f"  ↳ Animal Pens: {list(PENS.keys())}")
    print(f"  ↳ Structures: {list(STRUCTURES.keys())}")
    print(f"  ↳ Special Structures: {list(SPECIAL_STRUCTURES.keys())}")

    print(f"\n[LIVESTOCK BIOLOGY ACTIVE]")
    for name, animal_obj in LIVESTOCK.items():
        # Cleanly fallback to safe strings if an attribute evaluates to None
        pen_display = animal_obj.pen.name if animal_obj.pen else "None"
        prod_display = animal_obj.produces_item.name if animal_obj.produces_item else "None"
        food_display = animal_obj.required_food.name if animal_obj.required_food else "None"
        print(f"  ↳ {name:<10} lives in [{pen_display}], produces [{prod_display}], eats [{food_display}]")

    print("\n[RECIPE LINKER STATE SANITY CHECK]")
    # Let's verify a multiline recipe object link like Vanilla Ice Cream!
    ice_cream = ITEMS.get("Vanilla Ice Cream")
    if ice_cream and hasattr(ice_cream, 'ingredients'):
        print(f"  ↳ {ice_cream.name} Ingredients:")
        for obj_key, quantity in ice_cream.ingredients.items():
            print(f"    - Requires {quantity}x {obj_key.name} (Verified Object Type: {type(obj_key).__name__})")

    print("\n==================================================")