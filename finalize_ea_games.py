import json
import os

def manual_corrections():
    """Correzioni manuali dei titoli EA"""
    return {
        # Titoli abbreviati da espandere
        "NFS Heat": "Need for Speed Heat",
        
        # Rimuovi duplicati
        "Mass Effect 2": "Mass Effect 2",
        "Mass Effect 2 (2010) Edition": None,  # Duplicato, rimuovi
        
        # Rimuovi elementi non-giochi
        "Dragon Age 2 Unlock - Ser Isaac's Armor - PC/Mac - WW": None,
        "Dragon Age 2 Unlock - Staff of Parthalan - PC/Mac - WW": None,
        "Mass Effect 2 DLC - Alternate Appearance Pack 1": None,  # È un DLC
        
        # Normalizza titoli con suffissi strani
        "Battlefield 1 - Twitch Prime Gaming": "Battlefield 1",
        "Battlefield V - Twitch Prime Gaming": "Battlefield V",
        "Knockout City - Twitch Prime Gaming": "Knockout City",
        "Madden 2022 Prime Gaming": "Madden NFL 22",
        "Plants VS Zombies Battle For Neighborville - Prime Gaming": "Plants vs. Zombies: Battle for Neighborville",
        "Mass Effect Legendary Edition - Twitch Prime Gaming": None,  # Duplicato
        "Rocket Arena (WEST EU)": "Rocket Arena",
        
        # Dragon Age
        "Dragon Age Inquisition - Jaws Of Hakkon": None,  # È DLC
        "Dragon Age Inquisition - Spoils Of The Qunari (IP3)": None,  # È DLC
        "Dragon Age Inquisition - The Descent": None,  # È DLC
        "Dragon Age Inquisition - Trespasser": None,  # È DLC
        "Dragon Age Inquisition: The Black Emporium (IP 1)": None,  # È DLC
        "Dragon Age Origins - Blood Dragon Armor for DAO": None,  # È DLC
        "Dragon Age Origins - Collector's Edition Bonus Items": None,  # È contenuto bonus
        "Dragon Age: Inquisition": "Dragon Age: Inquisition",
        "Dragon Age Origins": "Dragon Age: Origins",
        
        # Battlefield
        "Battlefield 1 In the Name of the Tsar": None,  # È DLC
        "Battlefield 3": "Battlefield 3",
        
        # Dead Space
        "Dead Space": "Dead Space",
        
        # SimCity
        "SimCity": "SimCity (2013)",
        "SimCity 2000 Special Edition": "SimCity 2000",
    }

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, 'sources', 'ea_library_cleaned.json')
    output_file = os.path.join(base_dir, 'sources', 'ea_library.json')
    
    # Carica i dati bonificati
    with open(input_file, 'r', encoding='utf-8') as f:
        games = json.load(f)
    
    corrections = manual_corrections()
    
    # Applica le correzioni
    corrected_games = []
    removed_count = 0
    corrected_count = 0
    
    for game in games:
        title = game['title']
        
        if title in corrections:
            new_title = corrections[title]
            if new_title is None:
                # Rimuovi questo gioco
                removed_count += 1
                print(f"❌ Rimosso: {title}")
                continue
            else:
                # Correggi il titolo
                game['title'] = new_title
                corrected_count += 1
                print(f"✏️  Corretto: {title} → {new_title}")
        
        corrected_games.append(game)
    
    # Rimuovi duplicati dopo le correzioni
    seen = set()
    final_games = []
    duplicates = 0
    
    for game in corrected_games:
        if game['title'] not in seen:
            seen.add(game['title'])
            final_games.append(game)
        else:
            duplicates += 1
            print(f"🔄 Duplicato rimosso: {game['title']}")
    
    # Salva il risultato finale
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_games, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'=' * 80}")
    print(f"✅ RIEPILOGO:")
    print(f"{'=' * 80}")
    print(f"  📊 Giochi originali:      {len(games)}")
    print(f"  ❌ Rimossi:              {removed_count}")
    print(f"  ✏️  Corretti:             {corrected_count}")
    print(f"  🔄 Duplicati eliminati:  {duplicates}")
    print(f"  ✅ Giochi finali:        {len(final_games)}")
    print(f"\n  💾 Salvato in: {output_file}\n")
    
    print("🎮 LISTA FINALE DEI GIOCHI EA:")
    print("=" * 80)
    for i, game in enumerate(sorted(final_games, key=lambda x: x['title']), 1):
        print(f"  {i:2d}. {game['title']}")

if __name__ == "__main__":
    main()
