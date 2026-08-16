# Floating disclaimer footer
import json
import math

from game_data.game_data import CURRENT_LEVEL, MAX_LEVEL
from visualizers.helpers.formatting import get_base64_asset

# <a href="{path_prefix}daily_dirt_newspaper_countdown.html">Dirt Countdown</a> |
# disclaimer also update this in calculator.html
DISCLAIMER_FOOTER = """
<div class="sc-disclaimer-footer">
    <div style="margin-bottom: 6px; font-weight: bold;">
        <a href="{path_prefix}general_profitability.html">Profit Rankings</a> | 
        <a href="{path_prefix}overnight_strategies.html">Overnight Strategy</a> |
        <a href="{path_prefix}calculator.html">Calculator</a>
    </div>
    <hr style="border: 0; border-top: 1px solid #444; margin: 6px 0;">
    This material is unofficial and is not endorsed by Supercell. For more information see <a href="https://www.supercell.com/fan-content-policy" target="_blank">Supercell's Fan Content Policy</a>.
</div>
"""

# PyVis Main map styles
LAYOUT_STYLE_RESET = """
<style type="text/css">
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    .sc-disclaimer-footer {
        position: fixed !important;
        bottom: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        z-index: 999999 !important;
        background-color: rgba(33, 33, 33, 0.95) !important;
        border: 1px solid #444444 !important;
        border-radius: 30px !important;
        padding: 10px 24px !important;
        color: #b0b0b0 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-size: 0.72rem !important;
        text-align: center !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6) !important;
        max-width: 90% !important;
        width: max-content !important;
        pointer-events: auto !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
    }
    .sc-disclaimer-footer a {
        color: #f1a80a !important;
        text-decoration: none !important;
        font-weight: 600 !important;
    }
    .sc-disclaimer-footer a:hover {
        text-decoration: underline !important;
    }
</style>
"""

# PyVis interactive navigation handler
INTERACTIVE_NAV_SCRIPT = """
<script type="text/javascript">
    window.addEventListener('load', function() {
        if (typeof network !== 'undefined') {
            network.on("click", function (params) {
                var originalEvent = params.event ? (params.event.srcEvent || params.event) : null;
                var isModifierPressed = originalEvent ? (originalEvent.ctrlKey || originalEvent.metaKey) : false;

                if (params.nodes.length > 0 && isModifierPressed) {
                    var nodeId = params.nodes[0];
                    var nodeData = network.body.data.nodes.get(nodeId);

                    if (nodeData && nodeData.url) {
                        console.log("Modifier+Click detected! Opening:", nodeData.url);
                        window.open(nodeData.url, "_blank");
                    }
                }
            });
        } else {
            console.error("PyVis 'network' object could not be found.");
        }
    });
</script>
"""

# Base style rules shared across detail pages
BASE_CSS = """
    body { background-color: #222222; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 40px 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; box-sizing: border-box; }
    .card { background-color: #2d2d2d; border-radius: 16px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); width: 100%; max-width: 500px; padding: 40px 30px; text-align: center; border: 1px solid #444444; }
    .item-image { width: 110px; height: 110px; margin-bottom: 15px; object-fit: contain; filter: drop-shadow(0px 6px 8px rgba(0,0,0,0.6)); }
    h1 { margin: 5px 0 10px 0; font-size: 2rem; color: #f1a80a; font-weight: 700; letter-spacing: 0.5px; }
    .price { font-size: 1.1rem; color: #b0b0b0; font-weight: 500; background: #3a3a3a; display: inline-block; padding: 6px 16px; border-radius: 20px; border: 1px solid #555555; }
    .section-title { text-align: left; font-size: 0.95rem; color: #f1a80a; border-bottom: 2px solid #444444; padding-bottom: 6px; margin-top: 25px; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600; }
    .grid { display: flex; flex-wrap: wrap; gap: 15px; justify-content: flex-start; margin-bottom: 30px; }
    .grid-item { background-color: #353535; border: 1px solid #484848; border-radius: 12px; width: 90px; padding: 15px 5px; display: flex; flex-direction: column; align-items: center; position: relative; text-decoration: none; color: inherit; transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); box-sizing: border-box; }
    .grid-item:hover { transform: translateY(-5px) scale(1.03); background-color: #404040; border-color: #f1a80a; box-shadow: 0 5px 15px rgba(241, 168, 10, 0.2); }
    .grid-item img { width: 48px; height: 48px; object-fit: contain; margin-bottom: 8px; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.4)); }
    .grid-item .name { font-size: 0.72rem; text-align: center; font-weight: 600; line-height: 1.2; word-break: break-word; padding: 0 4px; }
    .grid-item .qty-badge { position: absolute; top: -8px; right: -8px; background-color: #f1a80a; color: #222222; font-size: 0.7rem; font-weight: 800; padding: 2px 6px; border-radius: 8px; box-shadow: 0 3px 6px rgba(0,0,0,0.4); border: 1.5px solid #2d2d2d; }
    .no-items { color: #888888; font-style: italic; text-align: center; width: 100%; padding: 25px 10px; background-color: #353535; border-radius: 8px; border: 1px dashed #484848; margin-bottom: 5px; box-sizing: border-box; font-size: 0.9rem; }
    .back-btn { display: inline-block; background-color: #f1a80a; color: #222222; text-decoration: none; padding: 12px 35px; border-radius: 30px; font-weight: bold; transition: all 0.2s ease; box-shadow: 0 4px 15px rgba(241, 168, 10, 0.3); font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 15px; }
    .back-btn:hover { background-color: #ffc233; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(241, 168, 10, 0.5); }

    /* Shared summary flex rows */
    .summary-box { display: flex; flex-direction: column; background-color: #1e1e1e; border-radius: 12px; padding: 15px; margin-bottom: 30px; border: 1px solid #3a3a3a; gap: 8px; text-align: left; }
    .summary-row { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #2d2d2d; padding-bottom: 6px; }
    .summary-row:last-child { border-bottom: none; padding-bottom: 0; }
    .sum-label { font-size: 0.75rem; color: #888888; text-transform: uppercase; letter-spacing: 0.8px; }
    .sum-val { font-size: 0.95rem; font-weight: 700; color: #ffffff; }

    /* Floating Disclaimer Footer Styles */
    .sc-disclaimer-footer {
        position: fixed !important;
        bottom: 20px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        z-index: 999999 !important;
        background-color: rgba(33, 33, 33, 0.95) !important;
        border: 1px solid #444444 !important;
        border-radius: 30px !important;
        padding: 10px 24px !important;
        color: #b0b0b0 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        font-size: 0.72rem !important;
        text-align: center !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6) !important;
        max-width: 90% !important;
        width: max-content !important;
        pointer-events: auto !important;
        backdrop-filter: blur(8px) !important;
        -webkit-backdrop-filter: blur(8px) !important;
    }
    .sc-disclaimer-footer a {
        color: #f1a80a !important;
        text-decoration: none !important;
        font-weight: 600 !important;
    }
    .sc-disclaimer-footer a:hover {
        text-decoration: underline !important;
    }
    
    /* Level Slider Control */
    .level-control { background: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 12px; padding: 14px 18px; margin-bottom: 25px; text-align: left; }
    .level-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .level-title { font-size: 0.75rem; color: #888888; text-transform: uppercase; letter-spacing: 0.8px; font-weight: bold; }
    .level-value { font-size: 1.1rem; font-weight: 800; color: #f1a80a; }
    .level-slider { -webkit-appearance: none; appearance: none; width: 100%; height: 6px; background: #444; outline: none; border-radius: 3px; cursor: pointer; }
    .level-slider::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 18px; height: 18px; border-radius: 50%; background: #f1a80a; cursor: pointer; box-shadow: 0 0 8px rgba(241, 168, 10, 0.5); }
    
    /* Machine Count Banner */
    .machine-count-status { font-size: 0.85rem; font-weight: bold; color: #2ecc71; margin-top: 8px; border-top: 1px solid #2d2d2d; padding-top: 6px; }
    .machine-count-status.zero { color: #e74c3c; }

    /* Locked Grid Items */
    .grid-item.locked { filter: grayscale(100%) opacity(0.35); pointer-events: none; border-color: #333333 !important; }
    .grid-item .lock-badge { display: none; position: absolute; top: 4px; left: 4px; background: rgba(0,0,0,0.85); color: #e74c3c; font-size: 0.65rem; font-weight: 800; padding: 2px 5px; border-radius: 4px; border: 1px solid #e74c3c; z-index: 2; }
    .grid-item.locked .lock-badge { display: block; }

    /* Main Machine Lock Visuals */
    .machine-img-wrapper {
        position: relative;
        display: inline-block;
    }
    .machine-img-wrapper.locked .item-image {
        filter: grayscale(100%) opacity(0.35) drop-shadow(0px 0px 0px transparent);
    }
    .machine-img-wrapper .main-lock-badge {
        display: none;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0, 0, 0, 0.85);
        color: #e74c3c;
        padding: 8px 14px;
        border-radius: 20px;
        border: 1.5px solid #e74c3c;
        font-weight: 800;
        font-size: 0.9rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        white-space: nowrap;
        pointer-events: none;
    }
    .machine-img-wrapper.locked .main-lock-badge {
        display: block;
    }
"""

LEVEL_FILTER_STORAGE_KEY = "hayday_shared_level_filter_v1"


def render_level_filter_persistence_script(storage_key=LEVEL_FILTER_STORAGE_KEY):
    return f"""
    <script type="text/javascript">
        window.HayDayLevelFilterPersistence = window.HayDayLevelFilterPersistence || (function() {{
            const storageKey = "{storage_key}";

            function readWindowNameValue() {{
                const prefix = storageKey + '=';
                const parts = String(window.name || '').split('\u001f').filter(Boolean);
                const match = parts.find(part => part.startsWith(prefix));
                return match ? match.slice(prefix.length) : null;
            }}

            function writeWindowNameValue(level) {{
                const prefix = storageKey + '=';
                const parts = String(window.name || '').split('\u001f').filter(part => !part.startsWith(prefix));
                parts.push(prefix + String(level));
                window.name = parts.join('\u001f');
            }}

            function readStoredLevel(defaultLevel, maxLevel) {{
                try {{
                    const raw = localStorage.getItem(storageKey);
                    const fallbackRaw = raw !== null ? raw : readWindowNameValue();
                    if (fallbackRaw === null) return defaultLevel;

                    const parsed = parseInt(fallbackRaw, 10);
                    if (Number.isNaN(parsed)) return defaultLevel;
                    return typeof maxLevel === 'number' ? Math.min(Math.max(parsed, 1), maxLevel) : Math.max(parsed, 1);
                }} catch (error) {{
                    const fallbackRaw = readWindowNameValue();
                    if (fallbackRaw === null) return defaultLevel;

                    const parsed = parseInt(fallbackRaw, 10);
                    if (Number.isNaN(parsed)) return defaultLevel;
                    return typeof maxLevel === 'number' ? Math.min(Math.max(parsed, 1), maxLevel) : Math.max(parsed, 1);
                }}
            }}

            function writeStoredLevel(level) {{
                try {{
                    localStorage.setItem(storageKey, String(level));
                }} catch (error) {{
                    writeWindowNameValue(level);
                    console.warn('Could not persist level filter:', error);
                    return;
                }}

                writeWindowNameValue(level);
            }}

            return {{ readStoredLevel, writeStoredLevel }};
        }})();
    </script>
    """

def generate_unlock_schedule_component(full_schedule, name, asset_folder="machines", base_path=""):
    """
    Generates the HTML for an unlock schedule section given a schedule list.
    full_schedule format: [(level, count, [costs]), ...] or [(level, count), ...]
    """
    img_base64 = get_base64_asset(name, asset_folder, base_path=base_path)
    inline_img = (
        f'<img src="{img_base64}" alt="{name}" style="width: 30px; height: 30px; object-fit: contain; vertical-align: middle; margin: 0 6px;">'
        if img_base64 else f" {name}"
    )

    coin_asset = get_base64_asset("coin", "items", base_path=base_path)
    coin_img = f'<img src="{coin_asset}" alt="Coins" style="width: 16px; height: 16px; object-fit: contain; vertical-align: middle; margin-left: 3px;">' if coin_asset else " Coins"

    schedule_rows = ""
    total_unlocked = 0

    for item in full_schedule:
        lvl = item[0]
        count = item[1]
        tier_costs = item[2] if len(item) > 2 else []

        if tier_costs:
            cost_groups = []
            for cost in tier_costs:
                if cost_groups and cost_groups[-1]['cost'] == cost:
                    cost_groups[-1]['qty'] += 1
                else:
                    cost_groups.append({'cost': cost, 'qty': 1})
        else:
            cost_groups = [{'cost': 0, 'qty': count}]

        for group in cost_groups:
            sub_qty = group['qty']
            cost = group['cost']
            total_unlocked += sub_qty

            cost_display = f"{cost:,}{coin_img}" if cost > 0 else "Free"

            schedule_rows += f"""
            <div class="summary-row" style="min-height: 48px;" data-unlock-level="{lvl}">
                <span class="sum-label">Level {lvl}</span>
                <span class="sum-val" style="display: inline-flex; align-items: center;">
                    +{sub_qty} {inline_img} 
                    <span style="font-size: 0.85rem; color: #f1a80a; margin-left: 6px; margin-right: 8px; font-weight: bold; display: inline-flex; align-items: center;">
                        ({cost_display})
                    </span>
                    <span style="font-size: 0.8rem; color: #888888;">({total_unlocked} Total)</span>
                </span>
            </div>
            """

    return f"""
    <div class="section-title">Unlock Schedule</div>
    <div class="summary-box">
        {schedule_rows}
    </div>
    """

def render_level_slider_script(current_level, unlock_schedule=None, max_level=MAX_LEVEL):
    # Normalize unlock_schedule if passed as an int/float single level value
    if isinstance(unlock_schedule, (int, float)):
        unlock_schedule = [(int(unlock_schedule), 1)]

    schedule_list = unlock_schedule or []
    schedule_json = json.dumps(schedule_list)

    # Determine minimum unlock level
    if schedule_list:
        machine_unlock_level = min([lvl for lvl, *_ in schedule_list])
    else:
        machine_unlock_level = 1

    # Hide status text element if no schedule was originally provided or if it's a single value
    show_status_badge = bool(unlock_schedule) and not (len(schedule_list) == 1 and schedule_list[0][1] == 1)

    persistence_script = render_level_filter_persistence_script()

    return f"""
    {persistence_script}
    <div class="level-control">
        <div class="level-header">
            <span class="level-title">Level Filter</span>
            <span class="level-value" id="levelDisplay">Level {current_level}</span>
        </div>
        <input type="range" min="1" max="{max_level}" value="{current_level}" class="level-slider" id="levelSlider">
        <div class="machine-count-status" id="machineCountDisplay" style="display: {'block' if show_status_badge else 'none'};"></div>
    </div>

    <script type="text/javascript">
        (function() {{
            const slider = document.getElementById('levelSlider');
            const display = document.getElementById('levelDisplay');
            const countDisplay = document.getElementById('machineCountDisplay');
            const unlockSchedule = {schedule_json};
            const machineUnlockLevel = {machine_unlock_level};
            const defaultLevel = {current_level};
            const maxLevel = {max_level};

            function updateLevel(currentLevel) {{
                display.textContent = 'Level ' + currentLevel;

                // 1. Toggle Grayed Out State on Main Image Header
                const machWrapper = document.getElementById('mainMachineWrapper');
                if (machWrapper) {{
                    const mainReqLvl = parseInt(machWrapper.getAttribute('data-unlock-level') || machineUnlockLevel, 10);
                    if (currentLevel < mainReqLvl) {{
                        machWrapper.classList.add('locked');
                    }} else {{
                        machWrapper.classList.remove('locked');
                    }}
                }}

                // 2. Calculate unlocked count if schedule is present
                if (unlockSchedule.length > 0 && countDisplay && countDisplay.style.display !== 'none') {{
                    let totalUnlocked = 0;
                    for (let i = 0; i < unlockSchedule.length; i++) {{
                        const [lvl, count] = unlockSchedule[i];
                        if (currentLevel >= lvl) {{
                            totalUnlocked += count;
                        }}
                    }}

                    if (totalUnlocked === 0) {{
                        countDisplay.className = 'machine-count-status zero';
                        countDisplay.textContent = 'Locked (Requires Level ' + machineUnlockLevel + ')';
                    }} else {{
                        countDisplay.className = 'machine-count-status';
                        countDisplay.textContent = totalUnlocked + ' Unlocked at Level ' + currentLevel;
                    }}
                }}

                // 3. Lock / Unlock child elements, habitat links, feed links, & product cards
                const unlockables = document.querySelectorAll('[data-unlock-level]');
                unlockables.forEach(el => {{
                    const reqLevel = parseInt(el.getAttribute('data-unlock-level'), 10);
                    if (currentLevel < reqLevel) {{
                        el.classList.add('locked');
                    }} else {{
                        el.classList.remove('locked');
                    }}
                }});
            }}

            const initialLevel = window.HayDayLevelFilterPersistence
                ? window.HayDayLevelFilterPersistence.readStoredLevel(defaultLevel, maxLevel)
                : defaultLevel;

            slider.value = String(initialLevel);
            slider.addEventListener('input', (e) => {{
                const nextLevel = parseInt(e.target.value, 10);
                updateLevel(nextLevel);
                if (window.HayDayLevelFilterPersistence) {{
                    window.HayDayLevelFilterPersistence.writeStoredLevel(nextLevel);
                }}
            }});
            updateLevel(initialLevel);
        }})();
    </script>
    """

# =====================================================================
# INDIVIDUAL DETAIL PAGE RENDERING TEMPLATES
# =====================================================================

def render_item_page(name, img_tag, price_display, time_display_html, producer_html, profit_html, price_breakdown_html, ingredients_html, used_in_html, back_target, unlock_schedule=None):
    slider_component = render_level_slider_script(current_level=CURRENT_LEVEL, unlock_schedule=unlock_schedule)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Details</title>
    <style>
        {BASE_CSS}
        .producer-section {{ margin-bottom: 25px; }}
        .producer-label {{ font-size: 0.72rem; color: #888888; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }}
        .producer-badge {{ display: inline-flex; align-items: center; background-color: #1e1e1e; padding: 8px 18px; border-radius: 25px; border: 1px solid #3a3a3a; gap: 12px; transition: filter 0.3s ease, opacity 0.3s ease; }}
        .producer-badge img {{ width: 32px; height: 32px; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.5)); }}
        .producer-badge span {{ font-size: 0.9rem; font-weight: 700; color: #ffffff; }}

        .financial-summary {{ display: flex; justify-content: space-between; background-color: #1e1e1e; border-radius: 12px; padding: 15px; margin-bottom: 30px; border: 1px solid #3a3a3a; gap: 10px; }}
        .fin-col {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
        .fin-col:not(:last-child) {{ border-right: 1px solid #333333; }}
        .fin-label {{ font-size: 0.72rem; color: #888888; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 5px; }}
        .fin-val {{ font-size: 0.95rem; font-weight: 700; }}
        .profit-positive .fin-val {{ color: #2ecc71; }}
        .profit-negative .fin-val {{ color: #e74c3c; }}
        .profit-neutral .fin-val {{ color: #b0b0b0; }}

        /* Locking & Main Image Wrapper */
        .item-img-wrapper {{
            position: relative;
            display: inline-block;
            margin: 0 auto 15px auto;
        }}
        .item-img-wrapper .item-image {{
            transition: filter 0.3s ease, opacity 0.3s ease;
        }}
        .item-img-wrapper .main-lock-badge {{
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(192, 57, 43, 0.9);
            color: #ffffff;
            font-weight: bold;
            font-size: 0.85rem;
            padding: 6px 14px;
            border-radius: 20px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
            pointer-events: none;
            white-space: nowrap;
            border: 1px solid rgba(255, 255, 255, 0.3);
            z-index: 2;
        }}

        .item-img-wrapper.locked .item-image {{
            filter: grayscale(100%) opacity(0.35);
        }}
        .item-img-wrapper.locked .main-lock-badge {{
            display: block;
        }}

        /* Grid Items, Producer Badge & Dynamic Locking */
        [data-unlock-level].locked {{
            filter: grayscale(100%) opacity(0.4);
            pointer-events: none;
        }}

        .grid-item {{
            position: relative;
            transition: filter 0.3s ease, opacity 0.3s ease;
        }}
        .grid-item .lock-badge {{
            display: none;
            position: absolute;
            top: 6px;
            left: 6px;
            background: rgba(0, 0, 0, 0.75);
            color: #ff6b6b;
            font-size: 0.65rem;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid rgba(255, 107, 107, 0.4);
            z-index: 2;
        }}
        .grid-item.locked .lock-badge {{
            display: block;
        }}
    </style>
</head>
<body>
    {DISCLAIMER_FOOTER.format(path_prefix="../")}
    <div class="card">
        {img_tag}
        <h1>{name}</h1>

        <div style="display: flex; justify-content: center; align-items: center; gap: 12px; margin-bottom: 25px;">
            <div class="price" style="margin-bottom: 0;">💰 {price_display}</div>
            {time_display_html}
        </div>

        <div>
            {producer_html}
        </div>

        {profit_html}

        {slider_component}

        <div class="section-title" style="margin-top: 20px;">Ingredients Required</div>
        <div class="grid">
            {ingredients_html}
        </div>

        <div class="section-title">Used in Recipes</div>
        <div class="grid">
            {used_in_html}
        </div>

        <a class="back-btn" href="../{back_target}">Back to Map</a>
        {price_breakdown_html}
    </div>
</body>
</html>
"""


def render_machine_page(name, img_tag, produces_html, unlock_schedule_html, mastery_html, back_target, unlock_schedule=None):
    slider_html = render_level_slider_script(
        current_level=CURRENT_LEVEL,
        unlock_schedule=unlock_schedule
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{name} - Production Machine</title>
    <style>
        {BASE_CSS}
    </style>
</head>
<body>
    {DISCLAIMER_FOOTER.format(path_prefix="../")}
    <div class="card">
        {img_tag}
        <h1>{name}</h1>

        {slider_html}

        <div class="section-title">Products</div>
        <div class="grid">
            {produces_html}
        </div>

        {unlock_schedule_html}

        {mastery_html}

        <a class="back-btn" href="../{back_target}">Back to Map</a>
    </div>
</body>
</html>
"""


def render_pen_page(name, img_tag, residents_html, back_target, unlock_schedule_html, unlock_schedule=None):
    slider_component = render_level_slider_script(current_level=CURRENT_LEVEL, unlock_schedule=unlock_schedule)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Animal Pen</title>
    <style>
        {BASE_CSS}
        .header-tag {{ font-size: 0.75rem; font-weight: bold; color: #3498db; text-transform: uppercase; letter-spacing: 1.5px; border: 1.5px solid #3498db; padding: 4px 12px; border-radius: 15px; display: inline-block; margin-bottom: 12px; }}

        /* Locking & Image Wrappers */
        .item-img-wrapper {{
            position: relative;
            display: inline-block;
            margin: 0 auto 15px auto;
        }}
        .item-img-wrapper .item-image {{
            transition: filter 0.3s ease, opacity 0.3s ease;
        }}
        .item-img-wrapper .main-lock-badge {{
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(192, 57, 43, 0.9);
            color: #ffffff;
            font-weight: bold;
            font-size: 0.85rem;
            padding: 6px 14px;
            border-radius: 20px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
            pointer-events: none;
            white-space: nowrap;
            border: 1px solid rgba(255, 255, 255, 0.3);
            z-index: 2;
        }}

        .item-img-wrapper.locked .item-image {{
            filter: grayscale(100%) opacity(0.35);
        }}
        .item-img-wrapper.locked .main-lock-badge {{
            display: block;
        }}

        /* Resident Grid Items & Badges */
        .grid-item {{
            position: relative;
            transition: filter 0.3s ease, opacity 0.3s ease;
        }}
        .grid-item.locked {{
            filter: grayscale(100%) opacity(0.4);
            pointer-events: none;
        }}
        .grid-item .lock-badge {{
            display: none;
            position: absolute;
            top: 6px;
            left: 6px;
            background: rgba(0, 0, 0, 0.75);
            color: #ff6b6b;
            font-size: 0.65rem;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid rgba(255, 107, 107, 0.4);
            z-index: 2;
        }}
        .grid-item.locked .lock-badge {{
            display: block;
        }}
    </style>
</head>
<body>
    {DISCLAIMER_FOOTER.format(path_prefix="../")}
    <div class="card">
        {img_tag}
        <h1>{name}</h1>

        {slider_component}

        <div class="section-title" style="margin-top: 20px;">Pen Inhabitants</div>
        <div class="grid">
            {residents_html}
        </div>

        {unlock_schedule_html}

        <a class="back-btn" href="../{back_target}">Back to Map</a>
    </div>
</body>
</html>
"""


def render_plantable_structure_page(
        name,
        img_tag,
        produces_html,
        back_target,
        unlock_schedule=None,
        unlock_schedule_html="",
        removal_tool_html="",
        harvest_schedule_html="",
):
    slider_component = render_level_slider_script(
        current_level=CURRENT_LEVEL, unlock_schedule=unlock_schedule
    )

    return f"""<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{name} - Plantable Structure</title>
            <style>
                {BASE_CSS}
                .header-tag {{ font-size: 0.75rem; font-weight: bold; color: #2ecc71; text-transform: uppercase; letter-spacing: 1.5px; border: 1.5px solid #2ecc71; padding: 4px 12px; border-radius: 15px; display: inline-block; margin-bottom: 12px; }}

                /* Locking & Main Image Wrapper */
                .item-img-wrapper {{
                    position: relative;
                    display: inline-block;
                    margin: 0 auto 15px auto;
                }}
                .item-img-wrapper .item-image {{
                    transition: filter 0.3s ease, opacity 0.3s ease;
                }}
                .item-img-wrapper .main-lock-badge {{
                    display: none;
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: rgba(192, 57, 43, 0.9);
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 0.85rem;
                    padding: 6px 14px;
                    border-radius: 20px;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
                    pointer-events: none;
                    white-space: nowrap;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    z-index: 2;
                }}

                .item-img-wrapper.locked .item-image {{
                    filter: grayscale(100%) opacity(0.35);
                }}
                .item-img-wrapper.locked .main-lock-badge {{
                    display: block;
                }}

                /* Grid Items & Badges */
                .grid-item {{
                    position: relative;
                    transition: filter 0.3s ease, opacity 0.3s ease;
                }}
                .grid-item.locked {{
                    filter: grayscale(100%) opacity(0.4);
                    pointer-events: none;
                }}
                .grid-item .lock-badge {{
                    display: none;
                    position: absolute;
                    top: 6px;
                    left: 6px;
                    background: rgba(0, 0, 0, 0.75);
                    color: #ff6b6b;
                    font-size: 0.65rem;
                    font-weight: bold;
                    padding: 2px 6px;
                    border-radius: 4px;
                    border: 1px solid rgba(255, 107, 107, 0.4);
                    z-index: 2;
                }}
                .grid-item.locked .lock-badge {{
                    display: block;
                }}
            </style>
        </head>
        <body>
            {DISCLAIMER_FOOTER.format(path_prefix="../")}
            <div class="card">
                {img_tag}
                <h1>{name}</h1>

                {slider_component}

                <div class="section-title" style="margin-top: 20px;">Produces</div>
                <div class="grid">
                    {produces_html}
                </div>

                {removal_tool_html}

                {harvest_schedule_html}

                {unlock_schedule_html}

                <a class="back-btn" href="../{back_target}">Back to Map</a>
            </div>
        </body>
        </html>
        """

def render_special_structure_page(name, img_tag, produces_html, back_target, unlock_schedule=None, unlock_schedule_html=""):
    slider_component = render_level_slider_script(current_level=CURRENT_LEVEL, unlock_schedule=unlock_schedule)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Special Structure</title>
    <style>
        {BASE_CSS}
        .header-tag {{ font-size: 0.75rem; font-weight: bold; color: #9b59b6; text-transform: uppercase; letter-spacing: 1.5px; border: 1.5px solid #9b59b6; padding: 4px 12px; border-radius: 15px; display: inline-block; margin-bottom: 12px; }}

        /* Locking & Main Image Wrapper */
        .item-img-wrapper {{
            position: relative;
            display: inline-block;
            margin: 0 auto 15px auto;
        }}
        .item-img-wrapper .item-image {{
            transition: filter 0.3s ease, opacity 0.3s ease;
        }}
        .item-img-wrapper .main-lock-badge {{
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(192, 57, 43, 0.9);
            color: #ffffff;
            font-weight: bold;
            font-size: 0.85rem;
            padding: 6px 14px;
            border-radius: 20px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
            pointer-events: none;
            white-space: nowrap;
            border: 1px solid rgba(255, 255, 255, 0.3);
            z-index: 2;
        }}

        .item-img-wrapper.locked .item-image {{
            filter: grayscale(100%) opacity(0.35);
        }}
        .item-img-wrapper.locked .main-lock-badge {{
            display: block;
        }}

        /* Grid Items & Badges */
        .grid-item {{
            position: relative;
            transition: filter 0.3s ease, opacity 0.3s ease;
        }}
        .grid-item.locked {{
            filter: grayscale(100%) opacity(0.4);
            pointer-events: none;
        }}
        .grid-item .lock-badge {{
            display: none;
            position: absolute;
            top: 6px;
            left: 6px;
            background: rgba(0, 0, 0, 0.75);
            color: #ff6b6b;
            font-size: 0.65rem;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid rgba(255, 107, 107, 0.4);
            z-index: 2;
        }}
        .grid-item.locked .lock-badge {{
            display: block;
        }}
    </style>
</head>
<body>
    {DISCLAIMER_FOOTER.format(path_prefix="../")}
    <div class="card">
        {img_tag}
        <h1>{name}</h1>

        {slider_component}

        <div class="section-title" style="margin-top: 20px;">Available Resources</div>
        <div class="grid">
            {produces_html}
        </div>

        {unlock_schedule_html}

        <a class="back-btn" href="../{back_target}">Back to Map</a>
    </div>
</body>
</html>
"""


def render_field_page(name, img_tag, produces_html, back_target, unlock_schedule=None, unlock_schedule_html=""):
    slider_component = render_level_slider_script(current_level=CURRENT_LEVEL, unlock_schedule=unlock_schedule)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Farm Fields</title>
    <style>
        {BASE_CSS}
        .header-tag {{ font-size: 0.75rem; font-weight: bold; color: #f1c40f; text-transform: uppercase; letter-spacing: 1.5px; border: 1.5px solid #f1c40f; padding: 4px 12px; border-radius: 15px; display: inline-block; margin-bottom: 12px; }}

        /* Locking & Main Image Wrapper */
        .item-img-wrapper {{
            position: relative;
            display: inline-block;
            margin: 0 auto 15px auto;
        }}
        .item-img-wrapper .item-image {{
            transition: filter 0.3s ease, opacity 0.3s ease;
        }}
        .item-img-wrapper .main-lock-badge {{
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(192, 57, 43, 0.9);
            color: #ffffff;
            font-weight: bold;
            font-size: 0.85rem;
            padding: 6px 14px;
            border-radius: 20px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
            pointer-events: none;
            white-space: nowrap;
            border: 1px solid rgba(255, 255, 255, 0.3);
            z-index: 2;
        }}

        .item-img-wrapper.locked .item-image {{
            filter: grayscale(100%) opacity(0.35);
        }}
        .item-img-wrapper.locked .main-lock-badge {{
            display: block;
        }}

        /* Grid Items & Badges */
        .grid-item {{
            position: relative;
            transition: filter 0.3s ease, opacity 0.3s ease;
        }}
        .grid-item.locked {{
            filter: grayscale(100%) opacity(0.4);
            pointer-events: none;
        }}
        .grid-item .lock-badge {{
            display: none;
            position: absolute;
            top: 6px;
            left: 6px;
            background: rgba(0, 0, 0, 0.75);
            color: #ff6b6b;
            font-size: 0.65rem;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid rgba(255, 107, 107, 0.4);
            z-index: 2;
        }}
        .grid-item.locked .lock-badge {{
            display: block;
        }}
    </style>
</head>
<body>
    {DISCLAIMER_FOOTER.format(path_prefix="../")}
    <div class="card">
        {img_tag}
        <h1>{name}</h1>

        {slider_component}

        <div class="section-title" style="margin-top: 20px;">Crops</div>
        <div class="grid">
            {produces_html}
        </div>

        {unlock_schedule_html}

        <a class="back-btn" href="../{back_target}">Back to Map</a>
    </div>
</body>
</html>
"""


def render_animal_page(name, img_tag, food_html, produces_html, lives_in_html, back_target, unlock_schedule=None):
    slider_component = render_level_slider_script(current_level=CURRENT_LEVEL, unlock_schedule=unlock_schedule)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Livestock</title>
    <style>
        {BASE_CSS}
        .header-tag {{ font-size: 0.75rem; font-weight: bold; color: #1abc9c; text-transform: uppercase; letter-spacing: 1.5px; border: 1.5px solid #1abc9c; padding: 4px 12px; border-radius: 15px; display: inline-block; margin-bottom: 12px; }}
        .split-grid {{ display: flex; gap: 20px; justify-content: space-between; text-align: left; margin-bottom: 30px; }}
        .split-panel {{ flex: 1; background-color: #1e1e1e; border: 1px solid #3a3a3a; border-radius: 12px; padding: 15px; }}
        .split-title {{ font-size: 0.75rem; color: #888888; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px; border-bottom: 1px solid #2d2d2d; padding-bottom: 5px; font-weight: bold; }}

        /* Locking & Image Wrappers */
        .item-img-wrapper {{
            position: relative;
            display: inline-block;
            margin: 0 auto 15px auto;
        }}
        .item-img-wrapper .item-image {{
            transition: filter 0.3s ease, opacity 0.3s ease;
        }}
        .item-img-wrapper .main-lock-badge {{
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(192, 57, 43, 0.9);
            color: #ffffff;
            font-weight: bold;
            font-size: 0.85rem;
            padding: 6px 14px;
            border-radius: 20px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
            pointer-events: none;
            white-space: nowrap;
            border: 1px solid rgba(255, 255, 255, 0.3);
            z-index: 2;
        }}

        .item-img-wrapper.locked .item-image {{
            filter: grayscale(100%) opacity(0.35);
        }}
        .item-img-wrapper.locked .main-lock-badge {{
            display: block;
        }}

        /* Grid & Link Locking */
        [data-unlock-level].locked {{
            filter: grayscale(100%) opacity(0.4);
            pointer-events: none;
        }}

        .grid-item {{
            position: relative;
            transition: filter 0.3s ease, opacity 0.3s ease;
        }}
        .grid-item .lock-badge {{
            display: none;
            position: absolute;
            top: 6px;
            left: 6px;
            background: rgba(0, 0, 0, 0.75);
            color: #ff6b6b;
            font-size: 0.65rem;
            font-weight: bold;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid rgba(255, 107, 107, 0.4);
            z-index: 2;
        }}
        .grid-item.locked .lock-badge {{
            display: block;
        }}
    </style>
</head>
<body>
    {DISCLAIMER_FOOTER.format(path_prefix="../")}
    <div class="card">
        {img_tag}
        <h1>{name}</h1>

        {slider_component}

        <div class="split-grid" style="margin-top: 20px;">
            <div class="split-panel">
                <div class="split-title">🏡 Habitat</div>
                {lives_in_html}
            </div>
            <div class="split-panel">
                <div class="split-title">🌾 Feed</div>
                {food_html}
            </div>
        </div>

        <div class="section-title">Produces</div>
        <div class="grid">
            {produces_html}
        </div>

        <a class="back-btn" href="../{back_target}">Back to Map</a>
    </div>
</body>
</html>
"""


def render_price_breakdown_component(name, unit_price, max_qty=10, base_path=""):
    """
    Returns an HTML snippet containing a bulk price breakdown list (1 to max_qty).
    Displays the item icon, quantity, and total floored price formatted to .1f.
    """
    if unit_price == 'N/A' or unit_price is None:
        return '<div class="no-items" style="margin-top: 25px;">⚠️ Bulk pricing unavailable (Unsellable)</div>'

    # Fetch item thumbnail image asset
    item_b64 = get_base64_asset(name, "items", base_path=base_path)
    item_img = f'<img src="{item_b64}" alt="{name}" style="width: 22px; height: 22px; object-fit: contain; vertical-align: middle; margin-right: 6px;">' if item_b64 else ""

    # Fetch coin icon asset
    coin_b64 = get_base64_asset("coin", "items", base_path=base_path)
    coin_img = f'<img src="{coin_b64}" style="width: 14px; height: 14px; object-fit: contain; vertical-align: middle; margin-left: 3px;">' if coin_b64 else " Coins"

    rows_html = ""
    for qty in range(1, max_qty + 1):
        total_cost = math.floor(float(unit_price) * qty)
        rows_html += f"""
        <div class="summary-row">
            <span class="sum-label" style="display: inline-flex; align-items: center;">
                {item_img} <b>x{qty}</b>
            </span>
            <span class="sum-val">{total_cost:.0f}{coin_img}</span>
        </div>
        """

    return f"""
    <style>
        .bulk-breakdown-wrapper {{
            margin-top: 30px;
            text-align: left;
        }}
    </style>

    <div class="bulk-breakdown-wrapper">
        <div class="section-title">Bulk Cost Summary</div>
        <div class="summary-box">
            {rows_html}
        </div>
    </div>
    """