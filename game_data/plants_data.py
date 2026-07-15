import yaml
import os
from models import PlantableItem
from .plant_structures_data import STRUCTURES

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_input')

def load_plants_yaml(filepath):
    with open(filepath, 'r') as f:
        raw_data = yaml.safe_load(f)

    plants = {}
    for name, data in raw_data.items():
        # Look up the required structure object
        struct_obj = STRUCTURES.get(data.pop("struct_name"))

        # Instantiate the PlantableItem
        plants[name] = PlantableItem(
            name=name,
            structure=struct_obj,
            **data
        )
    return plants

# Registry initialization
YAML_PATH = os.path.join(DATA_DIR, 'plants.yaml')
PLANTS = load_plants_yaml(YAML_PATH)