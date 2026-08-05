import os
import json
from collections import defaultdict

from game_data import ITEMS, INFRASTRUCTURE

prepart = ""
# prepart = "/hay_day_ecosystem"

base_path_v2 = f"{prepart}/api/v2"
machines_dir_v2 = "machines"
items_dir_v2 = "items"
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
    for item_name, item_obj in ITEMS.items():
        producing_machine = getattr(item_obj, 'machine', None)
        if producing_machine:
            item_id = item_name.lower().replace(" ", "_").replace("-", "_")

            item_data = {
                "id": item_id,
                "name": item_name,
                "unlock_level": getattr(item_obj, 'unlock_level', 1),
                "time_to_make_minutes": getattr(item_obj, 'time_to_make', None),
                "links": {
                    "detail": f"{base_path_v2}/{items_dir_v2}/{item_id}.json"
                }
            }

            # Key by machine name
            machine_products_map[producing_machine.name].append(item_data)

    # 1. Root API Endpoint (/api/index.json)
    root_payload = {
        "message": "Welcome to the Hay Day Static REST API V2 (this is still a WIP)",
        "_links": {
            "self": f"{base_path_v2}/index.json",
            "machines": f"{base_path_v2}/{machines_dir_v2}/index.json",
        }
    }
    with open(os.path.join(api_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(root_payload, f, indent=2)

    # 2. machines Endpoints (/machines/index.json & /machines/<id>.json)
    machines_dir = os.path.join(api_dir, machines_dir_v2)
    os.makedirs(machines_dir, exist_ok=True)

    machines_collection = []

    for machine_name, machine_obj in INFRASTRUCTURE["machines"].items():
        print(machine_name, "//", machine_obj)
        machine_id = machine_name.lower().replace(" ", "_").replace("-", "_")

        # Build individual machine detail file
        machine_detail = {
            "id": machine_id,
            "name": machine_name,
            "min_allowed_slots": getattr(machine_obj, 'min_allowed_slots', None),
            "max_allowed_slots": getattr(machine_obj, 'max_allowed_slots', None),
            "unlock_schedule": [
                {"level": comp[0], "extra_unlocks": comp[1]}
                for comp in (getattr(machine_obj, 'unlock_schedule', None) or [])
            ],
            "costs": getattr(machine_obj, 'costs', None),
            "mastery": format_mastery(machine_obj),
            "produces": machine_products_map.get(machine_name, []),
            "links": {
                "self": f"{base_path_v2}/{machines_dir_v2}/{machine_id}.json",
                "collection": f"{base_path_v2}/{machines_dir_v2}/index.json",
                "image": f"{assets_path_v2}/{machines_dir_v2}/{machine_id}.png",
                "html_details": f"{details_path_v2}/details_{machine_id}.html"
            }
        }
    #
        # Save single item detail JSON
        with open(os.path.join(machines_dir, f"{machine_id}.json"), "w", encoding="utf-8") as f:
            json.dump(machine_detail, f, indent=2)
    #
        # Append summary to collection index
        machines_collection.append({
            "id": machine_id,
            "name": machine_name,
            "links": {
                "detail": f"{base_path_v2}/{machines_dir_v2}/{machine_id}.json"
            }
        })

    # Save items collection index
    machines_index_payload = {
        "count": len(machines_collection),
        "items": machines_collection,
        "links": {
            "self": f"{base_path_v2}/{machines_dir_v2}/index.json",
            "parent": f"{base_path_v2}/index.json"
        }
    }
    with open(os.path.join(machines_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(machines_index_payload, f, indent=2)


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