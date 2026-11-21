# Dreszcz — gra paragrafowa

Cyfrowa wersja gry paragrafowej „Dreszcz” Jacka Ciesielskiego: 387 paragrafów,
walki, kości i ekwipunek. Działa w przeglądarce, na telefonie i bez internetu.

**Zagraj: https://xmslyz.github.io/Dreszcz/**

## Instalacja na telefonie

Gra jest aplikacją PWA: instalujesz ją prosto ze strony, bez sklepu.

- **iPhone:** otwórz adres w Safari → Udostępnij → „Do ekranu początkowego”.
- **Android:** otwórz adres w Chrome → menu ⋮ → „Zainstaluj aplikację”
  (albo „Dodaj do ekranu głównego”).

Po pierwszym uruchomieniu gra działa offline. Nowa wersja pojawia się przy
drugim uruchomieniu po aktualizacji.

## Jak się gra

- Na początku losujesz bohatera: **Zręczność** (1K+6), **Wytrzymałość** (2K+12)
  i **Szczęście** (1K+6). W plecaku masz Prowiant na 8 posiłków.
- Zabierasz jedną butelkę **eliksiru** (Zręczności, Wytrzymałości albo Szczęścia).
  Przywraca cechę do poziomu początkowego; możesz wypić go dwa razy, w dowolnej chwili.
- Czytasz paragraf i wybierasz drogę przyciskiem. Gra sama pilnuje cech, złota,
  ekwipunku, kluczy i tego, gdzie już byłeś.
- **Walka:** w każdej rundzie Ty i potwór rzucacie dwiema kośćmi i dodajecie
  Zręczność. Kto ma mniej, traci 2 punkty Wytrzymałości.
- **SSS (Sprawdź Swoje Szczęście):** rzut dwiema kośćmi przeciw Szczęściu.
  Każda próba kosztuje 1 punkt Szczęścia.
- **Kości:** rzucasz dotknięciem albo — po włączeniu „Potrząśnij” w stopce —
  potrząśnięciem telefonu.
- **Mapa** pokazuje odwiedzone paragrafy i niezbadane wyjścia.
- **Wędrujące potwory** (do zaznaczenia na starcie): w korytarzach czasem wychodzi
  potwór spoza książki, tym groźniejszy, im głębiej jesteś.
- **Tryb tajemny** (do zaznaczenia na starcie) tasuje numery paragrafów, żeby
  książka i pamięć z poprzednich gier nie podpowiadały drogi.
- Postęp zapisuje się sam na urządzeniu. „Nowa gra” zaczyna od początku.

## Dla programisty

```
git clone https://github.com/xmslyz/Dreszcz.git
cd Dreszcz
node --test web/silnik.test.js      # testy silnika gry
python3 -m unittest -v test_ksiega  # testy spójności książki
python3 sprawdz_ksiege.py           # walidator danych
python3 web/zbuduj.py               # buduje stronę w _site/
```

Podgląd lokalny: `cd _site && python3 -m http.server`, potem
http://localhost:8000 w przeglądarce.

| Plik | Rola |
|---|---|
| `shiver.json` | Cała książka jako graf: tekst, przejścia, walki, efekty |
| `web/silnik.js` | Zasady gry (czyste funkcje, bez ekranu) |
| `web/index.html` | Ekran gry |
| `web/sw.js`, `web/manifest.webmanifest` | Instalacja i działanie offline |
| `web/zbuduj.py` | Budowa strony publikowanej na GitHub Pages |

Każdy push na gałąź `master` uruchamia testy i publikuje grę
(`.github/workflows/strona.yml`). Zasady pracy nad projektem i opis zapisu
danych są w `CLAUDE.md`.

Pliki `*.py` w katalogu głównym (`game.py`, `menu.py`, `game_mechanics.py`
i pozostałe) to wcześniejsza, niedokończona wersja konsolowa w Pythonie.
Zostają jako archiwum i nie są rozwijane.

## Zmiany względem książki

Imiona potworów:

- paragraf 69: UPIÓR (drugi) → OBLEC
- paragraf 98: HERSZT GOBLINÓW → GROBOK
- paragrafy 170, 255, 244, 361: STRAŻNIK TAJEMNICY → BLACKTHORNE

Poprawione odnośniki (prawdopodobne błędy druku; szczegóły w `ToDo.md`):

- 63: sieć prowadzi do 377 zamiast 337
- 166: „za złoto” prowadzi do 353 zamiast 320
- 172: druga przeprawa prowadzi do 266 zamiast 15
- 174: po pułapce 315 wracasz do 210 zamiast 200

## Autorzy i prawa

- Książka „Dreszcz”: **Jacek Ciesielski**. Tekst paragrafów należy do autora
  i wydawcy; ta wersja powstała do użytku prywatnego.
- Program: **Maciej Słyż**, licencja MIT (plik `LICENSE`). Licencja obejmuje tylko kod,
  nie tekst książki. Pytania, uwagi i błędy: xmslyz@gmail.com albo
  zgłoszenie (Issue) w tym repozytorium.
