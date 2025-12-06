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
    -   **Smart Filtering**: Filter by Platform, Genre, and Played/Not Played status.
    -   **Random Picker**: "Random Game" button helper to decide what to play next.
    -   **Edit Mode**: Comprehensive editing via modal (Rating 0-100, Notes, Genres).
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
│   └── amazon_library.json
├── logos/                  # Directory containing platform images (png)
└── README.md               # This file
```

## How to Use the Web Viewer

1.  **Open `index.html`** in any modern web browser.
2.  **Browsing**: Use the search bar or dropdown filters to find games.
3.  **Editing**:
    -   Click the **Pencil Icon** on any card to edit details.
    -   **Rating**: Set a score from 0-100 using the slider or input box.
    -   **Genres**: Add or remove genres.
    -   **Notes**: Add personal notes.
    -   **Status**: Toggle "Played" status directly from the card.
4.  **Statistics**: Click the **Statistics** button to view charts of your library's composition. You can toggle between "Entire Library" and "Current Filter" to see specific stats.
5.  **Saving Changes**: Click **Export JSON** to download the updated `merged_games.json`. **Overwrite the original file** in your project folder to save your changes permanently.

## How to Update Your Library

### 1. Configure the Project
1.  **Environment Setup**:
    -   Copy `.env.example` (if provided) or create a `.env` file in the root directory.
    -   Define the filenames of your source JSON files in `.env`:
        ```ini
        AMAZON_LIBRARY=my_amazon_games.json
        EPIC_LIBRARY=my_epic_library.json
        GOG_LIBRARY=my_gog_games.json
        STEAM_LIBRARY=steam_output.json
        ```
    -   *Note: The script defaults to `amazon_library.json` etc., if no `.env` is found.*

### 2. Export Data
First, obtain your game library data in JSON format.
-   **Steam**: Use [this API endpoint](https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=YOUR_API_KEY&steamid=YOUR_STEAM_ID&include_appinfo=1&format=json).
    -   Get your Steam ID from [steamid.io](https://steamid.io).
    -   Get an API Key from [Steam Community](https://steamcommunity.com/dev/apikey).
-   **Epic, GOG, Amazon**: Export JSON files using **[Heroic Games Launcher](https://heroicgameslauncher.com/)**.

### 3. Place Files
Move your exported JSON files into the `sources/` folder. Ensure their names match what you defined in `.env`.

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

## Credits & API
-   **Steam API**: Used for fetching game usage data and genre information.
-   **Heroic Games Launcher**: Used for exporting libraries from other platforms. 
