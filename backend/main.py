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
    platforms: List[str] = []
    genres: List[str] = []
    notes: Optional[str] = ""
    played: bool = False
    rating: Optional[int] = None
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
    deleted: Optional[bool] = None

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

@app.get("/games", response_model=List[GameModel], tags=["Games"])
async def list_games(
    search: Optional[str] = None,
    platform: Optional[str] = None,
    genre: Optional[str] = None,
    played: Optional[bool] = None,
    limit: int = 1000
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

    games_cursor = app.mongodb[COLLECTION_NAME].find(query).limit(limit)
    games = await games_cursor.to_list(length=limit)
    return games

@app.post("/games", response_model=GameModel, tags=["Games"])
async def create_game(game: GameModel):
    new_game = game.model_dump(by_alias=True, exclude=["id"])
    result = await app.mongodb[COLLECTION_NAME].insert_one(new_game)
    created_game = await app.mongodb[COLLECTION_NAME].find_one({"_id": result.inserted_id})
    return created_game

@app.put("/games/{id}", response_model=GameModel, tags=["Games"])
async def update_game(id: str, game_update: UpdateGameModel):
    update_data = {k: v for k, v in game_update.model_dump().items() if v is not None}
    
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

