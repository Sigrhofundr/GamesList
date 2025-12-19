from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, BeforeValidator
from typing import List, Optional, Annotated
import os
from bson import ObjectId

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for now (dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Config
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "games_library")
COLLECTION_NAME = "games"

# Models
# Helper to handle ObjectId as string
PyObjectId = Annotated[str, BeforeValidator(str)]

class GameModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    title: str
    custom_title: Optional[str] = None
    platforms: List[str] = []  # Stores/Providers: Steam, EA, Epic, etc.
    device: List[str] = ["PC"]  # Gaming systems: PC, PS3, Xbox, etc.
    genres: List[str] = []
    notes: Optional[str] = ""
    played: bool = False
    rating: Optional[int] = None
    is_dlc: bool = False  # Indicates if this is DLC/Expansion content
    to_play: bool = False  # Indicates if this is in the "to play" list
    to_play_order: Optional[int] = None  # Order in the "to play" list
    description: Optional[str] = None  # Game description
    release_date: Optional[str] = None  # Game release date
    deleted: Optional[bool] = False

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "title": "Super Mario Bros",
                "platforms": ["Nintendo"],
                "genres": ["Platformer"],
                "played": True,
                "rating": 90
            }
        }

class UpdateGameModel(BaseModel):
    title: Optional[str] = None
    custom_title: Optional[str] = None
    platforms: Optional[List[str]] = None
    genres: Optional[List[str]] = None
    notes: Optional[str] = None
    played: Optional[bool] = None
    rating: Optional[int] = None
    to_play: Optional[bool] = None
    to_play_order: Optional[int] = None
    description: Optional[str] = None
    release_date: Optional[str] = None
    deleted: Optional[bool] = None

class PaginatedGameResponse(BaseModel):
    items: List[GameModel]
    total: int
    skip: int
    limit: int

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(MONGO_URL)
    app.mongodb = app.mongodb_client[DB_NAME]

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

# Routes

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "GamesList API is running"}

@app.get("/games", response_model=PaginatedGameResponse, tags=["Games"])
async def list_games(
    search: Optional[str] = None,
    platform: Optional[str] = None,
    genre: Optional[str] = None,
    played: Optional[bool] = None,
    include_dlc: bool = False,
    skip: int = 0,
    limit: int = 100
):
    query = {"deleted": {"$ne": True}}

    if search:
        # Case insensitive search on title or custom_title
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"custom_title": {"$regex": search, "$options": "i"}}
        ]
    
    if platform and platform != "all":
        query["platforms"] = platform
    
    if genre and genre != "all":
        query["genres"] = genre
        
    if played is not None:
        query["played"] = played
    
    # By default, exclude DLC unless explicitly requested
    if not include_dlc:
        query["is_dlc"] = {"$ne": True}

    total = await app.mongodb[COLLECTION_NAME].count_documents(query)
    games_cursor = app.mongodb[COLLECTION_NAME].find(query).skip(skip).limit(limit)
    games = await games_cursor.to_list(length=limit)
    
    return {
        "items": games,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@app.post("/games", response_model=GameModel, tags=["Games"])
async def create_game(game: GameModel):
    new_game = game.model_dump(by_alias=True, exclude=["id"])
    result = await app.mongodb[COLLECTION_NAME].insert_one(new_game)
    created_game = await app.mongodb[COLLECTION_NAME].find_one({"_id": result.inserted_id})
    return created_game

@app.put("/games/{id}", response_model=GameModel, tags=["Games"])
async def update_game(id: str, game_update: UpdateGameModel):
    # Use exclude_unset to distinguish between "missing" (do not update) and "null" (update to None)
    update_data = game_update.model_dump(exclude_unset=True)
    
    if len(update_data) >= 1:
        update_result = await app.mongodb[COLLECTION_NAME].update_one(
            {"_id": ObjectId(id)}, {"$set": update_data}
        )
        if update_result.modified_count == 0:
            existing = await app.mongodb[COLLECTION_NAME].find_one({"_id": ObjectId(id)})
            if not existing:
                raise HTTPException(status_code=404, detail=f"Game {id} not found")
    
    if existing := await app.mongodb[COLLECTION_NAME].find_one({"_id": ObjectId(id)}):
        return existing
        
    raise HTTPException(status_code=404, detail=f"Game {id} not found")

@app.delete("/games/{id}", tags=["Games"])
async def delete_game(id: str):
    # Soft delete
    update_result = await app.mongodb[COLLECTION_NAME].update_one(
        {"_id": ObjectId(id)}, {"$set": {"deleted": True}}
    )
    if update_result.modified_count == 1:
        return {"message": "Game deleted"}
        
    raise HTTPException(status_code=404, detail=f"Game {id} not found")

@app.get("/games/random", response_model=GameModel, tags=["Games"])
async def get_random_game(
    search: Optional[str] = None,
    platform: Optional[str] = None,
    genre: Optional[str] = None,
    played: Optional[bool] = None,
):
    query = {"deleted": {"$ne": True}}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"custom_title": {"$regex": search, "$options": "i"}}
        ]
    if platform and platform != "all":
        query["platforms"] = platform
    if genre and genre != "all":
        query["genres"] = genre
    if played is not None:
        query["played"] = played

    # Use aggregation to sample 1 random document matches the query
    pipeline = [
        {"$match": query},
        {"$sample": {"size": 1}}
    ]
    
    cursor = app.mongodb[COLLECTION_NAME].aggregate(pipeline)
    result = await cursor.to_list(length=1)
    
    if result:
        return result[0]
    
    raise HTTPException(status_code=404, detail="No games found matching criteria")

@app.get("/stats", tags=["Games"])
async def get_stats():
    # Pipeline to count total, played, platforms, genres
    pipeline = [
        {"$match": {"deleted": {"$ne": True}}},
        {"$facet": {
            "total": [{"$count": "count"}],
            "played": [{"$match": {"played": True}}, {"$count": "count"}],
            "platforms": [
                {"$unwind": "$platforms"},
                {"$group": {"_id": "$platforms", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ],
            "genres": [
                {"$unwind": "$genres"},
                {"$group": {"_id": "$genres", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 15} # Top 15 genres
            ]
        }}
    ]
    
    cursor = app.mongodb[COLLECTION_NAME].aggregate(pipeline)
    result = await cursor.to_list(length=1)
    
    # Process result safely
    stats = result[0]
    
    return {
        "total": stats["total"][0]["count"] if stats["total"] else 0,
        "played_count": stats["played"][0]["count"] if stats["played"] else 0,
        "platforms": {item["_id"]: item["count"] for item in stats["platforms"]},
        "genres": {item["_id"]: item["count"] for item in stats["genres"]}
    }

@app.get("/games/to-play", response_model=List[GameModel], tags=["Games"])
async def get_to_play_list():
    """Get all games marked as 'to play', ordered by to_play_order."""
    query = {
        "deleted": {"$ne": True},
        "to_play": True
    }
    
    cursor = app.mongodb[COLLECTION_NAME].find(query).sort("to_play_order", 1)
    games = await cursor.to_list(length=1000)
    return games

@app.put("/games/{game_id}/to-play", response_model=GameModel, tags=["Games"])
async def toggle_to_play(game_id: str, to_play: bool = Body(...)):
    """Toggle the 'to play' status of a game."""
    try:
        object_id = ObjectId(game_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid game ID")
    
    update_data = {"to_play": to_play}
    
    # If adding to to_play list, set order to end
    if to_play:
        # Find the highest to_play_order
        highest = await app.mongodb[COLLECTION_NAME].find_one(
            {"to_play": True, "deleted": {"$ne": True}},
            sort=[("to_play_order", -1)]
        )
        new_order = (highest.get("to_play_order", 0) + 1) if highest else 1
        update_data["to_play_order"] = new_order
    else:
        # If removing from to_play list, clear the order
        update_data["to_play_order"] = None
    
    result = await app.mongodb[COLLECTION_NAME].find_one_and_update(
        {"_id": object_id},
        {"$set": update_data},
        return_document=True
    )
    
    if result:
        return result
    raise HTTPException(status_code=404, detail="Game not found")

@app.put("/games/to-play/reorder", tags=["Games"])
async def reorder_to_play_list(game_ids: List[str] = Body(...)):
    """Reorder the 'to play' list. Accepts an array of game IDs in the desired order."""
    for index, game_id in enumerate(game_ids, start=1):
        try:
            object_id = ObjectId(game_id)
            await app.mongodb[COLLECTION_NAME].update_one(
                {"_id": object_id},
                {"$set": {"to_play_order": index}}
            )
        except:
            continue  # Skip invalid IDs
    
    return {"message": "To play list reordered successfully"}
