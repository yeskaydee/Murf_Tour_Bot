import requests

def reverse_geocode(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "jsonv2",
        "lat": lat,
        "lon": lon,
        "zoom": 18,
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "murf_tour_bot/1.0 (yeskaydeecodes9@gmai.com)"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("display_name", "a location I couldn't identify")
    except Exception as e:
        print(f"[GEOCODE ERROR] {e}")
        return "somewhere I couldn't identify"
