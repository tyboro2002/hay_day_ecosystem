import base64

from PIL import Image

from visualizers.helpers import formatting


def test_format_duration_handles_common_cases():
    assert formatting.format_duration(None) == "Instant"
    assert formatting.format_duration(0) == "Instant"
    assert formatting.format_duration(-5) == "Instant"
    assert formatting.format_duration(59) == "59m"
    assert formatting.format_duration(60) == "1h"
    assert formatting.format_duration(61) == "1h 1m"
    assert formatting.format_duration(1440) == "1d"
    assert formatting.format_duration(1500) == "1d 1h"


def test_image_to_base64_returns_webp_payload_for_real_image(tmp_path):
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (16, 16), color="red").save(image_path)

    formatting.image_to_base64.cache_clear()
    data = formatting.image_to_base64(str(image_path))

    assert data is not None
    assert data.startswith("data:image/webp;base64,")
    payload = data.split(",", 1)[1]
    assert base64.b64decode(payload)


def test_image_to_base64_falls_back_when_file_is_missing(monkeypatch, tmp_path):
    missing_path = tmp_path / "missing.png"

    monkeypatch.setattr(formatting.os.path, "exists", lambda path: False)
    formatting.image_to_base64.cache_clear()

    result = formatting.image_to_base64(str(missing_path))

    assert result is not None
    assert result.startswith("data:image/webp;base64,")


def test_get_mastery_image_filename_uses_the_expected_patterns():
    coin_info = {"coin_bonus": 0.1}
    xp_info = {"xp_bonus": 0.05}
    speed_info = {"speed_bonus": 0.15}

    assert formatting.get_mastery_image_filename(2, coin_info, "Bakery") == "plus_10_coins_2_star"
    assert formatting.get_mastery_image_filename(3, xp_info, "Bakery") == "plus_5_xp_3_star"
    assert formatting.get_mastery_image_filename(1, speed_info, "Bakery") == "15_speed_1_star_bakery"
    assert formatting.get_mastery_image_filename(2, {}, "Bakery") == "star_2"


def test_format_mastery_bonus_text_builds_readable_output(monkeypatch):
    monkeypatch.setattr(formatting, "get_base64_asset", lambda name, subfolder: f"fake-{name}-{subfolder}")

    rendered = formatting.format_mastery_bonus_text({"coin_bonus": 0.1, "xp_bonus": 0.05, "speed_bonus": 0.15})

    assert "+10%" in rendered
    assert "+5%" in rendered
    assert "15% faster" in rendered
    assert "fake-coins-mastery" in rendered
    assert "fake-xp-mastery" in rendered
    assert "fake-time-mastery" in rendered


def test_format_mastery_bonus_text_returns_fallback_for_empty_info(monkeypatch):
    monkeypatch.setattr(formatting, "get_base64_asset", lambda name, subfolder: None)

    assert formatting.format_mastery_bonus_text({}) == "No bonus"
