"""
Script to add new fields (to_play, to_play_order, description, release_date) to existing games in MongoDB.
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27019")
DB_NAME = os.getenv("MONGO_DB_NAME", "games_library")
COLLECTION_NAME = "games"

async def update_games():
    print(f"Connecting to MongoDB at {MONGO_URL}...")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Add new fields to all existing games that don't have them
    result = await collection.update_many(
        {},
        {
            "$set": {
                "to_play": False,
                "to_play_order": None,
                "description": None,
                "release_date": None
            }
        }
    )
    
    print(f"Updated {result.modified_count} documents with new fields.")
    print("✅ Migration complete!")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(update_games())
