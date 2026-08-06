import os
import json
from collections import defaultdict

from game_data import ITEMS, INFRASTRUCTURE
from game_data.animal_feeds_data import FEEDS
from game_data.animal_items_data import ANIMAL_ITEMS
from game_data.animals_data import ANIMALS
from game_data.crops_data import CROPS
from game_data.machined_items_data import MACHINED_ITEMS
from game_data.plants_data import PLANTS
from game_data.special_items_data import SPECIAL_ITEMS

# TODO maybe assets of mastery
# TODO maybe assets of storage

# prepart = ""
prepart = "/hay_day_ecosystem"

base_path_v2 = f"{prepart}/api/v2"
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
assets_path_v2 = f"{prepart}/assets"
details_path_v2 = f"{prepart}/details"


base_path = "/hay_day_ecosystem/api/v1/"
assets_path = "/hay_day_ecosystem/assets/"
details_path = "/hay_day_ecosystem/details/"
infrastructure_path = "/infrastructure/"

# Relative base path strategy to ensure compatibility across local & GitHub Pages
def build_static_api(output_dir="docs"):
    # build_v1(output_dir=output_dir)
    print("generated V1 API")
    build_v2(output_dir=output_dir)
    print("generated V2 API")

def build_v1(output_dir="docs"):
    api_dir = os.path.join(output_dir, "api", "v1")
    os.makedirs(api_dir, exist_ok=True)

    # 1. Root API Endpoint (/api/index.json)
    root_payload = {
        "message": "Welcome to the Hay Day Static REST API",
        "_links": {
            "self": f"{base_path}index.json",
            "items": f"{base_path}items/index.json",
            "infrastructure": f"{base_path}infrastructure/index.json"
        }
    }
    with open(os.path.join(api_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(root_payload, f, indent=2)

    # 2. Items Endpoints (/api/items/index.json & /api/items/<id>.json)
    items_dir = os.path.join(api_dir, "items")
    os.makedirs(items_dir, exist_ok=True)

    items_collection = []

    for item_name, item_obj in ITEMS.items():
        item_id = item_name.lower().replace(" ", "_").replace("-", "_")

        # Build individual item detail file
        item_detail = {
            "id": item_id,
            "name": item_name,
            "sell_price": getattr(item_obj, 'sell_price', None),
            "unlock_level": getattr(item_obj, 'unlock_level', 1),
            "time_to_make_minutes": getattr(item_obj, 'time_to_make', None),
            "_links": {
                "self": f"{base_path}items/{item_id}.json",
                "collection": f"{base_path}items/index.json",
                "image": f"{assets_path}items/{item_id}.png",
                "html_details": f"{details_path}details_{item_id}.html"
            }
        }

        # Handle Ingredients Links
        if hasattr(item_obj, 'ingredients') and item_obj.ingredients:
            item_detail["ingredients"] = []
            for ing_obj, qty in item_obj.ingredients.items():
                ing_id = ing_obj.name.lower().replace(" ", "_").replace("-", "_")
                item_detail["ingredients"].append({
                    "name": ing_obj.name,
                    "quantity": qty,
                    "_links": {
                        "detail": f"{base_path}items/{ing_id}.json"
                    }
                })

        # Save single item detail JSON
        with open(os.path.join(items_dir, f"{item_id}.json"), "w", encoding="utf-8") as f:
            json.dump(item_detail, f, indent=2)

        # Append summary to collection index
        items_collection.append({
            "id": item_id,
            "name": item_name,
            "_links": {
                "detail": f"{base_path}items/{item_id}.json"
            }
        })

    # Save items collection index
    items_index_payload = {
        "count": len(items_collection),
        "items": items_collection,
        "_links": {
            "self": f"{base_path}items/index.json",
            "parent": f"{base_path}index.json"
        }
    }
    with open(os.path.join(items_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(items_index_payload, f, indent=2)

    # 3. Infrastructure Endpoints (/api/infrastructure/index.json)
    infra_dir = os.path.join(api_dir, "infrastructure")
    os.makedirs(infra_dir, exist_ok=True)

    infra_collection = []

    # Process machines, fields, etc.
    all_infra = {}
    for cat_name, category in INFRASTRUCTURE.items():
        if isinstance(category, dict):
            for name, obj in category.items():
                all_infra[name] = (cat_name, obj)

    for infra_name, (cat_folder, infra_obj) in all_infra.items():
        infra_id = infra_name.lower().replace(" ", "_").replace("-", "_")

        infra_detail = {
            "id": infra_id,
            "name": infra_name,
            "category": cat_folder,
            "unlock_level": getattr(infra_obj, 'unlock_level', 1),
            "_links": {
                "self": f"{base_path[:-1]}{infrastructure_path}{infra_id}.json",
                "collection": f"{base_path[:-1]}{infrastructure_path}index.json",
                "image": f"{assets_path}{cat_folder}/{infra_id}.png"
            }
        }

        with open(os.path.join(infra_dir, f"{infra_id}.json"), "w", encoding="utf-8") as f:
            json.dump(infra_detail, f, indent=2)

        infra_collection.append({
            "id": infra_id,
            "name": infra_name,
            "_links": {
                "detail": f"{base_path[:-1]}{infrastructure_path}{infra_id}.json"
            }
        })

    infra_index_payload = {
        "count": len(infra_collection),
        "infrastructure": infra_collection,
        "_links": {
            "self": f"{base_path[:-1]}{infrastructure_path}index.json",
            "parent": f"{base_path}index.json"
        }
    }
    with open(os.path.join(infra_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(infra_index_payload, f, indent=2)

    print("Static REST API successfully built in docs/api/")

def build_v2(output_dir="docs"):
    api_dir = os.path.join(output_dir, "api", "v2")
    os.makedirs(api_dir, exist_ok=True)

    # 1. Pre-index all items by their producing machine once
    machine_products_map = defaultdict(list)
    for machined_item_name, machined_item_obj in ITEMS.items():
        producing_machine = getattr(machined_item_obj, 'machine', None)
        if producing_machine:
            machined_item_id = machined_item_name.lower().replace(" ", "_").replace("-", "_")

            # Route feed mill items to animal_feeds_dir_v2, others to machined_items_dir_v2
            target_dir = (
                animal_feeds_dir_v2
                if producing_machine.name.lower().replace(" ", "_") == "feed_mill"
                else machined_items_dir_v2
            )

            machine_products_map[producing_machine.name].append({
                "id": machined_item_id,
                "name": machined_item_name,
                "unlock_level": getattr(machined_item_obj, 'unlock_level', 1),
                "time_to_make_minutes": getattr(machined_item_obj, 'time_to_make', None),
                "links": {
                    "detail": f"{base_path_v2}/{target_dir}/{machined_item_id}.json"
                }
            })

    # 2. Root API Endpoint (/api/index.json)
    root_payload = {
        "message": "Welcome to the Hay Day Static REST API V2 (this is still a WIP)",
        "_links": {
            "self": f"{base_path_v2}/index.json",
            "machined_items": f"{base_path_v2}/{machined_items_dir_v2}/index.json",
            "animal_feeds": f"{base_path_v2}/{animal_feeds_dir_v2}/index.json",
            "crops": f"{base_path_v2}/{crops_dir_v2}/index.json",
            "plants": f"{base_path_v2}/{plants_dir_v2}/index.json",
            "animal_items": f"{base_path_v2}/{animal_items_dir_v2}/index.json",
            "special_items": f"{base_path_v2}/{special_items_dir_v2}/index.json",

            "machines": f"{base_path_v2}/{machines_dir_v2}/index.json",
            "pens": f"{base_path_v2}/{pens_dir_v2}/index.json",
            "plant_structures": f"{base_path_v2}/{plant_structures_dir_v2}/index.json",
            "special_structures": f"{base_path_v2}/{special_structures_dir_v2}/index.json",
            "fields": f"{base_path_v2}/{fields_dir_v2}/index.json",

            "animals": f"{base_path_v2}/{livestock_dir_v2}/index.json",
        }
    }
    with open(os.path.join(api_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(root_payload, f, indent=2)

    # 3. Helper to format machine detail payloads
    def process_machine(m_id, m_name, m_obj):
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

    # 4. Helper to format machined item detail payloads
    def process_machined_item(item_id, item_name, item_obj):
        return {
            "id": item_id,
            "name": item_name,
            "links": {
                "self": f"{base_path_v2}/{machined_items_dir_v2}/{item_id}.json",
                "collection": f"{base_path_v2}/{machined_items_dir_v2}/index.json",
                "image": f"{assets_path_v2}/{general_items_dir_v2}/{item_id}.png",
                "html_details": f"{details_path_v2}/details_{item_id}.html"
            }
        }

    def process_animal_feed(feed_id, feed_name, feed_obj):
        if " Feed" in feed_name:
            animal_name = feed_name.replace(" Feed", "")
            animal_id = animal_name.lower().replace(" ", "_").replace("-", "_")
            feeds_animal_link = f"{base_path_v2}/{livestock_dir_v2}/{animal_id}.json"
        # elif feed_name == "Wheat Bundle":
        #     # Special case: Sanctuary / Farm Animals if applicable
        #     feeds_animal_link = f"{base_path_v2}/{livestock_dir_v2}/sanctuary_animals.json"
        # elif feed_name == "Meat Bucket":
        #     # Special case: Carnivores / Sanctuary Animals
        #     feeds_animal_link = f"{base_path_v2}/{livestock_dir_v2}/sanctuary_carnivores.json"
        else:
            feeds_animal_link = None

        return {
            "id": feed_id,
            "name": feed_name,
            "feeds_animal": feeds_animal_link,
            # "unlock_level": feed_obj.unlock_level,
            # "time_to_make": feed_obj.time_to_make,
            # "sell_price": feed_obj.sell_price,
            # "xp": feed_obj.xp,
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

    # 5. Run generator for all collections
    generate_collection(api_dir, machined_items_dir_v2, MACHINED_ITEMS, process_machined_item)
    generate_collection(api_dir, animal_feeds_dir_v2, FEEDS, process_animal_feed)
    generate_collection(api_dir, crops_dir_v2, CROPS, process_crop)
    generate_collection(api_dir, plants_dir_v2, PLANTS, process_plant)
    generate_collection(api_dir, animal_items_dir_v2, ANIMAL_ITEMS, process_animal_item)
    generate_collection(api_dir, special_items_dir_v2, SPECIAL_ITEMS, process_special_item)

    generate_collection(api_dir, machines_dir_v2, INFRASTRUCTURE["machines"], process_machine)
    generate_collection(api_dir, pens_dir_v2, INFRASTRUCTURE["pens"], process_pen)
    generate_collection(api_dir, plant_structures_dir_v2, INFRASTRUCTURE["plant_structures"], process_plant_structure)
    generate_collection(api_dir, special_structures_dir_v2, INFRASTRUCTURE["special_structures"], process_special_structure)
    generate_collection(api_dir, fields_dir_v2, INFRASTRUCTURE["fields"], process_field)

    generate_collection(api_dir, livestock_dir_v2, ANIMALS, process_animal)


def generate_collection(api_dir, collection_dir_name, items_dict, process_item_fn):
    """
    Generic generator for a REST collection directory.
    - Saves individual item files (<id>.json)
    - Saves collection index file (index.json)
    """
    target_dir = os.path.join(api_dir, collection_dir_name)
    os.makedirs(target_dir, exist_ok=True)

    collection_summary = []

    for name, obj in items_dict.items():
        item_id = name.lower().replace(" ", "_").replace("-", "_")

        # Delegate individual payload construction to the callback
        item_detail = process_item_fn(item_id, name, obj)

        # 1. Save individual item detail JSON
        with open(os.path.join(target_dir, f"{item_id}.json"), "w", encoding="utf-8") as f:
            json.dump(item_detail, f, indent=2)

        # 2. Add summary link to collection index
        collection_summary.append({
            "id": item_id,
            "name": name,
            "links": {
                "detail": f"{base_path_v2}/{collection_dir_name}/{item_id}.json"
            }
        })

    # 3. Save collection index
    index_payload = {
        "count": len(collection_summary),
        "items": collection_summary,
        "links": {
            "self": f"{base_path_v2}/{collection_dir_name}/index.json",
            "parent": f"{base_path_v2}/index.json"
        }
    }

    with open(os.path.join(target_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index_payload, f, indent=2)

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