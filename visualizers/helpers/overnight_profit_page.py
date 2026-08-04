import os
import json

from calculators.overnight_strategy import calculate_overnight_strategy, TOTAL_FIELDS
from game_data.crops_data import CROPS
from game_data.game_data import DIAMOND_COST, MAX_LEVEL, CURRENT_LEVEL
from game_data.machines_data import MACHINES
from game_data.plants_data import PLANTS
from visualizers.helpers.formatting import get_base64_asset
from visualizers.helpers.templates import DISCLAIMER_FOOTER, render_level_filter_persistence_script


def load_all_assets(base, folders):
    asset_bank = {}
    valid_extensions = ('.png',)

    for folder in folders:
        folder = base + folder
        if not os.path.exists(folder):
            continue

        category = os.path.basename(os.path.normpath(folder))

        for entry in os.listdir(folder):
            full_path = os.path.join(folder, entry)

            if os.path.isfile(full_path) and entry.lower().endswith(valid_extensions):
                asset_name = os.path.splitext(entry)[0].lower().strip()
                b64_val = get_base64_asset(asset_name, category)

                if b64_val:
                    asset_bank[asset_name] = b64_val

    return asset_bank


TARGET_FOLDERS = ["items", "storage", "machines", "fields"]
GLOBAL_ASSETS = load_all_assets("assets/", TARGET_FOLDERS)


def get_asset_ref(asset_name, css_class="", alt_text=""):
    key = asset_name.lower().strip().replace(" ", "_").replace("-", "_")
    class_attr = f' class="{css_class}"' if css_class else ""
    alt_attr = f' alt="{alt_text or asset_name}"'

    return f'<img{class_attr} data-asset="{key}"{alt_attr}>'


def build_strategy_json_payload(durations, detail_dir, max_level=MAX_LEVEL):
    """
    Calculates strategy data for all duration tabs and levels, returning a compact JSON payload
    instead of thousands of pre-rendered HTML DOM elements.
    """
    strategy_payload = {}

    for mins in durations:
        tab_key = f"tab-{mins // 60}h"
        level_strategies = calculate_overnight_strategy(mins, max_level=max_level)
        strategy_payload[tab_key] = {}

        for lvl in range(1, max_level + 1):
            lvl_data = level_strategies.get(lvl, {})
            plan = lvl_data.get("strategy", {})

            rows_data = []

            for source_name, data in plan.items():
                if source_name == "Fields":
                    if not data.get('combination'):
                        continue

                    combo_list = []
                    ingredients = {}

                    for item_obj, count in data['combination'].items():
                        combo_list.append({"name": item_obj.name, "count": count})
                        ingredients[item_obj.name] = count

                    rows_data.append({
                        "type": "fields",
                        "name": "Fields",
                        "profit": data['total_profit'],
                        "combination": combo_list,
                        "ingredients": ingredients
                    })
                else:
                    m_obj = MACHINES.get(source_name)
                    if not m_obj:
                        continue

                    unlocked_count = m_obj.max_allowed_at_level(lvl) if hasattr(m_obj, 'max_allowed_at_level') else (1 if getattr(m_obj, 'unlock_level', 1) <= lvl else 0)
                    if unlocked_count == 0:
                        continue

                    by_mastery_data = data.get('by_mastery', {})
                    mastery_payload = {}

                    for star_key, by_slots_data in by_mastery_data.items():
                        slots_payload = {}
                        if isinstance(by_slots_data, list):
                            for s_count, slot_eval in enumerate(by_slots_data):
                                if not slot_eval:
                                    continue

                                combo_list = []
                                single_machine_ingredients = {}

                                for item_obj, count in slot_eval['combination'].items():
                                    combo_list.append({"name": item_obj.name, "count": count})

                                    ingredients_dict = getattr(item_obj, 'ingredients', {})
                                    if isinstance(ingredients_dict, dict):
                                        for ing_obj, qty in ingredients_dict.items():
                                            single_machine_ingredients[ing_obj.name] = single_machine_ingredients.get(ing_obj.name, 0) + (qty * count)

                                slots_payload[s_count] = {
                                    "profit": slot_eval['total_profit'],
                                    "combination": combo_list,
                                    "ingredients": single_machine_ingredients
                                }
                        mastery_payload[star_key] = slots_payload

                    unlock_schedule = getattr(m_obj, 'unlock_schedule', None)
                    total_possible = sum(e[1] for e in unlock_schedule) if (unlock_schedule and isinstance(unlock_schedule, list)) else 1

                    for idx in range(1, unlocked_count + 1):
                        instance_label = f"{source_name} #{idx}" if total_possible > 1 else source_name
                        base_asset_key = source_name.lower().replace(" ", "_").replace("-", "_")
                        instance_id = f"{base_asset_key}_{idx}"

                        rows_data.append({
                            "type": "machine",
                            "id": instance_id,
                            "name": instance_label,
                            "source": source_name,
                            "mastery_map": mastery_payload
                        })

            strategy_payload[tab_key][str(lvl)] = rows_data

    return strategy_payload


def generate_overnight_page(outp, detail_dir, current_level=CURRENT_LEVEL, max_level=MAX_LEVEL):
    coin_img_html = get_asset_ref("coin", css_class="coin-icon", alt_text="coins")
    diamond_img_html = get_asset_ref("diamond", css_class="inline-item-img", alt_text="diamond")

    durations = [1*60, 2*60, 4*60, 8*60, 12*60, 24*60]
    strategy_payload = build_strategy_json_payload(durations, detail_dir, max_level=max_level)

    asset_bank_json = json.dumps(GLOBAL_ASSETS)
    strategy_data_json = json.dumps(strategy_payload)

    crops_set = json.dumps(list(CROPS.keys()))
    plants_set = json.dumps(list(PLANTS.keys()))

    machine_config_data = []

    for m_name, m_obj in MACHINES.items():
        base_asset_key = m_name.lower().replace(" ", "_").replace("-", "_")

        levels = getattr(m_obj, 'unlock_schedule', None)
        amount_owned = getattr(m_obj, 'amount_owned', 1)

        min_allowed = getattr(m_obj, 'min_allowed_slots', None)
        if min_allowed is None:
            min_allowed = 1 if m_name in ["Lobster Pool", "Duck Salon"] else 2

        max_allowed = getattr(m_obj, 'max_allowed_slots', None) or 9
        current_slots = getattr(m_obj, 'max_slots', None) or min_allowed
        current_mastery = getattr(m_obj, 'mastery_level', 0)

        if levels and isinstance(levels, list):
            current_total_owned = 0

            for entry in levels:
                if isinstance(entry, (tuple, list)) and len(entry) >= 2:
                    lvl, new_unlocks = entry[0], entry[1]

                    for _ in range(new_unlocks):
                        current_total_owned += 1
                        machine_config_data.append({
                            "id": f"{base_asset_key}_{current_total_owned}",
                            "assetKey": base_asset_key,
                            "name": f"{m_name} #{current_total_owned}" if new_unlocks > 1 or len(levels) > 1 else m_name,
                            "minLevel": lvl,
                            "minSlots": min_allowed,
                            "maxSlots": max_allowed,
                            "currentSlots": current_slots,
                            "currentMastery": current_mastery,
                            "initialSelected": current_total_owned <= amount_owned
                        })

    machine_config_json = json.dumps(machine_config_data)

    silo_img_html = get_asset_ref("silo", css_class="stat-icon", alt_text="Silo")
    barn_img_html = get_asset_ref("barn", css_class="stat-icon", alt_text="Barn")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Hay Day Factory Ledger - Overnight Queue Matrix</title>
    <link rel="stylesheet" href="overnight.css">
</head>
<body>

    <div class="tabs-container">
        <a class="back-btn" href="index.html">⬅ Back to Farm Map</a>
        <h1>Overnight Queue Optimization</h1>
        <p class="subtitle">Calculates the most profitable combination of long-running items to fill your production slots before you log off, ensuring your farm keeps making coins efficiently while you sleep.</p>

        <div class="level-filter-container">
            <div class="level-slider-group">
                <label for="overnightLevelRange">Filter Level:</label>
                <input type="range" id="overnightLevelRange" class="level-slider" min="1" max="{max_level}" value="{current_level}" oninput="switchLevel(this.value)">
                <span id="overnightLevelDisplay" class="level-badge">Lvl {current_level}</span>
            </div>
        </div>

        <div class="diamond-notice">
            {diamond_img_html} <b>Note:</b> Raw inputs requiring diamonds as base components default to an assumed utility valuation cost of <b>{DIAMOND_COST} {coin_img_html}</b>.
        </div>

        <ul class="tabs">
            <li class="tab-link active" onclick="switchTab(event, 'tab-1h')">1-Hour Break</li>
            <li class="tab-link" onclick="switchTab(event, 'tab-2h')">2-Hour Nap</li>
            <li class="tab-link" onclick="switchTab(event, 'tab-4h')">4-Hour Snooze</li>
            <li class="tab-link" onclick="switchTab(event, 'tab-8h')">8-Hour Standard Sleep</li>
            <li class="tab-link" onclick="switchTab(event, 'tab-12h')">12-Hour Extended Hibernation</li>
            <li class="tab-link" onclick="switchTab(event, 'tab-24h')">24-Hour Day Off</li>
        </ul>

        <!-- Single reusable DOM Shell for rendering active tab views -->
        <div class="tab-content">
            <div class="dashboard-grid">
                <div class="stat-card">
                    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
                        <div id="display-total-profit" class="stat-val" style="color: #2ecc71; display: flex; align-items: center; gap: 6px;">
                            0{coin_img_html}
                        </div>
                        <div class="stat-lbl">Projected Surplus Margin</div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-content-wrapper">
                        {silo_img_html}
                        <div>
                            <div id="display-silo-space" class="stat-val" style="color: #3498db;">0</div>
                            <div class="stat-lbl">Required Silo Space (Seeds/Crops)</div>
                        </div>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-content-wrapper">
                        {barn_img_html}
                        <div>
                            <div id="display-barn-space" class="stat-val" style="color: #9b59b6;">0</div>
                            <div class="stat-lbl">Required Barn Space (Inputs)</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="strategy-split">
                <div class="main-table-pane">
                    <h3>Machine Queue Allocations</h3>
                    <table>
                        <thead>
                            <tr><th style="width:25%">Production Line</th><th style="width:60%">Optimal Loading Queue</th><th style="width:15%">Net Value</th></tr>
                        </thead>
                        <tbody id="strategy-table-body">
                            <!-- Dynamically generated via overnight.js -->
                        </tbody>
                    </table>
                </div>
                <div class="shopping-pane">
                    <h3>Pre-Bed Stocking List</h3>
                    <ul id="shopping-list-container" class="shopping-list"></ul>
                </div>
            </div>

            <div class="machine-selector-section">
                <div class="machine-settings-bar">
                    <button type="button" class="machine-settings-btn primary" onclick="exportMachineSettings()">Export Machine State</button>
                    <button type="button" class="machine-settings-btn" onclick="importMachineSettings()">Import Machine State</button>
                    <button type="button" class="machine-settings-btn" onclick="clearMachineSettings()">Clear Local State</button>
                    <div class="machine-settings-note">Auto-saved locally in your browser. Export creates a portable JSON file you can import on another device.</div>
                </div>

                <div class="machine-settings-divider"></div>

                <h3>Configure Active Machine Slots & Mastery Stars (Click Body to Toggle Active State)</h3>
                <div id="machines-container" class="machine-grid"></div>
            </div>
        </div>

        {DISCLAIMER_FOOTER.format(path_prefix="")}
    </div>

    {render_level_filter_persistence_script()}

    <script>
        window.ASSET_BANK = {asset_bank_json};
        window.STRATEGY_DATA = {strategy_data_json};
        window.MACHINE_CONFIGS = {machine_config_json};
        window.SILO_ITEMS = new Set({crops_set}.concat({plants_set}));
        window.DETAIL_DIR = "{detail_dir}";
    </script>
    <script src="overnight.js"></script>
</body>
</html>"""

    target_path = os.path.join(outp, "overnight_strategies.html")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(html_content)