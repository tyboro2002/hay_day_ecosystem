import requests
import re
# TODO search for options as this does not work

def get_authorized_session():
    session = requests.Session()

    # 1. Set base headers (mimic a real browser)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://fankit.supercell.com/d/QSVyhmM7gdGe/game-assets"
    })

    # 2. GET the page to initialize the session and get the CSRF token
    response = session.get("https://fankit.supercell.com/d/QSVyhmM7gdGe/game-assets")

    # 3. Extract the CSRF token from the HTML meta tags
    # Most modern sites put it in: <meta name="csrf-token" content="TOKEN_HERE">
    match = re.search(r'name="csrf-token" content="([^"]+)"', response.text)
    if not match:
        print("Could not find CSRF token in HTML. Checking cookies...")
        # Fallback: Check if it was set as a cookie
        csrf_token = session.cookies.get('csrf_token')
    else:
        csrf_token = match.group(1)

    if not csrf_token:
        raise Exception("Failed to retrieve CSRF token. The site's security might be blocking the request.")

    # 4. Set the token in the headers for all future POST requests
    session.headers.update({"X-CSRF-TOKEN": csrf_token})
    print(f"Handshake complete. Token extracted: {csrf_token[:10]}...")

    return session

# --- Execution ---
try:
    session = get_authorized_session()

    url = "https://fankit.supercell.com/api/asset/required-licenses"
    payload = {"asset_ids": [157482, 157481, 157480]}

    response = session.post(url, json=payload)

    if response.status_code == 200:
        print("Success! API responded with:")
        print(response.json())
    else:
        print(f"Request failed with status {response.status_code}: {response.text}")

except Exception as e:
    print(f"Automation failed: {e}")