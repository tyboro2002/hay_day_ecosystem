# Floating disclaimer footer
DISCLAIMER_FOOTER = """
<div class="sc-disclaimer-footer">
    This material is unofficial and is not endorsed by Supercell. For more information see <a href="https://www.supercell.com/fan-content-policy" target="_blank">Supercell's Fan Content Policy</a>.
</div>
"""

# PyVis Main map styles
LAYOUT_STYLE_RESET = """
<style type="text/css">
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
    }
    .sc-disclaimer-footer {
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

# PyVis interactive navigation handler
INTERACTIVE_NAV_SCRIPT = """
<script type="text/javascript">
    window.addEventListener('load', function() {
        if (typeof network !== 'undefined') {
            network.on("click", function (params) {
                var originalEvent = params.event ? (params.event.srcEvent || params.event) : null;
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

def render_item_page(name, img_tag, price_display, time_display_html, producer_html, profit_html, ingredients_html, used_in_html, back_target):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} - Details</title>
    <style>
        body {{ background-color: #222222; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 40px 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; box-sizing: border-box; }}
        .card {{ background-color: #2d2d2d; border-radius: 16px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); width: 100%; max-width: 500px; padding: 40px 30px; text-align: center; border: 1px solid #444444; }}
        .item-image {{ width: 110px; height: 110px; margin-bottom: 15px; object-fit: contain; filter: drop-shadow(0px 6px 8px rgba(0,0,0,0.6)); }}
        h1 {{ margin: 5px 0 10px 0; font-size: 2rem; color: #f1a80a; font-weight: 700; letter-spacing: 0.5px; }}
        .price {{ font-size: 1.1rem; color: #b0b0b0; font-weight: 500; background: #3a3a3a; display: inline-block; padding: 6px 16px; border-radius: 20px; border: 1px solid #555555; }}
        .producer-section {{ margin-bottom: 25px; }}
        .producer-label {{ font-size: 0.72rem; color: #888888; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px; }}
        .producer-badge {{ display: inline-flex; align-items: center; background-color: #1e1e1e; padding: 8px 18px; border-radius: 25px; border: 1px solid #3a3a3a; gap: 12px; }}
        .producer-badge img {{ width: 32px; height: 32px; object-fit: contain; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.5)); }}
        .producer-badge span {{ font-size: 0.9rem; font-weight: 700; color: #ffffff; }}
        .financial-summary {{ display: flex; justify-content: space-between; background-color: #1e1e1e; border-radius: 12px; padding: 15px; margin-bottom: 30px; border: 1px solid #3a3a3a; gap: 10px; }}
        .fin-col {{ flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
        .fin-col:not(:last-child) {{ border-right: 1px solid #333333; }}
        .fin-label {{ font-size: 0.72rem; color: #888888; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 5px; }}
        .fin-val {{ font-size: 0.95rem; font-weight: 700; }}
        .profit-positive .fin-val {{ color: #2ecc71; }}
        .profit-negative .fin-val {{ color: #e74c3c; }}
        .profit-neutral .fin-val {{ color: #b0b0b0; }}
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
        .sc-disclaimer-footer {{ position: fixed !important; bottom: 20px !important; left: 50% !important; transform: translateX(-50%) !important; z-index: 999999 !important; background-color: rgba(33, 33, 33, 0.95) !important; border: 1px solid #444444 !important; border-radius: 30px !important; padding: 10px 24px !important; color: #b0b0b0 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important; font-size: 0.72rem !important; text-align: center !important; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6) !important; max-width: 90% !important; width: max-content !important; pointer-events: auto !important; backdrop-filter: blur(8px) !important; -webkit-backdrop-filter: blur(8px) !important; }}
        .sc-disclaimer-footer a {{ color: #f1a80a !important; text-decoration: none !important; font-weight: 600 !important; }}
        .sc-disclaimer-footer a:hover {{ text-decoration: underline !important; }}
    </style>
</head>
<body>
    {DISCLAIMER_FOOTER}
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

        <a class="back-btn" href="../{back_target}">Back to Map</a>
    </div>
</body>
</html>
"""

def render_non_item_page(name, img_tag, extra_html, produces_html, back_target):
    return f"""<!DOCTYPE html>
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
    {DISCLAIMER_FOOTER}
    <div class="card">
        {img_tag}
        <h1>{name}</h1>

        {extra_html}

        <div class="section-title">Yields / Produces</div>
        <div class="grid">
            {produces_html}
        </div>

        <a class="back-btn" href="../{back_target}">Back to Map</a>
    </div>
</body>
</html>
"""