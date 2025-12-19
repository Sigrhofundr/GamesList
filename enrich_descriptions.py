import json
import os
import time
import urllib.request
import urllib.parse
import re
from html.parser import HTMLParser

# Steam API endpoints
SEARCH_URL = "https://store.steampowered.com/api/storesearch/?term={term}&l=english&cc=US"
DETAILS_URL = "https://store.steampowered.com/api/appdetails?appids={appid}&l=english&cc=US"

class HTMLStripper(HTMLParser):
    """Helper to strip HTML tags from text."""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    
    def handle_data(self, d):
        self.text.append(d)
    
    def get_data(self):
        return ''.join(self.text)

def strip_html(html):
    """Remove HTML tags from string."""
    s = HTMLStripper()
    s.feed(html)
    return s.get_data()

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

def truncate_description(text, max_sentences=2):
    """Truncate description to a maximum of 2 sentences."""
    if not text:
        return ""
    
    # Remove extra whitespace and newlines
    text = ' '.join(text.split())
    
    # Split by sentence endings (., !, ?)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Take only the first max_sentences
    truncated = ' '.join(sentences[:max_sentences])
    
    # If text was truncated and doesn't end with punctuation, add ellipsis
    if len(sentences) > max_sentences and not truncated.endswith(('.', '!', '?')):
        truncated += '...'
    
    return truncated

def get_steam_description(title):
    """Get short description from Steam API."""
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
    
    # Try to get short_description first (it's already brief)
    description = game_data.get('short_description', '')
    
    # If short_description is empty or too long, try detailed_description
    if not description or len(description) > 300:
        detailed = game_data.get('detailed_description', '')
        if detailed:
            # Strip HTML tags
            description = strip_html(detailed)
            # Truncate to 2 sentences
            description = truncate_description(description, max_sentences=2)
    
    # Final cleanup
    if description:
        description = description.strip()
        # Ensure it's not too long (max 250 chars for safety)
        if len(description) > 250:
            description = description[:247] + '...'
    
    return description if description else None

def main():
    # Use the script's directory as base
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'merged_games.json')
    
    games = load_json(json_path)
    if not games:
        print("No merged_games.json found to enrich.")
        return

    print("Starting description enrichment process... (Press Ctrl+C to stop, progress is saved)")
    print("Fetching brief descriptions from Steam API (English, max 2 sentences)\n")
    
    count_updated = 0
    count_skipped = 0
    count_failed = 0
    
    try:
        for i, game in enumerate(games):
            current_description = game.get('description', '')
            
            # Skip if already has description
            if current_description and current_description.strip():
                count_skipped += 1
                continue
            
            print(f"[{i+1}/{len(games)}] Searching description for: {game['title']}...")
            
            description = get_steam_description(game['title'])
            
            if description:
                game['description'] = description
                count_updated += 1
                print(f"  ✓ Found: {description[:80]}{'...' if len(description) > 80 else ''}")
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
        print(f"  ⏭️  Skipped (already had description): {count_skipped}")
        print(f"  ❌ Not found/Failed: {count_failed}")
        print(f"{'='*60}")
        print(f"Files saved to {base_dir}")

if __name__ == "__main__":
    main()
