import json
import os
import re

def load_json(filepath):
    """Loads a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: File not found: {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filepath}")
        return None

def normalize_title(title):
    """
    Normalizes a game title for deduplication.
    Removes special characters, extra spaces, and converts to lowercase.
    """
    if not title:
        return ""
    # Remove TM, R, copyright symbols
    title = re.sub(r'[™®©]', '', title)
    # Remove special chars but keep alphanumeric and spaces
    title = re.sub(r'[^\w\s]', '', title)
    return " ".join(title.lower().split())

def process_amazon(data, games_map):
    """Processes Amazon library data."""
    if not data or 'library' not in data:
        return
    
    for game in data['library']:
        title = game.get('title')
        if not title:
            continue
            
        norm_title = normalize_title(title)
        
        genres = []
        if 'extra' in game and 'genres' in game['extra']:
            genres = game['extra']['genres']
            
        if norm_title not in games_map:
            games_map[norm_title] = {
                'title': title, # Keep the first title found as display title
                'platforms': set(),
                'genres': set(genres)
            }
        
        games_map[norm_title]['platforms'].add('Amazon')
        games_map[norm_title]['genres'].update(genres)

def process_epic(data, games_map):
    """
    Processes Epic library data.
    Epic JSON structure seems to be a list of games, or {library: [...]}.
    Based on file view, it is {library: [...]}.
    """
    if not data:
        return
        
    library = data.get('library', []) if isinstance(data, dict) else data
    
    for game in library:
        title = game.get('title')
        if not title:
            # Fallback to app_name if title is missing, though unlikely
            title = game.get('app_name', 'Unknown')
            
        norm_title = normalize_title(title)
        
        # Epic usually doesn't provide genres in this export, but we check if they exist
        genres = []
        # If there's an 'extra' field with tags/genres? (Check implied they were missing)
        
        if norm_title not in games_map:
             games_map[norm_title] = {
                'title': title,
                'platforms': set(),
                'genres': set(genres)
            }
        
        games_map[norm_title]['platforms'].add('Epic')
        # No genre update for Epic as it lacks them usually

def process_gog(data, games_map):
    """Processes GOG library data."""
    if not data or 'games' not in data:
        return

    for game in data['games']:
        title = game.get('title')
        if not title:
            continue
            
        norm_title = normalize_title(title)
        
        genres = []
        if 'extra' in game and 'genres' in game['extra']:
            genres = game['extra']['genres']
            
        if norm_title not in games_map:
             games_map[norm_title] = {
                'title': title,
                'platforms': set(),
                'genres': set(genres)
            }
        
        games_map[norm_title]['platforms'].add('GOG')
        games_map[norm_title]['genres'].update(genres)

def main():
    base_dir = '/mnt/secondisk/dev/GamesList'
    # Load .env file
    env_path = os.path.join(base_dir, '.env')
    env_vars = {}
    if os.path.exists(env_path):
        print("Loading configuration from .env...")
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Get filenames from env or use defaults/placeholders
    amazon_file = env_vars.get('AMAZON_LIBRARY', 'amazon_library.json')
    epic_file = env_vars.get('EPIC_LIBRARY', 'epic_library.json')
    gog_file = env_vars.get('GOG_LIBRARY', 'gog_library.json')
    steam_file = env_vars.get('STEAM_LIBRARY', 'steam_library.json')

    files = {
        'Amazon': os.path.join(base_dir, 'sources', amazon_file),
        'Epic': os.path.join(base_dir, 'sources', epic_file),
        'GOG': os.path.join(base_dir, 'sources', gog_file)
    }
    
    # Map: normalized_title -> {title, platforms, genres, notes, played}
    games_map = {}
    
    # Load existing merged_games.json to preserve manual edits
    output_path_json = os.path.join(base_dir, 'merged_games.json')
    files_existed = False
    if os.path.exists(output_path_json):
        print("Loading existing merged_games.json to preserve data...")
        existing_data = load_json(output_path_json)
        if existing_data:
            files_existed = True
            for game in existing_data:
                norm_title = normalize_title(game.get('title'))
                if norm_title:
                    games_map[norm_title] = {
                        'title': game.get('title'),
                        'platforms': set(game.get('platforms', [])),
                        'genres': set(game.get('genres', [])),
                        'notes': game.get('notes', ""),
                        'played': game.get('played', False),
                        'rating': game.get('rating', None)
                    }

    print(f"Loading Amazon ({amazon_file})...")
    amazon_data = load_json(files['Amazon'])
    if amazon_data: process_amazon(amazon_data, games_map)
    
    print(f"Loading Epic ({epic_file})...")
    epic_data = load_json(files['Epic'])
    if epic_data: process_epic(epic_data, games_map)
    
    print(f"Loading GOG ({gog_file})...")
    gog_data = load_json(files['GOG'])
    if gog_data: process_gog(gog_data, games_map)
    
    print(f"Loading Steam ({steam_file})...")
    try:
        steam_path = os.path.join(base_dir, 'sources', steam_file)
        if os.path.exists(steam_path):
            steam_data = load_json(steam_path)
            # Steam structure: {'response': {'games': [...]}}
            if steam_data and 'response' in steam_data and 'games' in steam_data['response']:
                steam_games = steam_data['response']['games']
                print(f"Loaded {len(steam_games)} Steam games.")
                for game in steam_games:
                     name = game.get('name')
                     if name:
                         norm_title = normalize_title(name)
                         
                         playtime = game.get('playtime_forever', 0)
                         played =  playtime > 0
                         
                         genres = [] # Steam JSON from user doesn't have genres, strictly for enrichment
                         
                         if norm_title not in games_map:
                             games_map[norm_title] = {
                                 'title': name,
                                 'platforms': set(),
                                 'genres': set(genres),
                                 'notes': "",
                                 'played': played,
                                 'rating': None
                             }
                         else:
                             # If game exists, ensure valid defaults if missing
                             if 'played' not in games_map[norm_title]:
                                 games_map[norm_title]['played'] = False
                             # Update played status: if it was false but steam says played, set true
                             if played:
                                 games_map[norm_title]['played'] = True
                         
                         games_map[norm_title]['platforms'].add('Steam')
                         # Do not add genres (as it is empty list)
            else:
                 print("Steam library structure invalid or empty.")
    except Exception as e:
        print(f"Error loading Steam library: {e}")

    # Convert sets to lists for JSON serialization
    output_list = []
    for game in games_map.values():
        game['platforms'] = sorted(list(game['platforms']))
        
        # Handle Genres
        # Logic change: Do NOT default to Sconosciuto here.
        # Leave empty so enrich_games.py can attempt to find them.
        # Only enrich_games.py should definitively set Sconosciuto if not found.
        # if not game['genres']:
        #    game['genres'] = ["Sconosciuto"]
        
        if len(game['genres']) > 1 and "Sconosciuto" in game['genres']:
             game['genres'].remove("Sconosciuto")
        
        game['genres'] = sorted(list(game['genres']))
            
        # Ensure optional fields exist
        if 'notes' not in game:
            game['notes'] = ""
        if 'played' not in game:
            game['played'] = False
        if 'rating' not in game:
            game['rating'] = None
            
        output_list.append(game)
    
    # Sort by title
    output_list.sort(key=lambda x: x['title'])
    
    with open(output_path_json, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, indent=2, ensure_ascii=False)
        
    # Also export as JS for local viewing without server (CORS bypass)
    output_path_js = os.path.join(base_dir, 'merged_games.js')
    with open(output_path_js, 'w', encoding='utf-8') as f:
        json_str = json.dumps(output_list, indent=2, ensure_ascii=False)
        f.write(f"window.gamesData = {json_str};")

    print(f"Successfully exported {len(output_list)} unique games.")
    print(f"JSON: {output_path_json}")
    print(f"JS (for local viewer): {output_path_js}")

if __name__ == "__main__":
    main()
