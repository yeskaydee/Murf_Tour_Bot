from pymongo import MongoClient
import os

# Replace with your actual connection string
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://murf_db:CjW6pUXnujpreYIR@cluster0.dgzxcyv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client["awaaz_tourbot"]
locations_collection = db["user_locations"]

def get_user(user_id: int):
    return locations_collection.find_one({"user_id": user_id})

def set_user_location(user_id, location_string, lat, lon):

    parts = location_string.split(", ")
    cleaned_location = ", ".join(parts[:3])  # e.g., "India Gate, Rajpath Marg"

    locations_collection.update_one(
        {"user_id": user_id},
        {"$set": {"location": location_string}},
        upsert=True
    )

    locations_collection.update_one(
        {"user_id": user_id},
        {"$set": {"cleaned_location": cleaned_location}},
        upsert=True
    )

# to be added later for using with routing services
    # locations_collection.update_one(
    #     {"user_id": user_id},   
    #     {"$set": {"last_updated": datetime.datetime.now(datetime.timezone.utc)}},
    #     upsert=True
    # )

    locations_collection.update_one(
        {"user_id": user_id},
        {"$set": {"latitude": lat, "longitude": lon}},
        upsert=True
    )

def get_user_language(user_id):
    doc = locations_collection.find_one({"user_id": user_id})
    return doc["language"] if doc and "language" in doc else "en-US"

def get_user_location(user_id):
    doc = locations_collection.find_one({"user_id": user_id})
    return doc["location"] if doc else None

def get_user_cleaned_location(user_id):
    doc = locations_collection.find_one({"user_id": user_id})
    return doc["cleaned_location"] if doc else None

def get_user_location_coordinates(user_id):
    doc = locations_collection.find_one({"user_id": user_id})
    if doc and "latitude" in doc and "longitude" in doc:
        return doc["latitude"], doc["longitude"]
    return None, None

def get_user_preferences(user_id: int) -> tuple[str, str]:
    user = get_user(user_id)
    if not user:
        return "en-US", "default"
    return user.get("language", "en-US"), user.get("message_type", "default")
