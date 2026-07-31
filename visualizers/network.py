# get new assets from
# https://fankit.supercell.com/d/QSVyhmM7gdGe/game-assets
# if not found there look at
# https://hayday.fandom.com/wiki

import os

from pyvis.network import Network
from game_data import ITEMS, INFRASTRUCTURE, LIVESTOCK
from game_data.game_data import MAX_LEVEL, CURRENT_LEVEL

# Import helpers from the subdirectory package!
from visualizers.helpers.formatting import format_duration, get_base64_asset
import visualizers.helpers.formatting as formatting
import visualizers.helpers.templates as templates
from visualizers.helpers.overnight_profit_page import generate_overnight_page
from visualizers.helpers.profit_ranking_page import generate_profitability_ranking_page

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


def generate_interactive_farm_graph(output_filename=f"{outp}/{outp_file}"):
    net = Network(height="800px", width="100%", bgcolor="#222222", font_color="white", directed=True)
    net.barnes_hut()

    # Helper to resolve item unlock level safely
    def get_unlock_level(obj):
        return getattr(obj, "unlock_level", 1)

    # =====================================================================
    # 1. GENERATE ALL INFRASTRUCTURE NODES
    # =====================================================================
    for name, mach_obj in INFRASTRUCTURE["machines"].items():
        detail_url = f"{detail_dir}/details_{name.lower().replace(' ', '_')}.html"
        lvl = get_unlock_level(mach_obj)
        net.add_node(name, label=name, shape="image", image=get_base64_asset(name, "machines"), size=MACHINE_SIZE, url=detail_url, unlock_level=lvl)
        prods = [item for item in ITEMS.values() if getattr(item, 'machine', None) and item.machine.name == name]
        generate_detail_page_machine(name, prods, mach_obj)

    for name, pen_obj in INFRASTRUCTURE["pens"].items():
        detail_url = f"{detail_dir}/details_{name.lower().replace(' ', '_')}.html"
        lvl = get_unlock_level(pen_obj)
        net.add_node(name, label=name, shape="image", image=get_base64_asset(name, "pens"), size=PEN_SIZE, url=detail_url, unlock_level=lvl)
        residents = [anim for anim_name, anim in LIVESTOCK.items() if anim.pen and anim.pen.name == name]
        generate_detail_page_pen(name, residents, pen_obj)

    for name, plant_obj in INFRASTRUCTURE["plant_structures"].items():
        detail_url = f"{detail_dir}/details_{name.lower().replace(' ', '_')}.html"
        lvl = get_unlock_level(plant_obj)
        net.add_node(name, label=name, shape="image", image=get_base64_asset(name, "plant_structures"), size=PLANT_STRUCTURE_SIZE, url=detail_url, unlock_level=lvl)
        prods = []
        for item_name, item in ITEMS.items():
            if type(item).__name__ == "PlantableItem":
                first_word_item = item_name.lower().split()[0]
                if item_name.lower() in name.lower() or first_word_item in name.lower():
                    prods.append(item)
        generate_detail_page_plantable_structure(name, prods)

    for name, spec_obj in INFRASTRUCTURE["special_structures"].items():
        detail_url = f"{detail_dir}/details_{name.lower().replace(' ', '_')}.html"
        lvl = get_unlock_level(spec_obj)
        net.add_node(name, label=name, shape="image", image=get_base64_asset(name, "special_structures"), size=SPECIAL_STRUCTURE_SIZE, url=detail_url, unlock_level=lvl)
        prods = []
        if name == "Mine":
            prods = [item for item_name, item in ITEMS.items() if item_name in ["Silver Ore", "Gold Ore", "Platinum Ore", "Iron Ore", "Coal"]]
        elif name == "Fishing Lake":
            prods = [item for item_name, item in ITEMS.items() if item_name == "Fish Fillet"]
        generate_detail_page_special_structure(name, prods)

    for obj in INFRASTRUCTURE["fields"].keys():
        detail_url = f"{detail_dir}/details_{obj.lower().replace(' ', '_')}.html"
        net.add_node(obj, label=obj, shape="image", image=get_base64_asset(obj, "fields"), size=FIELD_SIZE, url=detail_url, unlock_level=1)
        prods = [item for item in ITEMS.values() if hasattr(item, 'planted_on') and item.planted_on and list(item.planted_on.keys())[0] == obj]
        generate_detail_page_field(obj, prods, obj)

    # =====================================================================
    # 2. GENERATE LIVESTOCK (ANIMALS) NODES
    # =====================================================================
    for name, animal_obj in LIVESTOCK.items():
        detail_url = f"{detail_dir}/details_{name.lower().replace(' ', '_')}.html"
        lvl = get_unlock_level(animal_obj)
        net.add_node(name, label=name, shape="image", image=get_base64_asset(name, "animals"), size=ANIMAL_SIZE, url=detail_url, unlock_level=lvl)

        extra_info = {}
        if animal_obj.pen:
            extra_info["Lives In"] = f'<a href="details_{animal_obj.pen.name.lower().replace(" ", "_")}.html" style="color:#f1a80a; font-weight:bold;">{animal_obj.pen.name}</a>'
        if animal_obj.required_food:
            extra_info["Eats"] = f'<a href="details_{animal_obj.required_food.name.lower().replace(" ", "_")}.html" style="color:#f1a80a; font-weight:bold;">{animal_obj.required_food.name}</a>'

        generate_detail_page_animal(name, animal_obj)

    # =====================================================================
    # 3. GENERATE ALL ITEM NODES & INGREDIENT LINKS
    # =====================================================================
    for name, item_obj in ITEMS.items():
        detail_filename = f"details_{name.lower().replace(' ', '_')}.html"
        detail_url = f"{detail_dir}/{detail_filename}"

        class_type = type(item_obj).__name__
        price_lbl = f"\n({item_obj.sell_price}🪙)" if hasattr(item_obj, 'sell_price') else ""
        lvl = get_unlock_level(item_obj)

        net.add_node(name, label=f"{name}{price_lbl}", shape="image", image=get_base64_asset(name, "items"), size=ITEM_SIZE, url=detail_url, unlock_level=lvl)

        generate_detail_page_item(name, item_obj, detail_filename)

        if hasattr(item_obj, 'machine') and item_obj.machine:
            net.add_edge(item_obj.machine.name, name, color="dimgray", label="made in")
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

    # Connect ingredients
    for name, item_obj in ITEMS.items():
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

    # Generate html template
    net.html = net.generate_html()

    # Top level filter bar fixed UI component
    top_slider_html = f"""
    <div id="top-fixed-dock" style="
        position: fixed;
        top: 15px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 99999;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        flex-wrap: wrap;
        width: max-content;
        max-width: 95vw;
        pointer-events: none;
    ">
        <div id="graph-level-filter-bar" style="
            pointer-events: auto;
            background-color: rgba(30, 30, 30, 0.95);
            border: 1px solid #e67e22;
            border-radius: 30px;
            padding: 10px 20px;
            display: flex;
            align-items: center;
            gap: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(5px);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        ">
            <label for="graphLevelRange" style="font-weight: bold; color: #e67e22; white-space: nowrap; font-size: 0.9rem;">
                Filter Level:
            </label>
            <input type="range" id="graphLevelRange" min="1" max="{MAX_LEVEL}" value="{CURRENT_LEVEL}" oninput="filterGraphByLevel(this.value)" style="
                width: 150px;
                accent-color: #e67e22;
                cursor: pointer;
            ">
            <span id="graphLevelDisplay" style="
                background-color: #e67e22;
                color: #fff;
                padding: 3px 10px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 0.85rem;
                min-width: 55px;
                text-align: center;
            ">Lvl {CURRENT_LEVEL}</span>
            <span id="graphNodeCount" style="
                font-size: 0.8rem;
                color: #aaa;
                background-color: #111;
                padding: 3px 8px;
                border-radius: 4px;
                border: 1px solid #333;
                white-space: nowrap;
            ">Visible Nodes: -</span>
        </div>
    </div>

    <script>
        function filterGraphByLevel(selectedLevel) {{
            selectedLevel = parseInt(selectedLevel);
            document.getElementById("graphLevelDisplay").innerText = "Lvl " + selectedLevel;

            if (typeof network === "undefined" || typeof nodes === "undefined") return;

            let allNodes = nodes.get();
            let allEdges = edges.get();

            let hiddenNodeIds = new Set();
            let updateNodes = [];
            let visibleCount = 0;

            allNodes.forEach(node => {{
                let nodeLvl = parseInt(node.unlock_level) || 1;
                let shouldHide = nodeLvl > selectedLevel;

                if (shouldHide) {{
                    hiddenNodeIds.add(node.id);
                }} else {{
                    visibleCount++;
                }}

                updateNodes.push({{
                    id: node.id,
                    hidden: shouldHide
                }});
            }});

            let updateEdges = allEdges.map(edge => ({{
                id: edge.id,
                hidden: hiddenNodeIds.has(edge.from) || hiddenNodeIds.has(edge.to)
            }}));

            nodes.update(updateNodes);
            edges.update(updateEdges);

            document.getElementById("graphNodeCount").innerText = "Visible Nodes: " + visibleCount;
        }}

        // Initialize filtering once vis.js network is ready
        window.addEventListener("load", function() {{
            setTimeout(function() {{
                let slider = document.getElementById("graphLevelRange");
                if (slider) filterGraphByLevel(slider.value);
            }}, 300);
        }});
    </script>
    """

    # Inject layout styles, top slider bar, interactive nav script, and footer disclaimer
    net.html = net.html.replace("</head>", templates.LAYOUT_STYLE_RESET + "</head>")
    net.html = net.html.replace(
        "</body>",
        templates.INTERACTIVE_NAV_SCRIPT + top_slider_html + templates.DISCLAIMER_FOOTER.format(path_prefix="") + "</body>"
    )

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(net.html)

    print(f"Graph generated at {output_filename}")
    if formatting.non_found:
        print(f"{formatting.non_found} asset(s) were not found")

    # create profitability ranking page
    generate_profitability_ranking_page(outp, detail_dir=detail_dir)
    print(f"Profit Rankings generated")

    # create overnight strategy page
    generate_overnight_page(outp, detail_dir=detail_dir)
    print(f"Overnight Strategy generated")


def generate_detail_page_item(name, item_obj, filename):
    item_img_base64 = get_base64_asset(name, "items")
    img_tag = f'<img class="item-image" src="{item_img_base64}" alt="{name}">' if item_img_base64 else ""

    sell_price = getattr(item_obj, 'sell_price', 'N/A')
    if sell_price is None:
        sell_price = 'N/A'

    coin_b64 = get_base64_asset("coin", "items")
    coin_img = f'<img src="{coin_b64}" alt="coins" style="width: 18px; height: 18px; object-fit: contain; vertical-align: middle; margin-left: 3px; margin-top: -2px; display: inline-block;">' if coin_b64 else " Coins"

    price_display = f"{sell_price}{coin_img}" if sell_price != 'N/A' else "Unsellable"

    producer_name = None
    producer_folder = None
    class_type = type(item_obj).__name__

    if hasattr(item_obj, 'machine') and item_obj.machine:
        producer_name = item_obj.machine.name
        producer_folder = "machines"
    else:
        for animal_name, animal_obj in LIVESTOCK.items():
            if hasattr(animal_obj, 'produces_item') and animal_obj.produces_item:
                if animal_obj.produces_item.name.lower().strip() == name.lower().strip():
                    producer_name = animal_name
                    producer_folder = "animals"
                    break

    if not producer_name:
        if hasattr(item_obj, 'planted_on') and item_obj.planted_on:
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

    producer_html = ""
    if producer_name and producer_folder:
        producer_img = get_base64_asset(producer_name, producer_folder)
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

    raw_duration = getattr(item_obj, 'time_to_make', None)
    time_display_html = ""
    if raw_duration:
        formatted_time = format_duration(raw_duration)
        if formatted_time:
            time_display_html = f'<div class="price" style="background:#1e1e1e; border-color:#3498db; color:#3498db; margin-bottom: 0;">⏱️ {formatted_time}</div>'

    ingredients_dict = {}
    if hasattr(item_obj, 'ingredients') and item_obj.ingredients:
        for ing_item, qty in item_obj.ingredients.items():
            ingredients_dict[ing_item] = qty

    associated_feed = None
    for animal_name, animal_obj in LIVESTOCK.items():
        if hasattr(animal_obj, 'produces_item') and animal_obj.produces_item:
            if animal_obj.produces_item.name.lower().strip() == name.lower().strip():
                if hasattr(animal_obj, 'required_food') and animal_obj.required_food:
                    associated_feed = animal_obj.required_food
                    ingredients_dict[associated_feed] = 1
                    break

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

            ing_price = getattr(ing_item, 'sell_price', 'N/A')
            if ing_price is None:
                ing_price = 'N/A'

            if ing_price == 'N/A':
                unsellable_ingredients = True
            else:
                total_ingredient_cost += ing_price * qty

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
        coin_b64 = get_base64_asset("coin", "items")
        coin_img_html = f'<img src="{coin_b64}" alt="coins" style="width: 18px; height: 18px; object-fit: contain; vertical-align: middle; margin-left: 3px; margin-top: -2px; display: inline-block;">' if coin_b64 else "Coins"

        profit_html = f"""
        <div class="financial-summary">
            <div class="fin-col profit-positive" style="width: 100%;">
                <span class="fin-label">Production Status</span>
                <span class="fin-val" style="display: inline-flex; align-items: center; vertical-align: middle;">
                    🌱 Pure Profit (+{sell_price}{coin_img_html} / 100%)
                </span>
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
        percentage_yield = (net_profit / total_ingredient_cost) * 100 if total_ingredient_cost > 0 else 100.0
        pct_str = f"{percentage_yield:+.1f}%"

        if net_profit > 0:
            status_class, status_icon, status_label, val_prefix = "profit-positive", "📈", "Net Profit", "+"
        elif net_profit < 0:
            status_class, status_icon, status_label, val_prefix = "profit-negative", "📉", "Net Loss", ""
        else:
            status_class, status_icon, status_label, val_prefix = "profit-neutral", "⚖️", "Break-even", "±"

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

    price_breakdown_html = templates.render_price_breakdown_component(name, sell_price)

    html_content = templates.render_item_page(
        name=name, img_tag=img_tag, price_display=price_display,
        time_display_html=time_display_html, producer_html=producer_html,
        profit_html=profit_html, price_breakdown_html=price_breakdown_html,
        ingredients_html=ingredients_html, used_in_html=used_in_html,
        back_target=outp_file
    )

    os.makedirs(os.path.join(outp, "details"), exist_ok=True)
    with open(os.path.join(outp, "details", filename), "w", encoding="utf-8") as f:
        f.write(html_content)


def generate_detail_page_machine(name, prods, mach_obj):
    full_schedule = mach_obj.full_unlock_schedule if mach_obj else [(1, 1)]
    machine_unlock_lvl = mach_obj.unlock_level if mach_obj else 1

    img_base64 = get_base64_asset(name, "machines")
    if img_base64:
        img_tag = f"""
        <div class="machine-img-wrapper" id="mainMachineWrapper" data-unlock-level="{machine_unlock_lvl}">
            <span class="main-lock-badge">Requires Lvl {machine_unlock_lvl}</span>
            <img class="item-image" src="{img_base64}" alt="{name}">
        </div>
        """
    else:
        img_tag = ""

    produces_html = ""
    if prods:
        for prod_item in prods:
            prod_img = get_base64_asset(prod_item.name, "items")
            prod_url = f"details_{prod_item.name.lower().replace(' ', '_')}.html"
            time_lbl = ""
            raw_time = getattr(prod_item, 'time_to_make', None)
            if raw_time:
                formatted_time = format_duration(raw_time)
                if formatted_time:
                    time_lbl = f'<div class="qty-badge" style="background-color: #3498db; color: white; font-size: 0.6rem;">{formatted_time}</div>'

            prod_unlock_lvl = getattr(prod_item, 'unlock_level', 1)

            produces_html += f"""
            <a class="grid-item" href="{prod_url}" data-unlock-level="{prod_unlock_lvl}">
                <span class="lock-badge">🔒 Lvl {prod_unlock_lvl}</span>
                {time_lbl}
                <img src="{prod_img}" alt="{prod_item.name}">
                <div class="name">{prod_item.name}</div>
            </a>
            """
    else:
        produces_html = '<div class="no-items">💤 Nothing directly produced here.</div>'

    # Extracted function used here
    unlock_schedule_html = templates.generate_unlock_schedule_component(full_schedule, name, asset_folder="machines")

    has_mastery = False
    if mach_obj:
        star1_info = mach_obj.get_star_info(1) or {}
        star2_info = mach_obj.get_star_info(2) or {}
        star3_info = mach_obj.get_star_info(3) or {}
        if any([star1_info, star2_info, star3_info]):
            has_mastery = True

    if has_mastery:
        mastery_columns_html = ""
        for star in range(1, 4):
            info = mach_obj.get_star_info(star) if mach_obj else {}
            hours = info.get("hours_required", 0)
            hours_str = f"{hours:,} hrs" if hours > 0 else "-"

            bonus_desc = formatting.format_mastery_bonus_text(info)
            asset_key = formatting.get_mastery_image_filename(star, info, name)
            mastery_img_b64 = get_base64_asset(asset_key, "mastery")

            if mastery_img_b64:
                img_element = f'<img src="{mastery_img_b64}" alt="{asset_key}" style="max-width: 100%; max-height: 80px; object-fit: contain;">'
            else:
                stars_render = "⭐" * star
                img_element = f'<div style="font-size: 1.5rem; padding: 10px;">{stars_render}</div>'

            is_active = (mach_obj and mach_obj.mastery_level >= star)
            active_class = "mastery-col active" if is_active else "mastery-col"

            mastery_columns_html += f"""
            <div class="{active_class}" style="flex: 1; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; overflow: hidden; background: rgba(0, 0, 0, 0.25); display: flex; flex-direction: column; text-align: center;">
                <div style="background: rgba(255, 255, 255, 0.05); padding: 6px 4px; font-weight: bold; font-size: 0.9rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #f1a80a;">
                    {"★" * star}
                    <div style="font-size: 0.85rem; color: #d0d0d0; margin-top: 2px;">{hours_str}</div>
                </div>
                <div style="padding: 10px 4px; flex-grow: 1; display: flex; align-items: center; justify-content: center; min-height: 85px;">
                    {img_element}
                </div>
                <div style="background: rgba(0, 0, 0, 0.15); padding: 8px 4px; font-weight: bold; font-size: 0.85rem; border-top: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff;">
                    {bonus_desc}
                </div>
            </div>
            """

        mastery_content = f"""
        <div class="mastery-container" style="display: flex; gap: 10px; margin-top: 10px;">
            {mastery_columns_html}
        </div>
        """
    else:
        mastery_content = '<div class="no-items">This machine cannot be mastered.</div>'

    mastery_html = f"""
    <div class="section-title">Mastery</div>
    {mastery_content}
    """

    filename = f"details_{name.lower().replace(' ', '_')}.html"

    html_content = templates.render_machine_page(
        name=name,
        img_tag=img_tag,
        produces_html=produces_html,
        unlock_schedule_html=unlock_schedule_html,
        mastery_html=mastery_html,
        back_target=outp_file,
        unlock_schedule=mach_obj.unlock_schedule if mach_obj else [(1, 1)]
    )

    os.makedirs(os.path.join(outp, "details"), exist_ok=True)
    with open(os.path.join(outp, "details", filename), "w", encoding="utf-8") as f:
        f.write(html_content)


def generate_detail_page_pen(name, residents, pen_obj=None):
    # Retrieve schedule if pen_obj carries schedule data, otherwise fallback to resident levels
    full_schedule = pen_obj.full_unlock_schedule if pen_obj else [(1, 1)]
    pen_unlock_lvl = pen_obj.unlock_level if pen_obj else 1

    img_base64 = get_base64_asset(name, "pens")
    if img_base64:
        img_tag = f"""
        <div class="item-img-wrapper" id="mainMachineWrapper" data-unlock-level="{pen_unlock_lvl}">
            <span class="main-lock-badge">Requires Lvl {pen_unlock_lvl}</span>
            <img class="item-image" src="{img_base64}" alt="{name}">
        </div>
        """
    else:
        img_tag = ""

    residents_html = ""
    if residents:
        for res in residents:
            res_img = get_base64_asset(res.name, "animals")
            res_url = f"details_{res.name.lower().replace(' ', '_')}.html"
            res_unlock_lvl = getattr(res, 'unlock_level', 1)

            residents_html += f"""
            <a class="grid-item" href="{res_url}" data-unlock-level="{res_unlock_lvl}">
                <span class="lock-badge">🔒 Lvl {res_unlock_lvl}</span>
                <img src="{res_img}" alt="{res.name}">
                <div class="name">{res.name}</div>
            </a>
            """
    else:
        residents_html = '<div class="no-items">💤 Vacant Habitat.</div>'

    # Reuse extracted schedule component for pens
    unlock_schedule_html = templates.generate_unlock_schedule_component(full_schedule, name, asset_folder="pens")

    filename = f"details_{name.lower().replace(' ', '_')}.html"
    html_content = templates.render_pen_page(
        name=name,
        img_tag=img_tag,
        residents_html=residents_html,
        unlock_schedule_html=unlock_schedule_html,
        back_target=outp_file,
        unlock_schedule=pen_obj.unlock_schedule if pen_obj else [(1, 1)]
    )

    os.makedirs(os.path.join(outp, "details"), exist_ok=True)
    with open(os.path.join(outp, "details", filename), "w", encoding="utf-8") as f:
        f.write(html_content)


def generate_detail_page_plantable_structure(name, prods):
    img_base64 = get_base64_asset(name, "plant_structures")
    img_tag = f'<img class="item-image" src="{img_base64}" alt="{name}">' if img_base64 else ""

    produces_html = ""
    if prods:
        for prod_item in prods:
            prod_img = get_base64_asset(prod_item.name, "items")
            prod_url = f"details_{prod_item.name.lower().replace(' ', '_')}.html"
            produces_html += f"""
            <a class="grid-item" href="{prod_url}">
                <img src="{prod_img}" alt="{prod_item.name}">
                <div class="name">{prod_item.name}</div>
            </a>
            """
    else:
        produces_html = '<div class="no-items">💤 Nothing grown here.</div>'

    filename = f"details_{name.lower().replace(' ', '_')}.html"
    html_content = templates.render_plantable_structure_page(name, img_tag, produces_html, outp_file)
    with open(os.path.join(outp, "details", filename), "w", encoding="utf-8") as f:
        f.write(html_content)


def generate_detail_page_special_structure(name, prods):
    img_base64 = get_base64_asset(name, "special_structures")
    img_tag = f'<img class="item-image" src="{img_base64}" alt="{name}">' if img_base64 else ""

    produces_html = ""
    if prods:
        for prod_item in prods:
            prod_img = get_base64_asset(prod_item.name, "items")
            prod_url = f"details_{prod_item.name.lower().replace(' ', '_')}.html"
            produces_html += f"""
            <a class="grid-item" href="{prod_url}">
                <img src="{prod_img}" alt="{prod_item.name}">
                <div class="name">{prod_item.name}</div>
            </a>
            """
    else:
        produces_html = '<div class="no-items">💤 Nothing harvested here.</div>'

    filename = f"details_{name.lower().replace(' ', '_')}.html"
    html_content = templates.render_special_structure_page(name, img_tag, produces_html, outp_file)
    with open(os.path.join(outp, "details", filename), "w", encoding="utf-8") as f:
        f.write(html_content)


def generate_detail_page_field(name, prods, field_obj=None):
    # Determine schedule or base unlock level
    full_schedule = getattr(field_obj, 'full_unlock_schedule', None) if field_obj else None

    if full_schedule:
        field_unlock_lvl = full_schedule[0][0]
    else:
        # Fallback to the lowest crop unlock level or 1
        field_unlock_lvl = min([getattr(p, 'unlock_level', 1) for p in prods]) if prods else 1
        full_schedule = field_unlock_lvl

    img_base64 = get_base64_asset(name, "fields")
    if img_base64:
        img_tag = f"""
        <div class="item-img-wrapper" id="mainMachineWrapper" data-unlock-level="{field_unlock_lvl}">
            <span class="main-lock-badge">Requires Lvl {field_unlock_lvl}</span>
            <img class="item-image" src="{img_base64}" alt="{name}">
        </div>
        """
    else:
        img_tag = ""

    produces_html = ""
    if prods:
        for prod_item in prods:
            prod_img = get_base64_asset(prod_item.name, "items")
            prod_url = f"details_{prod_item.name.lower().replace(' ', '_')}.html"
            prod_unlock_lvl = getattr(prod_item, 'unlock_level', 1)

            time_lbl = ""
            raw_time = getattr(prod_item, 'time_to_make', None)
            if raw_time:
                formatted_time = format_duration(raw_time)
                if formatted_time:
                    time_lbl = f'<div class="qty-badge" style="background-color: #3498db; color: white; font-size: 0.6rem;">{formatted_time}</div>'

            produces_html += f"""
            <a class="grid-item" href="{prod_url}" data-unlock-level="{prod_unlock_lvl}">
                <span class="lock-badge">🔒 Lvl {prod_unlock_lvl}</span>
                {time_lbl}
                <img src="{prod_img}" alt="{prod_item.name}">
                <div class="name">{prod_item.name}</div>
            </a>
            """
    else:
        produces_html = '<div class="no-items">💤 Crop soil is currently fallow.</div>'

    # Generate schedule section if a schedule list is present
    unlock_schedule_html = ""
    if isinstance(full_schedule, list) and len(full_schedule) > 0:
        unlock_schedule_html = templates.generate_unlock_schedule_component(full_schedule, name, asset_folder="fields")

    filename = f"details_{name.lower().replace(' ', '_')}.html"
    html_content = templates.render_field_page(
        name=name,
        img_tag=img_tag,
        produces_html=produces_html,
        back_target=outp_file,
        unlock_schedule=full_schedule,
        unlock_schedule_html=unlock_schedule_html
    )

    os.makedirs(os.path.join(outp, "details"), exist_ok=True)
    with open(os.path.join(outp, "details", filename), "w", encoding="utf-8") as f:
        f.write(html_content)


def generate_detail_page_animal(name, animal_obj):
    animal_unlock_lvl = getattr(animal_obj, 'unlock_level', 1)

    img_base64 = get_base64_asset(name, "animals")
    if img_base64:
        img_tag = f"""
        <div class="item-img-wrapper" id="mainMachineWrapper" data-unlock-level="{animal_unlock_lvl}">
            <span class="main-lock-badge">Requires Lvl {animal_unlock_lvl}</span>
            <img class="item-image" src="{img_base64}" alt="{name}">
        </div>
        """
    else:
        img_tag = ""

    lives_in_html = '<span style="color:#888;">Nomad / No Pen</span>'
    if animal_obj.pen:
        pen_name = animal_obj.pen.name
        pen_img = get_base64_asset(pen_name, "pens")
        pen_url = f"details_{pen_name.lower().replace(' ', '_')}.html"
        pen_unlock_lvl = getattr(animal_obj.pen, 'unlock_level', 1)

        lives_in_html = f"""
        <a href="{pen_url}" style="text-decoration:none; display:flex; align-items:center; gap:8px;" data-unlock-level="{pen_unlock_lvl}">
            <img src="{pen_img}" style="width:24px; height:24px; object-fit:contain;" alt="{pen_name}">
            <span style="color:#f1a80a; font-weight:bold; font-size:0.85rem;">{pen_name}</span>
        </a>
        """

    food_html = '<span style="color:#888;">Forages / No Food</span>'
    if animal_obj.required_food:
        food_name = animal_obj.required_food.name
        food_img = get_base64_asset(food_name, "items")
        food_url = f"details_{food_name.lower().replace(' ', '_')}.html"
        food_unlock_lvl = getattr(animal_obj.required_food, 'unlock_level', 1)

        food_html = f"""
        <a href="{food_url}" style="text-decoration:none; display:flex; align-items:center; gap:8px;" data-unlock-level="{food_unlock_lvl}">
            <img src="{food_img}" style="width:24px; height:24px; object-fit:contain;" alt="{food_name}">
            <span style="color:#f1a80a; font-weight:bold; font-size:0.85rem;">{food_name}</span>
        </a>
        """

    produces_html = ""
    if animal_obj.produces_item:
        prod_name = animal_obj.produces_item.name
        prod_img = get_base64_asset(prod_name, "items")
        prod_url = f"details_{prod_name.lower().replace(' ', '_')}.html"
        prod_unlock_lvl = getattr(animal_obj.produces_item, 'unlock_level', 1)

        time_lbl = ""
        raw_time = getattr(animal_obj.produces_item, 'time_to_make', None)
        if raw_time:
            formatted_time = format_duration(raw_time)
            if formatted_time:
                time_lbl = f'<div class="qty-badge" style="background-color: #3498db; color: white; font-size: 0.6rem;">{formatted_time}</div>'

        produces_html += f"""
        <a class="grid-item" href="{prod_url}" data-unlock-level="{prod_unlock_lvl}">
            <span class="lock-badge">🔒 Lvl {prod_unlock_lvl}</span>
            {time_lbl}
            <img src="{prod_img}" alt="{prod_name}">
            <div class="name">{prod_name}</div>
        </a>
        """
    else:
        produces_html = '<div class="no-items">💤 Yields no products.</div>'

    filename = f"details_{name.lower().replace(' ', '_')}.html"

    # Pass animal_unlock_lvl directly as an integer or tuple/list
    html_content = templates.render_animal_page(
        name=name,
        img_tag=img_tag,
        food_html=food_html,
        produces_html=produces_html,
        lives_in_html=lives_in_html,
        back_target=outp_file,
        unlock_schedule=animal_unlock_lvl
    )

    os.makedirs(os.path.join(outp, "details"), exist_ok=True)
    with open(os.path.join(outp, "details", filename), "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    generate_interactive_farm_graph()