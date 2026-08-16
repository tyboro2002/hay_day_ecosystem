import os

from calculators.profitability import analyze_value_added
from game_data.game_data import (
    ANIMAL_ITEMS,
    CROPS,
    CURRENT_LEVEL,
    DIAMOND_COST,
    FEEDS,
    MACHINED_ITEMS,
    MAX_LEVEL,
    PLANTS,
)
from visualizers.helpers.formatting import get_base64_asset
from visualizers.helpers.templates import (
    DISCLAIMER_FOOTER,
    render_level_filter_persistence_script,
)


def get_item_category(item_name):
    """Categorizes an item name based on game_data registry mappings."""
    if item_name in CROPS:
        return "crops", "Crops"
    elif item_name in PLANTS:
        return "plants", "Plants & Orchards"
    elif item_name in ANIMAL_ITEMS:
        return "animal_items", "Animal Products"
    elif item_name in FEEDS:
        return "feeds", "Animal Feeds"
    elif item_name in MACHINED_ITEMS:
        return "machined_items", "Machined Goods"
    return "other", "Other"


def generate_profitability_ranking_page(outp, detail_dir):
    """Generates a complete, interactive HTML ranking report with aligned filters and scannable tables."""
    data = analyze_value_added(silent=True)

    # Fetch global coin image asset for dynamic inline use
    coin_b64 = get_base64_asset("coin", "items")
    coin_img_html = (
        f'<img class="coin-icon" src="{coin_b64}" alt="coins">'
        if coin_b64
        else "coins"
    )
    coin_per_h_html = (
        f'<span class="coin-rate">{coin_img_html}/h</span>'
        if coin_b64
        else "coins/h"
    )

    # Sort data variations
    by_max_price = sorted(data, key=lambda x: x["final_price"], reverse=True)
    by_value = sorted(data, key=lambda x: x["value_added"], reverse=True)
    by_pph = sorted(data, key=lambda x: x["pph"], reverse=True)
    by_roi = sorted(
        [x for x in data if x["direct_cost"] > 0],
        key=lambda x: x["roi"],
        reverse=True,
    )

    def build_table_rows(dataset, score_type):
        rows_html = ""
        for item in dataset:
            warning = "⚠️" if item["value_added"] < 0 else ""

            # Retrieve item unlock level (defaults to 1 if not present)
            unlock_level = item.get(
                "unlock_level",
                getattr(item.get("item_obj", None), "unlock_level", 1),
            )

            # Determine category key for JS filtering
            category_key, _ = get_item_category(item["name"])

            # Retrieve the base64 string for the item's image
            img_base64 = get_base64_asset(item["name"], "items")
            img_tag = (
                f'<img class="table-item-img" src="{img_base64}"'
                f' alt="{item["name"]}">'
                if img_base64
                else ""
            )

            # Format custom metrics based on table column scope
            if score_type == "value":
                metric_td = (
                    '<td style="white-space:nowrap;">'
                    f'<b>{item["value_added"]:+.1f}</b>{coin_img_html}</td>'
                )
            elif score_type == "pph":
                metric_td = (
                    '<td style="white-space:nowrap;">'
                    f'<b>{item["pph"]:+.1f}</b>{coin_per_h_html}</td>'
                )
            elif score_type == "max_price":
                metric_td = (
                    '<td style="white-space:nowrap;">'
                    f'<b>{item["value_added"]:+.1f}</b>{coin_img_html}</td>'
                )
            else:
                metric_td = f"<td><b>{item['roi']:.1f}%</b></td>"

            clean_filename = f"{detail_dir}/details_{item['name'].lower().replace(' ', '_').replace('-', '_')}.html"

            rows_html += f"""
            <tr class="item-row" data-unlock-level="{unlock_level}" data-category="{category_key}">
                <td class="item-name-cell">
                    {warning}
                    <a href="{clean_filename}" class="item-link">
                        {img_tag}
                        <span>{item['name']}</span>
                    </a>
                </td>
                <td style="white-space:nowrap;">Lvl {unlock_level}</td>
                <td style="white-space:nowrap;">{item['final_price']}{coin_img_html}</td>
                <td style="white-space:nowrap;">{item['direct_cost']:.1f}{coin_img_html}</td>
                <td>{item['time_hours']:.2f}h</td>
                {metric_td}
            </tr>
            """
        return rows_html

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Hay Day Factory Ledger - Profitability Rankings</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1a1a1a; color: #e0e0e0; padding: 20px; }}
            h1 {{ color: #e67e22; text-align: center; margin-bottom: 5px; }}
            p.subtitle {{ text-align: center; color: #888; margin-bottom: 30px; }}

            /* Control Panel Section */
            .level-filter-container {{
                max-width: 1000px;
                margin: 0 auto 20px auto;
                background-color: #252525;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 15px 20px;
                display: flex;
                flex-direction: column;
                gap: 12px;
            }}
            .filter-row {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 15px;
                width: 100%;
            }}
            .level-slider-group {{
                display: flex;
                align-items: center;
                gap: 15px;
                flex-grow: 1;
            }}
            .level-slider-group label {{
                font-weight: bold;
                color: #e67e22;
                white-space: nowrap;
            }}
            .level-slider {{
                flex-grow: 1;
                accent-color: #e67e22;
                cursor: pointer;
                height: 6px;
            }}
            .level-badge {{
                background-color: #e67e22;
                color: #fff;
                padding: 4px 12px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 0.9rem;
                min-width: 60px;
                text-align: center;
            }}

            /* Category Filter Dropdown Styling */
            .category-filter-group {{
                display: flex;
                align-items: center;
                gap: 10px;
                margin-left: auto;
            }}
            .category-filter-group label {{
                font-weight: bold;
                color: #e67e22;
                white-space: nowrap;
            }}
            .category-select {{
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 0.9rem;
                cursor: pointer;
                outline: none;
                transition: border-color 0.2s ease;
            }}
            .category-select:hover, .category-select:focus {{
                border-color: #e67e22;
            }}

            .item-count-badge {{
                font-size: 0.85rem;
                color: #aaa;
                background-color: #1a1a1a;
                padding: 4px 10px;
                border-radius: 4px;
                border: 1px solid #333;
                white-space: nowrap;
            }}

            /* Diamond Cost Notice Banner */
            .diamond-notice {{ 
                max-width: 1000px; 
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

            /* Metric Context Explanations */
            .metric-context {{
                background-color: #282828;
                border: 1px dashed #444;
                border-radius: 4px;
                padding: 12px 16px;
                margin: 10px 0 20px 0;
                font-size: 0.9rem;
                line-height: 1.45;
                color: #b0b0b0;
            }}
            .metric-context b {{ color: #e67e22; }}
            .metric-context ul {{ margin: 6px 0 0 0; padding-left: 20px; }}
            .metric-context li {{ margin-bottom: 4px; }}

            .back-btn {{ display: inline-block; background-color: #34495e; color: #fff; padding: 8px 15px; border-radius: 4px; text-decoration: none; margin-bottom: 20px; font-size: 0.9rem; }}
            .back-btn:hover {{ background-color: #2c3e50; }}

            /* CSS Tabs Layout */
            .tabs-container {{ max-width: 1000px; margin: 0 auto; }}
            .tabs {{ display: flex; list-style: none; padding: 0; margin: 0; border-bottom: 2px solid #333; }}
            .tab-link {{ padding: 12px 24px; cursor: pointer; background: #252525; color: #aaa; font-weight: bold; border-radius: 6px 6px 0 0; margin-right: 4px; border: 1px solid #333; border-bottom: none; }}
            .tab-link.active {{ background: #e67e22; color: white; border-color: #e67e22; }}

            .tab-content {{ background: #222; border: 1px solid #333; border-top: none; padding: 20px; border-radius: 0 0 6px 6px; }}
            .content-panel {{ display: none; }}
            .content-panel.active {{ display: block; }}

            /* Responsive Tables */
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; color: #ddd; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #333; vertical-align: middle; }}
            th {{ background-color: #2d2d2d; color: #e67e22; font-weight: 600; }}
            tr:hover {{ background-color: #2a2a2a; }}
            tr td:last-child {{ color: #2ecc71; }}

            /* Coin Asset Scaling & Inline Rules */
            .coin-icon {{ width: 18px; height: 18px; object-fit: contain; vertical-align: middle; display: inline-block; margin-left: 3px; margin-top: -2px; }}
            .coin-rate {{ display: inline-flex; align-items: center; vertical-align: middle; }}
            .coin-rate .coin-icon {{ margin-right: 1px; }}

            /* Layout styling for inline item assets */
            .item-name-cell {{ display: flex; align-items: center; gap: 10px; }}
            .table-item-img {{ width: 32px; height: 32px; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.5)); }}

            /* Seamless Item Link Styling */
            .item-link {{ display: inline-flex; align-items: center; gap: 10px; color: inherit; text-decoration: none; }}
            .item-link:hover, .item-link:visited, .item-link:active {{ color: inherit; text-decoration: none; }}

            /* Global footer styles */
            .sc-disclaimer-footer {{ margin-top: 40px; color: #666; font-size: 0.8rem; text-align: center; line-height: 1.4; }}
            .sc-disclaimer-footer a {{ color: #3498db; text-decoration: none; }}
            .sc-disclaimer-footer a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>

        <div class="tabs-container">
            <a class="back-btn" href="index.html">⬅ Back to Farm Map</a>
            <h1>Profit Analytics</h1>

            <!-- Dynamic Level Selector & Category Filter Control -->
            <div class="level-filter-container">
                <!-- Row 1: Level Slider & Item Counter -->
                <div class="filter-row">
                    <div class="level-slider-group">
                        <label for="levelRange">Filter Level:</label>
                        <input type="range" id="levelRange" class="level-slider" min="1" max="{MAX_LEVEL}" value="{CURRENT_LEVEL}" oninput="applyFilters()">
                        <span id="levelDisplay" class="level-badge">Lvl {CURRENT_LEVEL}</span>
                    </div>
                    <div id="unlockedCount" class="item-count-badge">Showing all items</div>
                </div>

                <!-- Row 2: Category Dropdown (Right-aligned to flush with unlockedCount above) -->
                <div class="filter-row">
                    <div class="category-filter-group">
                        <label for="categorySelect">Category:</label>
                        <select id="categorySelect" class="category-select" onchange="applyFilters()">
                            <option value="all">All Categories</option>
                            <option value="crops">Crops</option>
                            <option value="plants">Plants & Orchards</option>
                            <option value="animal_items">Animal Products</option>
                            <option value="feeds">Animal Feeds</option>
                            <option value="machined_items">Machined Goods</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Dynamic Diamond Cost Disclaimer Banner -->
            <div class="diamond-notice">
                💎 <b>Note:</b> For items requiring raw diamonds as recipe ingredients, missing market values default to an imputed substitute cost of <b>{DIAMOND_COST} {coin_img_html}</b> per diamond.
            </div>

            <ul class="tabs">
                <li class="tab-link active" onclick="switchTab(event, 'value-tab')">Value Added / Item</li>
                <li class="tab-link" onclick="switchTab(event, 'pph-tab')">Profit / Hour (PPH)</li>
                <li class="tab-link" onclick="switchTab(event, 'roi-tab')">Return on Investment (ROI)</li>
                <li class="tab-link" onclick="switchTab(event, 'max-price-tab')">Max Price</li>
            </ul>

            <div class="tab-content">
                <!-- PANEL 1: VALUE ADDED -->
                <div id="value-tab" class="content-panel active">
                    <h3>Sorted by Absolute Value Added (Market Price minus Material Costs)</h3>
                    <div class="metric-context">
                        <b>Calculation:</b> <code>Max Roadside Price - Total Cost of Raw Ingredients</code>.
                        <br><b>What it means:</b> The pure net coin expansion gained solely from processing ingredients into this final product. Negative values (⚠️) mean processing raw components actually destroys coin wealth compared to selling ingredients directly.
                        <br><b>How to use it:</b> Ideal strategy for setting up overnight queue production or when your machine slots sit idle for long chunks of the day.
                    </div>
                    <table>
                        <thead>
                            <tr><th>Item Name</th><th>Req Lvl</th><th>Max Price</th><th>Material Costs</th><th>Craft Time</th><th>Value Added</th></tr>
                        </thead>
                        <tbody>{build_table_rows(by_value, "value")}</tbody>
                    </table>
                </div>

                <!-- PANEL 2: PROFIT PER HOUR -->
                <div id="pph-tab" class="content-panel">
                    <h3>Sorted by Active Time Optimization (Hourly Velocity)</h3>
                    <div class="metric-context">
                        <b>Calculation:</b> <code>Value Added &divide; Machine Craft Time (Hours)</code>.
                        <br><b>What it means:</b> The financial velocity of a machine slot. It measures how aggressively an active machine generates margin every 60 minutes it runs.
                        <br><b>How to use it:</b> Essential benchmark for active play-sessions. If you are constantly managing your farm and clearing machine outputs, queuing high-PPH items yields the absolute maximum cash flow across a gaming session.
                    </div>
                    <table>
                        <thead>
                            <tr><th>Item Name</th><th>Req Lvl</th><th>Max Price</th><th>Material Costs</th><th>Craft Time</th><th>Profit / Hour</th></tr>
                        </thead>
                        <tbody>{build_table_rows(by_pph, "pph")}</tbody>
                    </table>
                </div>

                <!-- PANEL 3: ROI -->
                <div id="roi-tab" class="content-panel">
                    <h3>Sorted by Relative Returns (Yield Efficiency per spent coin)</h3>
                    <div class="metric-context">
                        <b>Calculation:</b> <code>(Value Added &divide; Material Costs) &times; 100%</code>.
                        <br><b>What it means:</b> Capital multiplication efficiency. It answers the question: "For every single coin I tie up buying or growing inputs, how much surplus interest does this item payout?"
                        <br><b>How to use it:</b> Best used when running a lean budget or when material reserves are tight. High ROI items stretch limited raw inventory into the largest possible return margins.
                    </div>
                    <table>
                        <thead>
                            <tr><th>Item Name</th><th>Req Lvl</th><th>Max Price</th><th>Material Costs</th><th>Craft Time</th><th>ROI Margin</th></tr>
                        </thead>
                        <tbody>{build_table_rows(by_roi, "roi")}</tbody>
                    </table>
                </div>

                <!-- PANEL 4: MAX PRICE -->
                <div id="max-price-tab" class="content-panel">
                    <h3>Sorted by Max Market Price</h3>
                    <div class="metric-context">
                        <b>Calculation:</b> <code>Max Roadside Price</code>.
                        <br><b>What it means:</b> The pure coins gained solely from selling this final product.
                        <br><b>How to use it:</b> Ideal strategy for setting up what to sell for quick coin gain.
                    </div>
                    <table>
                        <thead>
                            <tr><th>Item Name</th><th>Req Lvl</th><th>Max Price</th><th>Material Costs</th><th>Craft Time</th><th>Value Added</th></tr>
                        </thead>
                        <tbody>{build_table_rows(by_max_price, "max_price")}</tbody>
                    </table>
                </div>
            </div>
            {DISCLAIMER_FOOTER.format(path_prefix="")}
        </div>

        {render_level_filter_persistence_script()}

        <script>
            function switchTab(evt, tabId) {{
                let panels = document.getElementsByClassName("content-panel");
                for (let p of panels) {{ p.classList.remove("active"); }}

                let tabs = document.getElementsByClassName("tab-link");
                for (let t of tabs) {{ t.classList.remove("active"); }}

                document.getElementById(tabId).classList.add("active");
                evt.currentTarget.classList.add("active");
            }}

            function applyFilters() {{
                const selectedLevel = parseInt(document.getElementById("levelRange").value, 10);
                const selectedCategory = document.getElementById("categorySelect").value;

                document.getElementById("levelDisplay").innerText = "Lvl " + selectedLevel;

                let rows = document.querySelectorAll(".item-row");
                let visibleCount = 0;

                rows.forEach(row => {{
                    let itemLevel = parseInt(row.getAttribute("data-unlock-level")) || 1;
                    let itemCategory = row.getAttribute("data-category") || "";

                    let matchLevel = itemLevel <= selectedLevel;
                    let matchCategory = (selectedCategory === "all") || (itemCategory === selectedCategory);

                    if (matchLevel && matchCategory) {{
                        row.style.display = "";
                        visibleCount++;
                    }} else {{
                        row.style.display = "none";
                    }}
                }});

                // Divide total matching table rows by 4 (since items are replicated across all 4 tab panels)
                let uniqueVisible = Math.floor(visibleCount / 4);
                document.getElementById("unlockedCount").innerText = "Showing items: " + uniqueVisible;

                if (window.HayDayLevelFilterPersistence) {{
                    window.HayDayLevelFilterPersistence.writeStoredLevel(selectedLevel);
                }}
            }}

            // Run initial filter on page load
            document.addEventListener("DOMContentLoaded", function() {{
                const slider = document.getElementById("levelRange");
                const initialLevel = window.HayDayLevelFilterPersistence
                    ? window.HayDayLevelFilterPersistence.readStoredLevel(parseInt(slider.value || "{CURRENT_LEVEL}", 10), parseInt(slider.max || "{MAX_LEVEL}", 10))
                    : parseInt(slider.value || "{CURRENT_LEVEL}", 10);
                slider.value = String(initialLevel);
                applyFilters();
            }});
        </script>
    </body>
    </html>
    """

    # Ensure output target directory exists and save the file
    target_path = os.path.join(outp, "general_profitability.html")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(html_content)