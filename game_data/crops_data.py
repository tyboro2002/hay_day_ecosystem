import os
import yaml
from models import Crop
from .fields_data import FARM_FIELDS

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_input')

def load_crops_yaml(filepath):
    with open(filepath, 'r') as f:
        # safe_load is now all you need
        data = yaml.safe_load(f)

    crops = {}
    for name, params in data.items():
        # Directly pass the dictionary to the constructor
        crops[name] = Crop(name=name, planted_on=FARM_FIELDS, **params)
    return crops

# Define the path to the JSON file
YAML_PATH = os.path.join(DATA_DIR, 'crops.yaml')
CROPS = load_crops_yaml(YAML_PATH)
