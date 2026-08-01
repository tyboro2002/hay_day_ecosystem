from game_data import ITEMS, INFRASTRUCTURE, LIVESTOCK


def test_items_registry_contains_expected_entries():
    assert "Wheat" in ITEMS
    assert "Apple" in ITEMS
    assert "Egg" in ITEMS
    assert "Vanilla Ice Cream" in ITEMS


def test_items_registry_contains_many_entries():
    assert len(ITEMS) > 100


def test_item_subclasses_are_correctly_instantiated():
    assert type(ITEMS["Wheat"]).__name__ == "Crop"
    assert type(ITEMS["Apple"]).__name__ == "PlantableItem"
    assert type(ITEMS["Egg"]).__name__ == "AnimalItem"
    assert type(ITEMS["Chicken Feed"]).__name__ == "MachinedItem"
    assert type(ITEMS["Axe"]).__name__ == "SpecialItem"


def test_core_item_properties_are_populated():
    wheat = ITEMS["Wheat"]
    apple = ITEMS["Apple"]
    egg = ITEMS["Egg"]

    assert wheat.sell_price == 3.6
    assert wheat.xp == 1
    assert apple.unlock_level == 15
    assert egg.unlock_level == 2
    assert egg.sell_price == 18.0


def test_item_unlock_logic_matches_expected_levels():
    assert ITEMS["Wheat"].is_unlocked(1) is True
    assert ITEMS["Apple"].is_unlocked(14) is False
    assert ITEMS["Apple"].is_unlocked(15) is True
    assert ITEMS["Egg"].is_unlocked(1) is False
    assert ITEMS["Egg"].is_unlocked(2) is True


def test_infrastructure_groups_are_populated():
    expected_keys = {"machines", "pens", "plant_structures", "special_structures", "fields"}

    assert set(INFRASTRUCTURE.keys()) == expected_keys
    assert INFRASTRUCTURE["machines"]
    assert INFRASTRUCTURE["pens"]
    assert INFRASTRUCTURE["plant_structures"]
    assert INFRASTRUCTURE["special_structures"]
    assert INFRASTRUCTURE["fields"]


def test_specific_infrastructure_objects_are_present():
    assert "Bakery" in INFRASTRUCTURE["machines"]
    assert "Chicken Coop" in INFRASTRUCTURE["pens"]
    assert "Apple Tree" in INFRASTRUCTURE["plant_structures"]
    assert "Mine" in INFRASTRUCTURE["special_structures"]


def test_infrastructure_objects_have_expected_properties():
    bakery = INFRASTRUCTURE["machines"]["Bakery"]
    chicken_coop = INFRASTRUCTURE["pens"]["Chicken Coop"]
    apple_tree = INFRASTRUCTURE["plant_structures"]["Apple Tree"]
    mine = INFRASTRUCTURE["special_structures"]["Mine"]

    assert bakery.unlock_level == 4
    assert bakery.is_unlocked(1) is False
    assert bakery.is_unlocked(4) is True
    assert bakery.max_allowed_at_level(1) == 0
    assert chicken_coop.unlock_level == 1
    assert chicken_coop.is_unlocked(1) is True
    assert chicken_coop.max_pens_at_level(1) == 1
    assert apple_tree.unlock_level == 15
    assert apple_tree.is_unlocked(15) is True
    assert apple_tree.max_harvests == 4
    assert mine.unlock_level == 24
    assert mine.is_unlocked(23) is False
    assert mine.is_unlocked(24) is True


def test_livestock_registry_contains_known_animals():
    assert "Chicken" in LIVESTOCK
    assert "Cow" in LIVESTOCK
    assert "Bee" in LIVESTOCK
    assert len(LIVESTOCK) == 7


def test_livestock_objects_link_to_their_pen_and_products():
    chicken = LIVESTOCK["Chicken"]
    cow = LIVESTOCK["Cow"]

    assert chicken.pen.name == "Chicken Coop"
    assert chicken.produces_item.name == "Egg"
    assert chicken.required_food.name == "Chicken Feed"
    assert cow.pen.name == "Cow Pasture"
    assert cow.produces_item.name == "Milk"
    assert cow.required_food.name == "Cow Feed"


def test_livestock_unlock_logic_matches_pen_unlocks():
    chicken = LIVESTOCK["Chicken"]
    assert chicken.unlock_level == 1
    assert chicken.is_unlocked(1) is True
    assert chicken.max_allowed(1) == 6


def test_recipe_ingredients_are_linked_to_item_objects():
    vanilla_ice_cream = ITEMS["Vanilla Ice Cream"]

    assert vanilla_ice_cream.ingredients
    assert ITEMS["Milk"] in vanilla_ice_cream.ingredients
    assert ITEMS["Cream"] in vanilla_ice_cream.ingredients
    assert ITEMS["White Sugar"] in vanilla_ice_cream.ingredients
    assert set(vanilla_ice_cream.ingredients.values()) == {1}


def test_more_items_have_expected_types():
    assert type(ITEMS["Sugarcane"]).__name__ == "Crop"
    assert type(ITEMS["Milk"]).__name__ == "AnimalItem"
    assert type(ITEMS["White Sugar"]).__name__ == "MachinedItem"
    assert type(ITEMS["Dynamite"]).__name__ == "SpecialItem"


def test_animal_items_link_to_their_pen():
    milk = ITEMS["Milk"]
    egg = ITEMS["Egg"]

    assert milk.pen.name == "Cow Pasture"
    assert egg.pen.name == "Chicken Coop"


def test_machined_items_link_to_their_machine():
    chicken_feed = ITEMS["Chicken Feed"]
    cream = ITEMS["Cream"]
    white_sugar = ITEMS["White Sugar"]

    assert chicken_feed.machine.name == "Feed Mill"
    assert cream.machine.name == "Dairy"
    assert white_sugar.machine.name == "Sugar Mill"


def test_special_items_are_not_machine_or_pen_products():
    dynamite = ITEMS["Dynamite"]

    assert getattr(dynamite, "machine", None) is None
    assert getattr(dynamite, "pen", None) is None
    assert getattr(dynamite, "structure", None) is None


def test_crop_items_have_no_machine_pen_or_structure_links():
    wheat = ITEMS["Wheat"]
    corn = ITEMS["Corn"]

    assert getattr(wheat, "machine", None) is None
    assert getattr(wheat, "pen", None) is None
    assert getattr(wheat, "structure", None) is None
    assert getattr(corn, "machine", None) is None
    assert getattr(corn, "pen", None) is None
    assert getattr(corn, "structure", None) is None


def test_infrastructure_contains_expected_counts_of_entries():
    assert len(INFRASTRUCTURE["machines"]) >= 10
    assert len(INFRASTRUCTURE["pens"]) >= 7
    assert len(INFRASTRUCTURE["plant_structures"]) >= 7
    assert len(INFRASTRUCTURE["special_structures"]) >= 2
