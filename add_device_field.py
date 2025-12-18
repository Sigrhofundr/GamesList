import json
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    merged_file = os.path.join(base_dir, 'merged_games.json')
    
    # Carica i giochi
    with open(merged_file, 'r', encoding='utf-8') as f:
        games = json.load(f)
    
    print(f"📊 Aggiornamento di {len(games)} giochi...")
    
    updated_count = 0
    for game in games:
        if 'device' not in game:
            game['device'] = ['PC']
            updated_count += 1
    
    # Salva il file aggiornato
    with open(merged_file, 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=2, ensure_ascii=False)
    
    print(f"✅ {updated_count} giochi aggiornati con device=['PC']")
    print(f"💾 File salvato: {merged_file}")

if __name__ == "__main__":
    main()
