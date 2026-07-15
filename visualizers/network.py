import os
from pyvis.network import Network
from game_data import ITEMS, INFRASTRUCTURE, LIVESTOCK

# Import helpers from the subdirectory package!
from visualizers.helpers.formatting import format_duration, get_base64_asset
import visualizers.helpers.formatting as formatting
import visualizers.helpers.templates as templates

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

    # =====================================================================
    # 1. GENERATE ALL INFRASTRUCTURE NODES
    # =====================================================================
    for name in INFRASTRUCTURE["machines"].keys():
        detail_url = f"{detail_dir}/details_{name.lower().replace(' ', '_')}.html"
        net.add_node(name, label=name, shape="image", image=get_base64_asset(name, "machines"), size=MACHINE_SIZE, url=detail_url)
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
        detail_filename = f"details_{name.lower().replace(' ', '_')}.html"
        detail_url = f"{detail_dir}/{detail_filename}"

        class_type = type(item_obj).__name__
        price_lbl = f"\n({item_obj.sell_price}c)" if hasattr(item_obj, 'sell_price') else ""
        net.add_node(name, label=f"{name}{price_lbl}", shape="image", image=get_base64_asset(name, "items"), size=ITEM_SIZE, url=detail_url)

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

    # Generate and inject templates
    net.html = net.generate_html()
    net.html = net.html.replace("</head>", templates.LAYOUT_STYLE_RESET + "</head>")
    net.html = net.html.replace("</body>", templates.DISCLAIMER_FOOTER + templates.INTERACTIVE_NAV_SCRIPT + "</body>")

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(net.html)

    print(f"Graph generated at {output_filename}")
    if formatting.non_found:
        print(f"{formatting.non_found} asset(s) were not found")


def generate_detail_page_item(name, item_obj, filename):
    """Generates details view for individual catalog items."""
    item_img_base64 = get_base64_asset(name, "items")
    img_tag = f'<img class="item-image" src="{item_img_base64}" alt="{name}">' if item_img_base64 else ""

    sell_price = getattr(item_obj, 'sell_price', 'N/A')
    if sell_price is None:
        sell_price = 'N/A'
    price_display = f"{sell_price} Coins" if sell_price != 'N/A' else "Unsellable"

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

    html_content = templates.render_item_page(
        name=name, img_tag=img_tag, price_display=price_display,
        time_display_html=time_display_html, producer_html=producer_html,
        profit_html=profit_html, ingredients_html=ingredients_html,
        used_in_html=used_in_html, back_target=outp_file
    )

    os.makedirs(os.path.join(outp, "details"), exist_ok=True)
    with open(os.path.join(outp, "details", filename), "w", encoding="utf-8") as f:
        f.write(html_content)


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
    html_content = templates.render_non_item_page(
        name=name, img_tag=img_tag, extra_html=extra_html,
        produces_html=produces_html, back_target=outp_file
    )

    os.makedirs(os.path.join(outp, "details"), exist_ok=True)
    with open(os.path.join(outp, "details", filename), "w", encoding="utf-8") as f:
        f.write(html_content)


if __name__ == "__main__":
    generate_interactive_farm_graph()