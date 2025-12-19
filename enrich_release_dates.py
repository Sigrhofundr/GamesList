import json
import os
import time
import urllib.request
import urllib.parse
from datetime import datetime

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

def parse_steam_date(date_string):
    """
    Convert Steam date format to ISO date (YYYY-MM-DD).
    Steam formats: "10 Apr, 2023", "Apr 10, 2023", "2023", "Q2 2023", "Coming soon"
    """
    if not date_string or date_string.lower() in ['coming soon', 'to be announced', 'tba']:
        return None
    
    # Try common date formats
    formats = [
        "%d %b, %Y",      # 10 Apr, 2023
        "%b %d, %Y",      # Apr 10, 2023
        "%B %d, %Y",      # April 10, 2023
        "%d %B, %Y",      # 10 April, 2023
        "%b %Y",          # Apr 2023
        "%B %Y",          # April 2023
        "%Y"              # 2023
    ]
    
    for fmt in formats:
        try:
            parsed_date = datetime.strptime(date_string.strip(), fmt)
            return parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # If we can't parse it, try to extract just the year
    import re
    year_match = re.search(r'\b(19|20)\d{2}\b', date_string)
    if year_match:
        return f"{year_match.group(0)}-01-01"
    
    return None

def get_steam_release_date(title):
    """Get release date from Steam API."""
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
    
    # Get release date
    release_info = game_data.get('release_date', {})
    
    if release_info.get('coming_soon', False):
        return None  # Skip games not yet released
    
    date_string = release_info.get('date', '')
    return parse_steam_date(date_string)

def main():
    # Use the script's directory as base
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'merged_games.json')
    
    games = load_json(json_path)
    if not games:
        print("No merged_games.json found to enrich.")
        return

    print("Starting release date enrichment process... (Press Ctrl+C to stop, progress is saved)")
    print("Fetching release dates from Steam API\n")
    
    count_updated = 0
    count_skipped = 0
    count_failed = 0
    
    try:
        for i, game in enumerate(games):
            current_date = game.get('release_date', '')
            
            # Skip if already has release date
            if current_date and current_date.strip():
                count_skipped += 1
                continue
            
            print(f"[{i+1}/{len(games)}] Searching release date for: {game['title']}...")
            
            release_date = get_steam_release_date(game['title'])
            
            if release_date:
                game['release_date'] = release_date
                count_updated += 1
                print(f"  ✓ Found: {release_date}")
            else:
                count_failed += 1
                print("  ✗ Not found")
            
            # Rate limit: Steam is sensitive. 1.5s delay.
            time.sleep(1.5)
            
            # Save every 10 updates to be safe
            if (count_updated + count_failed) % 10 == 0 and (count_updated + count_failed) > 0:
                save_data(games, base_dir)
                print(f"  💾 Progress saved ({count_updated} updated so far)")
                
    except KeyboardInterrupt:
        print("\n⚠ Process interrupted by user.")
    finally:
        save_data(games, base_dir)
        print(f"\n{'='*60}")
        print(f"📊 Summary:")
        print(f"  ✅ Updated: {count_updated}")
        print(f"  ⏭️  Skipped (already had release date): {count_skipped}")
        print(f"  ❌ Not found/Failed: {count_failed}")
        print(f"{'='*60}")
        print(f"Files saved to {base_dir}")

if __name__ == "__main__":
    main()
