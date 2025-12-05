# Personal Game Library Manager

A local, serverless web application to organize and view your game collection from multiple sources (Steam, Epic Games, GOG, Amazon).

## Features
-   **Unified Library**: Merges games from multiple JSON sources into a single view.
-   **Enriched Data**: Automatically fetches missing genres via Steam API.
-   **Local & Portable**: Runs directly in the browser (`index.html`), no backend server required.
-   **Persistance**: Preserves manual edits (Notes, Played status, Ratings) across library updates.
-   **Advanced UI**:
    -   Dark mode with modern gradients and animations.
    -   Smart filtering (Platform, Genre, Played/Unplayed).
    -   **Edit Mode**: Modify game details, ratings (0-100), and genres via a dedicated modal.
    -   **Rating System**: Visual color-coded badges and slider input.

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
│   └── amazon_library.json
└── README.md               # This file
```

## How to Update Your Library

### 1. Export Data
First, obtain your game library data in JSON format.
-   **Steam**: Use [this API endpoint](https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=YOUR_API_KEY&steamid=YOUR_STEAM_ID&include_appinfo=1&format=json).
    -   Get your Steam ID from [steamid.io](https://steamid.io).
    -   Get an API Key from [Steam Community](https://steamcommunity.com/dev/apikey).
-   **Epic, GOG, Amazon**: Export JSON files using **[Heroic Games Launcher](https://heroicgameslauncher.com/)**.

### 2. Place Files
Move your exported JSON files into the `sources/` folder:
-   `sources/steam_library.json`
-   `sources/epic_library.json`
-   `sources/gog_library.json`
-   `sources/amazon_library.json`

### 3. Run Scripts
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

## Credits & API
-   **Steam API**: Used for fetching game usage data and genre information.
-   **Heroic Games Launcher**: Used for exporting libraries from other platforms.
