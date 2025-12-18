import json
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    merged_file = os.path.join(base_dir, 'merged_games.json')
    
    # Carica i giochi
    with open(merged_file, 'r', encoding='utf-8') as f:
        games = json.load(f)
    
    print(f"📊 Giochi totali prima della rimozione: {len(games)}")
    
    # Conta i giochi EA
    ea_games = [g for g in games if 'EA' in g.get('platforms', [])]
    print(f"🎮 Giochi EA da rimuovere: {len(ea_games)}")
    
    # Mostra quali giochi EA verranno rimossi
    print("\n❌ Giochi EA che verranno rimossi:")
    for game in ea_games:
        print(f"  • {game['title']}")
    
    # Rimuovi i giochi EA
    games_without_ea = [g for g in games if 'EA' not in g.get('platforms', [])]
    
    print(f"\n✅ Giochi rimanenti: {len(games_without_ea)}")
    
    # Salva il file aggiornato
    with open(merged_file, 'w', encoding='utf-8') as f:
        json.dump(games_without_ea, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 File aggiornato: {merged_file}")
    print("🔄 Ora esegui la migrazione a MongoDB per applicare le modifiche")

if __name__ == "__main__":
    main()
