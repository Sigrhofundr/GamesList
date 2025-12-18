#!/usr/bin/env python3
"""
Script to identify DLC and expansion content in existing game library.
Checks game titles for common DLC keywords and patterns.
"""

import json
import os
import re

# Patterns that commonly indicate DLC (regex) - more specific
DLC_PATTERNS = [
    r'\b(dlc|expansion)\b',  # Explicit DLC/expansion mentions
    r'season\s+pass',  # Season pass
    r':\s+(soundtrack|ost|artbook|wallpaper)',  # After colon (bonus content)
    r'(scenario|content|voice|map|expansion|dlc)\s+pack',  # Specific pack types
    r'\d+\s+dlc',  # "5 DLC" patterns
]

# Patterns to EXCLUDE from DLC detection (these are full games)
EXCLUDE_PATTERNS = [
    r'party\s+pack',  # Jackbox Party Pack series
    r'commander\s+pack',  # Total Annihilation Commander Pack is a full game
]

def is_dlc(title):
    """
    Check if a game title indicates it's DLC/expansion content.
    Returns (bool, reason) tuple.
    More conservative approach to avoid false positives.
    """
    title_lower = title.lower()
    
    # First check exclusions (games that look like DLC but aren't)
    for exclude_pattern in EXCLUDE_PATTERNS:
        if re.search(exclude_pattern, title_lower):
            return False, ""
    
    # Check regex patterns (most specific)
    for pattern in DLC_PATTERNS:
        if re.search(pattern, title_lower):
            return True, f"Matches pattern: '{pattern}'"
    
    return False, ""

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'merged_games.json')
    
    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}")
        return
    
    print(f"📂 Loading {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        games = json.load(f)
    
    print(f"🎮 Analyzing {len(games)} games...\n")
    
    dlc_found = []
    updated_count = 0
    
    for game in games:
        title = game.get('title', '')
        result, reason = is_dlc(title)
        
        if result:
            game['is_dlc'] = True
            dlc_found.append({
                'title': title,
                'reason': reason,
                'platforms': game.get('platforms', [])
            })
            updated_count += 1
        else:
            # Ensure field exists even if False
            game['is_dlc'] = False
    
    # Save updated JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(games, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated {updated_count} games with is_dlc=True")
    print(f"✅ Added is_dlc field to all {len(games)} games\n")
    
    if dlc_found:
        print("📋 DLC/Expansions identified:")
        print("-" * 80)
        for item in dlc_found:
            platforms = ', '.join(item['platforms'])
            print(f"• {item['title']}")
            print(f"  └─ Reason: {item['reason']}")
            print(f"  └─ Platforms: {platforms}\n")
    else:
        print("ℹ️  No DLC content detected based on title patterns.")
    
    # Save report
    report_path = os.path.join(base_dir, 'dlc_identification_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"DLC Identification Report\n")
        f.write(f"=" * 80 + "\n\n")
        f.write(f"Total games analyzed: {len(games)}\n")
        f.write(f"DLC/Expansions found: {len(dlc_found)}\n")
        f.write(f"Base games: {len(games) - len(dlc_found)}\n\n")
        
        if dlc_found:
            f.write("DLC/Expansions List:\n")
            f.write("-" * 80 + "\n")
            for item in dlc_found:
                platforms = ', '.join(item['platforms'])
                f.write(f"\n{item['title']}\n")
                f.write(f"  Reason: {item['reason']}\n")
                f.write(f"  Platforms: {platforms}\n")
    
    print(f"📄 Report saved to: {report_path}")

if __name__ == "__main__":
    main()
