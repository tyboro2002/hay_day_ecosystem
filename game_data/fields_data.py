import yaml
import os
from models import Field

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_input')

def load_fields_yaml(filepath):
    with open(filepath, 'r') as f:
        raw_data = yaml.safe_load(f)

    # Extract the data and initialize the Field object
    fields_data = raw_data['fields']
    return {"fields": Field(**fields_data)}

# Initialize the registry
YAML_PATH = os.path.join(DATA_DIR, 'fields.yaml')
FARM_FIELDS = load_fields_yaml(YAML_PATH)

# print("Level | Max Fields Unlocked")
# print("-" * 25)
#
# for lvl in range(1, 52):
#     max_fields = Field.max_allowed_at_level(lvl)
#     print(f"Lvl {lvl:2d} | {max_fields} fields")