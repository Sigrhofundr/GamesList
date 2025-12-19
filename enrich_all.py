import json
import os
import sys
import time
from enrich_games import get_steam_genres
from enrich_descriptions import get_steam_description
from enrich_release_dates import get_steam_release_date

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data, base_dir):
    json_path = os.path.join(base_dir, 'merged_games.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    js_path = os.path.join(base_dir, 'merged_games.js')
    with open(js_path, 'w', encoding='utf-8') as f:
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        f.write(f"window.gamesData = {json_str};")

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'merged_games.json')
    
    games = load_json(json_path)
    if not games:
        print("No merged_games.json found to enrich.")
        return

    print("="*70)
    print("🎮 GAME LIBRARY ENRICHMENT - ALL IN ONE")
    print("="*70)
    print("\nThis script will enrich your games with:")
    print("  • Genres (from Steam)")
    print("  • Descriptions (from Steam)")
    print("  • Release Dates (from Steam)")
    print("\nPress Ctrl+C to stop at any time. Progress is saved automatically.\n")
    print("="*70 + "\n")
    
    stats = {
        'genres': {'updated': 0, 'skipped': 0, 'failed': 0},
        'descriptions': {'updated': 0, 'skipped': 0, 'failed': 0},
        'dates': {'updated': 0, 'skipped': 0, 'failed': 0}
    }
    
    try:
        for i, game in enumerate(games):
            print(f"\n[{i+1}/{len(games)}] Processing: {game['title']}")
            
            # Enrich Genres
            current_genres = game.get('genres', [])
            if not current_genres or "Sconosciuto" in current_genres:
                print(f"  🎯 Searching genres...")
                genres = get_steam_genres(game['title'])
                if genres:
                    game['genres'] = genres
                    stats['genres']['updated'] += 1
                    print(f"    ✓ Found: {', '.join(genres)}")
                else:
                    game['genres'] = ["Sconosciuto"]
                    stats['genres']['failed'] += 1
                    print("    ✗ Not found")
            else:
                stats['genres']['skipped'] += 1
                print(f"  ⏭️  Genres: Already set")
            
            # Enrich Description
            current_description = game.get('description', '')
            if not current_description or not current_description.strip():
                print(f"  📝 Searching description...")
                description = get_steam_description(game['title'])
                if description:
                    game['description'] = description
                    stats['descriptions']['updated'] += 1
                    print(f"    ✓ Found: {description[:60]}...")
                else:
                    stats['descriptions']['failed'] += 1
                    print("    ✗ Not found")
            else:
                stats['descriptions']['skipped'] += 1
                print(f"  ⏭️  Description: Already set")
            
            # Enrich Release Date
            current_date = game.get('release_date', '')
            if not current_date or not current_date.strip():
                print(f"  📅 Searching release date...")
                release_date = get_steam_release_date(game['title'])
                if release_date:
                    game['release_date'] = release_date
                    stats['dates']['updated'] += 1
                    print(f"    ✓ Found: {release_date}")
                else:
                    stats['dates']['failed'] += 1
                    print("    ✗ Not found")
            else:
                stats['dates']['skipped'] += 1
                print(f"  ⏭️  Release Date: Already set")
            
            # Rate limit
            time.sleep(1.5)
            
            # Save every 10 games
            if (i + 1) % 10 == 0:
                save_data(games, base_dir)
                print(f"\n  💾 Progress saved (processed {i+1} games)")
                
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user.")
    finally:
        save_data(games, base_dir)
        print(f"\n\n{'='*70}")
        print("📊 FINAL SUMMARY")
        print("="*70)
        print(f"\n🎯 GENRES:")
        print(f"  ✅ Updated: {stats['genres']['updated']}")
        print(f"  ⏭️  Skipped: {stats['genres']['skipped']}")
        print(f"  ❌ Failed: {stats['genres']['failed']}")
        print(f"\n📝 DESCRIPTIONS:")
        print(f"  ✅ Updated: {stats['descriptions']['updated']}")
        print(f"  ⏭️  Skipped: {stats['descriptions']['skipped']}")
        print(f"  ❌ Failed: {stats['descriptions']['failed']}")
        print(f"\n📅 RELEASE DATES:")
        print(f"  ✅ Updated: {stats['dates']['updated']}")
        print(f"  ⏭️  Skipped: {stats['dates']['skipped']}")
        print(f"  ❌ Failed: {stats['dates']['failed']}")
        print(f"\n{'='*70}")
        print(f"Files saved to {base_dir}")

if __name__ == "__main__":
    main()
