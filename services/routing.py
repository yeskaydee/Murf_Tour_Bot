import requests
import os
from urllib.parse import quote

ORS_API_KEY = os.getenv("ORS_API_KEY")  # Set this in your .env

# def geocode_place(place_name: str, location_hint: str = None):
#     if location_hint:
#         # Extract just the last 2-3 parts of the location_hint
#         parts = location_hint.split(", ")
#         relevant_hint = ", ".join(parts[-3:]) if len(parts) >= 3 else location_hint
#         query = f"{place_name}, {relevant_hint}"
#     else:
#         query = place_name

#     url = f"https://nominatim.openstreetmap.org/search?q={quote(query)}&format=json&limit=1"
#     try:
#         print(f"[GEOCODE] Searching for: {query}")
#         resp = requests.get(url, headers={"User-Agent": "TourGuideBot/1.0 (ironkrish12@gmail.com)"})
#         resp.raise_for_status()
#         data = resp.json()
#         if data:
#             return float(data[0]['lat']), float(data[0]['lon'])
#         else:
#             return None, None
#     except Exception as e:
#         print(f"[GEOCODE ERROR] {e}")
#         print("Routing error in geocode_place")
#         return None, None
    
def geocode_search(query: str,lat,lon,radius = 200 ):
    url = f"https://api.openrouteservice.org/geocode/search?api_key={ORS_API_KEY}&size=10&text={quote(query)}&boundary.circle.lon={lon}&boundary.circle.lat={lat}&boundary.circle.radius={radius}"
    try:
        print(f"[GEOCODE SEARCH] Searching for: {query}")
        headers = {
            "Authorization": ORS_API_KEY,
            "Content-Type": "application/json"
        }
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        features = data.get("features", [])
        if features:
            coords = features[0]["geometry"]["coordinates"]  # [lon, lat]
            lon, lat = coords
            return lat, lon
        else:
            return None, None
    except Exception as e:
        print(f"[GEOCODE SEARCH ERROR] {e}")
        print("Routing error in geocode_search")
        return None, None


def get_directions(start_lat, start_lon, end_lat, end_lon):
    try:
        url = "https://api.openrouteservice.org/v2/directions/foot-walking"
        headers = {
            "Authorization": ORS_API_KEY,
            "Content-Type": "application/json"
        }
        body = {
            "coordinates": [[start_lon, start_lat], [end_lon, end_lat]]
        }

        print(f"[ROUTE] Start: {start_lat}, {start_lon} | Dest: {end_lat}, {end_lon}")

        response = requests.post(url, json=body, headers=headers)
        data = response.json()

        if 'error' in data:
            print(f"[ORS ERROR] {data}")
            return "Sorry, I couldn't find a route."

        # Corrected path for steps:
        steps = data['routes'][0]['segments'][0]['steps']
        instructions = [step['instruction'] for step in steps]
        return "Here's how you can get there:\n\n" + "\n".join(f"{i+1}. {instr}" for i, instr in enumerate(instructions))
    except Exception as e:
        print(f"[ROUTING ERROR] {e}")
        print("Routing error in get_directions")
        return "Sorry, I couldn't get directions right now."