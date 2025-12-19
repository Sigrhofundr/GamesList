import csv
import re
import os
from collections import defaultdict

def clean_title(title):
    """Pulisce il titolo EA rimuovendo suffissi e normalizzando"""
    original = title
    
    # Rimuovi tutto dopo i comuni pattern EA
    patterns_to_remove = [
        r'\s*-\s*PC\s*-.*$',           # - PC - WW, - PC - ROW, etc.
        r'\s*-\s*PCDD\s*-.*$',         # - PCDD - WW
        r'\s*-\s*PDLC\s*-.*$',         # - PDLC - WW
        r'\s*\(Origin.*?\)\s*$',       # (Origin.com), (Origin/3PDD), etc.
        r'\s*\(.*?Origin.*?\)\s*$',    # Qualsiasi parentesi con Origin
        r'\s*Standard Edition.*$',     # Standard Edition
        r'\s*Deluxe.*Edition.*$',      # Deluxe Edition
        r'\s*Ultimate Edition.*$',     # Ultimate Edition
        r'\s*Game of the Year.*$',     # GOTY
    ]
    
    for pattern in patterns_to_remove:
        title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    
    # Rimuovi trattini finali
    title = re.sub(r'\s*-\s*$', '', title)
    
    # Rimuovi spazi multipli
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title

def normalize_case(title):
    """Normalizza il case dei titoli (da CAPS a Title Case)"""
    # Lista di parole che dovrebbero rimanere uppercase
    always_upper = {'DLC', 'PC', 'WW', 'ROW', 'EA', 'NFS', 'VS', 'VR', 'MP', 'IP'}
    
    # Se il titolo è tutto maiuscolo, convertilo in title case
    if title.isupper() and len(title) > 5:
        words = title.split()
        normalized = []
        for word in words:
            if word in always_upper:
                normalized.append(word)
            elif '-' in word:
                # Gestisci parole con trattino
                parts = word.split('-')
                normalized.append('-'.join([p.capitalize() if p not in always_upper else p for p in parts]))
            else:
                normalized.append(word.capitalize())
        return ' '.join(normalized)
    return title

def identify_base_game(titles_list):
    """Identifica il gioco base da una lista di titoli simili"""
    # Criteri per identificare il gioco base:
    # 1. Titolo più corto
    # 2. Non contiene "DLC", "Expansion", "Pack", "Bundle"
    
    dlc_keywords = ['dlc', 'expansion', 'pack', 'bundle', 'content', 'unlock', 
                    'armor', 'weapon', 'appearance', 'bonus', 'multiplayer']
    
    candidates = []
    for title in titles_list:
        title_lower = title.lower()
        is_dlc = any(keyword in title_lower for keyword in dlc_keywords)
        
        if not is_dlc:
            candidates.append((len(title), title))
    
    if candidates:
        # Ritorna il titolo più corto tra i candidati
        candidates.sort()
        return candidates[0][1]
    else:
        # Se tutti sono DLC, prendi il più corto comunque
        return min(titles_list, key=len)

def group_by_game(games_dict):
    """Raggruppa giochi simili per identificare base + DLC"""
    groups = defaultdict(list)
    
    for title, date in games_dict.items():
        # Crea una chiave base rimuovendo numeri e parole comuni
        base_key = re.sub(r'\s+\d+\s*', ' ', title)  # Rimuovi numeri standalone
        base_key = re.sub(r'\s*:\s*.*$', '', base_key)  # Rimuovi tutto dopo i due punti
        base_key = base_key.lower().strip()
        
        groups[base_key].append(title)
    
    return groups

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, 'sources', 'eagames.CSV')
    output_file = os.path.join(base_dir, 'sources', 'ea_library_cleaned.json')
    
    if not os.path.exists(input_file):
        print(f"❌ File non trovato: {input_file}")
        return
    
    # Leggi il CSV
    games = {}
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            title = row['Entitlement_Name']
            date = row['Entitlement_Begin_Date']
            
            # Pulisci il titolo
            cleaned = clean_title(title)
            normalized = normalize_case(cleaned)
            
            if normalized:
                # Mantieni solo la prima occorrenza (data più vecchia)
                if normalized not in games:
                    games[normalized] = date
    
    print(f"📊 Letti {len(games)} giochi unici dopo la pulizia iniziale\n")
    
    # Raggruppa per identificare giochi base e DLC
    groups = group_by_game(games)
    
    base_games = set()
    dlc_games = set()
    
    for base_key, titles in groups.items():
        if len(titles) > 1:
            # Identifica il gioco base
            base_game = identify_base_game(titles)
            base_games.add(base_game)
            
            # Gli altri sono DLC
            for title in titles:
                if title != base_game:
                    dlc_games.add(title)
        else:
            # Se c'è un solo titolo, controlla se è un DLC standalone
            title = titles[0]
            title_lower = title.lower()
            dlc_keywords = ['dlc', 'expansion', 'pack', 'content', 'bundle']
            
            if any(keyword in title_lower for keyword in dlc_keywords):
                dlc_games.add(title)
            else:
                base_games.add(title)
    
    print("=" * 80)
    print(f"🎮 GIOCHI BASE ({len(base_games)}):")
    print("=" * 80)
    for game in sorted(base_games):
        print(f"  • {game}")
    
    print(f"\n{'=' * 80}")
    print(f"📦 DLC / ESPANSIONI ({len(dlc_games)}):")
    print("=" * 80)
    for dlc in sorted(dlc_games):
        print(f"  • {dlc}")
    
    # Crea JSON per l'import
    import json
    ea_games = []
    for game in sorted(base_games):
        ea_games.append({
            "title": game,
            "platform": "EA",
            "acquired_date": games.get(game, "")
        })
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(ea_games, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ File pulito salvato in: {output_file}")
    print(f"📝 Pronti per l'import: {len(ea_games)} giochi EA\n")
    
    # Mostra i titoli che potrebbero richiedere verifica manuale
    print("⚠️  TITOLI DA VERIFICARE (potrebbero essere normalizzati male):")
    print("=" * 80)
    suspect_titles = [g for g in base_games if len(g) < 10 or g.isupper()]
    if suspect_titles:
        for title in sorted(suspect_titles):
            print(f"  • {title}")
    else:
        print("  Nessuno - tutti i titoli sembrano OK!")

if __name__ == "__main__":
    main()
