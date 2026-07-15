import yaml
import os
from models import AnimalItem
from .animal_pens_data import PENS

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_input')

def load_animal_items_yaml(filepath):
    with open(filepath, 'r') as f:
        raw_data = yaml.safe_load(f)

    animal_items = {}
    for name, data in raw_data.items():
        # Handle the pen mapping
        pen_name = data.pop("pen_name")
        pen_obj = PENS.get(pen_name) if pen_name else None

        # Instantiate
        animal_items[name] = AnimalItem(
            name=name,
            pen=pen_obj,
            **data
        )
    return animal_items

YAML_PATH = os.path.join(DATA_DIR, 'animal_items.yaml')
ANIMAL_ITEMS = load_animal_items_yaml(YAML_PATH)