import yaml
import os
from models import Animal
from .animal_pens_data import PENS
from .animal_items_data import ANIMAL_ITEMS
from .animal_feeds_data import FEEDS

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_input')

def load_animals_yaml(filepath):
    with open(filepath, 'r') as f:
        raw_data = yaml.safe_load(f)

    animals = {}
    for name, data in raw_data.items():
        # Link the objects from the previously loaded registries
        animals[name] = Animal(
            name=name,
            pen=PENS.get(data["pen_name"]),
            item=ANIMAL_ITEMS.get(data["item_name"]),
            required_food=FEEDS.get(data["food_name"])
        )
    return animals

# Registry initialization
YAML_PATH = os.path.join(DATA_DIR, 'animals.yaml')
ANIMALS = load_animals_yaml(YAML_PATH)