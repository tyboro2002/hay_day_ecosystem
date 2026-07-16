import math
from collections import Counter


def find_possibilities(measurements):
    # measurements is a dict of {n: y_n}
    # Range is [1, 1000] for search, or whatever your bounds are
    possible_k = []
    for k in range(1, 8500): # Checking k up to 800.0 (on level 40 Diamond ring	with price 824 highest)
        x = k / 10
        if all(math.floor(n * x) == y for n, y in measurements.items()):
            possible_k.append(x)
    return possible_k

def possible_next_prices(possibilities):
    # Initialize dictionary where each key holds a Counter
    pos_map = {i: Counter() for i in range(1, 11)}

    for pos in possibilities:
        for i in range(1, 11):
            val = math.floor(pos * i)
            pos_map[i][val] += 1

    return pos_map

def get_discriminating_report(pos_map):
    report = {}

    for n, counts in pos_map.items():
        total_occurrences = sum(counts.values())

        # Determine valid values based on your criteria:
        # If only one result exists total, keep it.
        # Otherwise, keep values with a count of 1.
        if len(counts) == 1:
            valid_values = list(counts.keys())
        else:
            valid_values = [val for val, count in counts.items() if count == 1]

        report[n] = (valid_values, len(valid_values), total_occurrences)

    return report

def get_highest_key(data_dict):
    """
    Returns the highest key from a dictionary.
    Returns None if the dictionary is empty.
    """
    if not data_dict:
        return None
    return max(data_dict.keys())

def find_first_multivalue_discriminator(report):
    """
    Finds the first 'n' where the number of discriminating values is > 1.
    report structure: {n: ([values], amount, total)}
    """
    for n, (values, amount, total) in report.items():
        if amount > 1:
            return n
    return None

# Example usage:
# print(find_possibilities({3: 367, 4: 489, 7: 856, 8: 979}))
# print(find_possibilities({1: 205, 2: 410, 3: 615}))

item_measurements = {
    "Meat Bucket":{},
    "Honey Popcorn": {1: 360, 2: 720, 3: 1080, 4: 1440, 5: 1800, 6: 2160},
    "Apple Jam":{},
    "Raspberry Jam":{1: 388, 2: 777, 3: 1166, 4: 1555},
    "Cherry Jam":{1: 334},
    "Caffè Latte": {1: 219, 2: 439, 3: 658, 4: 878},
    "Caffè Mocha": {},
    "Chamomile": {},
    "Frutti Di Mare Pizza": {},
    "Soothing Pad": {}
}

def run_report():
    RED = "\033[91m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    ORANGE = "\033[38;5;208m" # 256-color mode for Orange (Color 208)
    RESET = "\033[0m"
    total_possibilities = 0
    total_items = 0
    unknown = []
    exactly_known = []

    # We iterate over the keys of the dictionary directly
    for name in item_measurements.keys():
        measurements = item_measurements[name]
        possibilities = find_possibilities(measurements)
        count = len(possibilities)
        total_possibilities += count
        total_items += 1

        pos_next = possible_next_prices(possibilities)
        report = get_discriminating_report(pos_next)
        highest_key = get_highest_key(measurements)
        result = find_first_multivalue_discriminator(report)

        if count == 1:
            print(f"{RED}{name:<20} | {count} possibilities | {possibilities}{RESET}")
            exactly_known.append(name)
        elif count == 2:
            print(f"{ORANGE}{name:<20} | {count} possibilities | {possibilities} | mes: {highest_key}, min: {result} | {report}{RESET}")
        elif count == 3:
            print(f"{YELLOW}{name:<20} | {count} possibilities | {possibilities} | mes: {highest_key}, min: {result} | {report}{RESET}")
        elif count == 8499:
            print(f"{CYAN}{name:<20} | {count} possibilities {RESET}")
            unknown.append(name)
        elif count <= 10:
            print(f"{name:<20} | {count} possibilities | mes: {highest_key}, min: {result} | {possibilities}")
        else:
            print(f"{name:<20} | mes: {highest_key}, min: {result} | {count} possibilities")
    print(f"this leaves {total_possibilities} possibilities over for {total_items} items that's {total_possibilities/total_items} average per item ({len(unknown)} unknown items) ({len(exactly_known)} known items)")
    print(f"unknown namely: {', '.join(unknown)}")
    print(f"exactly known namely: {', '.join(exactly_known)}")


if __name__ == "__main__":
    run_report()