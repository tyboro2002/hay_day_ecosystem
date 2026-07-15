import os
import yaml
from models import MachinedItem
from .machines_data import MACHINES

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_input')

def load_feeds_yaml(filepath):
    with open(filepath, 'r') as f:
        raw_data = yaml.safe_load(f)

    # HARDCODED: Access the Feed Mill object once
    feed_mill = MACHINES.get("Feed Mill")
    if feed_mill is None:
        raise ValueError("Feed Mill not found in machines data")
    feeds = {}
    for name, data in raw_data.items():
        batch_recipe = data.pop("batch_recipe")
        single_unit_ingredients = {item: qty / 3 for item, qty in batch_recipe.items()}

        feeds[name] = MachinedItem(
            name=name,
            machine=feed_mill,  # Using the hardcoded object
            ingredients=single_unit_ingredients,
            **data
        )
    return feeds

# Define the path to the JSON file
YAML_PATH = os.path.join(DATA_DIR, 'animal_feeds.yaml')
FEEDS = load_feeds_yaml(YAML_PATH)