import os
from functools import lru_cache

# Keep track of missing assets globally across generators
non_found = 0
RED = "\033[91m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
ORANGE = "\033[38;5;208m" # 256-color mode for Orange (Color 208)
RESET = "\033[0m"

def format_duration(minutes):
    """Formats a duration from raw minutes to a human-readable day/hour/minute string."""
    if not minutes or not isinstance(minutes, (int, float)) or minutes <= 0:
        return "Instant"

    days = int(minutes // 1440)
    hours = int((minutes % 1440) // 60)
    mins = int(minutes % 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if mins > 0 or not parts:
        parts.append(f"{mins}m")

    return " ".join(parts)


def get_base64_asset(name, subfolder, base_path=""):
    """
    Returns a relative web path for HTML <img> tags instead of base64 strings.
    Kept with the same name for backward compatibility across other visualizer scripts.
    """
    filename = f"{name.lower().replace(' ', '_')}.png"
    prefix = f"{base_path.rstrip('/')}/" if base_path else ""
    return f"{prefix}assets/{subfolder}/{filename}"


def get_mastery_image_filename(star_number, info, machine_name):
    """
    Constructs image filenames based on active bonus parameters:
    - Coin:  plus_10_coins_1_star
    - XP:    plus_5_xp_2_star
    - Speed: 15_speed_3_star_bakery (includes machine name for machine-specific art)
    """
    clean_mach_name = machine_name.lower().replace(" ", "_")

    if info.get("coin_bonus"):
        pct = int(info["coin_bonus"] * 100)
        return f"plus_{pct}_coins_{star_number}_star"

    if info.get("xp_bonus"):
        pct = int(info["xp_bonus"] * 100)
        return f"plus_{pct}_xp_{star_number}_star"

    if info.get("speed_bonus"):
        pct = int(info["speed_bonus"] * 100)
        return f"{pct}_speed_{star_number}_star_{clean_mach_name}"

    return f"star_{star_number}"


def format_mastery_bonus_text(info):
    """Formats raw mastery YAML data into human-readable text + inline asset icons."""
    # 1. Fetch web asset paths from the mastery directory
    coin_asset = get_base64_asset("coins", "mastery", base_path="../")
    xp_asset = get_base64_asset("xp", "mastery", base_path="../")
    time_asset = get_base64_asset("time", "mastery", base_path="../")

    # Helper inline HTML image generator with clean alignment styling
    def make_icon(src, alt):
        if src:
            return f'<img src="{src}" alt="{alt}" style="width: 16px; height: 16px; object-fit: contain; vertical-align: middle; margin-left: 3px;">'
        return f" {alt}"  # Fallback text if asset isn't found

    coins_img = make_icon(coin_asset, "Coins")
    xp_img = make_icon(xp_asset, "XP")
    time_img = make_icon(time_asset, "Time")

    # 2. Build bonus parts using image badges
    parts = []
    if info.get("coin_bonus"):
        pct = int(info["coin_bonus"] * 100)
        parts.append(f"+{pct}%{coins_img}")

    if info.get("xp_bonus"):
        pct = int(info["xp_bonus"] * 100)
        parts.append(f"+{pct}%{xp_img}")

    if info.get("speed_bonus"):
        pct = int(info["speed_bonus"] * 100)
        parts.append(f"{pct}% faster{time_img}")

    return " / ".join(parts) if parts else "No bonus"