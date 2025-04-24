import pathlib
from paragraph import Paragraph

def load_book(path: str = "shiver.json") -> tuple[dict, dict]:
    full_path = pathlib.Path.cwd() / path
    with open(full_path, encoding="utf-8") as f:
        raw = json.load(f)
    chapters = {k: Paragraph(k, v) for k, v in raw.items()}
    return raw, chapters


def update_text_from_dreszcz(dreszcz_path, shiver_path, output_path):
    with open(dreszcz_path, 'r', encoding='utf-8') as f:
        dreszcz = json.load(f)

    with open(shiver_path, 'r', encoding='utf-8') as f:
        shiver = json.load(f)

    updated = 0
    for para_id, data in dreszcz.items():
        if para_id in shiver and isinstance(data, str):
            shiver[para_id]['text'] = data
            updated += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(shiver, f, ensure_ascii=False, indent=2)

    print(f"Zaktualizowano {updated} paragrafów. Wynik zapisano do {output_path}")

def is_valid_move(book_chapters: dict, current: str, target: str) -> bool:
    """
    Checks whether moving from the current chapter to the target is allowed.

    Args:
        book_chapters (dict): All paragraphs in the game.
        current (str): The current paragraph number.
        target (str): The desired paragraph number.

    Returns:
        bool: True if the move is valid, False otherwise.
    """
    paragraph = book_chapters.get(current)
    return paragraph is not None and target in paragraph.edges


def find_invalid_edges(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    invalid_edges = {}

    for pid, paragraph in data.items():
        edges = paragraph.get("edges")
        if edges is not None and not isinstance(edges, list):
            invalid_edges[pid] = type(edges).__name__

    if invalid_edges:
        print("⚠️ Znaleziono niepoprawne wpisy w 'edges':")
        for pid, edge_type in invalid_edges.items():
            print(f" - paragraf {pid}: edges typu {edge_type}")
    else:
        print("✅ Wszystkie 'edges' są poprawnymi listami.")




import json
from collections import deque, defaultdict

def analyze_graph(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    graph = {}
    all_targets = set()

    for pid, info in data.items():
        edges = info.get("edges", [])
        targets = [str(e["target"]) for e in edges if e.get("target")]
        graph[pid] = targets
        all_targets.update(targets)

    # 1. Najkrótsza ścieżka od "1" do "END"
    def bfs_shortest_path(start, goal="END"):
        visited = set()
        queue = deque([(start, [start])])
        while queue:
            current, path = queue.popleft()
            if current == goal:
                return path
            for neighbor in graph.get(current, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return None

    path_to_end = bfs_shortest_path("1", "END")

    # 2. Puste linki
    empty_links = {
        pid: [e for e in info.get("edges", []) if not e.get("target")]
        for pid, info in data.items()
        if "edges" in info
    }
    empty_links = {k: v for k, v in empty_links.items() if v}

    # 3. Ślepe paragrafy (brak edges i != END)
    blind_ends = [pid for pid, edges in graph.items() if not edges and pid != "END"]

    # 4. Martwe paragrafy (nikt tam nie prowadzi)
    all_paragraphs = set(data.keys())
    dead_paragraphs = all_paragraphs - all_targets - {"1"}

    print("\n✅ Najkrótsza ścieżka do END:")
    if path_to_end:
        print(" → ".join(path_to_end))
    else:
        print("Brak ścieżki do END")

    print(f"\n⚠️ Puste linki w: {len(empty_links)} paragrafach")
    for pid, links in empty_links.items():
        print(f" - {pid}: {links}")

    print(f"\n🛑 Ślepe paragrafy (bez wyjść): {len(blind_ends)}")
    print(blind_ends)

    print(f"\n☠️ Martwe paragrafy (nikt tam nie prowadzi): {len(dead_paragraphs)}")
    print(dead_paragraphs)


import json

def collect_all_keys(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    keys = set()

    def is_numeric(s):
        try:
            int(s)
            return True
        except (ValueError, TypeError):
            return False

    def recurse(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if not is_numeric(k):
                    keys.add(k)
                recurse(v)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item)

    recurse(data)

    print("🗂️ Wszystkie unikalne klucze w pliku:")
    for k in sorted(keys):
        print(f" - {k}")

    return keys








if __name__ == "__main__":
    # korekta text w shiver.json
    # update_text_from_dreszcz('dreszcz.json', 'shiver.json', 'shiver.json')

    # Przykład użycia:
    analyze_graph("shiver.json")

    # Przykład użycia:
    collect_all_keys("shiver.json")

    # Przykład użycia:
    find_invalid_edges("shiver.json")