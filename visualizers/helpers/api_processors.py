from game_data import ITEMS, INFRASTRUCTURE
from game_data.animal_feeds_data import FEEDS
from game_data.animal_items_data import ANIMAL_ITEMS
from game_data.animals_data import ANIMALS
from game_data.crops_data import CROPS
from game_data.machined_items_data import MACHINED_ITEMS
from game_data.plants_data import PLANTS
from game_data.special_items_data import SPECIAL_ITEMS

# prepart = ""
prepart = "/hay_day_ecosystem"
base_path_v2 = f"{prepart}/api/v2"
assets_path_v2 = f"{prepart}/assets"
details_path_v2 = f"{prepart}/details"

machines_dir_v2 = "machines"
machined_items_dir_v2 = "machined_items"
animal_feeds_dir_v2 = "animal_feeds"
crops_dir_v2 = "crops"
plants_dir_v2 = "plants"
animal_items_dir_v2 = "animal_items"
special_items_dir_v2 = "special_items"
pens_dir_v2 = "pens"
plant_structures_dir_v2 = "plant_structures"
special_structures_dir_v2 = "special_structures"
fields_dir_v2 = "fields"
livestock_dir_v2 = "animals"

general_items_dir_v2 = "items"
general_animals_dir_v2 = "animals"
general_fields_dir_v2 = "fields"
general_pens_dir_v2 = "pens"
general_plant_structures_dir_v2 = "plant_structures"
general_special_structures_dir_v2 = "special_structures"

def format_mastery(machine_obj):
    raw_mastery = getattr(machine_obj, 'mastery_config', None)
    if not raw_mastery:
        return None

    formatted = {}
    for star_key, star_data in raw_mastery.items():
        formatted[star_key] = {
            "hours_required": star_data.get("hours_required", 0),
            "coin_bonus": star_data.get("coin_bonus", 0.0),
            "xp_bonus": star_data.get("xp_bonus", 0.0),
            "speed_bonus": star_data.get("speed_bonus", 0.0),
        }
    return formatted

def process_machine(m_id, m_name, m_obj, machine_products_map):
    return {
        "id": m_id,
        "name": m_name,
        "min_allowed_slots": getattr(m_obj, 'min_allowed_slots', None),
        "max_allowed_slots": getattr(m_obj, 'max_allowed_slots', None),
        "unlock_schedule": [
            {"level": comp[0], "extra_unlocks": comp[1]}
            for comp in (getattr(m_obj, 'unlock_schedule', None) or [])
        ],
        "costs": getattr(m_obj, 'costs', None),
        "mastery": format_mastery(m_obj),
        "produces": machine_products_map.get(m_name, []),
        "links": {
            "self": f"{base_path_v2}/{machines_dir_v2}/{m_id}.json",
            "collection": f"{base_path_v2}/{machines_dir_v2}/index.json",
            "image": f"{assets_path_v2}/{machines_dir_v2}/{m_id}.png",
            "html_details": f"{details_path_v2}/details_{m_id}.html"
        }
    }

def process_machined_item(item_id, item_name, item_obj, get_dir_fn):
    formatted_ingredients = []
    if hasattr(item_obj, 'ingredients') and item_obj.ingredients:
        for ing_obj, single_qty in item_obj.ingredients.items():
            ing_id = ing_obj.name.lower().replace(" ", "_").replace("-", "_")
            ing_dir = get_dir_fn(ing_id) or machined_items_dir_v2

            formatted_ingredients.append({
                "id": ing_id,
                "name": ing_obj.name,
                "quantity": single_qty,
                "links": {
                    "detail": f"{base_path_v2}/{ing_dir}/{ing_id}.json"
                }
            })

    return {
        "id": item_id,
        "name": item_name,
        "unlock_level": getattr(item_obj, 'unlock_level', None),
        "time_to_make": getattr(item_obj, 'time_to_make', None),
        "sell_price": getattr(item_obj, 'sell_price', None),
        "xp": getattr(item_obj, 'xp', None),
        "ingredients": formatted_ingredients,
        "links": {
            "self": f"{base_path_v2}/{machined_items_dir_v2}/{item_id}.json",
            "collection": f"{base_path_v2}/{machined_items_dir_v2}/index.json",
            "image": f"{assets_path_v2}/{general_items_dir_v2}/{item_id}.png",
            "html_details": f"{details_path_v2}/details_{item_id}.html"
        }
    }

def process_animal_feed(feed_id, feed_name, feed_obj, get_dir_fn):
    if " Feed" in feed_name:
        animal_name = feed_name.replace(" Feed", "")
        animal_id = animal_name.lower().replace(" ", "_").replace("-", "_")
        feeds_animal_link = f"{base_path_v2}/{livestock_dir_v2}/{animal_id}.json"
    else:
        feeds_animal_link = None

    formatted_batch_ingredients = []
    if hasattr(feed_obj, 'ingredients') and feed_obj.ingredients:
        for ing_obj, single_qty in feed_obj.ingredients.items():
            ing_id = ing_obj.name.lower().replace(" ", "_").replace("-", "_")
            ing_dir = get_dir_fn(ing_id) or crops_dir_v2
            batch_qty = int(round(single_qty * 3))

            formatted_batch_ingredients.append({
                "id": ing_id,
                "name": ing_obj.name,
                "quantity": batch_qty,
                "links": {
                    "detail": f"{base_path_v2}/{ing_dir}/{ing_id}.json"
                }
            })

    return {
        "id": feed_id,
        "name": feed_name,
        "feeds_animal": feeds_animal_link,
        "unlock_level": getattr(feed_obj, 'unlock_level', None),
        "time_to_make": getattr(feed_obj, 'time_to_make', None),
        "sell_price": getattr(feed_obj, 'sell_price', None),
        "xp": getattr(feed_obj, 'xp', None),
        "batch_size": 3,
        "batch_ingredients": formatted_batch_ingredients,
        "links": {
            "self": f"{base_path_v2}/{animal_feeds_dir_v2}/{feed_id}.json",
            "collection": f"{base_path_v2}/{animal_feeds_dir_v2}/index.json",
            "image": f"{assets_path_v2}/{general_items_dir_v2}/{feed_id}.png",
            "html_details": f"{details_path_v2}/details_{feed_id}.html"
        }
    }

def process_crop(crop_id, crop_name, crop_obj):
    return {
        "id": crop_id,
        "name": crop_name,
        "unlock_level": getattr(crop_obj, 'unlock_level', None),
        "time_to_make": getattr(crop_obj, 'time_to_make', None),
        "sell_price": getattr(crop_obj, 'sell_price', None),
        "xp": getattr(crop_obj, 'xp', None),
        "yield_multiplier": getattr(crop_obj, 'yield_multiplier', None),
        "links": {
            "self": f"{base_path_v2}/{crops_dir_v2}/{crop_id}.json",
            "collection": f"{base_path_v2}/{crops_dir_v2}/index.json",
            "image": f"{assets_path_v2}/{general_items_dir_v2}/{crop_id}.png",
            "html_details": f"{details_path_v2}/details_{crop_id}.html"
        }
    }

def process_plant(plant_id, plant_name, plant_obj):
    return {
        "id": plant_id,
        "name": plant_name,
        "links": {
            "self": f"{base_path_v2}/{plants_dir_v2}/{plant_id}.json",
            "collection": f"{base_path_v2}/{plants_dir_v2}/index.json",
            "image": f"{assets_path_v2}/{general_items_dir_v2}/{plant_id}.png",
            "html_details": f"{details_path_v2}/details_{plant_id}.html"
        }
    }

def process_animal_item(animal_item_id, animal_item_name, animal_item_obj):
    return {
        "id": animal_item_id,
        "name": animal_item_name,
        "links": {
            "self": f"{base_path_v2}/{animal_items_dir_v2}/{animal_item_id}.json",
            "collection": f"{base_path_v2}/{animal_items_dir_v2}/index.json",
            "image": f"{assets_path_v2}/{general_items_dir_v2}/{animal_item_id}.png",
            "html_details": f"{details_path_v2}/details_{animal_item_id}.html"
        }
    }

def process_special_item(special_item_id, special_item_name, special_item_obj):
    return {
        "id": special_item_id,
        "name": special_item_name,
        "links": {
            "self": f"{base_path_v2}/{special_items_dir_v2}/{special_item_id}.json",
            "collection": f"{base_path_v2}/{special_items_dir_v2}/index.json",
            "image": f"{assets_path_v2}/{general_items_dir_v2}/{special_item_id}.png",
            "html_details": f"{details_path_v2}/details_{special_item_id}.html"
        }
    }

def process_pen(pen_id, pen_name, pen_obj):
    return {
        "id": pen_id,
        "name": pen_name,
        "links": {
            "self": f"{base_path_v2}/{pens_dir_v2}/{pen_id}.json",
            "collection": f"{base_path_v2}/{pens_dir_v2}/index.json",
            "image": f"{assets_path_v2}/{general_pens_dir_v2}/{pen_id}.png",
            "html_details": f"{details_path_v2}/details_{pen_id}.html"
        }
    }

def process_plant_structure(plant_structure_id, plant_structure_name, plant_structure_obj):
    return {
        "id": plant_structure_id,
        "name": plant_structure_name,
        "links": {
            "self": f"{base_path_v2}/{plant_structures_dir_v2}/{plant_structure_id}.json",
            "collection": f"{base_path_v2}/{plant_structures_dir_v2}/index.json",
            "image": f"{assets_path_v2}/{general_plant_structures_dir_v2}/{plant_structure_id}.png",
            "html_details": f"{details_path_v2}/details_{plant_structure_id}.html"
        }
    }

def process_special_structure(special_structure_id, special_structure_name, special_structure_obj):
    return {
        "id": special_structure_id,
        "name": special_structure_name,
        "links": {
            "self": f"{base_path_v2}/{special_structures_dir_v2}/{special_structure_id}.json",
            "collection": f"{base_path_v2}/{special_structures_dir_v2}/index.json",
            "image": f"{assets_path_v2}/{general_special_structures_dir_v2}/{special_structure_id}.png",
            "html_details": f"{details_path_v2}/details_{special_structure_id}.html"
        }
    }

def process_field(field_id, field_name, field_obj):
    return {
        "id": field_id,
        "name": field_name,
        "links": {
            "self": f"{base_path_v2}/{fields_dir_v2}/{field_id}.json",
            "collection": f"{base_path_v2}/{fields_dir_v2}/index.json",
            "image": f"{assets_path_v2}/{general_fields_dir_v2}/{field_id}.png",
            "html_details": f"{details_path_v2}/details_{field_id}.html"
        }
    }

def process_animal(animal_id, animal_name, animal_obj):
    return {
        "id": animal_id,
        "name": animal_name,
        "links": {
            "self": f"{base_path_v2}/{livestock_dir_v2}/{animal_id}.json",
            "collection": f"{base_path_v2}/{livestock_dir_v2}/index.json",
            "image": f"{assets_path_v2}/{general_animals_dir_v2}/{animal_id}.png",
            "html_details": f"{details_path_v2}/details_{animal_id}.html"
        }
    }