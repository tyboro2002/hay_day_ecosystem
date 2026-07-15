import yaml
import os
from models import MachinedItem
from .machines_data import MACHINES

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_input')

def load_machined_items_reverse():
    machines_dir = os.path.join(DATA_DIR, 'machines')
    machined_items = {}

    # Iterate through the MACHINES registry first
    for machine_name, machine_obj in MACHINES.items():
        # Convert "Feed Mill" to "feed_mill.yaml"
        filename = f"{machine_name.lower().replace(' ', '_')}.yaml"
        filepath = os.path.join(machines_dir, filename)

        # Check if the file exists for this machine
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                items_data = yaml.safe_load(f)

            if items_data:
                for name, data in items_data.items():
                    machined_items[name] = MachinedItem(
                        name=name,
                        machine=machine_obj,
                        **data
                    )
        else:
            if machine_name == "Feed Mill": # feed mill is done in animal_feeds.yaml
                continue
            # Helpful warning if you have a machine but forgot to create its file
            print(f"Warning: No data file found for machine: {machine_name} (Expected: {filename})")

    return machined_items

MACHINED_ITEMS = load_machined_items_reverse()