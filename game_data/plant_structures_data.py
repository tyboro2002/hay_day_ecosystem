import yaml
import os
from models import PlantableStructure

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_input')

def load_structures_yaml(filepath):
    with open(filepath, 'r') as f:
        raw_data = yaml.safe_load(f)

    structures = {}
    for name, data in raw_data.items():
        structures[name] = PlantableStructure(name=name, **data)
    return structures

# Registry initialization
YAML_PATH = os.path.join(DATA_DIR, 'plantable_structures.yaml')
STRUCTURES = load_structures_yaml(YAML_PATH)