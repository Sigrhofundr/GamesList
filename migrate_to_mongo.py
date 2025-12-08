import json
import pymongo
import os
import sys

# Configuration
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "games_library"
COLLECTION_NAME = "games"
JSON_FILE = "merged_games.json"

def migrate():
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found.")
        sys.exit(1)

    print(f"Connecting to MongoDB at {MONGO_URI}...")
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Check connection
        client.server_info()
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Ensure Docker container is running: docker-compose up -d mongodb")
        sys.exit(1)

    print(f"Loading {JSON_FILE}...")
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("Error: JSON root is not a list.")
        sys.exit(1)

    print(f"Found {len(data)} games in JSON.")
    
    # Drop existing to ensure clean state
    collection.drop()
    print("Dropped existing collection.")

    if data:
        result = collection.insert_many(data)
        print(f"Successfully inserted {len(result.inserted_ids)} documents.")
    else:
        print("No data to insert.")

if __name__ == "__main__":
    migrate()
