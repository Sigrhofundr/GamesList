# Personal Game Library Manager

A local, serverless web application to organize and view your game collection from multiple sources (Steam, Epic Games, GOG, Amazon).

## Features
-   **Unified Library**: Merges games from multiple JSON sources into a single view.
-   **Enriched Data**: Automatically fetches missing genres via Steam API.
-   **Local & Portable**: Runs directly in the browser (`index.html`), no backend server required.
-   **Persistance**: Preserves manual edits (Notes, Played status, Ratings) across library updates.
-   **Advanced UI**:
    -   Dark mode with modern gradients and animations.
    -   **Visual Stats**: Statistics Dashboard showing distributions for Genres, Platforms, Status, and Ratings.
-   **Smart Filtering**: Filter by Platform (including Microsoft), Genre, and Played/Not Played status.
-   **Full CRUD**: Add, Edit, and Delete games directly from the interface.
-   **Game Form**: Comprehensive modal to edit Title, Platform, Genres, Rating (0-100), Notes, and Status.
-   **Random Picker**: "Random Game" button helper to decide what to play next.
-   **To Play List**: Mark games as "to play" and create a prioritized list with drag-and-drop reordering.
-   **Game Details**: Add custom descriptions and release dates for each game.
-   **DLC Management**: Automatically detect and filter DLC/expansion content (hidden by default).
-   **Rich Visuals**: Local, high-quality platform logos and color-coded rating badges.

## Project Structure
```
/GamesList
├── index.html              # Main application (open this in browser)
├── normalize_games.py      # Script to ingest and merge source JSONs
├── enrich_games.py         # Script to fetch missing genres from Steam
├── merged_games.json       # The master database file (generated)
├── merged_games.js         # The JS version for local browser access (generated)
├── sources/                # Directory for your source library files
│   ├── steam_library.json
│   ├── epic_library.json
│   ├── gog_library.json
│   ├── amazon_library.json
│   └── microsoft_library.json
├── logos/                  # Directory containing platform images (png)
└── README.md               # This file
```

## How to Use the Web Viewer

1.  **Open `index.html`** in any modern web browser.
2.  **Browsing**: Use the search bar or dropdown filters to find games.
3.  **Adding Games**: Click the **+ FAB Button** (bottom-right) to manually add a new game.
4.  **Editing**:
    -   Click the **Pencil Icon** on any card to open the Edit form.
    -   **Full Control**: You can now change proper titles, platforms, genres, ratings, and even DELETE games.
5.  **Statistics**: Click the **Statistics** button to view charts of your library's composition. You can toggle between "Entire Library" and "Current Filter" to see specific stats.
6.  **Saving Changes**: Click **Export JSON** to download the updated `merged_games.json`. **Overwrite the original file** in your project folder to save your changes permanently.
    > [!IMPORTANT]
    > **After overwriting the JSON file**, you must run `python3 normalize_games.py` again! This step is crucial to update the `merged_games.js` file used by the browser and to align your edits with the source data.

## Docker Deployment (Recommended)

### Quick Start
1. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env if needed (default values should work)
   ```

2. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

3. **Access the Application**:
   - Frontend: http://localhost:8090
   - Backend API: http://localhost:5000
   - MongoDB: localhost:27019

### Port Configuration
The default ports are:
- MongoDB: 27019 (mapped to avoid conflicts with local MongoDB instances)
- Backend: 5000
- Frontend: 8090

If you need to change these ports, edit the [docker-compose.yml](docker-compose.yml) file.

## How to Update Your Library

### 1. Configure the Project
1.  **Environment Setup**:
    -   Copy `.env.example` (if provided) or create a `.env` file in the root directory.
    -   Define the filenames of your source JSON files in `.env` (optional, script has defaults):
        ```ini
        AMAZON_LIBRARY=my_amazon_games.json
        EPIC_LIBRARY=my_epic_library.json
        GOG_LIBRARY=my_gog_games.json
        STEAM_LIBRARY=steam_output.json
        MICROSOFT_LIBRARY=xbox_games.json
        ```
    -   *Note: The script defaults to `amazon_library.json` etc., if no `.env` is found.*

### 2. Export Data
First, obtain your game library data in JSON format.
-   **Steam**: Use [this API endpoint](https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=YOUR_API_KEY&steamid=YOUR_STEAM_ID&include_appinfo=1&format=json).
    -   Get your Steam ID from [steamid.io](https://steamid.io).
    -   Get an API Key from [Steam Community](https://steamcommunity.com/dev/apikey).
-   **Epic, GOG, Amazon**: Export JSON files using **[Heroic Games Launcher](https://heroicgameslauncher.com/)**.
-   **Microsoft**: Add your `microsoft_library.json` (format: `{"games": ["Title1", "Title2"]}`).

### 3. Place Files
Move your exported JSON files into the `sources/` folder.

### 4. Run Scripts
Open a terminal in the project folder and run:


1.  **Normalize & Merge**:
    ```bash
    python3 normalize_games.py
    ```
    *This creates `merged_games.json`, preserving any manual edits you've made nicely.*

2.  **Enrich (Optional but Recommended)**:
    ```bash
    python3 enrich_games.py
    ```
    *This searches Steam for missing genres. It skips games marked as "Unknown" to save time.*

3.  **Done!** Open `index.html` to view your library.
## Python Scripts Reference

### Core Scripts

#### `normalize_games.py`
Main script that merges game libraries from multiple sources into a unified database.
- **Purpose**: Consolidates games from Steam, Epic, GOG, Amazon, Microsoft, and EA into a single JSON file
- **Features**:
  - Normalizes game titles (removes special characters, converts to lowercase)
  - Preserves manual edits (custom titles, notes, ratings, played status)
  - Handles duplicate detection across platforms
  - Adds `device` field (PC, PS3, PS4, PS5, Xbox, Switch)
  - Generates both `merged_games.json` (for backend) and `merged_games.js` (for standalone HTML viewer)
- **Usage**: `python normalize_games.py`
- **Input**: JSON files in `sources/` directory
- **Output**: `merged_games.json`, `merged_games.js`

#### `enrich_games.py`
Enriches game data by fetching missing genres from the Steam API.
- **Purpose**: Automatically populate genre information for games without genres
- **Features**:
  - Searches Steam Store API by game title
  - Adds genre tags to games
  - Skips games already marked as "Sconosciuto" (Unknown)
  - Rate-limited to avoid API throttling (1.5s between requests)
  - Auto-saves progress every 10 games
  - Safe interruption with Ctrl+C
- **Usage**: `python enrich_games.py`
- **Input**: `merged_games.json`
- **Output**: Updated `merged_games.json` with enriched genres

#### `enrich_descriptions.py`
Fetches short descriptions for games from the Steam API.
- **Purpose**: Add brief game descriptions (max 2 sentences, 250 characters)
- **Features**:
  - Prioritizes Steam's `short_description` field
  - Falls back to `detailed_description` with HTML tag removal
  - Truncates to 2 sentences maximum
  - Skips "Coming soon" games without descriptions
  - Rate-limited (1.5s between requests)
  - Auto-saves progress every 10 games
  - Tracks statistics (updated, skipped, not found)
- **Usage**: `python enrich_descriptions.py`
- **Input**: `merged_games.json`
- **Output**: Updated `merged_games.json` with description field populated
- **Example Output**: 
  ```
  Processed 1652 games
  Updated: 1331, Skipped: 0, Not found: 321
  ```

#### `enrich_release_dates.py`
Fetches and normalizes release dates from the Steam API.
- **Purpose**: Add release date information in ISO format (YYYY-MM-DD)
- **Features**:
  - Parses multiple Steam date formats ("10 Apr, 2023", "Apr 10, 2023", "2023")
  - Converts all dates to ISO format (YYYY-MM-DD)
  - Handles year-only dates (defaults to YYYY-01-01)
  - Skips "Coming soon" and "TBA" entries
  - Rate-limited (1.5s between requests)
  - Auto-saves progress every 10 games
  - Tracks statistics (updated, skipped, not found)
- **Usage**: `python enrich_release_dates.py`
- **Input**: `merged_games.json`
- **Output**: Updated `merged_games.json` with release_date field populated
- **Date Format Examples**:
  - "10 Apr, 2023" → "2023-04-10"
  - "2023" → "2023-01-01"

#### `enrich_all.py`
Unified enrichment script that runs all enrichment functions in sequence.
- **Purpose**: One-command enrichment for genres, descriptions, and release dates
- **Features**:
  - Calls `enrich_games()`, `enrich_descriptions()`, and `enrich_release_dates()` in a single pass
  - Comprehensive statistics for all three enrichment types
  - Auto-saves progress every 10 games
  - Rate-limited across all enrichment types
  - Single progress bar for all operations
- **Usage**: `python enrich_all.py`
- **Input**: `merged_games.json`
- **Output**: Updated `merged_games.json` with all enrichable fields populated
- **Recommended**: Use this script instead of running each enrichment script separately
- **Example Output**:
  ```
  === Enrichment Complete ===
  Genres - Updated: 245, Skipped: 1200, Not found: 207
  Descriptions - Updated: 1331, Skipped: 0, Not found: 321
  Release Dates - Updated: 1425, Skipped: 50, Not found: 177
  ```

### Backend Scripts

#### `backend/main.py`
FastAPI backend server providing REST API for game management.
- **Purpose**: Provides CRUD operations for games with MongoDB persistence
- **Endpoints**:
  - `GET /games` - List all games with filters
  - `POST /games` - Create new game
  - `PUT /games/{id}` - Update game
  - `DELETE /games/{id}` - Delete game
  - `GET /stats` - Library statistics
- **Usage**: Runs automatically via Docker Compose (port 5000)

#### `backend/migrate_to_mongo.py`
Migrates data from JSON file to MongoDB database.
- **Purpose**: Synchronize `merged_games.json` with MongoDB
- **Features**:
  - Drops existing collection for clean migration
  - Validates connection to MongoDB
  - Preserves all game data and metadata
- **Usage**: `python backend/migrate_to_mongo.py`
- **Requirements**: MongoDB running on port 27019

### Utility Scripts

#### `find_unknowns.py`
Identifies games with unknown or missing genre information.
- **Purpose**: Generate a report of games that need genre enrichment
- **Usage**: `python find_unknowns.py`
- **Output**: `unknowns_result.txt` with list of games missing genres

#### `verify_enrich.py`
Validates the genre enrichment process results.
- **Purpose**: Check which games were successfully enriched with genres
- **Usage**: `python verify_enrich.py`
- **Output**: `verify_result.txt` with enrichment statistics

#### `add_device_field.py`
One-time migration script to add the `device` field to existing games.
- **Purpose**: Updates all games in `merged_games.json` with `device: ["PC"]` field
- **Usage**: `python add_device_field.py` (run once after device field introduction)
- **Note**: This was used for the initial schema migration and may not be needed again

### EA Games Processing Scripts

#### `process_ea_games.py`
Processes EA games CSV export and cleans the data.
- **Purpose**: Parse EA library CSV, remove suffixes, identify DLC vs base games
- **Features**:
  - Removes "-WW", "™", "®" and other suffixes
  - Converts ALL CAPS titles to Title Case
  - Identifies potential DLC entries
- **Usage**: `python process_ea_games.py`
- **Input**: EA CSV export file
- **Output**: `ea_processed.json`

#### `finalize_ea_games.py`
Applies manual corrections to processed EA games.
- **Purpose**: Final cleanup and correction of EA game titles
- **Usage**: `python finalize_ea_games.py`
- **Note**: Currently EA import is disabled pending corrections

#### `remove_ea_games.py`
Removes all EA games from the database.
- **Purpose**: Clean removal of EA platform games
- **Usage**: `python remove_ea_games.py`
- **Note**: Used for rollback after incorrect EA import
## Deployment

For detailed instructions on deploying updates to your Raspberry Pi production environment, see [DEPLOYMENT.md](DEPLOYMENT.md).

Quick deployment workflow:
1. **PC**: Commit and push code changes to GitHub
2. **PC**: Transfer `merged_games.json` via SCP
3. **Raspberry Pi**: Pull code, rebuild containers, migrate database
4. **Verify**: Check logs and test endpoints

## Credits & API
-   **Steam API**: Used for fetching game usage data and genre information.
-   **Heroic Games Launcher**: Used for exporting libraries from other platforms. 
