# Errata i notatki o książce

Zadania do zrobienia są w `CLAUDE.md` (lista wątków). Tu zostaje wiedza o książce.

* „Zapisz ten numer” — ROZWIĄZANE
  Gra pamięta numer sama: przejście ma pole `return_to`, a cel `RETURN`
  wraca pod zapisany numer (stos powrotów, jak wywołanie funkcji i `return`).
  Zapisany numer widać w Ekwipunku jako kartkę.
  - 15 → 113, powrót do 15 (przeprawa przez jezioro)
  - 195 → 113, powrót do 195
  - 20 → 238, powrót do 316 (Szalone Pola)
  - 27 → 238, powrót do 316
  - 273 → 238, powrót do 103
  - 143 → 315, powrót do 52
  - 52 → 315, powrót do 274
  - 174 → 315, powrót do 210 (errata, niżej)

* Błędy w scenariuszu (prawdopodobnie)
  - [174] „patrz 315, a potem 200”: powinno być 210 (jedyne wyjście z komnaty;
    200 to korytarz przy starcu, 15 kroków wcześniej, i nie da się stamtąd wrócić)
  - [63] sieć odsyła do 337, powinno być 377 (walka siecią z WILKOŁAKIEM)
  - [166] „za złoto” odsyła do 320, powinno być 353 (targ z KRASNALEM)
  - [172] przy drugiej przeprawie przez jezioro: 266 zamiast 15
    (266 opisuje przeprawę i i tak prowadzi do 15)
  Poprawione w przejściach (edges) w shiver.json; tekst bez zmian.

* Errata w internecie (sprawdzone 15.11.2026)
  - Oficjalna errata: tygodnik „Razem” nr 40/1987 (gra wyszła w nr 33 i 34).
    Jej treści nie ma w sieci – trzeba by zdobyć skan numeru.
  - Znany błąd wydań „Razem” i Ultima: paragraf 119 bez odnośnika, brakowało
    „patrz 102”. U nas tekst 119 już ma 102 – nic do poprawienia.
  - Skargi na „Szalone Pola” (20, 27 → 238 → 316 → 176): wraca się w kółko.
    U nas 176 ma też wyjście na wschód (230), więc pułapki nie ma.
  - Naszych poprawek (63, 166, 172, 174) nikt w sieci nie opisał – to nasze wnioski.

* Pętle (sprawdzone 20.11.2026)
  - 69 → 305 → 112/381 → … → 330 → 170 → 319 → 69: do komnaty da się wracać,
    więc rzut „co najmniej 18” można było powtarzać do skutku. Teraz przeszukanie
    jest jedno na grę (przejście 69 → 305 ma `nie_byl_w: 305`).
  - Inne przeszukania (58, 116, 119, 124, 180, 380…) nie mają losowej bramki,
    a ich efekty i tak działają raz na grę – bez zmian.
  - Hazard (40 → 62 → 201/145, 334) jest powtarzalny celowo: tak mówi książka.
