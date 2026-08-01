import os
import json
from collections import defaultdict

from calculators.overnight_strategy import calculate_overnight_strategy, TOTAL_FIELDS
from game_data.crops_data import CROPS
from game_data.game_data import DIAMOND_COST, MAX_LEVEL, CURRENT_LEVEL
from game_data.machines_data import MACHINES
from game_data.plants_data import PLANTS
from visualizers.helpers.formatting import get_base64_asset
from visualizers.helpers.templates import DISCLAIMER_FOOTER


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
    """Generates a lightweight data-asset HTML tag without embedding heavy Base64 strings."""
    key = asset_name.lower().strip().replace(" ", "_").replace("-", "_")
    class_attr = f' class="{css_class}"' if css_class else ""
    alt_attr = f' alt="{alt_text or asset_name}"'

    return f'<img{class_attr} data-asset="{key}"{alt_attr}>'


def get_unlocked_machine_count_at_level(machine_obj, player_level):
    if hasattr(machine_obj, 'max_allowed_at_level'):
        return machine_obj.max_allowed_at_level(player_level)
    return 1 if getattr(machine_obj, 'unlock_level', 1) <= player_level else 0


def render_single_level_panel(plan, global_profit, detail_dir, player_level=1):
    coin_img_html = get_asset_ref("coin", css_class="coin-icon", alt_text="coins")
    machine_rows_html = ""

    for source_name, data in plan.items():
        if source_name == "Fields":
            if not data.get('combination'):
                continue

            machine_clean_filename = f"{detail_dir}/details_fields.html"

            combo_parts = []
            row_ingredients = {}

            for item_obj, count in data['combination'].items():
                clean_filename = f"{detail_dir}/details_{item_obj.name.lower().replace(' ', '_').replace('-', '_')}.html"
                img_html = get_asset_ref(item_obj.name, css_class="inline-item-img", alt_text=item_obj.name)
                combo_parts.append(
                    f'<a href="{clean_filename}" class="item-link queue-pill">'
                    f'{img_html} {count}x {item_obj.name}</a>'
                )
                row_ingredients[item_obj.name] = count

            ing_json = json.dumps(row_ingredients)
            machine_img_html = get_asset_ref("fields", css_class="inline-machine-img", alt_text="Fields")

            machine_rows_html += f"""
                <tr data-machine="Fields" data-profit="{data['total_profit']}" data-ingredients='{ing_json}'>
                    <td class="source-cell">
                        <a href="{machine_clean_filename}" class="machine-label-wrapper item-link">
                            {machine_img_html}
                            <b>Fields</b>
                        </a>
                    </td>
                    <td><div class="queue-flex">{" ".join(combo_parts)}</div></td>
                    <td style="color:#2ecc71; font-weight:bold; white-space:nowrap;" class="row-profit-cell">
                        {data['total_profit']:+.0f}{coin_img_html}
                    </td>
                </tr>
                """
        else:
            m_obj = MACHINES.get(source_name)
            if not m_obj:
                continue

            unlocked_count = get_unlocked_machine_count_at_level(m_obj, player_level)
            if unlocked_count == 0:
                continue

            machine_img_html = get_asset_ref(source_name, css_class="inline-machine-img", alt_text=source_name)
            machine_clean_filename = f"{detail_dir}/details_{source_name.lower().replace(' ', '_').replace('-', '_')}.html"

            by_mastery_data = data.get('by_mastery', {})
            mastery_payload = {}

            for star_key, by_slots_data in by_mastery_data.items():
                slots_payload = {}
                if isinstance(by_slots_data, list):
                    for s_count, slot_eval in enumerate(by_slots_data):
                        if not slot_eval:
                            continue

                        combo_html_parts = []
                        single_machine_ingredients = {}

                        for item_obj, count in slot_eval['combination'].items():
                            clean_filename = f"{detail_dir}/details_{item_obj.name.lower().replace(' ', '_').replace('-', '_')}.html"
                            img_html = get_asset_ref(item_obj.name, css_class="inline-item-img", alt_text=item_obj.name)
                            combo_html_parts.append(
                                f'<a href="{clean_filename}" class="item-link queue-pill">'
                                f'{img_html} {count}x {item_obj.name}</a>'
                            )

                            ingredients_dict = getattr(item_obj, 'ingredients', {})
                            if isinstance(ingredients_dict, dict):
                                for ing_obj, qty in ingredients_dict.items():
                                    qty_needed = qty * count
                                    single_machine_ingredients[ing_obj.name] = single_machine_ingredients.get(ing_obj.name, 0) + qty_needed

                        slots_payload[s_count] = {
                            "profit": slot_eval['total_profit'],
                            "html": " ".join(combo_html_parts),
                            "ingredients": single_machine_ingredients
                        }
                mastery_payload[star_key] = slots_payload

            unlock_schedule = getattr(m_obj, 'unlock_schedule', None)
            total_possible = sum(e[1] for e in unlock_schedule) if (unlock_schedule and isinstance(unlock_schedule, list)) else 1

            mastery_json_attr = json.dumps(mastery_payload).replace("'", "&apos;")

            for idx in range(1, unlocked_count + 1):
                instance_label = f"{source_name} #{idx}" if total_possible > 1 else source_name
                base_asset_key = source_name.lower().replace(" ", "_").replace("-", "_")
                instance_id = f"{base_asset_key}_{idx}"

                machine_rows_html += f"""
                    <tr data-machine-id="{instance_id}" data-machine="{instance_label}" data-mastery-map='{mastery_json_attr}'>
                        <td class="source-cell">
                            <a href="{machine_clean_filename}" class="machine-label-wrapper item-link">
                                {machine_img_html}
                                <b>{instance_label}</b>
                            </a>
                        </td>
                        <td><div class="queue-flex queue-cell-content"></div></td>
                        <td style="color:#2ecc71; font-weight:bold; white-space:nowrap;" class="row-profit-cell">
                            0{coin_img_html}
                        </td>
                    </tr>
                    """

    silo_img_html = get_asset_ref("silo", css_class="stat-icon", alt_text="Silo")
    barn_img_html = get_asset_ref("barn", css_class="stat-icon", alt_text="Barn")

    return f"""
    <div class="dashboard-grid">
        <div class="stat-card">
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <div class="stat-val surplus-margin-val" style="color: #2ecc71; display: flex; align-items: center; gap: 6px;">
                    0{coin_img_html}
                </div>
                <div class="stat-lbl">Projected Surplus Margin</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-content-wrapper">
                {silo_img_html}
                <div>
                    <div class="stat-val silo-space-val" style="color: #3498db;">0</div>
                    <div class="stat-lbl">Required Silo Space (Seeds/Crops)</div>
                </div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-content-wrapper">
                {barn_img_html}
                <div>
                    <div class="stat-val barn-space-val" style="color: #9b59b6;">0</div>
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
                <tbody>
                    {machine_rows_html or '<tr><td colspan="3">No unlocked machines available for this time window.</td></tr>'}
                </tbody>
            </table>
        </div>
        <div class="shopping-pane">
            <h3>Pre-Bed Stocking List</h3>
            <ul class="shopping-list">
                <!-- Dynamically populated by updateStrategyVisibility() -->
            </ul>
        </div>
    </div>
    """


def build_duration_html(sleep_duration_mins, detail_dir, max_level=MAX_LEVEL):
    level_strategies = calculate_overnight_strategy(sleep_duration_mins, max_level=max_level)

    html_blocks = []
    for lvl in range(1, max_level + 1):
        lvl_data = level_strategies.get(lvl, {})
        plan = lvl_data.get("strategy", {})
        global_profit = lvl_data.get("total_profit", 0)

        panel_html = render_single_level_panel(plan, global_profit, detail_dir, player_level=lvl)
        html_blocks.append(f'<div class="level-panel" data-levels="{lvl}" style="display: none;">{panel_html}</div>')

    return "\n".join(html_blocks)


def generate_overnight_page(outp, detail_dir, current_level=CURRENT_LEVEL, max_level=MAX_LEVEL):
    coin_img_html = get_asset_ref("coin", css_class="coin-icon", alt_text="coins")
    diamond_img_html = get_asset_ref("diamond", css_class="inline-item-img", alt_text="diamond")
    asset_bank_json = json.dumps(GLOBAL_ASSETS)

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

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Hay Day Factory Ledger - Overnight Queue Matrix</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1a1a1a; color: #e0e0e0; padding: 20px; }}
            h1 {{ color: #e67e22; text-align: center; margin-bottom: 5px; }}
            p.subtitle {{ text-align: center; color: #888; max-width: 700px; margin: 0 auto 30px auto; font-size: 0.95rem; line-height: 1.4; }}

            .back-btn {{ display: inline-block; background-color: #34495e; color: #fff; padding: 8px 15px; border-radius: 4px; text-decoration: none; margin-bottom: 20px; font-size: 0.9rem; }}
            .back-btn:hover {{ background-color: #2c3e50; }}

            .level-filter-container {{
                max-width: 1100px;
                margin: 0 auto 20px auto;
                background-color: #252525;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 15px 20px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 20px;
            }}
            .level-slider-group {{
                display: flex;
                align-items: center;
                gap: 15px;
                flex-grow: 1;
            }}
            .level-slider-group label {{ font-weight: bold; color: #e67e22; white-space: nowrap; }}
            .level-slider {{ flex-grow: 1; accent-color: #e67e22; cursor: pointer; height: 6px; }}
            .level-badge {{ background-color: #e67e22; color: #fff; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 0.9rem; min-width: 70px; text-align: center; }}

            .diamond-notice {{ 
                max-width: 1100px; 
                margin: 0 auto 25px auto; 
                padding: 10px 15px; 
                background-color: #2c2519; 
                border-left: 4px solid #f1c40f; 
                border-radius: 4px; 
                color: #f39c12; 
                font-size: 0.85rem;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 5px;
            }}

            .tabs-container {{ max-width: 1100px; margin: 0 auto; }}
            .tabs {{ display: flex; list-style: none; padding: 0; margin: 0; border-bottom: 2px solid #333; }}
            .tab-link {{ padding: 12px 24px; cursor: pointer; background: #252525; color: #aaa; font-weight: bold; border-radius: 6px 6px 0 0; margin-right: 4px; border: 1px solid #333; border-bottom: none; }}
            .tab-link.active {{ background: #e67e22; color: white; border-color: #e67e22; }}

            .tab-content {{ background: #222; border: 1px solid #333; border-top: none; padding: 25px; border-radius: 0 0 6px 6px; margin-bottom: 30px; }}
            .content-panel {{ display: none; }}
            .content-panel.active {{ display: block; }}

            .dashboard-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px; }}
            .stat-card {{ background-color: #2d2d2d; border: 1px solid #3d3d3d; border-radius: 6px; padding: 15px; display: flex; align-items: center; justify-content: center; min-height: 80px; }}
            .stat-content-wrapper {{ display: flex; align-items: center; gap: 15px; text-align: left; width: 100%; padding-left: 10px; }}
            .stat-icon {{ width: 42px; height: 42px; object-fit: contain; flex-shrink: 0; }}
            .stat-val {{ font-size: 1.8rem; font-weight: bold; margin-bottom: 5px; text-align: center; }}
            .stat-card:not(:first-child) .stat-val {{ text-align: left; }}
            .stat-lbl {{ font-size: 0.85rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }}

            .coin-icon {{ width: 20px; height: 20px; object-fit: contain; vertical-align: middle; display: inline-block; margin-left: 3px; margin-top: -2px; }}
            .stat-val .coin-icon {{ width: 26px; height: 26px; margin-top: 0; }}

            .strategy-split {{ display: grid; grid-template-columns: 2.2fr 1fr; gap: 20px; }}
            h3 {{ color: #e67e22; margin-top: 0; border-bottom: 1px solid #333; padding-bottom: 8px; font-size: 1.1rem; }}

            table {{ width: 100%; border-collapse: collapse; color: #ddd; }}
            th, td {{ padding: 12px 10px; text-align: left; border-bottom: 1px solid #333; vertical-align: middle; }}
            th {{ background-color: #2d2d2d; color: #e67e22; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; }}
            tr:hover {{ background-color: #272727; }}
            .source-cell {{ color: #f39c12; }}

            .machine-label-wrapper {{ display: flex; align-items: center; gap: 10px; color: #f39c12; }}
            .inline-machine-img {{ width: 32px; height: 32px; object-fit: contain; flex-shrink: 0; }}

            .queue-flex {{ display: flex; flex-wrap: wrap; gap: 6px; }}
            .queue-pill {{ background: #2c3e50; color: #ecf0f1; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; display: flex; align-items: center; gap: 6px; border: 1px solid #34495e; }}
            .inline-item-img {{ width: 18px; height: 18px; object-fit: contain; vertical-align: middle; }}

            .shopping-list {{ list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }}
            .shopping-list li {{ background: #282828; padding: 8px 12px; border-radius: 4px; border: 1px solid #333; font-size: 0.9rem; display: flex; align-items: center; gap: 10px; }}
            .shopping-list b {{ color: #e67e22; min-width: 28px; display: inline-block; }}

            .item-link {{ color: inherit; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }}
            .item-link:hover, .item-link:visited, .item-link:active {{ color: inherit; text-decoration: none; }}
            .shopping-list li .item-link {{ gap: 10px; width: 100%; }}

            .machine-selector-section {{
                margin-top: 35px;
                border-top: 2px dashed #444;
                padding-top: 25px;
            }}
            .machine-grid {{
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                justify-content: center;
                margin-top: 15px;
            }}
            .machine-card {{
                border: 2px solid #444;
                background-color: #252525;
                border-radius: 10px;
                padding: 14px;
                width: 210px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                user-select: none;
                display: flex;
                flex-direction: column;
                align-items: center;
                cursor: pointer;
                opacity: 0.55;
                filter: grayscale(0.6);
                transition: transform 0.1s, border-color 0.2s, background-color 0.2s, opacity 0.2s, filter 0.2s;
            }}
            .machine-card.selected {{
                border-color: #2ecc71;
                background-color: #1e2d21;
                box-shadow: 0 0 10px rgba(46, 204, 113, 0.3);
                opacity: 1.0;
                filter: grayscale(0);
            }}
            .machine-card h4 {{
                margin: 0 0 4px 0;
                font-size: 0.95rem;
                color: #f39c12;
            }}
            .machine-card .lvl-tag {{
                font-size: 0.75rem;
                color: #888;
                margin-bottom: 8px;
            }}
            .machine-card .card-img {{
                width: 58px;
                height: 58px;
                object-fit: contain;
                margin-bottom: 8px;
            }}

            .mastery-stars-container {{
                display: flex;
                gap: 6px;
                margin-bottom: 10px;
                justify-content: center;
                min-height: 28px;
                align-items: center;
            }}
            .star-btn {{
                font-size: 22px;
                color: #555;
                cursor: pointer;
                line-height: 1;
                transition: color 0.15s, transform 0.1s;
            }}
            .star-btn.active {{
                color: #f1c40f;
                text-shadow: 0 0 6px rgba(241, 196, 15, 0.6);
            }}
            .star-btn:hover {{
                transform: scale(1.25);
            }}

            .slots-grid {{
                display: grid;
                grid-template-rows: repeat(2, 32px);
                grid-auto-flow: column;
                grid-auto-columns: 32px;
                gap: 5px;
                background-color: rgba(0,0,0,0.3);
                padding: 6px;
                border-radius: 6px;
                border: 1px solid #444;
                justify-content: center;
            }}
            .disabled-controls {{
                pointer-events: none;
                opacity: 0.4;
            }}
            .slot-tile {{
                width: 32px;
                height: 32px;
                border-radius: 4px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                font-size: 7.5px;
                font-weight: bold;
                box-sizing: border-box;
                cursor: pointer;
                transition: transform 0.1s, filter 0.1s;
            }}
            .slot-tile:hover {{
                transform: scale(1.08);
                filter: brightness(1.2);
            }}
            .slot-tile.empty-slot {{
                background: linear-gradient(135deg, #3a3a3a, #222);
                border: 1px solid #666;
                color: #ddd;
            }}
            .slot-tile.buy-slot {{
                background: linear-gradient(135deg, #4d3e1d, #2b210e);
                border: 1px dashed #f1c40f;
                color: #f39c12;
            }}
            .buy-diamond-icon {{
                width: 14px;
                height: 14px;
                object-fit: contain;
            }}

            .sc-disclaimer-footer {{ margin-top: 40px; color: #666; font-size: 0.8rem; text-align: center; line-height: 1.4; }}
            .sc-disclaimer-footer a {{ color: #3498db; text-decoration: none; }}
            .sc-disclaimer-footer a:hover {{ text-decoration: underline; }}
        </style>
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

            <div class="tab-content">
                <div id="tab-1h" class="content-panel active">
                    {build_duration_html(1*60, detail_dir, max_level=max_level)}
                </div>

                <div id="tab-2h" class="content-panel">
                    {build_duration_html(2*60, detail_dir, max_level=max_level)}
                </div>

                <div id="tab-4h" class="content-panel">
                    {build_duration_html(4*60, detail_dir, max_level=max_level)}
                </div>

                <div id="tab-8h" class="content-panel">
                    {build_duration_html(8*60, detail_dir, max_level=max_level)}
                </div>

                <div id="tab-12h" class="content-panel">
                    {build_duration_html(12*60, detail_dir, max_level=max_level)}
                </div>

                <div id="tab-24h" class="content-panel">
                    {build_duration_html(24*60, detail_dir, max_level=max_level)}
                </div>

                <div class="machine-selector-section">
                    <h3>Configure Active Machine Slots & Mastery Stars (Click Body to Toggle Active State)</h3>
                    <div id="machines-container" class="machine-grid"></div>
                </div>
            </div>

            {DISCLAIMER_FOOTER.format(path_prefix="")}
        </div>

        <script>
            const ASSET_BANK = {asset_bank_json};
            const MACHINE_CONFIGS = {machine_config_json};
            const SILO_ITEMS = new Set({crops_set}.concat({plants_set}));
            const DETAIL_DIR = "{detail_dir}";
            const machineInstances = [];

            function logMachineStateChange(action, machineState) {{
                console.log(`Current Active Machines List:`, getSelectedMachinesData());
                updateStrategyVisibility();
            }}

            function hydrateAssets(container = document) {{
                container.querySelectorAll("img[data-asset]").forEach(img => {{
                    const key = img.getAttribute("data-asset");
                    if (ASSET_BANK[key]) {{
                        img.src = ASSET_BANK[key];
                    }}
                }});
            }}

            function initMachineCards() {{
                const container = document.getElementById("machines-container");
                if (container) container.innerHTML = "";
                machineInstances.length = 0;

                MACHINE_CONFIGS.forEach(config => {{
                    createMachineCard(config);
                }});

                console.log("Initial Loaded Machine Config:", getSelectedMachinesData());
                updateStrategyVisibility();
            }}

            function updateStrategyVisibility() {{
                const instanceMap = new Map();
                machineInstances.forEach(m => instanceMap.set(m.id, m));

                const coinSrc = ASSET_BANK['coin'] || '';
                const coinImgHtml = `<img class="coin-icon" src="${{coinSrc}}" alt="coins">`;

                document.querySelectorAll('.level-panel').forEach(panel => {{
                    if (panel.style.display === 'none') return;

                    let panelTotalProfit = 0;
                    const dynamicIngredients = {{}};

                    panel.querySelectorAll('tr[data-machine], tr[data-machine-id]').forEach(row => {{
                        const machineId = row.getAttribute('data-machine-id');
                        const machineName = row.getAttribute('data-machine');

                        if (machineName === 'Fields') {{
                            row.style.display = '';
                            const profit = parseFloat(row.getAttribute('data-profit') || '0');
                            panelTotalProfit += profit;

                            const rowIngs = JSON.parse(row.getAttribute('data-ingredients') || '{{}}');
                            for (const [ingName, qty] of Object.entries(rowIngs)) {{
                                dynamicIngredients[ingName] = (dynamicIngredients[ingName] || 0) + qty;
                            }}
                        }} else if (machineId && instanceMap.has(machineId)) {{
                            const mState = instanceMap.get(machineId);
                            if (mState.selected) {{
                                row.style.display = '';

                                const masteryMap = JSON.parse(row.getAttribute('data-mastery-map') || '{{}}');
                                const starKey = mState.mastery === 1 ? "1_star" : `${{mState.mastery}}_stars`;
                                const slotsMap = masteryMap[starKey] || {{}};

                                let slotData = null;
                                for (let s = mState.slots; s >= 1; s--) {{
                                    if (slotsMap[s]) {{
                                        slotData = slotsMap[s];
                                        break;
                                    }}
                                }}

                                const queueCell = row.querySelector('.queue-cell-content');
                                const profitCell = row.querySelector('.row-profit-cell');

                                if (slotData) {{
                                    if (queueCell) queueCell.innerHTML = slotData.html || '<i>No item configuration fit in this window.</i>';
                                    if (profitCell) profitCell.innerHTML = `${{slotData.profit.toLocaleString('en-US', {{ maximumFractionDigits: 0 }})}}${{coinImgHtml}}`;

                                    panelTotalProfit += slotData.profit;

                                    if (slotData.ingredients) {{
                                        for (const [ingName, qty] of Object.entries(slotData.ingredients)) {{
                                            dynamicIngredients[ingName] = (dynamicIngredients[ingName] || 0) + qty;
                                        }}
                                    }}
                                }} else {{
                                    if (queueCell) queueCell.innerHTML = '<i>No items match time constraint.</i>';
                                    if (profitCell) profitCell.innerHTML = `0${{coinImgHtml}}`;
                                }}
                            }} else {{
                                row.style.display = 'none';
                            }}
                        }} else {{
                            row.style.display = 'none';
                        }}
                    }});

                    const surplusDisplay = panel.querySelector('.surplus-margin-val');
                    if (surplusDisplay) {{
                        surplusDisplay.innerHTML = `${{panelTotalProfit.toLocaleString('en-US', {{ maximumFractionDigits: 0 }})}}${{coinImgHtml}}`;
                    }}

                    let siloSpace = 0;
                    let barnSpace = 0;

                    const listContainer = panel.querySelector('.shopping-list');
                    const entries = Object.entries(dynamicIngredients).sort((a, b) => b[1] - a[1]);

                    if (listContainer) {{
                        if (entries.length === 0) {{
                            listContainer.innerHTML = '<li>None (No raw items processed).</li>';
                        }} else {{
                            listContainer.innerHTML = entries.map(([ingName, qty]) => {{
                                const cleanFilename = `${{DETAIL_DIR}}/details_${{ingName.toLowerCase().replace(/ /g, '_').replace(/-/g, '_')}}.html`;
                                const assetKey = ingName.toLowerCase().trim().replace(/ /g, '_');
                                const imgSrc = ASSET_BANK[assetKey] || '';
                                const imgHtml = imgSrc ? `<img class="inline-item-img" src="${{imgSrc}}" alt="${{ingName}}">` : '';

                                return `<li><a href="${{cleanFilename}}" class="item-link">${{imgHtml}} <b>${{qty}}x</b> ${{ingName}}</a></li>`;
                            }}).join('');
                        }}
                    }}

                    for (const [ingName, qty] of entries) {{
                        if (SILO_ITEMS.has(ingName)) {{
                            siloSpace += qty;
                        }} else {{
                            barnSpace += qty;
                        }}
                    }}

                    const siloDisplay = panel.querySelector('.silo-space-val');
                    if (siloDisplay) siloDisplay.innerText = siloSpace.toLocaleString('en-US');

                    const barnDisplay = panel.querySelector('.barn-space-val');
                    if (barnDisplay) barnDisplay.innerText = barnSpace.toLocaleString('en-US');

                    hydrateAssets(panel);
                }});
            }}

            function createMachineCard(config) {{
                const container = document.getElementById("machines-container");
                if (!container) return;

                const isFirstInstance = config.id.endsWith('_1');

                const state = {{
                    id: config.id,
                    assetKey: config.assetKey,
                    name: config.name,
                    minLevel: config.minLevel,
                    selected: !!config.initialSelected,
                    slots: Math.min(Math.max(config.currentSlots, config.minSlots), config.maxSlots),
                    minSlots: config.minSlots,
                    maxSlots: config.maxSlots,
                    mastery: config.currentMastery || 0
                }};

                const card = document.createElement('div');
                card.className = state.selected ? 'machine-card selected' : 'machine-card';
                card.setAttribute('data-min-level', config.minLevel);

                const imgSrc = ASSET_BANK[config.assetKey] || "";
                const diamondImgSrc = ASSET_BANK["diamond"] || "";

                card.innerHTML = `
                    <h4>${{config.name}}</h4>
                    <div class="lvl-tag">Unlocked Level ${{config.minLevel}}</div>
                    <img src="${{imgSrc}}" class="card-img" alt="${{config.name}}">
                    <div class="mastery-stars-container ${{state.selected ? '' : 'disabled-controls'}}"></div>
                    <div class="slots-grid ${{state.selected ? '' : 'disabled-controls'}}"></div>
                `;

                container.appendChild(card);
                const starsContainer = card.querySelector('.mastery-stars-container');
                const slotsGrid = card.querySelector('.slots-grid');

                function renderStars() {{
                    starsContainer.innerHTML = '';
                    if (!isFirstInstance) return; // Only render star controls on the 1st machine instance

                    for (let star = 1; star <= 3; star++) {{
                        const starSpan = document.createElement('span');
                        starSpan.className = `star-btn ${{star <= state.mastery ? 'active' : ''}}`;
                        starSpan.innerHTML = '★';
                        starSpan.title = `Mastery Star ${{star}}`;

                        starSpan.addEventListener('click', (e) => {{
                            e.stopPropagation();
                            const newMastery = (state.mastery === star) ? star - 1 : star;

                            // Propagate the star level to all matching machines (e.g. Smelters 1..5)
                            machineInstances.forEach(other => {{
                                if (other.assetKey === state.assetKey) {{
                                    other.mastery = newMastery;
                                }}
                            }});

                            renderStars();
                            logMachineStateChange('Mastery Changed', state);
                        }});
                        starsContainer.appendChild(starSpan);
                    }}
                }}

                function renderSlots() {{
                    slotsGrid.innerHTML = '';

                    for (let i = 0; i < state.slots; i++) {{
                        const tile = document.createElement('div');
                        tile.className = 'slot-tile empty-slot';
                        tile.innerText = 'EMPTY';
                        tile.title = "Click to remove this slot";

                        tile.addEventListener('click', (e) => {{
                            e.stopPropagation();
                            if (state.slots > state.minSlots) {{
                                state.slots--;
                                renderSlots();
                                logMachineStateChange('Slot Removed', state);
                            }}
                        }});

                        slotsGrid.appendChild(tile);
                    }}

                    if (state.slots < state.maxSlots) {{
                        const buyTile = document.createElement('div');
                        buyTile.className = 'slot-tile buy-slot';

                        if (diamondImgSrc) {{
                            buyTile.innerHTML = `<span style="font-size:10px; line-height:1;">+</span><img src="${{diamondImgSrc}}" class="buy-diamond-icon" alt="diamond">`;
                        }} else {{
                            buyTile.innerHTML = `<span style="font-size:10px; line-height:1;">+</span><img class="buy-diamond-icon" data-asset="diamond" alt="diamond">`;
                        }}
                        buyTile.title = "Click to buy another slot";

                        buyTile.addEventListener('click', (e) => {{
                            e.stopPropagation();
                            if (state.slots < state.maxSlots) {{
                                state.slots++;
                                renderSlots();
                                logMachineStateChange('Slot Purchased', state);
                            }}
                        }});

                        slotsGrid.appendChild(buyTile);
                    }}
                }}

                card.addEventListener('click', () => {{
                    state.selected = !state.selected;
                    card.classList.toggle('selected', state.selected);
                    starsContainer.classList.toggle('disabled-controls', !state.selected);
                    slotsGrid.classList.toggle('disabled-controls', !state.selected);

                    logMachineStateChange(state.selected ? 'Machine Enabled' : 'Machine Disabled', state);
                }});

                renderStars();
                renderSlots();
                machineInstances.push(state);
            }}

            function getSelectedMachinesData() {{
                return machineInstances.filter(m => m.selected).map(m => ({{
                    id: m.id,
                    name: m.name,
                    slots: m.slots,
                    mastery: m.mastery
                }}));
            }}

            function switchTab(evt, tabId) {{
                let panels = document.getElementsByClassName("content-panel");
                for (let p of panels) {{ p.classList.remove("active"); }}

                let tabs = document.getElementsByClassName("tab-link");
                for (let t of tabs) {{ t.classList.remove("active"); }}

                document.getElementById(tabId).classList.add("active");
                evt.currentTarget.classList.add("active");
                updateStrategyVisibility();
            }}

            function switchLevel(selectedLevel) {{
                selectedLevel = selectedLevel.toString();
                const numLevel = parseInt(selectedLevel, 10);
                document.getElementById("overnightLevelDisplay").innerText = "Lvl " + selectedLevel;

                let levelPanels = document.querySelectorAll(".level-panel");
                levelPanels.forEach(panel => {{
                    let validLevels = (panel.getAttribute("data-levels") || panel.getAttribute("data-level") || "").split(",");
                    if (validLevels.includes(selectedLevel)) {{
                        panel.style.display = "block";
                    }} else {{
                        panel.style.display = "none";
                    }}
                }});

                document.querySelectorAll('.machine-card').forEach(card => {{
                    const minLvl = parseInt(card.getAttribute('data-min-level') || '1', 10);
                    if (minLvl > numLevel) {{
                        card.style.display = 'none';
                    }} else {{
                        card.style.display = 'flex';
                    }}
                }});
                updateStrategyVisibility();
            }}

            document.addEventListener("DOMContentLoaded", function() {{
                initMachineCards();
                hydrateAssets();
                let slider = document.getElementById("overnightLevelRange");
                if (slider) switchLevel(slider.value);
            }});
        </script>
    </body>
    </html>
    """

    target_path = os.path.join(outp, "overnight_strategies.html")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(html_content)