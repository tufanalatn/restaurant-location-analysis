import time
import requests

OVERPASS_URLS = [
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter",
]

HEADERS = {
    "User-Agent": "restaurant-location-analysis/1.0"
}


def run_query(query: str, max_attempts=6):

    last_error = None

    for attempt in range(max_attempts):

        url = OVERPASS_URLS[attempt % len(OVERPASS_URLS)]

        try:
            print(f"  Overpass server: {url}")

            response = requests.post(
                url,
                data={"data": query},
                headers=HEADERS,
                timeout=180,
            )

            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:

            last_error = e

            wait_seconds = 10 * (attempt + 1)

            print(
                f"  Attempt {attempt + 1} failed: "
                f"{type(e).__name__}"
            )

            if attempt < max_attempts - 1:
                print(f"  Waiting {wait_seconds}s...")
                time.sleep(wait_seconds)

    raise last_error
