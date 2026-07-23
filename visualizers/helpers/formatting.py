import io
from PIL import Image
import os
import base64

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


def image_to_base64(image_path):
    """Converts a local image file to a base64 string for embedding."""
    global non_found
    if not os.path.exists(image_path):
        non_found += 1
        # Fallback to a default if the specific asset isn't found
        print(f"{ORANGE}Did not find {image_path}{RESET}")
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