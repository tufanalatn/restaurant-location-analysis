import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

HEADERS = {
    "User-Agent": "restaurant-location-analysis/1.0"
}


def run_query(query: str):
    response = requests.post(
        OVERPASS_URL,
        data={"data": query},
        headers=HEADERS,
        timeout=60,
    )

    response.raise_for_status()
    return response.json()


if __name__ == "__main__":

    query = """
    [out:json][timeout:25];

    node
      ["amenity"="restaurant"]
      (around:500,40.7536,-73.9832);

    out;
    """

    data = run_query(query)

    print("Overpass connection: OK")
    print("Restaurants found:", len(data["elements"]))

    for place in data["elements"][:10]:
        print(
            place.get("tags", {}).get("name", "Unnamed"),
            place.get("tags", {}).get("cuisine", "unknown")
        )
