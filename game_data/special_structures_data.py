import yaml
import os
from models import SpecialStructure

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_input')

def load_special_structures_yaml(filepath):
    with open(filepath, 'r') as f:
        raw_data = yaml.safe_load(f)

    special_structures = {}
    for name, data in raw_data.items():
        special_structures[name] = SpecialStructure(name=name, **data)
    return special_structures

# Registry initialization
YAML_PATH = os.path.join(DATA_DIR, 'special_structures.yaml')
SPECIAL_STRUCTURES = load_special_structures_yaml(YAML_PATH)