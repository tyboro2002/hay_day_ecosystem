from calculators.overnight_strategy import (
    calculate_strategy_for_single_level,
    calculate_overnight_strategy,
)
from game_data.machines_data import MACHINES


def test_calculate_strategy_for_single_level_returns_strategy_and_profit():
    plan, profit = calculate_strategy_for_single_level(240, 10)

    assert isinstance(plan, dict)
    assert profit > 0
    assert "Feed Mill" in plan
    assert "Fields" in plan
    assert "Bakery" in plan


def test_strategy_contains_expected_structure_for_feed_mill():
    plan, _ = calculate_strategy_for_single_level(240, 10)
    feed_mill = plan["Feed Mill"]

    assert "by_mastery" in feed_mill
    assert feed_mill["min_slots"] == 3
    assert feed_mill["max_slots"] == 9
    assert feed_mill["unlocked_count"] == 1
    assert feed_mill["by_mastery"]["0_stars"][3] is not None
    assert feed_mill["by_mastery"]["0_stars"][3]["total_profit"] == 54.0


def test_fields_strategy_is_present_for_level_10():
    plan, _ = calculate_strategy_for_single_level(240, 10)
    fields = plan["Fields"]

    assert fields["unlocked_count"] == 1
    assert fields["total_profit"] == 259.2
    assert fields["combination"][next(iter(fields["combination"].keys()))] == 18


def test_get_best_overnight_strategy_returns_levelwise_results_for_max_level():
    results = calculate_overnight_strategy(240, 2)

    assert len(results) == 2
    assert all(isinstance(item, int) for item in results)