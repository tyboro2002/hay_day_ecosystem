import io
from PIL import Image
import os
import base64
from pyvis.network import Network
from game_data import ITEMS, INFRASTRUCTURE, LIVESTOCK
# get new assets from
# https://fankit.supercell.com/d/QSVyhmM7gdGe/game-assets
# if not found there look at
# https://hayday.fandom.com/wiki

outp = "docs"
outp_file = "index.html"
detail_dir = "details"

NODE_SIZE = 80
MACHINE_SIZE = 160
PEN_SIZE = NODE_SIZE
PLANT_STRUCTURE_SIZE = NODE_SIZE
SPECIAL_STRUCTURE_SIZE = NODE_SIZE
FIELD_SIZE = NODE_SIZE
ANIMAL_SIZE = NODE_SIZE
ITEM_SIZE = NODE_SIZE

non_found = 0

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

def image_to_base64(image_path):
    """Converts a local image file to a base64 string for embedding."""
    if not os.path.exists(image_path):
        global non_found
        non_found += 1
        # Fallback to a default if the specific asset isn't found
        print(f"Did not find {image_path}")
        image_path = os.path.join("assets", "default_icon.png")

    try:
        with Image.open(image_path) as img:
            # Force all images to a standard size for consistency
            img = img.convert("RGBA")
            img.thumbnail((128, 128), Image.Resampling.LANCZOS)

            # Save to buffer
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")

            encoded = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return f"data:image/png;base64,{encoded}"
    except Exception as e:
        print(f"Error encoding {image_path}: {e}")
        return None

def get_base64_asset(name, subfolder):
    """Helper to get base64 string based on name and subfolder."""
    filename = f"{name.lower().replace(' ', '_')}.png"
    filepath = os.path.join("assets", subfolder, filename)
    return image_to_base64(filepath)

def generate_interactive_farm_graph(output_filename=f"{outp}/{outp_file}"):
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    net.barnes_hut()

    # =====================================================================
    # 1. GENERATE ALL INFRASTRUCTURE NODES
    # =====================================================================
    for name in INFRASTRUCTURE["machines"].keys():
        detail_url = f"{detail_dir}/details_{name.lower().replace(' ', '_')}.html"
        net.add_node(name, label=name, shape="image", image=get_base64_asset(name, "machines"), size=MACHINE_SIZE, url=detail_url)
        # Find all items produced by this machine
        prods = [item for item in ITEMS.values() if getattr(item, 'machine', None) and item.machine.name == name]
        generate_detail_page_non_item(name, "machines", prods)

    for name in INFRASTRUCTURE["pens"].keys():
        detail_url = f"{detail_dir}/details_{name.lower().replace(' ', '_')}.html"
        net.add_node(name, label=name, shape="image", image=get_base64_asset(name, "pens"), size=PEN_SIZE, url=detail_url)
        residents = [anim for anim_name, anim in LIVESTOCK.items() if anim.pen and anim.pen.name == name]
        extra_info = {"Residents": ", ".join([r.name for r in residents])} if residents else None
        generate_detail_page_non_item(name, "pens", [], extra_info)

    for name in INFRASTRUCTURE["plant_structures"].keys():
        detail_url = f"{detail_dir}/details_{name.lower().replace(' ', '_')}.html"
        net.add_node(name, label=name, shape="image", image=get_base64_asset(name, "plant_structures"), size=PLANT_STRUCTURE_SIZE, url=detail_url)
        # Items matching this plant type
        prods = []
        for item_name, item in ITEMS.items():
            if type(item).__name__ == "PlantableItem":
                first_word_item = item_name.lower().split()[0]
                if item_name.lower() in name.lower() or first_word_item in name.lower():
                    prods.append(item)
        generate_detail_page_non_item(name, "plant_structures", prods)

    for name in INFRASTRUCTURE["special_structures"].keys():
        detail_url = f"{detail_dir}/details_{name.lower().replace(' ', '_')}.html"
        net.add_node(name, label=name, shape="image", image=get_base64_asset(name, "special_structures"), size=SPECIAL_STRUCTURE_SIZE, url=detail_url)
        prods = []
        if name == "Mine":
            prods = [item for item_name, item in ITEMS.items() if item_name in ["Silver Ore", "Gold Ore", "Platinum Ore", "Iron Ore", "Coal"]]
        elif name == "Fishing Lake":
            prods = [item for item_name, item in ITEMS.items() if item_name == "Fish Fillet"]
        generate_detail_page_non_item(name, "special_structures", prods)

    for obj in INFRASTRUCTURE["fields"].keys():
        detail_url = f"{detail_dir}/details_{obj.lower().replace(' ', '_')}.html"
        net.add_node(obj, label=obj, shape="image", image=get_base64_asset(obj, "fields"), size=FIELD_SIZE, url=detail_url)
        prods = [item for item in ITEMS.values() if hasattr(item, 'planted_on') and item.planted_on and list(item.planted_on.keys())[0] == obj]
        generate_detail_page_non_item(obj, "fields", prods)

    # =====================================================================
    # 2. GENERATE LIVESTOCK (ANIMALS) NODES
    # =====================================================================
    for name, animal_obj in LIVESTOCK.items():
        detail_url = f"{detail_dir}/details_{name.lower().replace(' ', '_')}.html"
        net.add_node(name, label=name, shape="image", image=get_base64_asset(name, "animals"), size=ANIMAL_SIZE, url=detail_url)

        extra_info = {}
        if animal_obj.pen:
            extra_info["Lives In"] = f'<a href="details_{animal_obj.pen.name.lower().replace(" ", "_")}.html" style="color:#f1a80a; font-weight:bold;">{animal_obj.pen.name}</a>'
        if animal_obj.required_food:
            extra_info["Eats"] = f'<a href="details_{animal_obj.required_food.name.lower().replace(" ", "_")}.html" style="color:#f1a80a; font-weight:bold;">{animal_obj.required_food.name}</a>'

        prods = [animal_obj.produces_item] if animal_obj.produces_item else []
        generate_detail_page_non_item(name, "animals", prods, extra_info)

    # =====================================================================
    # 3. GENERATE ALL ITEM NODES & INGREDIENT LINKS
    # =====================================================================
    for name, item_obj in ITEMS.items():
        # Prepare URL path
        detail_filename = f"details_{name.lower().replace(' ', '_')}.html"
        # The URL needs to point to the subfolder where you save the file
        detail_url = f"{detail_dir}/{detail_filename}"

        class_type = type(item_obj).__name__

        price_lbl = f"\n({item_obj.sell_price}c)" if hasattr(item_obj, 'sell_price') else ""
        net.add_node(
            name,
            label=f"{name}{price_lbl}",
            shape="image",
            image=get_base64_asset(name, "items"),
            size=ITEM_SIZE,
            url=detail_url
        )

        # Generate the detail page
        generate_detail_page_item(name, item_obj, detail_filename)

        # --- INFRASTRUCTURE ORIGIN RESOLVER ---
        if hasattr(item_obj, 'machine') and item_obj.machine:
            net.add_edge(item_obj.machine.name, name, color="dimgray", label="made in")
        # elif hasattr(item_obj, 'pen') and item_obj.pen:
        #     net.add_edge(item_obj.pen.name, name, color="dimgray", label="made in")
        elif hasattr(item_obj, 'planted_on') and item_obj.planted_on:
            net.add_edge(list(item_obj.planted_on.keys())[0], name, color="dimgray", label="planted on")
        elif class_type == "PlantableItem":
            for struct_name in INFRASTRUCTURE["plant_structures"].keys():
                first_word_item = name.lower().split()[0]
                if name.lower() in struct_name.lower() or first_word_item in struct_name.lower():
                    net.add_edge(struct_name, name, color="forestgreen", label="grows on")
                    break
        elif name in ["Silver Ore", "Gold Ore", "Platinum Ore", "Iron Ore", "Coal"]:
            net.add_edge("Mine", name, color="dimgray", label="excavated in")
        elif name == "Fish Fillet":
            net.add_edge("Fishing Lake", name, color="dimgray", label="fished in")

    # now all items are created create the links
    for name, item_obj in ITEMS.items():
        # --- RECIPE INGREDIENT LINKS ---
        if hasattr(item_obj, 'ingredients') and item_obj.ingredients:
            for ingredient_obj, quantity in item_obj.ingredients.items():
                thickness = str(max(1.0, float(quantity)))

                net.add_edge(
                    ingredient_obj.name,
                    name,
                    label=f" x{quantity:.2f}" if isinstance(quantity, float) else f" x{quantity}",
                    color="brown",
                    penwidth=thickness,
                    fontname="Helvetica-Oblique",
                )

    for name, animal_obj in LIVESTOCK.items():
        if animal_obj.pen:
            net.add_edge(animal_obj.pen.name, name, color="#898989", dashes=True, label="lives in")

        if animal_obj.produces_item:
            net.add_edge(name, animal_obj.produces_item.name, color="royalblue", penwidth="2.5", label=" yields")

        if animal_obj.required_food:
            net.add_edge(animal_obj.required_food.name, name, color="crimson", style="dotted", penwidth="1.5", label=" eats")


    # Ensure net.html is generated first
    net.html = net.generate_html()

    # CSS reset block to strip default layout margins and block any accidental scrolling behavior
    layout_style_reset = """
        <style type="text/css">
            html, body {
                margin: 0 !important;
                padding: 0 !important;
                width: 100vw !important;
                height: 100vh !important;
                overflow: hidden !important;
            }
            /* Floating disclaimer footer - forced to screen viewport overlay */
            .sc-disclaimer-footer {
                position: fixed !important;
                bottom: 20px !important;
                left: 50% !important;
                transform: translateX(-50%) !important;
                z-index: 999999 !important; /* Forces it above PyVis canvas container */
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
                pointer-events: auto !important; /* Ensures the hyperlink is clickable */
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

    # Define the custom JavaScript for Ctrl+Click
    # 'ctrlKey' is a built-in property of the browser's mouse event
    nav_and_footer = """
        <div class="sc-disclaimer-footer">
            This material is unofficial and is not endorsed by Supercell. For more information see <a href="https://www.supercell.com/fan-content-policy" target="_blank">Supercell's Fan Content Policy</a>.
        </div>
        <script type="text/javascript">
            // Wait until the entire window (including drawGraph) is loaded
            window.addEventListener('load', function() {
                if (typeof network !== 'undefined') {
                    network.on("click", function (params) {
                        // Extract the original browser pointer event from Vis.js
                        var originalEvent = params.event ? (params.event.srcEvent || params.event) : null;

                        // Support both Ctrl (Windows/Linux) and Cmd (macOS) keys
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

    # Inject the layout reset rules directly into the page header
    net.html = net.html.replace("</head>", layout_style_reset + "</head>")
    # Append navigation actions right before the end of the body tag
    net.html = net.html.replace("</body>", nav_and_footer + "</body>")

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(net.html)
    print(f"Graph generated at {output_filename}")
    if non_found:
        if non_found == 1:
            print(f"{non_found} asset was not found")
        else:
            print(f"{non_found} assets were not found")


def generate_detail_page_item(name, item_obj, filename):
    """Generates a styled HTML file featuring interactive graphic recipes, cross-usages, and profit analysis."""
    # Pull the base64-encoded main item asset
    item_img_base64 = get_base64_asset(name, "items")
    img_tag = f'<img class="item-image" src="{item_img_base64}" alt="{name}">' if item_img_base64 else ""

    # Setup the price badge (normalize None to 'N/A')
    sell_price = getattr(item_obj, 'sell_price', 'N/A')
    if sell_price is None:
        sell_price = 'N/A'

    price_display = f"{sell_price} Coins" if sell_price != 'N/A' else "Unsellable"

    # --- RESOLVE PRODUCER/SOURCE ---
    producer_name = None
    producer_folder = None
    class_type = type(item_obj).__name__

    # 1. Check if produced by a machine
    if hasattr(item_obj, 'machine') and item_obj.machine:
        producer_name = item_obj.machine.name
        producer_folder = "machines"
    else:
        # 2. Reverse-lookup if this item is produced by an animal (livestock)
        for animal_name, animal_obj in LIVESTOCK.items():
            if hasattr(animal_obj, 'produces_item') and animal_obj.produces_item:
                if animal_obj.produces_item.name.lower().strip() == name.lower().strip():
                    producer_name = animal_name
                    producer_folder = "animals"
                    break

    # 3. If still not found, check fields, plantable structures, or special structures
    if not producer_name:
        if hasattr(item_obj, 'planted_on') and item_obj.planted_on:
            # Check if it's a Field instance or just a key
            field_obj = item_obj.planted_on
            producer_name = field_obj.name if hasattr(field_obj, 'name') else "Fields"
            producer_folder = "fields"
        elif class_type == "PlantableItem" and hasattr(item_obj, 'structure') and item_obj.structure:
            producer_name = item_obj.structure.name
            producer_folder = "plant_structures"
        elif name in ["Silver Ore", "Gold Ore", "Platinum Ore", "Iron Ore", "Coal"]:
            producer_name = "Mine"
            producer_folder = "special_structures"
        elif name == "Fish Fillet":
            producer_name = "Fishing Lake"
            producer_folder = "special_structures"

    # Build the Producer HTML block if a source was resolved
    producer_html = ""
    if producer_name and producer_folder:
        producer_img = get_base64_asset(producer_name, producer_folder)
        # Target path format for producer links
        producer_url = f"details_{producer_name.lower().replace(' ', '_')}.html"
        producer_html = f"""
        <div class="producer-section">
            <div class="producer-label">Source / Producer</div>
            <a class="producer-badge" href="{producer_url}" style="text-decoration: none; transition: transform 0.2s ease;">
                <img src="{producer_img}" alt="{producer_name}">
                <span>{producer_name}</span>
            </a>
        </div>
        """

    # --- FIXED: ACCURATE TIME EXTRACTION FROM MODEL ---
    # We pull directly from self.time_to_make defined in your HayDayItem model!
    raw_duration = getattr(item_obj, 'time_to_make', None)

    time_display_html = ""
    if raw_duration:
        formatted_time = format_duration(raw_duration)
        if formatted_time:
            # Removed left margin here to let the flex gap handle spacing cleanly
            time_display_html = f'<div class="price" style="background:#1e1e1e; border-color:#3498db; color:#3498db; margin-bottom: 0;">⏱️ {formatted_time}</div>'

    # --- COMBINE DIRECT INGREDIENTS & ANIMAL FEED ---
    ingredients_dict = {}

    # 1. Grab base recipes ingredients (if any)
    if hasattr(item_obj, 'ingredients') and item_obj.ingredients:
        for ing_item, qty in item_obj.ingredients.items():
            ingredients_dict[ing_item] = qty

    # 2. Fetch associated feed (using the animal lookup logic)
    associated_feed = None
    for animal_name, animal_obj in LIVESTOCK.items():
        if hasattr(animal_obj, 'produces_item') and animal_obj.produces_item:
            if animal_obj.produces_item.name.lower().strip() == name.lower().strip():
                if hasattr(animal_obj, 'required_food') and animal_obj.required_food:
                    associated_feed = animal_obj.required_food
                    ingredients_dict[associated_feed] = 1
                    break

    # --- 1. GENERATE VISUAL INGREDIENTS GRID (Inputs) ---
    ingredients_html = ""
    total_ingredient_cost = 0
    has_ingredients = len(ingredients_dict) > 0
    unsellable_ingredients = False

    if has_ingredients:
        for ing_item, qty in ingredients_dict.items():
            ing_name = ing_item.name
            ing_img = get_base64_asset(ing_name, "items")
            ing_url = f"details_{ing_name.lower().replace(' ', '_')}.html"
            qty_str = f"x{qty:.1f}" if isinstance(qty, float) else f"x{qty}"

            # Calculate Ingredient costs safely (normalize None to 'N/A')
            ing_price = getattr(ing_item, 'sell_price', 'N/A')
            if ing_price is None:
                ing_price = 'N/A'

            if ing_price == 'N/A':
                unsellable_ingredients = True
            else:
                total_ingredient_cost += ing_price * qty

            # Highlight feed badge with a green tone
            is_feed = associated_feed and ing_name == associated_feed.name
            badge_style = 'style="background-color: #2ecc71; color: #ffffff;"' if is_feed else ""

            ingredients_html += f"""
            <a class="grid-item" href="{ing_url}">
                <div class="qty-badge" {badge_style}>{qty_str}</div>
                <img src="{ing_img}" alt="{ing_name}">
                <div class="name">{ing_name}</div>
            </a>
            """
    else:
        ingredients_html = '<div class="no-items">🌾 Raw Material (Requires no ingredients)</div>'

    # --- 2. CALCULATE PROFIT AND LOSS MARGINS ---
    profit_html = ""
    if sell_price == 'N/A':
        profit_html = """
        <div class="financial-summary">
            <div class="fin-col profit-neutral" style="width: 100%;">
                <span class="fin-label">Production Status</span>
                <span class="fin-val">⚠️ Unsellable Item (Cannot calculate financial margin)</span>
            </div>
        </div>
        """
    elif not has_ingredients:
        profit_html = f"""
        <div class="financial-summary">
            <div class="fin-col profit-positive" style="width: 100%;">
                <span class="fin-label">Production Status</span>
                <span class="fin-val">🌱 Pure Profit (+{sell_price} Coins / 100%)</span>
            </div>
        </div>
        """
    elif unsellable_ingredients:
        profit_html = """
        <div class="financial-summary">
            <div class="fin-col profit-neutral" style="width: 100%;">
                <span class="fin-label">Production Status</span>
                <span class="fin-val">⚠️ Contains Unsellable Ingredients</span>
            </div>
        </div>
        """
    else:
        net_profit = sell_price - total_ingredient_cost

        if total_ingredient_cost > 0:
            percentage_yield = (net_profit / total_ingredient_cost) * 100
            pct_str = f"{percentage_yield:+.1f}%"
        else:
            pct_str = "+100.0%"

        if net_profit > 0:
            status_class = "profit-positive"
            status_icon = "📈"
            status_label = "Net Profit"
            val_prefix = "+"
        elif net_profit < 0:
            status_class = "profit-negative"
            status_icon = "📉"
            status_label = "Net Loss"
            val_prefix = ""
        else:
            status_class = "profit-neutral"
            status_icon = "⚖️"
            status_label = "Break-even"
            val_prefix = "±"

        profit_html = f"""
        <div class="financial-summary">
            <div class="fin-col">
                <span class="fin-label">Cost of Materials</span>
                <span class="fin-val">💰 {total_ingredient_cost:.0f}</span>
            </div>
            <div class="fin-col {status_class}">
                <span class="fin-label">{status_label}</span>
                <span class="fin-val">{status_icon} {val_prefix}{net_profit:.0f} ({pct_str})</span>
            </div>
        </div>
        """

    # --- 3. GENERATE "USED IN RECIPES" GRID (Outputs/Usages) ---
    used_in_html = ""
    used_in_list = []

    for other_name, other_item in ITEMS.items():
        if hasattr(other_item, 'ingredients') and other_item.ingredients:
            for ing_item, qty in other_item.ingredients.items():
                if ing_item.name.lower().strip() == name.lower().strip():
                    used_in_list.append((other_name, qty))
                    break

    if used_in_list:
        for recipe_name, qty in used_in_list:
            recipe_img = get_base64_asset(recipe_name, "items")
            recipe_url = f"details_{recipe_name.lower().replace(' ', '_')}.html"
            qty_str = f"x{qty:.1f}" if isinstance(qty, float) else f"x{qty}"

            used_in_html += f"""
            <a class="grid-item" href="{recipe_url}">
                <div class="qty-badge">{qty_str}</div>
                <img src="{recipe_img}" alt="{recipe_name}">
                <div class="name">{recipe_name}</div>
            </a>
            """
    else:
        used_in_html = '<div class="no-items">📦 Final Product (Not used in other recipes)</div>'

    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Details</title>
    <style>
        body {{
            background-color: #222222;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            box-sizing: border-box;
        }}
        .card {{
            background-color: #2d2d2d;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            width: 100%;
            max-width: 500px;
            padding: 40px 30px;
            text-align: center;
            border: 1px solid #444444;
        }}
        .item-image {{
            width: 110px;
            height: 110px;
            margin-bottom: 15px;
            object-fit: contain;
            filter: drop-shadow(0px 6px 8px rgba(0,0,0,0.6));
        }}
        h1 {{
            margin: 5px 0 10px 0;
            font-size: 2rem;
            color: #f1a80a;
            font-weight: 700;
            letter-spacing: 0.5px;
        }}
        .price {{
            font-size: 1.1rem;
            color: #b0b0b0;
            margin-bottom: 25px;
            font-weight: 500;
            background: #3a3a3a;
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            border: 1px solid #555555;
        }}

        .producer-section {{
            margin-bottom: 25px;
        }}
        .producer-label {{
            font-size: 0.72rem;
            color: #888888;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 8px;
        }}
        .producer-badge {{
            display: inline-flex;
            align-items: center;
            background-color: #1e1e1e;
            padding: 8px 18px;
            border-radius: 25px;
            border: 1px solid #3a3a3a;
            gap: 12px;
        }}
        .producer-badge img {{
            width: 32px;
            height: 32px;
            object-fit: contain;
            filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.5));
        }}
        .producer-badge span {{
            font-size: 0.9rem;
            font-weight: 700;
            color: #ffffff;
        }}

        .financial-summary {{
            display: flex;
            justify-content: space-between;
            background-color: #1e1e1e;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 30px;
            border: 1px solid #3a3a3a;
            gap: 10px;
        }}
        .fin-col {{
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }}
        .fin-col:not(:last-child) {{
            border-right: 1px solid #333333;
        }}
        .fin-label {{
            font-size: 0.72rem;
            color: #888888;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 5px;
        }}
        .fin-val {{
            font-size: 0.95rem;
            font-weight: 700;
        }}
        .profit-positive .fin-val {{
            color: #2ecc71;
        }}
        .profit-negative .fin-val {{
            color: #e74c3c;
        }}
        .profit-neutral .fin-val {{
            color: #b0b0b0;
        }}

        .section-title {{
            text-align: left;
            font-size: 0.95rem;
            color: #f1a80a;
            border-bottom: 2px solid #444444;
            padding-bottom: 6px;
            margin-top: 25px;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-weight: 600;
        }}

        .grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            justify-content: flex-start;
            margin-bottom: 30px;
        }}
        .grid-item {{
            background-color: #353535;
            border: 1px solid #484848;
            border-radius: 12px;
            width: 90px;
            padding: 15px 5px;
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            text-decoration: none;
            color: inherit;
            transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-sizing: border-box;
        }}
        .grid-item:hover {{
            transform: translateY(-5px) scale(1.03);
            background-color: #404040;
            border-color: #f1a80a;
            box-shadow: 0 5px 15px rgba(241, 168, 10, 0.2);
        }}
        .grid-item img {{
            width: 48px;
            height: 48px;
            object-fit: contain;
            margin-bottom: 8px;
            filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.4));
        }}
        .grid-item .name {{
            font-size: 0.72rem;
            text-align: center;
            font-weight: 600;
            line-height: 1.2;
            word-break: break-word;
            padding: 0 4px;
        }}
        .grid-item .qty-badge {{
            position: absolute;
            top: -8px;
            right: -8px;
            background-color: #f1a80a;
            color: #222222;
            font-size: 0.7rem;
            font-weight: 800;
            padding: 2px 6px;
            border-radius: 8px;
            box-shadow: 0 3px 6px rgba(0,0,0,0.4);
            border: 1.5px solid #2d2d2d;
        }}
        .no-items {{
            color: #888888;
            font-style: italic;
            text-align: center;
            width: 100%;
            padding: 25px 10px;
            background-color: #353535;
            border-radius: 8px;
            border: 1px dashed #484848;
            margin-bottom: 5px;
            box-sizing: border-box;
            font-size: 0.9rem;
        }}

        .back-btn {{
            display: inline-block;
            background-color: #f1a80a;
            color: #222222;
            text-decoration: none;
            padding: 12px 35px;
            border-radius: 30px;
            font-weight: bold;
            transition: all 0.2s ease;
            box-shadow: 0 4px 15px rgba(241, 168, 10, 0.3);
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 15px;
        }}
        .back-btn:hover {{
            background-color: #ffc233;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(241, 168, 10, 0.5);
        }}
        .sc-disclaimer-footer {{
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
        }}
        .sc-disclaimer-footer a {{
            color: #f1a80a !important;
            text-decoration: none !important;
            font-weight: 600 !important;
        }}
        .sc-disclaimer-footer a:hover {{
            text-decoration: underline !important;
        }}
    </style>
</head>
<body>
    <div class="sc-disclaimer-footer">
            This material is unofficial and is not endorsed by Supercell. For more information see <a href="https://www.supercell.com/fan-content-policy" target="_blank">Supercell's Fan Content Policy</a>.
    </div>
    <div class="card">
        {img_tag}
        <h1>{name}</h1>
        <div style="display: flex; justify-content: center; align-items: center; gap: 12px; margin-bottom: 25px;">
            <div class="price" style="margin-bottom: 0;">💰 {price_display}</div>
            {time_display_html}
        </div>

        <div style="margin-top: 25px;">
            {producer_html}
        </div>

        {profit_html}

        <div class="section-title">Ingredients Required</div>
        <div class="grid">
            {ingredients_html}
        </div>

        <div class="section-title">Used in Recipes</div>
        <div class="grid">
            {used_in_html}
        </div>

        <a class="back-btn" href="../{outp_file}">Back to Map</a>
    </div>
</body>
</html>
"""
    os.makedirs(os.path.join(outp, "details"), exist_ok=True)
    with open(os.path.join(outp, "details", filename), "w", encoding="utf-8") as f:
        f.write(content)

def generate_detail_page_non_item(name, category, produces_items, extra_info=None):
    """Generates a detail page for non-item nodes (Machines, Animals, Structures, etc.)"""
    img_base64 = get_base64_asset(name, category)
    img_tag = f'<img class="item-image" src="{img_base64}" alt="{name}">' if img_base64 else ""

    extra_html = ""
    if extra_info:
        extra_html += '<div class="financial-summary" style="flex-direction: column; text-align: left; gap: 8px;">'
        for k, v in extra_info.items():
            extra_html += f'<div><span class="fin-label" style="display:inline; margin-right:5px;">{k}:</span><span class="fin-val" style="font-size:0.9rem; color:#ffffff;">{v}</span></div>'
        extra_html += '</div>'

    produces_html = ""
    if produces_items:
        for prod_item in produces_items:
            prod_img = get_base64_asset(prod_item.name, "items")
            prod_url = f"details_{prod_item.name.lower().replace(' ', '_')}.html"
            time_lbl = ""

            # Grabs direct duration using your exact model attribute `time_to_make`
            raw_time = getattr(prod_item, 'time_to_make', None)
            if raw_time:
                formatted_time = format_duration(raw_time)
                if formatted_time:
                    time_lbl = f'<div class="qty-badge" style="background-color: #3498db; color: white; font-size: 0.6rem;">{formatted_time}</div>'

            produces_html += f"""
            <a class="grid-item" href="{prod_url}">
                {time_lbl}
                <img src="{prod_img}" alt="{prod_item.name}">
                <div class="name">{prod_item.name}</div>
            </a>
            """
    else:
        produces_html = '<div class="no-items">💤 Nothing directly produced here.</div>'

    filename = f"details_{name.lower().replace(' ', '_')}.html"
    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Details</title>
    <style>
        body {{ background-color: #222222; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 40px 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; box-sizing: border-box; }}
        .card {{ background-color: #2d2d2d; border-radius: 16px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); width: 100%; max-width: 500px; padding: 40px 30px; text-align: center; border: 1px solid #444444; }}
        .item-image {{ width: 110px; height: 110px; margin-bottom: 15px; object-fit: contain; filter: drop-shadow(0px 6px 8px rgba(0,0,0,0.6)); }}
        h1 {{ margin: 5px 0 20px 0; font-size: 2rem; color: #f1a80a; font-weight: 700; letter-spacing: 0.5px; }}
        .section-title {{ text-align: left; font-size: 0.95rem; color: #f1a80a; border-bottom: 2px solid #444444; padding-bottom: 6px; margin-top: 25px; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600; }}
        .grid {{ display: flex; flex-wrap: wrap; gap: 15px; justify-content: flex-start; margin-bottom: 30px; }}
        .grid-item {{ background-color: #353535; border: 1px solid #484848; border-radius: 12px; width: 90px; padding: 15px 5px; display: flex; flex-direction: column; align-items: center; position: relative; text-decoration: none; color: inherit; transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275); box-sizing: border-box; }}
        .grid-item:hover {{ transform: translateY(-5px) scale(1.03); background-color: #404040; border-color: #f1a80a; box-shadow: 0 5px 15px rgba(241, 168, 10, 0.2); }}
        .grid-item img {{ width: 48px; height: 48px; object-fit: contain; margin-bottom: 8px; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.4)); }}
        .grid-item .name {{ font-size: 0.72rem; text-align: center; font-weight: 600; line-height: 1.2; word-break: break-word; padding: 0 4px; }}
        .grid-item .qty-badge {{ position: absolute; top: -8px; right: -8px; background-color: #f1a80a; color: #222222; font-size: 0.7rem; font-weight: 800; padding: 2px 6px; border-radius: 8px; box-shadow: 0 3px 6px rgba(0,0,0,0.4); border: 1.5px solid #2d2d2d; }}
        .no-items {{ color: #888888; font-style: italic; text-align: center; width: 100%; padding: 25px 10px; background-color: #353535; border-radius: 8px; border: 1px dashed #484848; margin-bottom: 5px; box-sizing: border-box; font-size: 0.9rem; }}
        .back-btn {{ display: inline-block; background-color: #f1a80a; color: #222222; text-decoration: none; padding: 12px 35px; border-radius: 30px; font-weight: bold; transition: all 0.2s ease; box-shadow: 0 4px 15px rgba(241, 168, 10, 0.3); font-size: 0.95rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 15px; }}
        .back-btn:hover {{ background-color: #ffc233; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(241, 168, 10, 0.5); }}
        .financial-summary {{ display: flex; justify-content: space-between; background-color: #1e1e1e; border-radius: 12px; padding: 15px; margin-bottom: 30px; border: 1px solid #3a3a3a; gap: 10px; }}
        .fin-label {{ font-size: 0.72rem; color: #888888; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 5px; }}
        .fin-val {{ font-size: 0.95rem; font-weight: 700; color: #ffffff; }}
        .sc-disclaimer-footer {{ position: fixed !important; bottom: 20px !important; left: 50% !important; transform: translateX(-50%) !important; z-index: 999999 !important; background-color: rgba(33, 33, 33, 0.95) !important; border: 1px solid #444444 !important; border-radius: 30px !important; padding: 10px 24px !important; color: #b0b0b0 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; font-size: 0.72rem !important; text-align: center !important; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6) !important; max-width: 90% !important; width: max-content !important; pointer-events: auto !important; backdrop-filter: blur(8px) !important; -webkit-backdrop-filter: blur(8px) !important; }}
        .sc-disclaimer-footer a {{ color: #f1a80a !important; text-decoration: none !important; font-weight: 600 !important; }}
        .sc-disclaimer-footer a:hover {{ text-decoration: underline !important; }}
    </style>
</head>
<body>
    <div class="sc-disclaimer-footer">
            This material is unofficial and is not endorsed by Supercell. For more information see <a href="https://www.supercell.com/fan-content-policy" target="_blank">Supercell's Fan Content Policy</a>.
    </div>
    <div class="card">
        {img_tag}
        <h1>{name}</h1>

        {extra_html}

        <div class="section-title">Yields / Produces</div>
        <div class="grid">
            {produces_html}
        </div>

        <a class="back-btn" href="../{outp_file}">Back to Map</a>
    </div>
</body>
</html>
"""
    os.makedirs(os.path.join(outp, "details"), exist_ok=True)
    with open(os.path.join(outp, "details", filename), "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    generate_interactive_farm_graph()