import yaml
import os
from models import SpecialItem

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_input')

def load_special_items_yaml(filepath):
    with open(filepath, 'r') as f:
        raw_data = yaml.safe_load(f)

    special_items = {}
    for name, data in raw_data.items():
        special_items[name] = SpecialItem(name=name, **data)
    return special_items

# Registry initialization
YAML_PATH = os.path.join(DATA_DIR, 'special_items.yaml')
SPECIAL_ITEMS = load_special_items_yaml(YAML_PATH)