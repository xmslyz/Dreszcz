* problem z paragrafami, które polecają zapisać/zapamiętać numer. jeśli 
  włączę blokadę, nie będzie możliwe przeniesienie się do tej lokalizacji.
  - 52 -> 274,  
  - 195 -> 113, 
  - 273 -> 103,
  - 15 -> 113,
  - 20 -> 316,
  
* Błędy w scenariuszu (prawdopodobnie)
  - [174] odsyła do 200!

* Propozycje na rozwój GUI:
	1.	Dodanie pola escape_rule z checkboxem enabled, opcjami after_kill, max_round – jako sekcja z checkboxami i polem liczbowym.
	2.	Walidacja edges – np. sprawdzanie, czy target istnieje w self.data, albo czy nie ma literówki typu "25a".
	3.	Lista rozwijana dla istniejących ID – łatwe przełączanie się między paragrafami.
	4.	Wersja z tabelą edges (lista + przyciski “Dodaj”, “Usuń”, “Edytuj”) zamiast JSON-a.
	5.	Podgląd JSON lub eksport tylko jednego paragrafu (przydatne przy edycji pojedynczych wątków).
	6.	Tryb „nowy plik” – rozpoczęcie nowej gry od zera, z pustym słownikiem.