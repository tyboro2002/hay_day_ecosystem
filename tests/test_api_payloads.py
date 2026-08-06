import pytest
import visualizers.helpers.api_processors as proc
from game_data.animals_data import ANIMALS
from visualizers.helpers.generate_static_api import get_dir_by_id
from game_data import ITEMS, INFRASTRUCTURE
from game_data.animal_feeds_data import FEEDS
from game_data.animal_items_data import ANIMAL_ITEMS
from game_data.crops_data import CROPS
from game_data.machined_items_data import MACHINED_ITEMS
from game_data.plants_data import PLANTS
from game_data.special_items_data import SPECIAL_ITEMS

# =====================================================================
# ALLOWED NULL / EMPTY EXCEPTIONS REGISTRY
# Format: (entity_id, field_path)
# =====================================================================
ALLOWED_EMPTY_FIELDS = {
    ("lobster_tail", "ingredients"),
    ("duck_feather", "ingredients"),
    ("wheat_bundle", "feeds_animal"),
    ("fish_fillet", "collected_from"),
    ("diamond", "sell_price"),
    ("meat_bucket", "feeds_animal"),
    ("fish_fillet", "produced_by_animal"),
    ("lobster_pool", "mastery"),
    ("duck_salon", "mastery"),
    ("bee", "required_food"),
    ("squirrel", "required_food"),
}


def assert_no_unallowed_empty_values(data, entity_id, path=""):
    """
    Recursively inspects dicts and lists to ensure no None, [], or {} values
    exist unless explicitly declared in ALLOWED_EMPTY_FIELDS.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key

            # Check if this specific field path is exempted
            if (entity_id, current_path) in ALLOWED_EMPTY_FIELDS:
                continue

            # Check for None / Null
            assert value is not None, (
                f"Unexpected None at field '{current_path}' for entity '{entity_id}'"
            )

            # Check for empty dicts
            if isinstance(value, dict):
                assert len(value) > 0, (
                    f"Unexpected empty dict at '{current_path}' for entity '{entity_id}'"
                )
                assert_no_unallowed_empty_values(value, entity_id, current_path)

            # Check for empty lists
            elif isinstance(value, list):
                assert len(value) > 0, (
                    f"Unexpected empty list at '{current_path}' for entity '{entity_id}'"
                )
                for i, item in enumerate(value):
                    assert_no_unallowed_empty_values(item, entity_id, f"{current_path}[{i}]")

    elif isinstance(data, list):
        assert len(data) > 0, f"Unexpected empty list at '{path}' for entity '{entity_id}'"
        for i, item in enumerate(data):
            assert_no_unallowed_empty_values(item, entity_id, f"{path}[{i}]")


# =====================================================================
# PYTEST SUITE FOR ALL PROCESSORS
# =====================================================================

def test_machined_items_payloads():
    for name, obj in MACHINED_ITEMS.items():
        item_id = name.lower().replace(" ", "_").replace("-", "_")
        payload = proc.process_machined_item(item_id, name, obj, get_dir_by_id)
        assert_no_unallowed_empty_values(payload, item_id)


def test_animal_feeds_payloads():
    for name, obj in FEEDS.items():
        feed_id = name.lower().replace(" ", "_").replace("-", "_")
        payload = proc.process_animal_feed(feed_id, name, obj, get_dir_by_id)
        assert_no_unallowed_empty_values(payload, feed_id)


def test_crops_payloads():
    for name, obj in CROPS.items():
        crop_id = name.lower().replace(" ", "_").replace("-", "_")
        payload = proc.process_crop(crop_id, name, obj)
        assert_no_unallowed_empty_values(payload, crop_id)


def test_plants_payloads():
    for name, obj in PLANTS.items():
        plant_id = name.lower().replace(" ", "_").replace("-", "_")
        payload = proc.process_plant(plant_id, name, obj)
        assert_no_unallowed_empty_values(payload, plant_id)


def test_animal_items_payloads():
    for name, obj in ANIMAL_ITEMS.items():
        item_id = name.lower().replace(" ", "_").replace("-", "_")
        payload = proc.process_animal_item(item_id, name, obj)
        assert_no_unallowed_empty_values(payload, item_id)


def test_special_items_payloads():
    for name, obj in SPECIAL_ITEMS.items():
        item_id = name.lower().replace(" ", "_").replace("-", "_")
        payload = proc.process_special_item(item_id, name, obj)
        assert_no_unallowed_empty_values(payload, item_id)


def test_machines_payloads():
    # Pre-build dummy machine map for machines test
    machine_products_map = {m_name: [{"id": "item", "name": "Item"}] for m_name in INFRASTRUCTURE["machines"]}

    for name, obj in INFRASTRUCTURE["machines"].items():
        m_id = name.lower().replace(" ", "_").replace("-", "_")
        payload = proc.process_machine(m_id, name, obj, machine_products_map)
        assert_no_unallowed_empty_values(payload, m_id)


def test_pens_payloads():
    for name, obj in INFRASTRUCTURE["pens"].items():
        pen_id = name.lower().replace(" ", "_").replace("-", "_")
        payload = proc.process_pen(pen_id, name, obj)
        assert_no_unallowed_empty_values(payload, pen_id)


def test_plant_structures_payloads():
    for name, obj in INFRASTRUCTURE["plant_structures"].items():
        ps_id = name.lower().replace(" ", "_").replace("-", "_")
        payload = proc.process_plant_structure(ps_id, name, obj)
        assert_no_unallowed_empty_values(payload, ps_id)


def test_special_structures_payloads():
    for name, obj in INFRASTRUCTURE["special_structures"].items():
        ss_id = name.lower().replace(" ", "_").replace("-", "_")
        payload = proc.process_special_structure(ss_id, name, obj)
        assert_no_unallowed_empty_values(payload, ss_id)


def test_fields_payloads():
    for name, obj in INFRASTRUCTURE["fields"].items():
        field_id = name.lower().replace(" ", "_").replace("-", "_")
        payload = proc.process_field(field_id, name, obj)
        assert_no_unallowed_empty_values(payload, field_id)


def test_livestock_payloads():
    for name, obj in ANIMALS.items():
        animal_id = name.lower().replace(" ", "_").replace("-", "_")
        payload = proc.process_animal(animal_id, name, obj)
        assert_no_unallowed_empty_values(payload, animal_id)