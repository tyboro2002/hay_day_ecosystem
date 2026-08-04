import math
from collections import Counter


def find_possibilities(measurements):
    # measurements is a dict of {n: y_n}
    # Range is [1, 1000] for search, or whatever your bounds are
    possible_k = []
    for k in range(1, 12000): # Checking k up to 1200.0
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
    "Raspberry Jam":{1: 252, 2: 504, 3: 756, 4: 1008, 5: 1260, 6: 1512, 7: 1764},
    "Strawberry Jam": {1: 270, 2: 540, 3: 810, 4: 1080, 5: 1350},
    "Lobster Soup": {1: 612, 2: 1224, 3: 1836, 4: 2448, 5: 3060, 6: 3672, 7: 4284, 8: 4896},
    "Caramel Apple": {1: 255},
    "Pillow": {1: 676, 2: 1353},
    "Asparagus Soup": {1: 255},


    "Toffee": {},
    "Raspberry Candle": {},
    "Pineapple": {},
    "Pineapple Juice": {},
    "Fish Soup": {},
    "Lily": {},
    "Soy Sauce": {},
    "Chocolate": {},
    "Bean Dip": {},
    "Fancy Cake": {},
    "Rice": {},
    "Sushi Roll": {},
    "Olive": {},
    "Lollipop": {},
    "Lettuce": {},
    "Feta Salad": {},
    "Bean Salad": {},
    "Tower Doner Supreme": {},
    "Lobster Sushi": {},
    "Blanket": {},
    "Jelly Beans": {},
    "Olive Oil": {},
    "Garlic": {},
    "Garlic Bread": {},
    "Veggie Bagel": {},
    "Mayonnaise": {},
    "BLT Salad": {},
    "Caramel Latte": {},
    "Peanuts": {},
    "Sunflower": {},
    "Egg Sushi": {},
    "Honey Peanuts": {},
    "Seafood Salad": {},
    "Berry Smoothie": {},
    "Snack Mix": {},
    "Gingerbread Cookie": {},
    "Banana Bread": {},
    "Macaroon": {},
    "Pineapple Coconut Bars": {},
    "Grilled Asparagus": {},
    "Grilled Onion": {},
    "Winter Veggies": {},
    "Stuffed Peppers": {},
    "Grilled Eggplant": {},
    "Banana Pancakes": {},
    "Fish Skewer": {},
    "Cabbage": {},
    "Onion": {},
    "Cucumber": {},
    "Beetroot": {},
    "Bell Pepper": {},
    "Ginger": {},
    "Tea Leaf": {},
    "Peony": {},
    "Broccoli": {},
    "Grapes": {},
    "Mint": {},
    "Passion Fruit": {},
    "Mushroom": {},
    "Eggplant": {},
    "Watermelon": {},
    "Clay": {},
    "Chickpea": {},
    "Oats": {},
    "Lemon": {},
    "Orange": {},
    "Peach": {},
    "Banana": {},
    "Plum": {},
    "Mango": {},
    "Coconut": {},
    "Guava": {},
    "Pomegranate": {},
    "Chocolate Pie": {},
    "Lemon Pie": {},
    "Peach Tart": {},
    "Passion Fruit Pie": {},
    "Mushroom Pot Pie": {},
    "Eggplant Parmesan": {},
    "Flower Shawl": {},
    "Pineapple Cake": {},
    "Lemon Cake": {},
    "Fruit Cake": {},
    "Chocolate Roll": {},
    "Pomegranate Cake": {},
    "Orange Juice": {},
    "Grape Juice": {},
    "Passion Fruit Juice": {},
    "Watermelon Juice": {},
    "Mango Juice": {},
    "Guava Juice": {},
    "Peanut Butter Milkshake": {},
    "Orange Sorbet": {},
    "Affogato": {},
    "Peach Ice Cream": {},
    "Mint Ice Cream": {},
    "Banana Split": {},
    "Coconut Ice Cream": {},
    "Fruit Sorbet": {},
    "Blueberry Chutney": {},
    "Marmalade": {},
    "Peach Jam": {},
    "Grape Jam": {},
    "Plum Jam": {},
    "Passion Fruit Jam": {},
    "Flower Pendant": {},
    "Iced Banana Latte": {},
    "Cabbage Soup": {},
    "Onion Soup": {},
    "Noodle Soup": {},
    "Potato Soup": {},
    "Bell Pepper Soup": {},
    "Broccoli Soup": {},
    "Mushroom Soup": {},
    "Lemon Candle": {},
    "Colorful Candles": {},
    "Floral Candle": {},
    "Bright Bouquet": {},
    "Gracious Bouquet": {},
    "Candy Bouquet": {},
    "Birthday Bouquet": {},
    "Veggie Bouquet": {},
    "Cotton Candy": {},
    "Sesame Brittle": {},
    "Lemon Curd": {},
    "Olive Dip": {},
    "Tomato Sauce": {},
    "Salsa": {},
    "Hummus": {},
    "Tart Dressing": {},
    "Big Sushi Roll": {},
    "Rice Ball": {},
    "Pasta Salad": {},
    "Veggie Platter": {},
    "Coleslaw": {},
    "Beetroot Salad": {},
    "Summer Rolls": {},
    "Fruit Salad": {},
    "Summer Salad": {},
    "Mushroom Salad": {},
    "Orange Salad": {},
    "Bacon Toast": {},
    "Egg Sandwich": {},
    "Honey Toast": {},
    "Peanut Butter and Jelly Sandwich": {},
    "Cucumber Sandwich": {},
    "Onion Melt": {},
    "Goat Cheese Toast": {},
    "Hummus Wrap": {},
    "Fresh Pasta": {},
    "Rice Noodles": {},
    "Lemon Essential Oil": {},
    "Chamomile Essential Oil": {},
    "Ginger Essential Oil": {},
    "Mint Essential Oil": {},
    "Fried Rice": {},
    "Lamb Stir Fry": {},
    "Spicy Fish": {},
    "Peanut Noodles": {},
    "Tofu Stir Fry": {},
    "Green Smoothie": {},
    "Yogurt Smoothie": {},
    "Cucumber Smoothie": {},
    "Mixed Smoothie": {},
    "Black Sesame Smoothie": {},
    "Cocoa Smoothie": {},
    "Plum Smoothie": {},
    "Tropical Smoothie": {},
    "Cloche Hat": {},
    "Top Hat": {},
    "Sun Hat": {},
    "Flower Crown": {},
    "Hot Dog": {},
    "Tofu Dog": {},
    "Corn Dog": {},
    "Onion Dog": {},
    "Chocolate Fondue": {},
    "Bacon Fondue": {},
    "Cheese Fondue": {},
    "Tropical Fondue": {},
    "Tea Pot": {},
    "Potted Plant": {},
    "Clay Mug": {},
    "Plain Yogurt": {},
    "Strawberry Yogurt": {},
    "Tropical Yogurt": {},
    "Breakfast Bowl": {},
    "Chickpea Stew": {},
    "Chili Stew": {},
    "Winter Stew": {},
    "Vanilla Milkshake": {},
    "Mocha Milkshake": {},
    "Fruity Milkshake": {},
    "Apple Porridge": {},
    "Sweet Porridge": {},
    "Fresh Porridge": {},
    "Fresh Diffuser": {},
    "Zesty Perfume": {},
    "Calming Diffuser": {},
    "Plain Cupcake": {},
    "Guava Cupcake": {},
    "Tropical Cupcake": {},
    "Cookie Cupcake": {},
    "Gnocchi": {},
    "Veggie Lasagna": {},
    "Lobster Pasta": {},
    "Pasta Carbonara": {},
    "Broccoli Pasta": {},
    "Spicy Pasta": {},
    "Mushroom Pasta": {},
    "Plain Donut": {},
    "Sprinkled Donut": {},
    "Crunchy Donut": {},
    "Cream Donut": {},
    "Bacon Donut": {},
    "Filled Donut": {},
    "Taco": {},
    "Spicy Bean Taco" :{},
    "Fish Taco": {},
    "Quesadilla": {},
    "Nachos": {},
    "Colourful Omelet": {},
    "Spring Omelet": {},
    "Cheese Omelet": {},
    "Rice Omelet": {},
    "Potato Omelet": {},
    "Plain Waffles": {},
    "Berry Waffles": {},
    "Chocolate Waffles": {},
    "Blueberry Waffles": {},
    "Breakfast Waffles": {},
    "Rich Fudge": {},
    "Mint Fudge": {},
    "Chili Fudge": {},
    "Lemon Fudge": {},
    "Peanut Fudge": {},
    "Pickles": {},
    "Canned Fish": {},
    "Kimchi": {},
    "Dried Fruit": {},
    "Guava Compote": {},
    "Honey Soap": {},
    "Lemon Lotion": {},
    "Exfoliating Soap": {},
    "Honey Face Mask": {},
    "Rich Soap": {},
    "Green Tea": {},
    "Milk Tea": {},
    "Honey Tea": {},
    "Lemon Tea": {},
    "Apple Ginger Tea": {},
    "Orange Tea": {},
    "Iced Tea": {},
    "Mint Tea": {},
    "Chamomile Tea": {},
    "Pomegranate Tea": {},
    "Bacon Fries": {},
    "Hand Pies": {},
    "Chili Poppers": {},
    "Falafel": {},
    "Fried Candy Bar": {}
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
        elif count == 11999:
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