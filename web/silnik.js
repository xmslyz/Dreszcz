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
//   structuredClone(obj)   ↔  copy.deepcopy(obj)

const START = "1";

// ---------------------------------------------------------------- kości

/** Rzut jedną kostką. W testach podmieniamy ją na „ustawioną” kostkę. */
function k6() {
  return 1 + Math.floor(Math.random() * 6);
}

/** 2K – suma dwóch rzutów; zwracamy też pojedyncze oczka do wyświetlenia. */
function rzut2k(kostka) {
  const a = kostka(), b = kostka();
  return { suma: a + b, oczka: [a, b] };
}

// ---------------------------------------------------------------- bohater

/** Zasady I: Z = 1K+6, W = 2K+12, S = 1K+6, Prowiant na 8 posiłków. */
function nowyBohater(kostka = k6) {
  const rzuty = { Z: [kostka()], W: [kostka(), kostka()], S: [kostka()] };
  const Z = rzuty.Z[0] + 6;
  const W = rzuty.W[0] + rzuty.W[1] + 12;
  const S = rzuty.S[0] + 6;
  // rzuty zachowujemy tylko po to, by pokazać kości na ekranie startowym
  return { Z, W, S, start: { Z, W, S }, prowiant: 8, zloto: 0, rzuty };
}

/**
 * SSS – Sprawdzanie Swojego Szczęścia (zasady IV).
 * Rzut 2K ≤ aktualne S oznacza szczęście. Po każdym SSS S spada o 1.
 */
function sss(bohater, kostka = k6) {
  const r = rzut2k(kostka);
  const szczescie = r.suma <= bohater.S;
  return { szczescie, rzut: r, bohater: { ...bohater, S: bohater.S - 1 } };
}

// ---------------------------------------------------------------- gra

/** Nowa gra: stan to zwykły obiekt, łatwy do zapisania jako JSON. */
function nowaGra(bohater = null) {
  return {
    akapit: START,   // numer bieżącego paragrafu (tekst, jak klucze w shiver.json)
    stos: [],        // numery „zapisz ten numer” – stos powrotów (return_to)
    historia: [START],
    koniec: null,    // null = gra trwa; "porazka" albo "zwyciestwo"
    bohater,
    walka: null,     // trwająca walka albo null
    zastosowane: [], // paragrafy, których efekty już działały (raz na grę)
    wybrane: [],     // wzięte efekty opcjonalne, np. "89:0"
    posilki: [],     // paragrafy, w których zjedzono posiłek
    zmiany: [],      // opis ostatnich zmian do pokazania na ekranie
  };
}

/**
 * Wykonuje jedno przejście (edge) i zwraca NOWY stan.
 * Gdy podamy księgę, a w nowym paragrafie jest walka – walka się zaczyna.
 */
function wykonajPrzejscie(stan, przejscie, wybranyNumer = null, ksiega = null) {
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
    return { ...stan, stos, koniec, walka: null };
  }

  const walka = ksiega ? rozpocznijWalke(ksiega[cel]) : null;
  return { ...stan, akapit: cel, stos, historia: [...stan.historia, cel], walka, zmiany: [] };
}

// ---------------------------------------------------------------- walka

/** Tworzy stan walki dla paragrafu z polem "combat" (albo null). */
function rozpocznijWalke(akapit) {
  const opis = akapit?.combat;
  if (!opis?.monsters?.length) return null;
  return {
    potwory: structuredClone(opis.monsters), // kopia – nie psujemy księgi
    indeks: 0,              // z którym potworem walczymy (walka po kolei)
    rundaPotwora: 0,        // rundy z bieżącym potworem
    rundy: 0,               // wszystkie rundy
    ostatniaWygrana: null,  // czy gracz wygrał ostatnią rundę
    zakonczona: false,
    dziennik: [],           // opis rund do pokazania na ekranie
  };
}

/** Bieżący potwór albo null, gdy wszyscy pokonani. */
function biezacyPotwor(walka) {
  return walka.potwory[walka.indeks] ?? null;
}

/**
 * Jedna runda walki (zasady II i IV).
 *   A = 2K + Z potwora,  B = 2K + Z bohatera (+ premie z paragrafu)
 *   A > B → bohater traci 2 W;  A < B → potwór traci 2 W;  A = B → powtórka.
 * Z opcją uzyjSSS: rana zadana potworowi 4 albo 1, rana otrzymana 1 albo 3.
 */
function rundaWalki(stan, opis, uzyjSSS = false, kostka = k6) {
  const walka = structuredClone(stan.walka);
  let bohater = { ...stan.bohater };
  const potwor = biezacyPotwor(walka);

  const a = rzut2k(kostka);
  const b = rzut2k(kostka);
  const silaPotwora = a.suma + potwor.Z;
  const silaBohatera = b.suma + bohater.Z + (opis.hero_Z_bonus ?? 0) + (opis.hero_attack_bonus ?? 0);
  const wpis = { potwor: potwor.name, a, b, silaPotwora, silaBohatera };

  if (silaPotwora === silaBohatera) {
    wpis.wynik = "remis";
    walka.dziennik.push(wpis);
    return { ...stan, walka };  // remis nie liczy się jako runda
  }

  const wygrana = silaBohatera > silaPotwora;
  let rana;
  if (wygrana) {
    rana = opis.monster_immune ? 0 : (opis.hero_damage ?? 2);
  } else {
    rana = opis.monster_damage_d6 ? opis.monster_damage_d6[String(kostka())] : 2;
  }

  if (uzyjSSS && rana > 0) {
    const proba = sss(bohater, kostka);
    bohater = proba.bohater;
    wpis.sss = proba.szczescie;
    wpis.sssRzut = proba.rzut;
    if (wygrana) rana = proba.szczescie ? rana + 2 : rana - 1;
    else rana = proba.szczescie ? rana - 1 : rana + 1;
  }

  if (wygrana) potwor.W = Math.max(potwor.W - rana, 0);
  else bohater.W = Math.max(bohater.W - rana, 0);

  wpis.wynik = wygrana ? "trafiasz" : "obrywasz";
  wpis.rana = rana;
  walka.dziennik.push(wpis);
  walka.rundy += 1;
  walka.rundaPotwora += 1;
  walka.ostatniaWygrana = wygrana;

  if (bohater.W <= 0) {
    return { ...stan, bohater, walka: { ...walka, zakonczona: true }, koniec: "porazka" };
  }
  if (potwor.W <= 0) {
    walka.indeks += 1;
    walka.rundaPotwora = 0;
  }
  if (!biezacyPotwor(walka)) walka.zakonczona = true;
  if (opis.rounds && walka.rundy >= opis.rounds) walka.zakonczona = true;
  if (opis.until_round_won && wygrana) walka.zakonczona = true;

  return { ...stan, bohater, walka };
}

/** Czy teraz wolno uciec? (zasady III + reguły paragrafu) */
function moznaUciec(walka, opis) {
  const u = opis?.escape;
  if (!u || walka.zakonczona) return false;
  if (u.after_kill) return walka.indeks > 0 && walka.rundaPotwora === 0;
  return walka.rundaPotwora >= (u.from_round ?? 0);
}

/** Ucieczka: potwór zadaje 2 rany (z SSS: 1 albo 3), potem przejście. */
function ucieczka(stan, opis, uzyjSSS = false, kostka = k6, ksiega = null) {
  let bohater = { ...stan.bohater };
  let rana = 2;
  if (uzyjSSS) {
    const proba = sss(bohater, kostka);
    bohater = proba.bohater;
    rana = proba.szczescie ? 1 : 3;
  }
  bohater.W = Math.max(bohater.W - rana, 0);
  if (bohater.W <= 0) return { ...stan, bohater, koniec: "porazka" };
  return wykonajPrzejscie({ ...stan, bohater, walka: null }, opis.escape, null, ksiega);
}

/**
 * Które przejścia pokazać? W czasie walki – żadne.
 * Po walce na określoną liczbę rund – według wyniku ostatniej rundy.
 */
function dostepnePrzejscia(stan, akapit) {
  const wszystkie = akapit?.edges ?? [];
  const w = stan.walka;
  if (!w) return wszystkie;
  if (!w.zakonczona) return [];
  return wszystkie.filter((e) => {
    if (e.condition === "round_won") return w.ostatniaWygrana === true;
    if (e.condition === "round_lost") return w.ostatniaWygrana === false;
    return true;
  });
}

/**
 * Tekst paragrafu do pokazania. Znak "|" dzieli tekst na część przed walką
 * i część po walce – drugą pokazujemy dopiero, gdy walka się zakończy.
 * W Pythonie: przed, _, po = tekst.partition("|")
 */
function tekstAkapitu(stan, akapit) {
  const tekst = akapit?.text ?? "";
  const i = tekst.indexOf("|");
  if (i === -1) return tekst;
  const przed = tekst.slice(0, i).trim();
  const po = tekst.slice(i + 1).trim();
  const walkaTrwa = stan.walka && !stan.walka.zakonczona;
  const przegrana = stan.koniec === "porazka";
  if (walkaTrwa || przegrana || !po) return przed;
  return `${przed} ${po}`;
}

// ---------------------------------------------------------------- efekty

const CECHY = ["Z", "W", "S"];

/**
 * Zmienia cechy bohatera według jednego efektu, np. {"S": 2, "zloto": 3}.
 * Cechy nie przekraczają poziomu początkowego i nie spadają poniżej 0
 * (zasady V). "W": "pol" oznacza połowę Wytrzymałości (paragraf 110).
 * Zwraca nowego bohatera i listę opisów zmian.
 */
function zmienCechy(bohater, efekt) {
  const b = { ...bohater, zloto: bohater.zloto ?? 0 };
  const opisy = [];
  for (const cecha of CECHY) {
    if (!(cecha in efekt)) continue;
    const przed = b[cecha];
    const zmiana = efekt[cecha] === "pol" ? -Math.ceil(przed / 2) : efekt[cecha];
    b[cecha] = Math.min(Math.max(przed + zmiana, 0), b.start[cecha]);
    const naprawde = b[cecha] - przed;  // po przycięciu do poziomu początkowego
    if (naprawde !== 0) opisy.push(`${naprawde > 0 ? "+" : "−"}${Math.abs(naprawde)} ${cecha}`);
  }
  if ("zloto" in efekt) {
    b.zloto = Math.max(b.zloto + efekt.zloto, 0);
    opisy.push(`${efekt.zloto >= 0 ? "+" : "−"}${Math.abs(efekt.zloto)} złota`);
  }
  if ("prowiant" in efekt) {
    b.prowiant = Math.max(b.prowiant + efekt.prowiant, 0);
    opisy.push(`${efekt.prowiant >= 0 ? "+" : "−"}${Math.abs(efekt.prowiant)} posiłek`);
  }
  return { bohater: b, opisy };
}

/** Efekty działają dopiero, gdy nie trwa walka (po walce – po zwycięstwie). */
function efektyGotowe(stan) {
  if (stan.koniec) return false;
  return !stan.walka || stan.walka.zakonczona;
}

const czyAutomatyczny = (e) => !e.opcja && !e.posilek;

/**
 * Stosuje efekty automatyczne bieżącego paragrafu – raz na grę.
 * Wywołujemy po każdym ruchu; gdy nie ma czego robić, zwraca ten sam stan.
 */
function zastosujEfekty(stan, akapit) {
  const efekty = akapit?.efekty ?? [];
  const zastosowane = stan.zastosowane ?? [];
  if (!efekty.length || zastosowane.includes(stan.akapit) || !efektyGotowe(stan)) return stan;
  let bohater = stan.bohater;
  const zmiany = [];
  for (const e of efekty.filter(czyAutomatyczny)) {
    const wynik = zmienCechy(bohater, e);
    bohater = wynik.bohater;
    zmiany.push(...wynik.opisy);
  }
  const nowy = { ...stan, bohater, zmiany, zastosowane: [...zastosowane, stan.akapit] };
  return bohater.W <= 0 ? { ...nowy, koniec: "porazka" } : nowy;
}

/** Efekty do wyboru („Możesz je wziąć”), jeszcze niewzięte. */
function dostepneOpcje(stan, akapit) {
  if (!efektyGotowe(stan)) return [];
  return (akapit?.efekty ?? [])
    .map((efekt, i) => ({ efekt, klucz: `${stan.akapit}:${i}` }))
    .filter(({ efekt, klucz }) => efekt.opcja && !(stan.wybrane ?? []).includes(klucz));
}

function wezOpcje(stan, opcja) {
  const { bohater, opisy } = zmienCechy(stan.bohater, opcja.efekt);
  return { ...stan, bohater, zmiany: opisy, wybrane: [...(stan.wybrane ?? []), opcja.klucz] };
}

/** Posiłek tylko tam, gdzie tekst pozwala (zasady VI): +4 W, −1 Prowiant. */
function moznaJesc(stan, akapit) {
  return efektyGotowe(stan)
    && (akapit?.efekty ?? []).some((e) => e.posilek)
    && stan.bohater.prowiant > 0
    && !(stan.posilki ?? []).includes(stan.akapit);
}

function zjedzPosilek(stan) {
  const { bohater, opisy } = zmienCechy(stan.bohater, { W: 4, prowiant: -1 });
  return { ...stan, bohater, zmiany: opisy, posilki: [...(stan.posilki ?? []), stan.akapit] };
}

// ---------------------------------------------------------------- mapa

/** Numery paragrafów, do których prowadzą wyjścia (bez celów specjalnych). */
function wyjscia(akapit) {
  const wszystkie = [...(akapit?.edges ?? [])];
  if (akapit?.combat?.escape) wszystkie.push(akapit.combat.escape);
  return [...new Set(wszystkie.map((e) => String(e.target)).filter((t) => /^\d+$/.test(t)))];
}

/**
 * Graf wędrówki z historii ruchów:
 *   węzły – odwiedzone paragrafy (ile razy, czy bieżący, ile niezbadanych wyjść),
 *   krawędzie – przejścia, które gracz naprawdę wykonał (bez powtórzeń).
 * Niczego nie zdradza: o niezbadanych wyjściach mówi tylko, ile ich jest.
 */
function grafWedrowki(stan, ksiega) {
  const odwiedziny = new Map();          // Map ≈ dict z zachowaną kolejnością
  for (const nr of stan.historia) odwiedziny.set(nr, (odwiedziny.get(nr) ?? 0) + 1);

  const krawedzie = new Map();
  for (let i = 1; i < stan.historia.length; i++) {
    const [a, b] = [stan.historia[i - 1], stan.historia[i]];
    if (a !== b) krawedzie.set(`${a}>${b}`, [a, b]);
  }

  const wezly = [...odwiedziny].map(([id, ile]) => ({
    id,
    odwiedzin: ile,
    biezacy: id === stan.akapit,
    niezbadane: wyjscia(ksiega[id]).filter((t) => !odwiedziny.has(t)).length,
  }));
  return { wezly, krawedzie: [...krawedzie.values()] };
}

/** Pierwsze zdanie paragrafu – do podpisu na mapie. */
function pierwszeZdanie(akapit) {
  const tekst = (akapit?.text ?? "").split("|")[0].trim();
  const koniec = tekst.search(/[.!?](\s|$)/);
  return koniec === -1 ? tekst : tekst.slice(0, koniec + 1);
}

/** Etykieta przycisku – gdy w danych brak "label", pokazujemy „Patrz N”. */
function etykieta(przejscie) {
  if (przejscie.label) return przejscie.label;
  return `Patrz ${przejscie.target}`;
}

// W Node.js (testy) udostępniamy funkcje przez module.exports,
// w przeglądarce są po prostu globalne.
if (typeof module !== "undefined") {
  module.exports = {
    START, k6, rzut2k, nowyBohater, sss, nowaGra, wykonajPrzejscie,
    rozpocznijWalke, biezacyPotwor, rundaWalki, moznaUciec, ucieczka,
    dostepnePrzejscia, tekstAkapitu, etykieta,
    wyjscia, grafWedrowki, pierwszeZdanie,
    zmienCechy, zastosujEfekty, dostepneOpcje, wezOpcje, moznaJesc, zjedzPosilek,
  };
}
