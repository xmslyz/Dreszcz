"""
Sprawdza spójność książki w shiver.json.

Format przejścia (edge) w paragrafie:
    {"label": "...", "target": "25", "condition": "...", "return_to": "274"}

Cele specjalne:
    END       – koniec gry (opcjonalnie "ending": "victory")
    RETURN    – wróć do numeru zapisanego wcześniej przez "return_to"
                (paragraf działa jak funkcja: wywołanie -> powrót)
    KEYS_SUM  – suma liczb na trzech kluczach; możliwe cele w "possible_targets"

Uruchomienie:  python sprawdz_ksiege.py
"""
import json
import pathlib
import sys
from collections import deque

SPECIAL_TARGETS = {"END", "RETURN", "KEYS_SUM"}
BOOK_PATH = pathlib.Path(__file__).parent / "shiver.json"


def load_book(path=BOOK_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def next_paragraphs(edge: dict) -> list[str]:
    """Wszystkie paragrafy, do których może zaprowadzić jedno przejście."""
    targets = []
    target = str(edge["target"])
    if target not in SPECIAL_TARGETS:
        targets.append(target)
    if "return_to" in edge:          # po powrocie z „podprogramu”
        targets.append(str(edge["return_to"]))
    targets += [str(t) for t in edge.get("possible_targets", [])]
    return targets


def check_book(book: dict, start: str = "1") -> dict:
    """Zwraca słownik problemów; pusty słownik = książka spójna."""
    problems = {}

    no_edges = [k for k, p in book.items() if not p.get("edges")]
    if no_edges:
        problems["bez_przejsc"] = no_edges

    missing = [(k, t) for k, p in book.items()
               for e in p.get("edges", []) for t in next_paragraphs(e)
               if t not in book]
    if missing:
        problems["brakujace_cele"] = missing

    # Przeszukiwanie wszerz (BFS) od paragrafu startowego
    seen = {start}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for edge in book[current].get("edges", []):
            for target in next_paragraphs(edge):
                if target in book and target not in seen:
                    seen.add(target)
                    queue.append(target)
    unreachable = sorted(set(book) - seen, key=int)
    if unreachable:
        problems["nieosiagalne"] = unreachable

    return problems


if __name__ == "__main__":
    result = check_book(load_book())
    for name, items in result.items():
        print(f"{name} ({len(items)}): {items}")
    if not result:
        print("Książka spójna.")
    sys.exit(1 if result else 0)
