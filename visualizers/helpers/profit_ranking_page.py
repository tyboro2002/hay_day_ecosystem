import os

from calculators.profitability import analyze_value_added
from game_data.game_data import DIAMOND_COST
from visualizers.helpers.formatting import get_base64_asset
from visualizers.helpers.templates import DISCLAIMER_FOOTER


def generate_profitability_ranking_page(outp, detail_dir):
    """Generates a complete, interactive HTML ranking report with scannable tables."""
    data = analyze_value_added(silent=True)

    # Fetch global coin image asset for dynamic inline use
    coin_b64 = get_base64_asset("coin", "items")  # Resolves path items/coin.png via system asset helpers
    coin_img_html = f'<img class="coin-icon" src="{coin_b64}" alt="coins">' if coin_b64 else "coins"
    coin_per_h_html = f'<span class="coin-rate">{coin_img_html}/h</span>' if coin_b64 else "coins/h"

    # Sort data variations
    by_value = sorted(data, key=lambda x: x["value_added"], reverse=True)
    by_pph = sorted(data, key=lambda x: x["pph"], reverse=True)
    by_roi = sorted([x for x in data if x["direct_cost"] > 0], key=lambda x: x["roi"], reverse=True)

    def build_table_rows(dataset, score_type):
        rows_html = ""
        for item in dataset:
            warning = "⚠️" if item["value_added"] < 0 else ""

            # Retrieve the base64 string for the item's image
            img_base64 = get_base64_asset(item['name'], "items")
            img_tag = f'<img class="table-item-img" src="{img_base64}" alt="{item["name"]}">' if img_base64 else ""

            # Format custom metrics based on table column scope
            if score_type == "value":
                metric_td = f'<td style="white-space:nowrap;"><b>{item["value_added"]:+.1f}</b>{coin_img_html}</td>'
            elif score_type == "pph":
                metric_td = f'<td style="white-space:nowrap;"><b>{item["pph"]:+.1f}</b>{coin_per_h_html}</td>'
            else:
                metric_td = f"<td><b>{item['roi']:.1f}%</b></td>"

            clean_filename = f"{detail_dir}/details_{item['name'].lower().replace(' ', '_').replace('-', '_')}.html"

            rows_html += f"""
            <tr>
                <td class="item-name-cell">
                    {warning}
                    <a href="{clean_filename}" class="item-link">
                        {img_tag}
                        <span>{item['name']}</span>
                    </a>
                </td>
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
            
            /* Global footer styles match inside template variables */
            .sc-disclaimer-footer {{ margin-top: 40px; color: #666; font-size: 0.8rem; text-align: center; line-height: 1.4; }}
            .sc-disclaimer-footer a {{ color: #3498db; text-decoration: none; }}
            .sc-disclaimer-footer a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>

        <div class="tabs-container">
            <a class="back-btn" href="index.html">⬅ Back to Farm Map</a>
            <h1>Profit Analytics</h1>

            <!-- Dynamic Diamond Cost Disclaimer Banner -->
            <div class="diamond-notice">
                💎 <b>Note:</b> For items requiring raw diamonds as recipe ingredients, missing market values default to an imputed substitute cost of <b>{DIAMOND_COST} {coin_img_html}</b> per diamond.
            </div>

            <ul class="tabs">
                <li class="tab-link active" onclick="switchTab(event, 'value-tab')">Value Added / Item</li>
                <li class="tab-link" onclick="switchTab(event, 'pph-tab')">Profit / Hour (PPH)</li>
                <li class="tab-link" onclick="switchTab(event, 'roi-tab')">Return on Investment (ROI)</li>
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
                            <tr><th>Item Name</th><th>Max Price</th><th>Material Costs</th><th>Craft Time</th><th>Value Added</th></tr>
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
                            <tr><th>Item Name</th><th>Max Price</th><th>Material Costs</th><th>Craft Time</th><th>Profit / Hour</th></tr>
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
                            <tr><th>Item Name</th><th>Max Price</th><th>Material Costs</th><th>Craft Time</th><th>ROI Margin</th></tr>
                        </thead>
                        <tbody>{build_table_rows(by_roi, "roi")}</tbody>
                    </table>
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
    target_path = os.path.join(outp, "general_profitability.html")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(html_content)