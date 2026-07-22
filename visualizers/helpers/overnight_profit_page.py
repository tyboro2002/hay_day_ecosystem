import os
from collections import defaultdict

from calculators.overnight_strategy import get_best_overnight_strategy, TOTAL_FIELDS
from game_data.crops_data import CROPS
from game_data.game_data import DIAMOND_COST
from game_data.machines_data import MACHINES
from game_data.plants_data import PLANTS
from visualizers.helpers.formatting import get_base64_asset
from visualizers.helpers.templates import DISCLAIMER_FOOTER


def build_duration_html(sleep_duration_mins, detail_dir):
    """Calculates strategy data and generates the localized template blocks for a given time window."""
    plan, global_profit = get_best_overnight_strategy(sleep_duration_mins)

    # Fetch global coin image asset for dynamic inline use
    coin_b64 = get_base64_asset("coin", "items")  # Resolves path items/coin.png via system asset helpers
    coin_img_html = f'<img class="coin-icon" src="{coin_b64}" alt="coins">' if coin_b64 else "coins"

    global_ingredients = defaultdict(int)
    machine_rows_html = ""

    # Process Field/Machine allocations
    for source_name, data in plan.items():
        if not data['combination']:
            continue

        # Fetch machine/building visual asset with fallback for fields
        if source_name == "Fields":
            machine_b64 = get_base64_asset("fields", "fields")
        else:
            machine_b64 = get_base64_asset(source_name, "machines")

        machine_img_html = f'<img class="inline-machine-img" src="{machine_b64}" alt="{source_name}">' if machine_b64 else ""

        machine_clean_filename = f"{detail_dir}/details_{source_name.lower().replace(' ', '_').replace('-', '_')}.html"

        combo_parts = []
        for item_obj, count in data['combination'].items():
            clean_filename = f"{detail_dir}/details_{item_obj.name.lower().replace(' ', '_').replace('-', '_')}.html"
            img_b64 = get_base64_asset(item_obj.name, "items")
            img_html = f'<img class="inline-item-img" src="{img_b64}" alt="{item_obj.name}">' if img_b64 else ""
            combo_parts.append(f'<a href="{clean_filename}" class="item-link queue-pill">{img_html} {count}x {item_obj.name}</a>')

            # Aggregate ingredient requirements
            ingredients_dict = getattr(item_obj, 'ingredients', {})
            if isinstance(ingredients_dict, dict):
                for ing_obj, qty in ingredients_dict.items():
                    global_ingredients[ing_obj.name] += (qty * (count // max(1, getattr(MACHINES.get(source_name), 'amount_owned', 1))))

        machine_rows_html += f"""
        <tr>
            <td class="source-cell">
                <a href="{machine_clean_filename}" class="machine-label-wrapper item-link">
                    {machine_img_html}
                    <b>{source_name}</b>
                </a>
            </td>
            <td><div class="queue-flex">{" ".join(combo_parts)}</div></td>
            <td style="color:#2ecc71; font-weight:bold; white-space:nowrap;">
                {data['total_profit']:+.0f}{coin_img_html}
            </td>
        </tr>
        """

    # Append required seeds to pre-stock inventory if field production is used
    if "Fields" in plan:
        for crop_obj in plan["Fields"]["combination"].keys():
            global_ingredients[crop_obj.name] += TOTAL_FIELDS

    # Compute storage footprints
    silo_space = 0
    barn_space = 0
    shopping_list_html = ""

    for ing_name, qty in sorted(global_ingredients.items(), key=lambda x: x[1], reverse=True):
        clean_filename = f"{detail_dir}/details_{ing_name.lower().replace(' ', '_').replace('-', '_')}.html"
        img_b64 = get_base64_asset(ing_name, "items")
        img_html = f'<img class="inline-item-img" src="{img_b64}" alt="{ing_name}">' if img_b64 else ""

        shopping_list_html += f'<li><a href="{clean_filename}" class="item-link">{img_html} <b>{qty}x</b> {ing_name}</a></li>'
        if ing_name in CROPS or ing_name in PLANTS:
            silo_space += qty
        else:
            barn_space += qty

    # Clean display formatting for storage values (up to 2 decimals, trailing zeroes stripped)
    silo_space_str = f"{silo_space:,.2f}".rstrip('0').rstrip('.')
    barn_space_str = f"{barn_space:,.2f}".rstrip('0').rstrip('.')

    # Fetch storage assets
    silo_b64 = get_base64_asset("silo", "storage")
    barn_b64 = get_base64_asset("barn", "storage")

    silo_img_html = f'<img class="stat-icon" src="{silo_b64}" alt="Silo">' if silo_b64 else ""
    barn_img_html = f'<img class="stat-icon" src="{barn_b64}" alt="Barn">' if barn_b64 else ""

    # Construct and return the full localized panel block
    return f"""
    <div class="dashboard-grid">
        <div class="stat-card">
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <div class="stat-val" style="color: #2ecc71; display: flex; align-items: center; gap: 6px;">
                    {global_profit:,.0f}{coin_img_html}
                </div>
                <div class="stat-lbl">Projected Surplus Margin</div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-content-wrapper">
                {silo_img_html}
                <div>
                    <div class="stat-val" style="color: #3498db;">{silo_space_str}</div>
                    <div class="stat-lbl">Required Silo Space (Seeds/Crops)</div>
                </div>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-content-wrapper">
                {barn_img_html}
                <div>
                    <div class="stat-val" style="color: #9b59b6;">{barn_space_str}</div>
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
                    {machine_rows_html}
                </tbody>
            </table>
        </div>
        <div class="shopping-pane">
            <h3>Pre-Bed Stocking List</h3>
            <ul class="shopping-list">
                {shopping_list_html or "<li>None (No raw items processed).</li>"}
            </ul>
        </div>
    </div>
    """


def generate_overnight_page(outp, detail_dir):
    """Assembles independent sleep strategy options into a comprehensive web panel document."""

    # Also grab coin for the top notice banner inside generate_overnight_page
    coin_b64 = get_base64_asset("coin", "items")
    coin_img_html = f'<img class="coin-icon" src="{coin_b64}" alt="coins">' if coin_b64 else "coins"

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

            /* Diamond Cost Notice Banner */
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

            /* CSS Tabs Layout */
            .tabs-container {{ max-width: 1100px; margin: 0 auto; }}
            .tabs {{ display: flex; list-style: none; padding: 0; margin: 0; border-bottom: 2px solid #333; }}
            .tab-link {{ padding: 12px 24px; cursor: pointer; background: #252525; color: #aaa; font-weight: bold; border-radius: 6px 6px 0 0; margin-right: 4px; border: 1px solid #333; border-bottom: none; }}
            .tab-link.active {{ background: #e67e22; color: white; border-color: #e67e22; }}

            .tab-content {{ background: #222; border: 1px solid #333; border-top: none; padding: 25px; border-radius: 0 0 6px 6px; margin-bottom: 30px; }}
            .content-panel {{ display: none; }}
            .content-panel.active {{ display: block; }}

            /* Dashboard Cards Grid */
            .dashboard-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px; }}
            .stat-card {{ background-color: #2d2d2d; border: 1px solid #3d3d3d; border-radius: 6px; padding: 15px; display: flex; align-items: center; justify-content: center; min-height: 80px; }}
            .stat-content-wrapper {{ display: flex; align-items: center; gap: 15px; text-align: left; width: 100%; padding-left: 10px; }}
            .stat-icon {{ width: 42px; height: 42px; object-fit: contain; flex-shrink: 0; }}
            .stat-val {{ font-size: 1.8rem; font-weight: bold; margin-bottom: 5px; text-align: center; }}
            .stat-card:not(:first-child) .stat-val {{ text-align: left; }}
            .stat-lbl {{ font-size: 0.85rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }}

            /* Coin Asset Scaling */
            .coin-icon {{ width: 20px; height: 20px; object-fit: contain; vertical-align: middle; display: inline-block; margin-left: 3px; margin-top: -2px; }}
            .stat-val .coin-icon {{ width: 26px; height: 26px; margin-top: 0; }}

            /* Table and Component Layouts */
            .strategy-split {{ display: grid; grid-template-columns: 2.2fr 1fr; gap: 20px; }}
            h3 {{ color: #e67e22; margin-top: 0; border-bottom: 1px solid #333; padding-bottom: 8px; font-size: 1.1rem; }}

            table {{ width: 100%; border-collapse: collapse; color: #ddd; }}
            th, td {{ padding: 12px 10px; text-align: left; border-bottom: 1px solid #333; vertical-align: middle; }}
            th {{ background-color: #2d2d2d; color: #e67e22; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; }}
            tr:hover {{ background-color: #272727; }}
            .source-cell {{ color: #f39c12; }}

            /* Machine Labels Alignment */
            .machine-label-wrapper {{ display: flex; align-items: center; gap: 10px; color: #f39c12; }}
            .inline-machine-img {{ width: 32px; height: 32px; object-fit: contain; flex-shrink: 0; }}

            /* Queue Pills */
            .queue-flex {{ display: flex; flex-wrap: wrap; gap: 6px; }}
            .queue-pill {{ background: #2c3e50; color: #ecf0f1; padding: 4px 8px; border-radius: 12px; font-size: 0.8rem; display: flex; align-items: center; gap: 6px; border: 1px solid #34495e; }}
            .inline-item-img {{ width: 18px; height: 18px; object-fit: contain; }}

            /* Pre-bed Shopping Layout */
            .shopping-list {{ list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }}
            .shopping-list li {{ background: #282828; padding: 8px 12px; border-radius: 4px; border: 1px solid #333; font-size: 0.9rem; display: flex; align-items: center; gap: 10px; }}
            .shopping-list b {{ color: #e67e22; min-width: 28px; display: inline-block; }}
            
            /* Seamless Item Link Styling */
            .item-link {{ color: inherit; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; }}
            .item-link:hover, .item-link:visited, .item-link:active {{ color: inherit; text-decoration: none; }}
            .shopping-list li .item-link {{ gap: 10px; width: 100%; }}
            
            /* Global footer styles */
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

            <!-- Dynamic Diamond Cost Disclaimer Banner -->
            <div class="diamond-notice">
                💎 <b>Note:</b> Raw inputs requiring diamonds as base components default to an assumed utility valuation cost of <b>{DIAMOND_COST} {coin_img_html}</b>.
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
                <!-- PANEL 1: 1 HOURS -->
                <div id="tab-1h" class="content-panel active">
                    {build_duration_html(1*60, detail_dir)}
                </div>
                
                <!-- PANEL 2: 2 HOURS -->
                <div id="tab-2h" class="content-panel">
                    {build_duration_html(2*60, detail_dir)}
                </div>
                
                <!-- PANEL 3: 4 HOURS -->
                <div id="tab-4h" class="content-panel">
                    {build_duration_html(4*60, detail_dir)}
                </div>

                <!-- PANEL 4: 8 HOURS -->
                <div id="tab-8h" class="content-panel">
                    {build_duration_html(8*60, detail_dir)}
                </div>

                <!-- PANEL 5: 12 HOURS -->
                <div id="tab-12h" class="content-panel">
                    {build_duration_html(12*60, detail_dir)}
                </div>
                
                <!-- PANEL 6: 24 HOURS -->
                <div id="tab-24h" class="content-panel">
                    {build_duration_html(24*60, detail_dir)}
                </div>
            </div>

            {DISCLAIMER_FOOTER.format(path_prefix="")}
        </div>

        <script>
            function switchTab(evt, tabId) {{
                let panels = document.getElementsByClassName("content-panel");
                for (let p of panels) {{ p.classList.remove("active"); }}

                let tabs = document.getElementsByClassName("tab-link");
                for (let t of tabs) {{ t.classList.remove("active"); }}

                document.getElementById(tabId).classList.add("active");
                evt.currentTarget.classList.add("active");
            }}
        </script>
    </body>
    </html>
    """

    # Ensure output target directory exists and save the file
    target_path = os.path.join(outp, "overnight_strategies.html")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(html_content)