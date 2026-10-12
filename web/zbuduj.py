"""
Buduje gotową stronę PWA w katalogu _site/ (publikowaną na GitHub Pages).

web/index.html jest napisany jako „wnętrze” strony (bez <head>), bo w tej
postaci publikujemy go też jako podgląd. Ten skrypt:
  1. owija go w pełny dokument HTML z manifestem i ikonami,
  2. kopiuje pliki gry i shiver.json,
  3. wpisuje do sw.js wersję = skrót zawartości plików, żeby telefon
     pobrał nową grę po każdej zmianie.

Uruchomienie:  python web/zbuduj.py
"""
import hashlib
import pathlib
import shutil

KATALOG = pathlib.Path(__file__).parent
REPO = KATALOG.parent
WYJSCIE = REPO / "_site"

GLOWA = """<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#111513">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Dreszcz">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="ikona-192.png">
<link rel="apple-touch-icon" href="ikona-192.png">
<style>
:root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
body { margin: 0; }
img { max-width: 100%; }
[hidden] { display: none !important; }
</style>
</head>
<body>
"""
STOPKA = """
<script>
// Rejestracja service workera – od tej chwili gra działa też offline.
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("sw.js").catch(() => {});
}
</script>
</body>
</html>
"""

PLIKI = ["silnik.js", "manifest.webmanifest", "ikona-192.png", "ikona-512.png"]


def zbuduj() -> str:
    if WYJSCIE.exists():
        shutil.rmtree(WYJSCIE)
    WYJSCIE.mkdir()

    wnetrze = (KATALOG / "index.html").read_text(encoding="utf-8")
    (WYJSCIE / "index.html").write_text(GLOWA + wnetrze + STOPKA, encoding="utf-8")
    for nazwa in PLIKI:
        shutil.copy(KATALOG / nazwa, WYJSCIE / nazwa)
    shutil.copy(REPO / "shiver.json", WYJSCIE / "shiver.json")

    # Skrót (hash) wszystkich plików = wersja pamięci w service workerze.
    skrot = hashlib.sha256()
    for plik in sorted(WYJSCIE.iterdir()):
        skrot.update(plik.read_bytes())
    wersja = skrot.hexdigest()[:10]

    sw = (KATALOG / "sw.js").read_text(encoding="utf-8")
    sw = sw.replace('const WERSJA = "dev";', f'const WERSJA = "{wersja}";')
    (WYJSCIE / "sw.js").write_text(sw, encoding="utf-8")
    return wersja


if __name__ == "__main__":
    print(f"Zbudowano _site/ (wersja {zbuduj()})")
