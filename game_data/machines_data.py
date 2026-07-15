import yaml
import os
from models import HayDayMachine

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_input')

def load_machines_yaml(filepath):
    with open(filepath, 'r') as f:
        raw_data = yaml.safe_load(f)

    machines = {}
    for name, data in raw_data.items():
        machines[name] = HayDayMachine(name=name, **data)
    return machines

# Registry initialization
YAML_PATH = os.path.join(DATA_DIR, 'machines.yaml')
MACHINES = load_machines_yaml(YAML_PATH)