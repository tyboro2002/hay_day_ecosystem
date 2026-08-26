import os
import json
import urllib.request
from pathlib import Path
from visualizers.helpers.templates import DISCLAIMER_FOOTER

HOST_BASE = "https://tyboro2002.github.io"
API_BASE = f"{HOST_BASE}/hay_day_ecosystem/api/v2/"
ITEM_COLLECTIONS = [
    "crops",
    "plants",
    "animal_items",
    "machined_items",
    "animal_feeds",
    "special_items"
]

# ==============================================================================
# RULE CONFIGURATION FOR SPECIFIC FILTERS (EXACT MATCHES)
# ==============================================================================

BASE_PRICE_CAP_RULES = [
    {"names": ["axe", "saw"], "max_base_price": 500},
    {"names": ["dynamite", "tnt"], "max_base_price": 500},
    {"names": ["shovel", "pickaxe"], "max_base_price": 750},
    {"names": ["plank", "bolt", "duct tape"], "max_base_price": 4000},
    {"names": ["nail", "screw", "wood panel", "land deed", "mallet", "map piece", "marker stake", "brick", "hammer", "hand drill", "paint bucket", "stone block", "tar bucket"], "max_base_price" : 1500}
]

MAX_MULTIPLIER_RULES = []

# ==============================================================================
# CUSTOM MANUAL ITEMS
# ==============================================================================
CUSTOM_ITEMS = [
    {
        "id": "help",
        "name": "help",
        "category": "Custom Items",
        "image": "https://tyboro2002.github.io/hay_day_ecosystem/assets/extra/help.png",
        "max_base_price": 500,
        "max_multiplier": 1.0,
        "default_price": 500,
        "default_mult": 1.0
    },
    {
        "id": "bem_set",
        "name": "BEM Set",
        "category": "Custom Items",
        "image": "https://tyboro2002.github.io/hay_day_ecosystem/assets/extra/BEM_set.png",
        "max_base_price": 356000,
        "max_multiplier": 1.0,
        "default_price": 356000,
        "default_mult": 1.0
    },
    {
        "id": "sem_set",
        "name": "SEM Set",
        "category": "Custom Items",
        "image": "https://tyboro2002.github.io/hay_day_ecosystem/assets/extra/SEM_set.png",
        "max_base_price": 133500,
        "max_multiplier": 1.0,
        "default_price": 133500,
        "default_mult": 1.0
    },
    {
        "id": "lem_set",
        "name": "LEM Set",
        "category": "Custom Items",
        "image": "https://tyboro2002.github.io/hay_day_ecosystem/assets/extra/LEM_set.png",
        "max_base_price": 133500,
        "max_multiplier": 1.0,
        "default_price": 133500,
        "default_mult": 1.0
    },
    {
        "id": "tem_set",
        "name": "TEM Set",
        "category": "Custom Items",
        "image": "https://tyboro2002.github.io/hay_day_ecosystem/assets/extra/TEM_set.png",
        "max_base_price": 133500,
        "max_multiplier": 1.0,
        "default_price": 133500,
        "default_mult": 1.0
    }
]

def resolve_item_rules(item_name, collection_name, raw_base_price):
    name_lower = item_name.strip().lower()

    allowed_max_base = raw_base_price
    for rule in BASE_PRICE_CAP_RULES:
        rule_names = [n.lower() for n in rule["names"]]
        if name_lower in rule_names:
            allowed_max_base = rule["max_base_price"]

    allowed_max_mult = 1.0
    matched_mult_rule = False

    for rule in MAX_MULTIPLIER_RULES:
        rule_names = [n.lower() for n in rule["names"]]
        if name_lower in rule_names:
            allowed_max_mult = rule["max_multiplier"]
            matched_mult_rule = True
            break

    if not matched_mult_rule:
        if collection_name == "machined_items":
            allowed_max_mult = 5.0

    default_start_mult = 5.0 if collection_name == "machined_items" else 1.0
    default_start_mult = min(default_start_mult, allowed_max_mult)

    return allowed_max_base, allowed_max_mult, default_start_mult


def fetch_all_items():
    all_items = []

    for item in CUSTOM_ITEMS:
        all_items.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "category": item.get("category", "Custom Items"),
            "default_price": item.get("default_price", item.get("max_base_price")),
            "max_base_price": item.get("max_base_price"),
            "max_multiplier": item.get("max_multiplier"),
            "default_mult": item.get("default_mult", 1.0),
            "image": item.get("image")
        })

    print(f"Added {len(CUSTOM_ITEMS)} custom item(s).")
    print("Fetching item collections from API...")

    for col in ITEM_COLLECTIONS:
        url = f"{API_BASE}{col}/index.json"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                items = data.get("items", [])

                for item in items:
                    img_path = item.get("links", {}).get("image", "")
                    if img_path and not img_path.startswith("http"):
                        img_path = f"{HOST_BASE}{'' if img_path.startswith('/') else '/'}{img_path}"

                    raw_price = item.get("sell_price") or item.get("coin_cost") or 0
                    item_name = item.get("name", "")
                    item_id = item.get("id")

                    max_base, max_mult, default_mult = resolve_item_rules(item_name, col, raw_price)

                    all_items.append({
                        "id": item_id,
                        "name": item_name,
                        "category": col.replace("_", " ").title(),
                        "default_price": raw_price,
                        "max_base_price": max_base,
                        "max_multiplier": max_mult,
                        "default_mult": default_mult,
                        "image": img_path
                    })
            print(f"  ✓ Fetched {len(items)} items from '{col}'")
        except Exception as e:
            print(f"  ✗ Failed to fetch collection '{col}': {e}")

    return all_items

HTML_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hay Day Ticket & Shopping Grid Calculator</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <style>
        :root {{
            color-scheme: dark;
            --bg-1: #0f172a;
            --bg-2: #111827;
            --panel: rgba(17, 24, 39, 0.78);
            --panel-border: rgba(148, 163, 184, 0.18);
            --text: #e5e7eb;
            --muted: #94a3b8;
            --accent: #f59e0b;
            --accent-2: #fb7185;
            --shadow: rgba(0, 0, 0, 0.35);
        }}

        * {{ box-sizing: border-box; }}

        html, body {{
            margin: 0;
            width: 100%;
            min-height: 100vh;
            font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif;
            background:
                radial-gradient(circle at top left, rgba(245, 158, 11, 0.16), transparent 30%),
                radial-gradient(circle at bottom right, rgba(251, 113, 133, 0.13), transparent 28%),
                var(--bg-1);
            background-attachment: fixed;
            color: var(--text);
        }}

        body {{ padding: 24px 24px 60px; }}
        .wrap {{ max-width: 1200px; margin: 0 auto; }}
        header {{ margin-bottom: 24px; }}
        h1 {{ margin: 0 0 8px; font-size: clamp(1.8rem, 3vw, 2.8rem); letter-spacing: -0.04em; }}
        .subtitle {{ margin: 0; color: var(--muted); font-size: 0.95rem; }}

        .layout-grid {{
            display: grid;
            grid-template-columns: 1fr 440px;
            gap: 24px;
            align-items: start;
        }}

        @media (max-width: 900px) {{
            .layout-grid {{ grid-template-columns: 1fr; }}
        }}

        .card {{
            background: var(--panel);
            backdrop-filter: blur(16px);
            border: 1px solid var(--panel-border);
            border-radius: 24px;
            padding: 24px;
            box-shadow: 0 20px 60px var(--shadow);
        }}

        .filter-input, input[type="number"] {{
            background: rgba(15, 23, 42, 0.8);
            color: var(--text);
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 0.9rem;
            outline: none;
        }}

        .filter-input {{ width: 100%; margin-bottom: 12px; }}
        .filter-input:focus, input[type="number"]:focus {{ border-color: var(--accent); }}

        .asset-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
            gap: 10px;
            max-height: 240px;
            overflow-y: auto;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 16px;
            padding: 12px;
            margin-bottom: 20px;
        }}

        .asset-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 8px 6px;
            cursor: pointer;
            transition: all 0.15s ease;
            text-align: center;
        }}

        .asset-card:hover {{
            background: rgba(245, 158, 11, 0.15);
            border-color: var(--accent);
            transform: translateY(-2px);
        }}

        .asset-card.active {{
            background: rgba(245, 158, 11, 0.25);
            border-color: var(--accent);
            box-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
        }}

        .asset-card img {{ width: 40px; height: 40px; object-fit: contain; margin-bottom: 4px; }}
        .asset-card span {{ font-size: 0.7rem; color: var(--text); word-break: break-word; }}

        .row-list {{ display: flex; flex-direction: column; gap: 10px; }}
        .calc-row {{
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 14px;
            padding: 10px 14px;
            flex-wrap: wrap;
        }}

        .item-icon {{ width: 40px; height: 40px; object-fit: contain; }}
        .item-info {{ flex: 1; min-width: 120px; }}
        .item-title {{ font-weight: 600; font-size: 0.9rem; color: #fff; }}
        .item-sub {{ font-size: 0.75rem; color: var(--muted); display: block; }}

        .input-inline {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 2px;
        }}
        .input-inline label {{ font-size: 0.65rem; color: var(--muted); text-transform: uppercase; }}
        .input-inline input {{ width: 75px; text-align: center; }}

        .btn-inline-max {{
            background: rgba(245, 158, 11, 0.15);
            color: var(--accent);
            border: 1px solid rgba(245, 158, 11, 0.35);
            border-radius: 10px;
            height: 35px;
            padding: 0 10px;
            font-size: 0.75rem;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.15s ease;
        }}
        .btn-inline-max:hover {{
            background: rgba(245, 158, 11, 0.3);
            border-color: var(--accent);
        }}

        .btn-remove {{
            background: rgba(251, 113, 133, 0.15);
            color: var(--accent-2);
            border: 1px solid rgba(251, 113, 133, 0.3);
            border-radius: 10px;
            width: 35px;
            height: 35px;
            cursor: pointer;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .payment-section {{
            margin-top: 24px;
            padding-top: 16px;
            border-top: 1px dashed rgba(148, 163, 184, 0.2);
        }}

        .payment-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .payment-header h3 {{
            margin: 0;
            font-size: 0.95rem;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .payment-selected-info {{
            font-size: 0.8rem;
            color: var(--muted);
        }}

        .output-column {{ display: flex; flex-direction: column; gap: 28px; }}

        /* RECEIPT CARD STYLES */
        .receipt-card {{
            background: #fefce8;
            color: #1c1917;
            padding: 24px;
            border-radius: 4px;
            font-family: 'Courier New', Courier, monospace;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            position: relative;
        }}

        .receipt-card::after {{
            content: "";
            position: absolute;
            bottom: -8px;
            left: 0;
            right: 0;
            height: 8px;
            background: linear-gradient(-45deg, transparent 4px, #fefce8 0), linear-gradient(45deg, transparent 4px, #fefce8 0);
            background-repeat: repeat-x;
            background-size: 8px 8px;
        }}

        .receipt-header {{ text-align: center; margin-bottom: 16px; border-bottom: 1px dashed #78716c; padding-bottom: 12px; }}
        .receipt-header h2 {{ margin: 0; font-size: 1.3rem; color: #1c1917; text-transform: uppercase; word-break: break-word; }}
        .receipt-header p {{ margin: 4px 0 0; font-size: 0.75rem; color: #57534e; }}

        .receipt-table {{ width: 100%; border-collapse: collapse; font-size: 0.8rem; margin-bottom: 12px; }}
        .receipt-table th {{ text-align: left; border-bottom: 1px solid #a8a29e; padding-bottom: 4px; }}
        .receipt-table td {{ padding: 6px 0; vertical-align: top; }}
        .receipt-table .num {{ text-align: right; }}

        .receipt-divider {{ border-top: 1px dashed #78716c; margin: 8px 0; }}
        .receipt-total {{ display: flex; justify-content: space-between; font-weight: bold; font-size: 1rem; margin-top: 8px; }}

        .receipt-payment {{
            display: flex;
            justify-content: space-between;
            font-weight: bold;
            font-size: 0.85rem;
            color: #854d0e;
            margin-top: 6px;
            padding-top: 6px;
            border-top: 1px dashed #a8a29e;
        }}

        /* VISUAL SHOPPING LIST TILES GRID WINDOW */
        .shopping-grid-card {{
            background-color: #1e293b;
            border: 1px solid var(--panel-border);
            padding: 20px;
            border-radius: 16px;
            color: #fff;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }}

        .shopping-grid-header {{
            text-align: center;
            margin-bottom: 14px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 8px;
        }}

        .shopping-grid-header h3 {{
            margin: 0;
            font-size: 1.2rem;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .shopping-grid-display {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            background-color: rgba(15, 23, 42, 0.6);
            border-radius: 12px;
            padding: 8px;
            min-height: 120px;
        }}

        .grid-tile {{
            position: relative;
            background-color: rgba(30, 41, 59, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            aspect-ratio: 1 / 1;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }}

        .grid-tile img {{
            width: 75%;
            height: 75%;
            object-fit: contain;
        }}

        /* Multiplier Badge TOP LEFT */
        .tile-mult-top-left {{
            position: absolute;
            top: 4px;
            left: 6px;
            font-weight: 900;
            font-size: 0.9rem;
            color: #f59e0b;
            text-shadow: 
                -1px -1px 0 #000,  
                 1px -1px 0 #000,
                -1px  1px 0 #000,
                 1px  1px 0 #000,
                 2px 2px 3px rgba(0,0,0,0.9);
            font-family: Impact, sans-serif;
            letter-spacing: 0.5px;
        }}

        /* Amount/Quantity Badge BOTTOM RIGHT */
        .tile-qty-bottom-right {{
            position: absolute;
            bottom: 3px;
            right: 6px;
            font-weight: 900;
            font-size: 1.15rem;
            color: #ffffff;
            text-shadow: 
                -1.5px -1.5px 0 #000,  
                 1.5px -1.5px 0 #000,
                -1.5px  1.5px 0 #000,
                 1.5px  1.5px 0 #000,
                 2px 2px 3px rgba(0,0,0,0.9);
            font-family: Impact, sans-serif;
            letter-spacing: 0.5px;
        }}

        .shopping-grid-footer {{
            margin-top: 12px;
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: var(--muted);
            border-top: 1px dashed rgba(255, 255, 255, 0.1);
            padding-top: 8px;
        }}

        .btn {{
            background: var(--accent);
            color: #0f172a;
            font-weight: 700;
            padding: 10px 16px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: opacity 0.15s ease;
            text-align: center;
        }}
        .btn:hover {{ opacity: 0.9; }}
        .btn-secondary {{
            background: rgba(255, 255, 255, 0.1);
            color: var(--text);
            border: 1px solid var(--panel-border);
            width: 100%;
            margin-top: 8px;
        }}

        /* Disclaimer Footer Styling */
        .sc-disclaimer-footer {{ margin-top: 40px; color: #666; font-size: 0.8rem; text-align: center; line-height: 1.4; }}
        .sc-disclaimer-footer a {{ color: #3498db; text-decoration: none; }}
        .sc-disclaimer-footer a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <main class="wrap">
        <header>
            <h1>Hay Day Order Ticket & Shopping Grid</h1>
            <p class="subtitle">Select items, adjust quantities, and export both the text ticket and visual tiles window.</p>
        </header>

        <div class="layout-grid">
            <section class="card">
                <!-- Header Input -->
                <input type="text" id="title-input" class="filter-input" placeholder="🏷️ Custom Header Title..." oninput="updateReceiptTitle(this.value)">

                <!-- Item Picker -->
                <input type="text" id="item-search" class="filter-input" placeholder="🔍 Search items by name or category..." oninput="renderAssetGrid()">
                <div class="asset-grid" id="asset-picker-grid"></div>
                <div class="row-list" id="basket-rows"></div>

                <!-- Payment Selection Grid -->
                <div class="payment-section">
                    <div class="payment-header">
                        <h3>💳 Pay With Item</h3>
                        <span id="payment-selected-info" class="payment-selected-info">Selected: None</span>
                    </div>
                    <input type="text" id="payment-search" class="filter-input" placeholder="🔍 Search payment items..." oninput="renderPaymentGrid()">
                    <div class="asset-grid" id="payment-picker-grid"></div>
                </div>
            </section>

            <section class="output-column">
                <!-- OUTPUT 1: ORDER TICKET RECEIPT -->
                <div>
                    <div class="receipt-card" id="ticket-canvas-node">
                        <div class="receipt-header">
                            <h2 id="receipt-title-display">ORDER TICKET</h2>
                            <p id="receipt-date">Order Ticket</p>
                        </div>

                        <table class="receipt-table">
                            <thead>
                                <tr>
                                    <th>Item</th>
                                    <th class="num">Qty</th>
                                    <th class="num">Base</th>
                                    <th class="num">Mult</th>
                                    <th class="num">Total</th>
                                </tr>
                            </thead>
                            <tbody id="receipt-body">
                                <tr>
                                    <td colspan="5" style="text-align: center; color: #78716c; padding: 12px 0;">
                                        No items added yet.
                                    </td>
                                </tr>
                            </tbody>
                        </table>

                        <div class="receipt-divider"></div>
                        <div class="receipt-total">
                            <span>TOTAL:</span>
                            <span id="receipt-grand-total">0 Coins</span>
                        </div>

                        <!-- Payment Display -->
                        <div class="receipt-payment" id="receipt-payment-row" style="display: none;">
                            <span>PAYMENT:</span>
                            <span id="receipt-payment-text">0x Item</span>
                        </div>
                    </div>

                    <button class="btn btn-secondary" onclick="exportTicketCanvas()">Export Ticket Image</button>
                </div>

                <!-- OUTPUT 2: VISUAL TILES GRID WINDOW -->
                <div>
                    <div class="shopping-grid-card" id="shopping-canvas-node">
                        <div class="shopping-grid-header">
                            <h3 id="grid-title-display"></h3>
                        </div>

                        <!-- Visual Grid Display Container -->
                        <div class="shopping-grid-display" id="visual-grid-tiles"></div>

                        <div class="shopping-grid-footer">
                            <span id="grid-display-payment">Payment: None</span>
                            <span id="grid-display-total-items">(0 items total)</span>
                        </div>
                    </div>

                    <button class="btn btn-secondary" onclick="exportShoppingCanvas()">Export Visual Grid Image</button>
                </div>
            </section>
        </div>

        {DISCLAIMER_FOOTER.format(path_prefix="")}
    </main>

    <script>
        const EMBEDDED_ITEMS = __ITEMS_JSON__;
        let activeBasket = [];
        let selectedPaymentItemId = null;

        function init() {{
            document.getElementById("receipt-date").innerText = `Order Date: ${{new Date().toLocaleDateString()}}`;

            const savedTitle = localStorage.getItem("receiptTitle") || "";
            document.getElementById("title-input").value = savedTitle;

            const defaultItem = EMBEDDED_ITEMS.find(i => i.name.toLowerCase() === "diamond ring");
            if (defaultItem) {{
                selectedPaymentItemId = defaultItem.id;
                document.getElementById("payment-selected-info").innerText = `Selected: ${{defaultItem.name}} (Base: ${{defaultItem.max_base_price}})`;
            }}

            renderAssetGrid();
            renderPaymentGrid();
            updateTitleDisplay();
            updateAllCalculations();
        }}

        function updateReceiptTitle(val) {{
            localStorage.setItem("receiptTitle", val);
            updateTitleDisplay();
        }}

        function updateTitleDisplay() {{
            const rawTitle = document.getElementById("title-input").value.trim();
            const ticketTitleDisplay = document.getElementById("receipt-title-display");
            const gridTitleDisplay = document.getElementById("grid-title-display");

            const finalTitle = rawTitle !== "" ? rawTitle : "ORDER TICKET";

            ticketTitleDisplay.innerText = finalTitle;
            gridTitleDisplay.innerText = rawTitle !== "" ? `${{rawTitle}}` : "SHOPPING LIST";
        }}

        function renderAssetGrid() {{
            const query = document.getElementById("item-search").value.toLowerCase().trim();
            const grid = document.getElementById("asset-picker-grid");

            const filtered = EMBEDDED_ITEMS.filter(item => 
                item.name.toLowerCase().includes(query) || 
                item.category.toLowerCase().includes(query)
            );

            grid.innerHTML = filtered.map(item => `
                <div class="asset-card" onclick="addItemToBasket('${{item.id}}')">
                    <img src="${{item.image}}" alt="${{item.name}}" crossorigin="anonymous" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'40\\' height=\\'40\\'/>'">
                    <span>${{item.name}}</span>
                </div>
            `).join("");
        }}

        function renderPaymentGrid() {{
            const query = document.getElementById("payment-search").value.toLowerCase().trim();
            const grid = document.getElementById("payment-picker-grid");

            const filtered = EMBEDDED_ITEMS.filter(item => 
                item.name.toLowerCase().includes(query) || 
                item.category.toLowerCase().includes(query)
            );

            grid.innerHTML = filtered.map(item => {{
                const isActive = item.id === selectedPaymentItemId ? "active" : "";
                return `
                    <div class="asset-card ${{isActive}}" onclick="selectPaymentItem('${{item.id}}')">
                        <img src="${{item.image}}" alt="${{item.name}}" crossorigin="anonymous" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'40\\' height=\\'40\\'/>'">
                        <span>${{item.name}}</span>
                    </div>
                `;
            }}).join("");
        }}

        function selectPaymentItem(itemId) {{
            if (selectedPaymentItemId === itemId) {{
                const defaultItem = EMBEDDED_ITEMS.find(i => i.name.toLowerCase() === "diamond ring");
                if (defaultItem) {{
                    selectedPaymentItemId = defaultItem.id;
                    document.getElementById("payment-selected-info").innerText = `Selected: ${{defaultItem.name}} (Base: ${{defaultItem.max_base_price}})`;
                }} else {{
                    selectedPaymentItemId = null;
                    document.getElementById("payment-selected-info").innerText = "Selected: None";
                }}
            }} else {{
                selectedPaymentItemId = itemId;
                const item = EMBEDDED_ITEMS.find(i => i.id === itemId);
                if (item) {{
                    document.getElementById("payment-selected-info").innerText = `Selected: ${{item.name}} (Base: ${{item.max_base_price}})`;
                }}
            }}
            renderPaymentGrid();
            updateAllCalculations();
        }}

        function addItemToBasket(itemId) {{
            const existing = activeBasket.find(i => i.id === itemId);
            if (existing) {{
                existing.qty += 1;
            }} else {{
                const rawItem = EMBEDDED_ITEMS.find(i => i.id === itemId);
                if (!rawItem) return;
                activeBasket.push({{
                    id: rawItem.id,
                    name: rawItem.name,
                    image: rawItem.image,
                    maxBasePrice: rawItem.max_base_price,
                    overridePrice: Math.min(rawItem.default_price, rawItem.max_base_price),
                    maxMultiplier: rawItem.max_multiplier,
                    multiplier: rawItem.default_mult,
                    qty: 1
                }});
            }}
            renderBasketRows();
            updateAllCalculations();
        }}

        function renderBasketRows() {{
            const container = document.getElementById("basket-rows");
            container.innerHTML = "";

            activeBasket.forEach((item, index) => {{
                const row = document.createElement("div");
                row.className = "calc-row";
                row.innerHTML = `
                    <img class="item-icon" src="${{item.image}}" crossorigin="anonymous">
                    <div class="item-info">
                        <span class="item-title">${{item.name}}</span>
                        <span class="item-sub">Max Base: ${{item.maxBasePrice}} | Max Mult: ${{item.maxMultiplier}}x</span>
                    </div>
                    <div class="input-inline">
                        <label>Base Price</label>
                        <input type="number" step="1" max="${{item.maxBasePrice}}" value="${{item.overridePrice}}" oninput="updateItemBasePrice(${{index}}, this)">
                    </div>
                    <div class="input-inline">
                        <label>Multiplier</label>
                        <input type="number" step="0.1" min="0" max="${{item.maxMultiplier}}" value="${{item.multiplier}}" oninput="updateItemMultiplier(${{index}}, this)">
                    </div>
                    <div class="input-inline">
                        <label>Qty</label>
                        <input type="number" min="1" value="${{item.qty}}" oninput="updateItemQty(${{index}}, this.value)">
                    </div>
                    <div class="input-inline">
                        <label style="visibility:hidden;">Max</label>
                        <button class="btn-inline-max" onclick="maxOutItem(${{index}})">MAX</button>
                    </div>
                    <div class="input-inline">
                        <label style="visibility:hidden;">Del</label>
                        <button class="btn-remove" onclick="removeBasketItem(${{index}})">✕</button>
                    </div>
                `;
                container.appendChild(row);
            }});
        }}

        function maxOutItem(index) {{
            const item = activeBasket[index];
            item.overridePrice = item.maxBasePrice;
            item.multiplier = item.maxMultiplier;
            renderBasketRows();
            updateAllCalculations();
        }}

        function updateItemBasePrice(index, inputEl) {{
            const item = activeBasket[index];
            let val = parseFloat(inputEl.value) || 0;
            if (val > item.maxBasePrice) {{
                val = item.maxBasePrice;
                inputEl.value = val;
            }}
            item.overridePrice = val;
            updateAllCalculations();
        }}

        function updateItemMultiplier(index, inputEl) {{
            const item = activeBasket[index];
            let val = parseFloat(inputEl.value) || 0;
            if (val > item.maxMultiplier) {{
                val = item.maxMultiplier;
                inputEl.value = val;
            }}
            item.multiplier = val;
            updateAllCalculations();
        }}

        function updateItemQty(index, val) {{
            activeBasket[index].qty = parseInt(val) || 0;
            updateAllCalculations();
        }}

        function removeBasketItem(index) {{
            activeBasket.splice(index, 1);
            renderBasketRows();
            updateAllCalculations();
        }}

        function updateAllCalculations() {{
            const receiptBody = document.getElementById("receipt-body");
            const visualGridTiles = document.getElementById("visual-grid-tiles");

            let grandTotal = 0;
            let totalItemsCount = 0;

            if (activeBasket.length === 0) {{
                receiptBody.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align: center; color: #78716c; padding: 12px 0;">
                            No items added yet.
                        </td>
                    </tr>
                `;
                visualGridTiles.innerHTML = "";
            }} else {{
                receiptBody.innerHTML = activeBasket.map(item => {{
                    const unitPrice = item.overridePrice * item.multiplier;
                    const lineTotal = unitPrice * item.qty;
                    grandTotal += lineTotal;

                    return `
                        <tr>
                            <td>${{item.name}}</td>
                            <td class="num">${{item.qty}}</td>
                            <td class="num">${{Math.round(item.overridePrice).toLocaleString()}}</td>
                            <td class="num">${{item.multiplier}}x</td>
                            <td class="num">${{Math.round(lineTotal).toLocaleString()}}</td>
                        </tr>
                    `;
                }}).join("");

                visualGridTiles.innerHTML = activeBasket.map(item => {{
                    totalItemsCount += item.qty;
                    return `
                        <div class="grid-tile">
                            <span class="tile-mult-top-left">${{item.multiplier}}x</span>
                            <img src="${{item.image}}" alt="${{item.name}}" crossorigin="anonymous">
                            <span class="tile-qty-bottom-right">${{item.qty}}</span>
                        </div>
                    `;
                }}).join("");
            }}

            const roundedGrandTotal = Math.round(grandTotal);
            document.getElementById("receipt-grand-total").textContent = `${{roundedGrandTotal.toLocaleString()}} Coins`;

            const paymentRow = document.getElementById("receipt-payment-row");
            const paymentText = document.getElementById("receipt-payment-text");
            const gridPaymentText = document.getElementById("grid-display-payment");

            let paymentDisplayString = "Payment: None";

            if (selectedPaymentItemId && roundedGrandTotal > 0) {{
                const paymentItem = EMBEDDED_ITEMS.find(i => i.id === selectedPaymentItemId);
                if (paymentItem && paymentItem.max_base_price > 0) {{
                    const basePrice = paymentItem.max_base_price;
                    const count = Math.floor(roundedGrandTotal / basePrice);
                    const remainder = roundedGrandTotal % basePrice;

                    paymentDisplayString = `${{count.toLocaleString()}}x ${{paymentItem.name}}`;
                    if (remainder > 0) {{
                        paymentDisplayString += ` + ${{remainder.toLocaleString()}} coins`;
                    }}

                    paymentText.textContent = paymentDisplayString;
                    paymentRow.style.display = "flex";
                }} else {{
                    paymentRow.style.display = "none";
                }}
            }} else {{
                paymentRow.style.display = "none";
            }}

            gridPaymentText.textContent = `Payment: ${{paymentDisplayString}}`;
            document.getElementById("grid-display-total-items").textContent = `(${{totalItemsCount.toLocaleString()}} items total)`;
        }}

        /* Export Ticket Image with CORS settings enabled */
        async function exportTicketCanvas() {{
            const node = document.getElementById("ticket-canvas-node");
            const canvas = await html2canvas(node, {{ scale: 2, useCORS: true, allowTaint: true }});
            canvas.toBlob(async (blob) => {{
                const item = new ClipboardItem({{ "image/png": blob }});
                await navigator.clipboard.write([item]);
                alert("Order Ticket image copied to clipboard!");
            }});
        }}

        /* Export Visual Tiles Window Image without white corner artifacts */
        async function exportShoppingCanvas() {{
            const node = document.getElementById("shopping-canvas-node");
            const canvas = await html2canvas(node, {{ 
                scale: 2, 
                useCORS: true, 
                allowTaint: true,
                backgroundColor: null // Ensures rounded outer corners export as transparent instead of white background
            }});
            canvas.toBlob(async (blob) => {{
                const item = new ClipboardItem({{ "image/png": blob }});
                await navigator.clipboard.write([item]);
                alert("Shopping Grid image copied to clipboard!");
            }});
        }}

        window.onload = init;
    </script>
</body>
</html>
"""

def main():
    items = fetch_all_items()
    items_json = json.dumps(items)

    final_html = HTML_TEMPLATE.replace("__ITEMS_JSON__", items_json)

    output_dir = "docs"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "ticket.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_html)

    print(f"\nSuccessfully generated static single-page web app at: {output_path}")

if __name__ == "__main__":
    main()