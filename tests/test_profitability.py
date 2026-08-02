from calculators.profitability import (
    analyze_value_added,
    calculate_direct_ingredient_cost,
    find_animal_food_for_item,
    find_structure_for_plantable,
)
from game_data import ITEMS


def test_find_animal_food_for_item_returns_the_expected_feed():
    egg_feed = find_animal_food_for_item("Egg")
    milk_feed = find_animal_food_for_item("Milk")

    assert egg_feed is not None
    assert egg_feed.name == "Chicken Feed"
    assert milk_feed is not None
    assert milk_feed.name == "Cow Feed"


def test_find_structure_for_plantable_returns_the_matching_structure():
    apple_structure = find_structure_for_plantable("Apple")
    raspberry_structure = find_structure_for_plantable("Raspberry")

    assert apple_structure is not None
    assert apple_structure.name == "Apple Tree"
    assert raspberry_structure is not None
    assert raspberry_structure.name == "Raspberry Bush"


def test_calculate_direct_ingredient_cost_for_known_items():
    wheat = ITEMS["Wheat"]
    apple = ITEMS["Apple"]
    egg = ITEMS["Egg"]
    vanilla_ice_cream = ITEMS["Vanilla Ice Cream"]

    assert calculate_direct_ingredient_cost(wheat) == 0.0
    assert calculate_direct_ingredient_cost(apple) == 13.333333333333334
    assert calculate_direct_ingredient_cost(egg) == 7.2
    assert calculate_direct_ingredient_cost(vanilla_ice_cream) == 133.2


def test_analyze_value_added_returns_expected_report_shape():
    reports = analyze_value_added(silent=True)

    assert len(reports) == 136
    assert reports[0]["name"] in ITEMS
    assert all("name" in report for report in reports)
    assert all("value_added" in report for report in reports)
    assert all("roi" in report for report in reports)
    assert all("pph" in report for report in reports)
