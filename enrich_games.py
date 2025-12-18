import json
import os
import time
import urllib.request
import urllib.parse
import sys

# Steam API endpoints
SEARCH_URL = "https://store.steampowered.com/api/storesearch/?term={term}&l=english&cc=US"
DETAILS_URL = "https://store.steampowered.com/api/appdetails?appids={appid}&l=english&cc=US"

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data, base_dir):
    # Save JSON
    json_path = os.path.join(base_dir, 'merged_games.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Save JS
    js_path = os.path.join(base_dir, 'merged_games.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        f.write(f"window.gamesData = {json_str};")

def make_request(url):
    """Makes a request with proper headers to avoid 403/blocking."""
    req = urllib.request.Request(
        url, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.load(response)
    except Exception as e:
        print(f"Error requesting {url}: {e}")
        return None

def get_steam_genres(title):
    # Search for the game
    encoded_title = urllib.parse.quote(title)
    search_data = make_request(SEARCH_URL.format(term=encoded_title))
    
    if not search_data or 'items' not in search_data or not search_data['items']:
        return None
    
    # Get the first result's AppID
    appid = search_data['items'][0]['id']
    
    # Get details
    details_data = make_request(DETAILS_URL.format(appid=appid))
    
    if not details_data or str(appid) not in details_data or not details_data[str(appid)]['success']:
        return None
        
    game_data = details_data[str(appid)]['data']
    
    genres = []
    if 'genres' in game_data:
        genres = [g['description'] for g in game_data['genres']]
        
    return genres

def main():
    # Use the script's directory as base (works on Windows, Linux, macOS)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'merged_games.json')
    
    games = load_json(json_path)
    if not games:
        print("No merged_games.json found to enrich.")
        return

    print("Starting enrichment process... (Press Ctrl+C to stop, progress is saved)")
    
    count_updated = 0
    count_skipped = 0
    count_failed = 0
    
    try:
        for i, game in enumerate(games):
            # Only process games with no genres OR matching 'Sconosciuto' (if we wanted to retry, but user said skip if Sconosciuto is present as it's a failed attempts marker)
            # Actually user said: "questi sconosciuti verranno saltati dalla ricerca online"
            current_genres = game.get('genres', [])
            
            # If genres is empty OR contains "Sconosciuto", we might think to enrich.
            # But the requirement is: "proprio all'interno del file merged_games.json, voglio che tu metta 'Sconosciuto'... In questo modo... eseguendo lo script questi sconosciuti verranno saltati dalla ricerca online."
            # So if "Sconosciuto" is in genres, SKIP IT.
            
            should_enrich = False
            if not current_genres:
                should_enrich = True
            elif "Sconosciuto" in current_genres:
                should_enrich = False # Skip explicitly as requested
            
            # (Note: originally we enriched if empty. normalize_games now fills empty with Sconosciuto. So enrich_games needs to NOT enrich if Sconosciuto is present.)
            
            if should_enrich:
                print(f"[{i+1}/{len(games)}] Searching genre for: {game['title']}...")
                
                genres = get_steam_genres(game['title'])
                
                if genres:
                    game['genres'] = genres
                    count_updated += 1
                    print(f"  -> Found: {', '.join(genres)}")
                else:
                    count_failed += 1
                    game['genres'] = ["Sconosciuto"] # Mark as unknown so we don't retry forever
                    print("  -> Not found (marked Sconosciuto)")
                
                # Rate limit: Steam is sensitive. 1.5s delay.
                time.sleep(1.5)
                
                # Save every 10 updates to be safe
                if count_updated % 10 == 0 and count_updated > 0:
                     save_data(games, base_dir)
            else:
                count_skipped += 1
                
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    finally:
        save_data(games, base_dir)
        print(f"\nSummary:")
        print(f"  Updated: {count_updated}")
        print(f"  Skipped (already had genres): {count_skipped}")
        print(f"  Not found/Failed: {count_failed}")
        print(f"Files saved to {base_dir}")

if __name__ == "__main__":
    main()
