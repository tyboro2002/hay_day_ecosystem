# visualizers/graph.py
import os
from graphviz import Digraph
from game_data import ITEMS, INFRASTRUCTURE, LIVESTOCK

def generate_complete_farm_graph(output_filename="visualisation_outputs/hayday_complete_ecosystem"):
    dot = Digraph(comment="Hay Day Complete Production Ecosystem", format="png")

    # =====================================================================
    # LAYOUT ENGINE & OVERLAP REDUCTION GRAPH ATTRIBUTES
    # =====================================================================
    dot.attr(
        rankdir="LR",           # Left-to-Right Flowchart style
        size="40,40",           # Scale up canvas size so things can breathe
        dpi="600",
        splines="true",         # Crucial! Forces lines to curve cleanly *around* nodes instead of running over them
        nodesep="0.6",          # Increases vertical spacing between nodes
        ranksep="1.5",          # Increases horizontal spacing between structural columns
        concentrate="true",     # Merges overlapping identical destination lines to reduce visual noise
        overlap="false"         # Actively pushes nodes apart if they try to collide
    )

    # =====================================================================
    # 1. GENERATE ALL INFRASTRUCTURE NODES
    # =====================================================================
    for name in INFRASTRUCTURE["machines"].keys():
        dot.node(name, label=name, shape="box", style="filled,rounded", color="darkorange", fillcolor="moccasin", fontname="Helvetica-Bold")

    for name in INFRASTRUCTURE["pens"].keys():
        dot.node(name, label=name, shape="box", style="filled,rounded", color="peru", fillcolor="bisque", fontname="Helvetica-Bold")

    for name in INFRASTRUCTURE["plant_structures"].keys():
        dot.node(name, label=name, shape="box", style="filled,rounded", color="forestgreen", fillcolor="palegreen", fontname="Helvetica-Bold")

    for name in INFRASTRUCTURE["special_structures"].keys():
        dot.node(name, label=name, shape="box", style="filled,rounded", color="dodgerblue", fillcolor="lightskyblue", fontname="Helvetica-Bold")


    for obj in INFRASTRUCTURE["fields"].keys():
        dot.node(obj, label=obj, shape="box", style="filled,rounded", color="lightskyblue", fillcolor="yellow", fontname="Helvetica-Bold")

    # =====================================================================
    # 2. GENERATE LIVESTOCK (ANIMALS) NODES & LINKS
    # =====================================================================
    for name, animal_obj in LIVESTOCK.items():

        dot.node(name, label=name, shape="egg", style="filled", color="deeppink", fillcolor="lavenderblush", fontname="Helvetica-Bold")

        if animal_obj.pen:
            dot.edge(animal_obj.pen.name, name, color="gray40", style="dashed")

        if animal_obj.produces_item:
            dot.edge(name, animal_obj.produces_item.name, color="royalblue", penwidth="2.5", label=" yields")

        if animal_obj.required_food:
            dot.edge(animal_obj.required_food.name, name, color="crimson", style="dotted", penwidth="1.5", label=" eats")

    # =====================================================================
    # 3. GENERATE ALL ITEM NODES & INGREDIENT LINKS
    # =====================================================================
    for name, item_obj in ITEMS.items():
        class_type = type(item_obj).__name__

        if class_type == "Crop":
            color, fill = "olive", "darkkhaki"
        elif class_type == "PlantItem":
            color, fill = "forestgreen", "honeydew"
        elif class_type == "AnimalItem":
            color, fill = "navy", "aliceblue"
        elif class_type == "SpecialItem" and ("Ore" in name or name == "Coal"):
            color, fill = "slategrey", "lightgray" # Fixed typo ("slate=grey" -> "slategrey")
        else:
            color, fill = "darkgreen", "lightgoldenrodyellow"

        price_lbl = f"\n({item_obj.sell_price}c)" if hasattr(item_obj, 'sell_price') else ""
        dot.node(name, label=f"{name}{price_lbl}", shape="ellipse", style="filled", color=color, fillcolor=fill, fontname="Helvetica")

        # --- INFRASTRUCTURE ORIGIN RESOLVER ---
        if hasattr(item_obj, 'machine') and item_obj.machine:
            dot.edge(item_obj.machine.name, name, color="dimgray", penwidth="1.5")

        elif hasattr(item_obj, 'pen') and item_obj.pen:
            dot.edge(item_obj.pen.name, name, color="dimgray", penwidth="1.5")

        elif hasattr(item_obj, 'planted_on') and item_obj.planted_on:
            dot.edge(list(item_obj.planted_on.keys())[0], name, color="dimgray", penwidth="1.5")

        elif class_type == "PlantableItem":
            # Try a safe, case-insensitive substring match against your structure list
            matched = False
            for struct_name in INFRASTRUCTURE["plant_structures"].keys():
                if name.lower() in struct_name.lower():
                    dot.edge(struct_name, name, color="forestgreen", penwidth="1.5", style="solid")
                    matched = True
                    break

            # Fallback just in case your structure dictionary names are exact duplicates of the item names
            if not matched and name in INFRASTRUCTURE["plant_structures"]:
                dot.edge(name, name, color="forestgreen", penwidth="1.5", style="solid")

        elif name in ["Silver Ore", "Gold Ore", "Platinum Ore", "Iron Ore", "Coal"]:
            dot.edge("Mine", name, color="dimgray", penwidth="1.5")

        elif name == "Fish Fillet":
            dot.edge("Fishing Lake", name, color="dimgray", penwidth="1.5")

        # --- RECIPE INGREDIENT LINKS ---
        if hasattr(item_obj, 'ingredients') and item_obj.ingredients:
            for ingredient_obj, quantity in item_obj.ingredients.items():
                thickness = str(max(1.0, float(quantity)))

                dot.edge(
                    ingredient_obj.name,
                    name,
                    label=f" x{quantity:.2f}" if isinstance(quantity, float) else f" x{quantity}",
                    color="brown",
                    penwidth=thickness,
                    fontname="Helvetica-Oblique",
                    fontsize="9"
                )

    # Output to the project directory root path smoothly
    dot.render(output_filename, cleanup=True)
    print(f"Success! Your optimized farm ecosystem graph has been compiled into '{output_filename}.png'")

if __name__ == "__main__":
    generate_complete_farm_graph()