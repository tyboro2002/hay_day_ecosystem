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

import visualizers.helpers.api_processors as proc

# V1 Paths
base_path = "/hay_day_ecosystem/api/v1/"
assets_path = "/hay_day_ecosystem/assets/"
details_path = "/hay_day_ecosystem/details/"
infrastructure_path = "/infrastructure/"

# V2 Registry Dictionary mapping: Directory -> (Data Collection, Process Function)
V2_COLLECTION_REGISTRY = {
    proc.machined_items_dir_v2: (MACHINED_ITEMS, proc.process_machined_item),
    proc.animal_feeds_dir_v2: (FEEDS, proc.process_animal_feed),
    proc.crops_dir_v2: (CROPS, proc.process_crop),
    proc.plants_dir_v2: (PLANTS, proc.process_plant),
    proc.animal_items_dir_v2: (ANIMAL_ITEMS, proc.process_animal_item),
    proc.special_items_dir_v2: (SPECIAL_ITEMS, proc.process_special_item),
    proc.machines_dir_v2: (INFRASTRUCTURE["machines"], proc.process_machine),
    proc.pens_dir_v2: (INFRASTRUCTURE["pens"], proc.process_pen),
    proc.plant_structures_dir_v2: (INFRASTRUCTURE["plant_structures"], proc.process_plant_structure),
    proc.special_structures_dir_v2: (INFRASTRUCTURE["special_structures"], proc.process_special_structure),
    proc.fields_dir_v2: (INFRASTRUCTURE["fields"], proc.process_field),
    proc.livestock_dir_v2: (ANIMALS, proc.process_animal)
}

# Fast Lookup Cache mapping: item_id -> directory_name
_ID_DIR_MAP = {}

def build_id_directory_map():
    """Builds a lookup cache mapping every item/entity ID to its folder name."""
    global _ID_DIR_MAP
    _ID_DIR_MAP.clear()
    for dir_name, (data_dict, _) in V2_COLLECTION_REGISTRY.items():
        for name in data_dict.keys():
            item_id = name.lower().replace(" ", "_").replace("-", "_")
            _ID_DIR_MAP[item_id] = dir_name

def get_dir_by_id(item_id):
    """
    Looks up which V2 directory an item_id belongs to.
    Returns directory string (e.g., 'crops') or None if not found.
    """
    if not _ID_DIR_MAP:
        build_id_directory_map()
    return _ID_DIR_MAP.get(item_id)


def build_static_api(output_dir="docs"):
    # build_v1(output_dir=output_dir)
    print("generated V1 API")
    build_v2(output_dir=output_dir)
    print("generated V2 API")


def build_v2(output_dir="docs"):
    api_dir = os.path.join(output_dir, "api", "v2")
    os.makedirs(api_dir, exist_ok=True)

    # Rebuild ID -> Directory cache map
    build_id_directory_map()

    # 1. Pre-index all items by their producing machine
    machine_products_map = defaultdict(list)
    for machined_item_name, machined_item_obj in ITEMS.items():
        producing_machine = getattr(machined_item_obj, 'machine', None)
        if producing_machine:
            machined_item_id = machined_item_name.lower().replace(" ", "_").replace("-", "_")
            target_dir = get_dir_by_id(machined_item_id) or proc.machined_items_dir_v2

            machine_products_map[producing_machine.name].append({
                "id": machined_item_id,
                "name": machined_item_name,
                "unlock_level": getattr(machined_item_obj, 'unlock_level', 1),
                "time_to_make_minutes": getattr(machined_item_obj, 'time_to_make', None),
                "links": {
                    "detail": f"{proc.base_path_v2}/{target_dir}/{machined_item_id}.json"
                }
            })

    # 2. Root API Endpoint (/api/index.json)
    root_payload = {
        "message": "Welcome to the Hay Day Static REST API V2 (this is still a WIP)",
        "_links": {
            "self": f"{proc.base_path_v2}/index.json",
            **{folder: f"{proc.base_path_v2}/{folder}/index.json" for folder in V2_COLLECTION_REGISTRY.keys()}
        }
    }
    with open(os.path.join(api_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(root_payload, f, indent=2)

    # 3. Generate all collections dynamically using registry
    for collection_dir, (items_dict, process_fn) in V2_COLLECTION_REGISTRY.items():
        generate_collection(
            api_dir,
            collection_dir,
            items_dict,
            process_fn,
            machine_products_map=machine_products_map
        )


def generate_collection(api_dir, collection_dir_name, items_dict, process_item_fn, machine_products_map=None):
    target_dir = os.path.join(api_dir, collection_dir_name)
    os.makedirs(target_dir, exist_ok=True)

    collection_summary = []

    for name, obj in items_dict.items():
        item_id = name.lower().replace(" ", "_").replace("-", "_")

        # Pass extra kwargs if required by special processors
        if process_item_fn == proc.process_machine:
            item_detail = process_item_fn(item_id, name, obj, machine_products_map)
        elif process_item_fn in (proc.process_machined_item, proc.process_animal_feed):
            item_detail = process_item_fn(item_id, name, obj, get_dir_by_id)
        else:
            item_detail = process_item_fn(item_id, name, obj)

        with open(os.path.join(target_dir, f"{item_id}.json"), "w", encoding="utf-8") as f:
            json.dump(item_detail, f, indent=2)

        # Build light summary item for index.json
        summary_item = {
            "id": item_id,
            "name": name,
            "links": {
                "detail": f"{proc.base_path_v2}/{collection_dir_name}/{item_id}.json",
                "image": item_detail.get("links", {}).get("image")
            }
        }

        # Include pricing and cost arrays directly in index summary if they exist
        if "sell_price" in item_detail:
            summary_item["sell_price"] = item_detail["sell_price"]
        if "coin_cost" in item_detail:
            summary_item["coin_cost"] = item_detail["coin_cost"]
        if "costs" in item_detail:
            summary_item["costs"] = item_detail["costs"]

        collection_summary.append(summary_item)

    index_payload = {
        "count": len(collection_summary),
        "items": collection_summary,
        "links": {
            "self": f"{proc.base_path_v2}/{collection_dir_name}/index.json",
            "parent": f"{proc.base_path_v2}/index.json"
        }
    }

    with open(os.path.join(target_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index_payload, f, indent=2)

# =====================================================================
# API V1 CODE
# =====================================================================
def build_v1(output_dir="docs"):
    api_dir = os.path.join(output_dir, "api", "v1")
    os.makedirs(api_dir, exist_ok=True)

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

    items_dir = os.path.join(api_dir, "items")
    os.makedirs(items_dir, exist_ok=True)

    items_collection = []

    for item_name, item_obj in ITEMS.items():
        item_id = item_name.lower().replace(" ", "_").replace("-", "_")

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

        with open(os.path.join(items_dir, f"{item_id}.json"), "w", encoding="utf-8") as f:
            json.dump(item_detail, f, indent=2)

        items_collection.append({
            "id": item_id,
            "name": item_name,
            "_links": {
                "detail": f"{base_path}items/{item_id}.json"
            }
        })

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

    infra_dir = os.path.join(api_dir, "infrastructure")
    os.makedirs(infra_dir, exist_ok=True)

    infra_collection = []

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