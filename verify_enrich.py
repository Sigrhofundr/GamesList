import json

with open('merged_games.json', 'r') as f:
    data = json.load(f)

found = False
with open('verify_result.txt', 'w') as f_out:
    for game in data:
        if game['title'] == "Il Detective del lato Oscuro":
            f_out.write(json.dumps(game, indent=2))
            found = True
            break
    if not found:
        f_out.write("Game not found.")
