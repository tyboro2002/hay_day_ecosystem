import yaml
import os
from models import HayDayMachine

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_input')

def load_machines_yaml(filepath):
    with open(filepath, 'r') as f:
        raw_data = yaml.safe_load(f)

    machines = {}
    for name, data in raw_data.items():
        # Convert list of lists [[lvl, amt], ...] to list of tuples [(lvl, amt), ...]
        if 'unlock_schedule' in data and data['unlock_schedule']:
            data['unlock_schedule'] = [tuple(entry) for entry in data['unlock_schedule']]

        # Instantiate HayDayMachine with the unpacked data dictionary
        machines[name] = HayDayMachine(name=name, **data)

    return machines

# Registry initialization
YAML_PATH = os.path.join(DATA_DIR, 'machines.yaml')
MACHINES = load_machines_yaml(YAML_PATH)