import json

with open('merged_games.json', 'r') as f:
    data = json.load(f)

unknowns = []
for game in data:
    genres = game.get('genres', [])
    if not genres or "Sconosciuto" in genres:
        unknowns.append(game['title'])


with open('unknowns_result.txt', 'w') as f_out:
    f_out.write(f"Found {len(unknowns)} games with 'Sconosciuto' or empty genres:\n")
    for title in unknowns:
        f_out.write(f"- {title}\n")
print("Done writing.")
