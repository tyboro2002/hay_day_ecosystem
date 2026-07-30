import io
from PIL import Image
import os
import base64
from functools import lru_cache

# Keep track of missing assets globally across generators
non_found = 0
RED = "\033[91m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
ORANGE = "\033[38;5;208m" # 256-color mode for Orange (Color 208)
RESET = "\033[0m"

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

@lru_cache(maxsize=1024)  # Caches duplicate images so they only encode ONCE
def image_to_base64(image_path):
    """Converts a local image file to a compressed base64 webp string quickly."""
    global non_found
    if not os.path.exists(image_path):
        non_found += 1
        print(f"{ORANGE}Did not find {image_path}{RESET}")
        image_path = os.path.join("assets", "default_icon.png")

    try:
        with Image.open(image_path) as img:
            # BILINEAR or BOX resampling is significantly faster than LANCZOS for tiny icons
            img.thumbnail((128, 128), Image.Resampling.BILINEAR)

            buffered = io.BytesIO()

            # method=0 or method=4 gives 95% of the compression at a fraction of the time
            # quality=75 is the WebP sweet spot for small UI icons
            img.save(buffered, format="WEBP", quality=75, method=4)

            encoded = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return f"data:image/webp;base64,{encoded}"
    except Exception as e:
        print(f"Error encoding {image_path}: {e}")
        return None


def get_base64_asset(name, subfolder):
    """Helper to get base64 string based on name and subfolder."""
    filename = f"{name.lower().replace(' ', '_')}.png"
    filepath = os.path.join("assets", subfolder, filename)
    return image_to_base64(filepath)