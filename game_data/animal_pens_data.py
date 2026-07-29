import yaml
import os
from models import AnimalPen

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_input')

def load_pens_yaml(filepath):
    with open(filepath, 'r') as f:
        raw_data = yaml.safe_load(f)

    pens = {}
    for name, data in raw_data.items():
        # Converts list of lists [[1, 1], [12, 1]] into tuples if needed
        if 'unlock_schedule' in data:
            data['unlock_schedule'] = [tuple(item) for item in data['unlock_schedule']]

        pens[name] = AnimalPen(name=name, **data)
    return pens

# This registry is now accessible to the rest of your app
YAML_PATH = os.path.join(DATA_DIR, 'animal_pens.yaml')
PENS = load_pens_yaml(YAML_PATH)