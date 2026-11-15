# Dreszcz — pamięć projektu i zasady pracy

Ten plik Claude czyta na początku każdej sesji. Ma dwie role:
**pamięć** (co już wiemy i zrobiliśmy) oraz **porządek** (jak pracujemy).
Po każdym zamkniętym wątku aktualizuj sekcje „Stan” i „Lista wątków”.

## 1. Czym jest projekt

- Gra paragrafowa „Dreszcz” (autor książki: Jacek Ciesielski), 387 paragrafów.
- Cel: grywalna na wszystkich telefonach. Decyzja: **PWA w JavaScripcie**
  (jedna strona instalowana z przeglądarki, działa offline).
  Python zostaje do narzędzi, walidacji i testów danych.
- Adres gry: https://xmslyz.github.io/Dreszcz/
- Repo: `xmslyz/Dreszcz`, gałąź **`master`** (nie ma `main` — „push na main”
  z instrukcji projektu oznacza tutaj `master`).
- Prawa autorskie: tekst książki należy do autora/wydawcy. Użytek prywatny
  jest w porządku; publikacja w sklepach wymagałaby zgody.

## 2. Jak pracujemy

### Język i ton
- Po polsku, krótko i konkretnie. Bez długich podsumowań.

### Jeden wątek naraz
- Praca idzie według ponumerowanej listy wątków (sekcja 6), zawsze nad jednym.
- Jedno pytanie naraz.
- Następny wątek dopiero po zamknięciu bieżącego; na koniec 1–2 zdania, co zrobione.
- Nowe sprawy dopisuj na KONIEC listy, bez pytania. Numery się nie zmieniają.
- Wiadomość spoza bieżącego wątku: powiedz o tym, dopisz na koniec, wróć do wątku.
- Wątek czekający na działanie Macieja można na prośbę przenieść na koniec.

### Decyzje
- Propozycja z krótkim uzasadnieniem i pytanie „czy tak?”.
- Po „tak” / „działaj” — całość bez dalszych pytań.
- Gdy Maciej jest na telefonie: najrozsądniejsze założenia, praca,
  a na końcu sekcja **Założenia**.
- Pomyłkę nazwij wprost i popraw.

### Zasada nadrzędna: nauka
- Maciej uczy się programowania przy tej pracy. Każdą zmianę logiki lub
  zachowania zamknij krótkim **„Czego się nauczyć”**: dlaczego tak, oraz jakie
  nowe funkcje, konstrukcje języka lub techniki zostały użyte.

### Kod i repozytorium
- Zmiany małe, commit opisany po polsku.
- Po zmianie: testy → commit → push na `master` → podaj numer commita.
- Push na `master` sam publikuje grę (GitHub Actions → Pages).

## 3. Budowa repozytorium

| Miejsce | Co to jest |
|---|---|
| `shiver.json` | **Źródło prawdy**: 387 paragrafów jako graf (tekst + przejścia + efekty) |
| `web/silnik.js` | Silnik gry: czyste funkcje bez ekranu (stan, walka, efekty, warunki) |
| `web/index.html` | Interfejs: „wnętrze” strony bez `<head>`. Przyciski rzutu mają `data-rzut` — to je „naciska” potrząśnięcie |
| `web/silnik.test.js` | Testy silnika (`node --test`) |
| `web/sw.js`, `manifest.webmanifest`, `ikona-*.png` | Część PWA: offline i instalacja |
| `web/zbuduj.py` | Buduje `_site/`; wpisuje do `sw.js` wersję = skrót zawartości plików |
| `sprawdz_ksiege.py`, `test_ksiega.py` | Walidator spójności książki i jego testy |
| `.github/workflows/strona.yml` | Testy + budowa + publikacja przy każdym pushu |
| `ToDo.md` | Errata książki i stare notatki |
| `book/` | Surowy tekst książki |
| `*.py` w katalogu głównym, `shiver_old.json`, `dreszcz.json`, `SAVE/` | Stara wersja konsolowa w Pythonie — nierozwijana |

Na Macu: kod w `~/DEV/Dreszcz`, archiwum starej kopii w `~/DEV/Dreszcz ARCH`
(szczegóły w dokumencie projektu `claude/uklad-folderow.md`).

## 4. Polecenia

```
node --test web/silnik.test.js      # testy silnika (59)
python3 -m unittest -v test_ksiega  # testy książki (2)
python3 -m unittest test_game_mechanics  # stara wersja Pythonowa (11), poza workflow
python3 sprawdz_ksiege.py           # oczekiwane: „Książka spójna.”
python3 web/zbuduj.py               # buduje _site/
```

Sprawdzenie publikacji po pushu:
`gh run list -R xmslyz/Dreszcz -L 1` (po ok. minucie), potem porównać `WERSJA`
w https://xmslyz.github.io/Dreszcz/sw.js z lokalnym `_site/sw.js`.

Podgląd lokalny: `python3 -m http.server` w `_site/`, ekran 390×844.

## 5. Zapis danych w `shiver.json`

Każdy paragraf: `text`, `edges` oraz opcjonalnie `efekty`, `combat`,
`test_sss`, `rzut_kosci`, `limit_opcji`.

Przejście (`edges[]`): `target`, `label` i opcjonalne warunki:

| Klucz | Znaczenie |
|---|---|
| `ma`, `nie_ma`, `ma_wszystkie` | zależność od przedmiotów |
| `zloto_min` | wymagane złoto |
| `byl_w`, `nie_byl_w`, `pierwsza_wizyta`, `wizyty` | pamięć gry („czy już tu byłeś?”) |
| `sss` | wynik testu szczęścia |
| `suma` | wynik rzutu kośćmi |
| `efekt` | efekt przy wyborze tej drogi (zakup, wymiana) |
| `return_to` | powrót pod zapisany numer |

Walka (`combat`): `monsters`, `escape` oraz opcjonalnie
`oslona: {"ma": [rzeczy], "W": n}` — zapas punktów na czas tej walki,
przyjmuje rany przed Wytrzymałością (hełm w 2).

Efekty zależne od rzutu: `efekty: [{"gdy_suma": [od, do], ...}]` razem z
`rzut_kosci`; działają przy każdej wizycie. Dodatkowo `gdy_parzysta: true/false`.
Wartości z rzutu dla `W` i `zloto`: `"kosc"` = plus oczka, `"-kosc"` = minus oczka;
`"zostaw_W": 1` = nie mniej niż 1 W (240). Złoto nie spada poniżej 0.

Liczniki (`stan.liczniki`, np. `{"jatka": 3}`): rosną przez `combat.licznik`
(każdy zabity potwór) albo `rzut_kosci: {"trafienie": 5, "na_probe": 2, "licznik": ...}`
(udane próby). Wypłata: efekt `{"zloto_za": {"licznik": nazwa, "po": 5}}`.

Zasady, których się trzymamy:
- Cechy, złoto, posiłki i przedmioty idą **jednym zapisem** `efekty`
  i jedną funkcją `zmienCechy()`. Nie tworzymy osobnych mechanizmów.
- Filtrowanie warunkami nigdy nie może zostawić gracza bez wyjścia.
- Pokonane potwory nie wstają po powrocie do paragrafu.
- Erratę wprowadzamy w `edges`; tekstu książki nie zmieniamy.
- Stare klucze angielskie (`effects`, `actions`, `requires_*`, `condition`,
  `stat_change(s)` itd.) to pozostałość do stopniowego przeniesienia.

## 6. Stan (15.11.2026)

Ostatni commit z kodem: „Errata: 174 wraca do 210” (15.11.2026).

Zrobione: gra w przeglądarce, walka, PWA na GitHub Pages, kości na ekranie,
efekty paragrafów, ekwipunek, mapa wędrówki, pamięć odwiedzin, SSS poza walką,
rzuty kością w paragrafach, przejścia zależne od przedmiotów i złota,
osłona na czas walki (hełm w 2), efekty zależne od rzutu (74, 240, 315),
hazard (145, 201, 334), liczniki i nagrody (193, 26),
rzut potrząśnięciem (przycisk „Potrząśnij” w stopce, domyślnie wyłączony;
sprawdzony przez Macieja na telefonie), tryb testowy (tymczasowy).

Znane usterki: brak.

## 7. Lista wątków

Bieżący: **11**.

- 11\. `ToDo.md`: „zapisz numer” rozwiązany — uaktualnić
- 14\. Eliksir
- 16\. Tryb tajemny (losowe numery paragrafów)
- 17\. Losowe spotkania z potworami
- 18\. Workflow: podbić wersje akcji (Node 20 przestarzały)
- 20\. Pamięć „z warunkiem”: 97, 189, 261, 290
- 21\. Skąd szmaragd? (12 go tylko zużywa)
- 22\. Przed wydaniem: ukryć tryb testowy
- 23\. 95: kara −1 Z w najbliższej walce
- 24\. Pętle w książce: powtarzalne przeszukanie 305
- 25\. Przejrzeć etykiety przycisków przy długich paragrafach
- 26\. Licencja kodu: stare README mówiło „MIT”, ale pliku `LICENSE` nie ma — zdecydować
- 27\. Zdobyć oficjalną erratę („Razem” nr 40/1987) i porównać z naszymi poprawkami

Zamknięte: 1–10, 12, 13, 15, 19.

## 8. Otwarte ustalenia projektowe

- Miecz zaczarowany: nierozstrzygnięte, czy premia dotyczy całej Zręczności,
  czy tylko ataku w walce.
- Czujniki telefonu (żyroskop, kroki): tylko jako opcja w wybranych momentach,
  nie stała mechanika. Wibracje pasują do klimatu.
