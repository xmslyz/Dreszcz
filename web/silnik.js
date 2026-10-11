// Silnik gry Dreszcz – wersja przeglądarkowa.
// Same „czyste” funkcje: dostają stan, zwracają nowy stan.
// Nie dotykają ekranu, dzięki czemu da się je testować w Node.js.
//
// Ściąga JavaScript ↔ Python:
//   const x = 1            ↔  x = 1  (const = nie zmienię przypisania)
//   { klucz: "a" }         ↔  {"klucz": "a"}   (obiekt ≈ dict)
//   [1, 2, 3]              ↔  [1, 2, 3]        (tablica ≈ list)
//   tablica.push(x)        ↔  lista.append(x)
//   tablica.pop()          ↔  lista.pop()
//   { ...stan, a: 1 }      ↔  {**stan, "a": 1} (kopia z jedną zmianą)
//   x ?? "domyślne"        ↔  x if x is not None else "domyślne"

const START = "1";

/** Nowa gra: stan to zwykły obiekt, łatwy do zapisania jako JSON. */
function nowaGra() {
  return {
    akapit: START,   // numer bieżącego paragrafu (tekst, jak klucze w shiver.json)
    stos: [],        // numery „zapisz ten numer” – stos powrotów (return_to)
    historia: [START],
    koniec: null,    // null = gra trwa; "porazka" albo "zwyciestwo"
  };
}

/**
 * Wykonuje jedno przejście (edge) i zwraca NOWY stan.
 * Stary stan zostaje nietknięty – tak jak w Pythonie zwracamy kopię
 * zamiast modyfikować argument.
 */
function wykonajPrzejscie(stan, przejscie, wybranyNumer = null) {
  const stos = [...stan.stos];          // kopia listy: list(stan.stos)
  if (przejscie.return_to) {
    stos.push(String(przejscie.return_to));
  }

  let cel = String(przejscie.target);

  if (cel === "RETURN") {
    // Powrót z „podprogramu” (np. 315 albo 238) do zapisanego numeru.
    cel = stos.pop() ?? stan.akapit;
  } else if (cel === "KEYS_SUM") {
    // Gracz sam dodaje liczby z kluczy i podaje wynik.
    cel = String(wybranyNumer);
  } else if (cel === "END") {
    const koniec = przejscie.ending === "victory" ? "zwyciestwo" : "porazka";
    return { ...stan, stos, koniec };
  }

  return { ...stan, akapit: cel, stos, historia: [...stan.historia, cel] };
}

/** Etykieta przycisku – gdy w danych brak "label", pokazujemy „Patrz N”. */
function etykieta(przejscie) {
  if (przejscie.label) return przejscie.label;
  return `Patrz ${przejscie.target}`;
}

// W Node.js (testy) udostępniamy funkcje przez module.exports,
// w przeglądarce są po prostu globalne.
if (typeof module !== "undefined") {
  module.exports = { nowaGra, wykonajPrzejscie, etykieta, START };
}
