import json

def update_text_from_dreszcz(dreszcz_path, shiver_path, output_path):
    with open(dreszcz_path, 'r', encoding='utf-8') as f:
        dreszcz = json.load(f)

    with open(shiver_path, 'r', encoding='utf-8') as f:
        shiver = json.load(f)

    updated = 0
    for para_id, data in dreszcz.items():
        # Sprawdzamy czy paragraf istnieje w shiver.json
        if para_id in shiver and 'str' in data:
            shiver[para_id]['text'] = data
            updated += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(shiver, f, ensure_ascii=False, indent=2)

    print(f"Zaktualizowano {updated} paragrafów. Wynik zapisano do {output_path}")

if __name__ == "__main__":
    update_text_from_dreszcz('dreszcz.json', 'shiver.json', 'shiver.json')