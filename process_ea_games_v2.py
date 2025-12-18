#!/usr/bin/env python3
"""
Process EA Games CSV with device mapping and DLC detection.
Handles the new Entitlement_Platform column for device assignment.
"""

import csv
import json
import os
import re

def normalize_title(title):
    """Clean and normalize game titles."""
    # Remove common suffixes and patterns
    patterns_to_remove = [
        r'\s*-\s*PCDD\s*-\s*.*$',
        r'\s*-\s*PDLC\s*-\s*.*$',
        r'\s*-\s*PC\s*-\s*.*$',
        r'\s*-\s*Mac/PC\s*-\s*.*$',
        r'\s*-\s*WW\s*.*$',
        r'\s*-\s*ROW\s*.*$',
        r'\s*-\s*RoW\s*.*$',
        r'\s*-\s*Twitch Prime.*$',
        r'\s*-\s*TWITCH PRIME.*$',
        r'\s*\(Origin[^)]*\)',
        r'\s*\(3PDD[^)]*\)',
        r'\s*\(RTP\)',
        r'\s*\(IP\d+\)',
        r'\s*\(Pre-Order\)',
        r'\s*\(reward item.*\)',
        r'\s*\(Bundled.*\)',
        r'\s*\(incl.*\)',
        r'\s*\(Legacy.*\)',
        r'\s*\(WEST EU\)',
        r'\s*\(MP Pack \d+\)',
    ]
    
    cleaned = title
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Remove multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Remove trailing dashes
    cleaned = re.sub(r'\s*-\s*$', '', cleaned).strip()
    
    return cleaned

def map_device(platform):
    """Map Entitlement_Platform to device."""
    platform = platform.upper().strip()
    
    if platform in ['PCWIN', 'UNKNOWN', 'MAC']:
        return ['PC']
    elif platform == 'PS3':
        return ['PS3']
    elif platform == 'XBOX':
        return ['Xbox 360']
    else:
        return ['PC']  # Default fallback

def is_dlc(title, cleaned_title):
    """Determine if a game is DLC/expansion content."""
    title_lower = title.lower()
    cleaned_lower = cleaned_title.lower()
    
    # Explicit DLC indicators
    dlc_indicators = [
        'dlc', 'expansion', 'pack', 'bundle', 'content',
        'stuff', 'kit', 'episode', 'unlock', 'armor',
        'weapon', 'appearance', 'skin', 'cosmetic',
        'multiplayer expansion', 'mp expansion',
        'extra content', 'bonus', 'digital',
    ]
    
    for indicator in dlc_indicators:
        if indicator in title_lower:
            return True
    
    # Specific game patterns
    if 'the sims 4' in cleaned_lower:
        if 'standard edition' not in cleaned_lower:
            return True
    
    if 'dragon age' in cleaned_lower:
        if any(x in title_lower for x in ['dlc', 'unlock', 'bundle', 'origin dlc']):
            return True
    
    if 'mass effect 2' in cleaned_lower:
        if any(x in title_lower for x in ['dlc', 'origin dlc']):
            return True
    
    if 'battlefield' in cleaned_lower:
        if any(x in title_lower for x in ['expansion pack', 'china rising', 'in the name of the tsar']):
            return True
    
    if 'simcity' in cleaned_lower:
        if any(x in title_lower for x in ['pack', 'set', 'roof topper']):
            return True
    
    return False

def process_ea_csv(csv_path):
    """Process EA games CSV file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    games = {}
    dlcs = []
    skipped = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        
        for row in reader:
            original_title = row['Entitlement_Name'].strip()
            platform = row.get('Entitlement_Platform', 'UNKNOWN').strip()
            
            # Skip obviously non-game entries
            if '**NOT FOR RETAIL SALE**' in original_title:
                skipped.append(original_title)
                continue
            
            cleaned_title = normalize_title(original_title)
            device = map_device(platform)
            is_dlc_content = is_dlc(original_title, cleaned_title)
            
            # Create normalized key for deduplication
            norm_key = re.sub(r'[^\w\s]', '', cleaned_title.lower())
            norm_key = ' '.join(norm_key.split())
            
            game_data = {
                'title': cleaned_title,
                'original_title': original_title,
                'platform': platform,
                'device': device,
                'is_dlc': is_dlc_content
            }
            
            if is_dlc_content:
                dlcs.append(game_data)
            else:
                # For base games, merge devices if same title
                if norm_key in games:
                    # Merge devices
                    existing_devices = set(games[norm_key]['device'])
                    new_devices = set(device)
                    games[norm_key]['device'] = sorted(list(existing_devices | new_devices))
                else:
                    games[norm_key] = game_data
    
    # Convert to lists
    base_games = list(games.values())
    
    return base_games, dlcs, skipped

def main():
    csv_path = os.path.join(os.path.dirname(__file__), 'sources', 'eagames.CSV')
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return
    
    print(f"📂 Processing {csv_path}...")
    base_games, dlcs, skipped = process_ea_csv(csv_path)
    
    print(f"\n📊 Processing Results:")
    print(f"   Base Games: {len(base_games)}")
    print(f"   DLC/Expansions: {len(dlcs)}")
    print(f"   Skipped: {len(skipped)}")
    
    print(f"\n🎮 Base Games:")
    print("=" * 80)
    for game in sorted(base_games, key=lambda x: x['title']):
        devices = ', '.join(game['device'])
        print(f"• {game['title']}")
        print(f"  └─ Device: {devices}")
    
    print(f"\n📦 DLC/Expansions ({len(dlcs)} total):")
    print("=" * 80)
    for dlc in sorted(dlcs, key=lambda x: x['title'])[:20]:  # Show first 20
        devices = ', '.join(dlc['device'])
        print(f"• {dlc['title']}")
        print(f"  └─ Device: {devices}")
    if len(dlcs) > 20:
        print(f"... and {len(dlcs) - 20} more DLCs")
    
    # Save to JSON
    output_path = os.path.join(os.path.dirname(__file__), 'ea_games_processed.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            'base_games': base_games,
            'dlcs': dlcs,
            'skipped': skipped
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved to {output_path}")
    
    # Create EA library format for normalize_games.py
    ea_library = {
        'library': []
    }
    
    # Add base games
    for game in base_games:
        ea_library['library'].append({
            'title': game['title'],
            'device': game['device'],
            'is_dlc': False
        })
    
    # Add DLCs
    for dlc in dlcs:
        ea_library['library'].append({
            'title': dlc['title'],
            'device': dlc['device'],
            'is_dlc': True
        })
    
    ea_json_path = os.path.join(os.path.dirname(__file__), 'sources', 'ea_library.json')
    with open(ea_json_path, 'w', encoding='utf-8') as f:
        json.dump(ea_library, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created EA library: {ea_json_path}")
    print(f"\n📋 Summary:")
    print(f"   Total games to import: {len(base_games) + len(dlcs)}")
    print(f"   - Base games: {len(base_games)}")
    print(f"   - DLC/Expansions: {len(dlcs)}")

if __name__ == "__main__":
    main()
