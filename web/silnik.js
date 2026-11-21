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
  // Zasady I: na start miecz, tarcza, plecak na Prowiant i latarnia.
  const ekwipunek = ["miecz", "tarcza", "plecak", "latarnia"];
  return { Z, W, S, start: { Z, W, S }, prowiant: 8, zloto: 0, ekwipunek, rzuty };
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
function wykonajPrzejscie(stan, przejscie, wybranyNumer = null, ksiega = null, kostka = k6) {
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

  // Przejście może samo coś zmienić, np. wymiana z KRASNALEM: motyl za złoto.
  let bohater = stan.bohater;
  let zmiany = [];
  if (przejscie.efekt && bohater) ({ bohater, opisy: zmiany } = zmienCechy(bohater, przejscie.efekt));

  // Potwory pokonane raz już nie wstają (np. pętla 170 → 319 → 69 → … → 330 → 170).
  // Wyjątek: "powtarzalna" – za każdym razem inny potwór (trzech ZŁYCH w 367).
  const juzPokonani = (stan.pokonani ?? []).includes(cel) && !ksiega?.[cel]?.combat?.powtarzalna;
  let walka = ksiega && !juzPokonani ? rozpocznijWalke(ksiega[cel], bohater) : null;

  // Tryb „wędrujące potwory”: w korytarzu może ktoś wyjść naprzeciw.
  let spotkane = stan.spotkane ?? [];
  if (!walka && stan.spotkania && ksiega && !spotkane.includes(cel)) {
    const potwor = losujSpotkanie(ksiega, cel, kostka);
    if (potwor) {
      walka = rozpocznijWalke({ combat: { monsters: [potwor] } }, bohater);
      // Opis tej walki nie pochodzi z księgi, więc niesiemy go w stanie.
      walka.opis = { wedrujacy: true, monsters: [potwor], escape: { from_round: 1 } };
      spotkane = [...spotkane, cel];
    }
  }
  // Kara „do najbliższej walki” (rękawice z 95) przeszła właśnie do walki – z bohatera znika.
  if (walka?.kara) { bohater = { ...bohater }; delete bohater.karaWalki; }

  // Paragraf z zakładami (211): siada nowy przeciwnik ze swoim złotem.
  const reguly = ksiega?.[cel]?.zaklady;
  const zaklad = reguly ? { zloto: reguly.zloto, rundy: [], koniec: null } : null;
  const liczniki = reguly?.licznik_gier ? doliczDoLicznika(stan.liczniki ?? {}, reguly.licznik_gier, 1) : stan.liczniki;
  return { ...stan, bohater, akapit: cel, stos, historia: [...stan.historia, cel], walka, zmiany, testSSS: null, kosci: null, spotkane, zaklad, liczniki };
}

// ---------------------------------------------------------------- zakłady (strzałki ze ZŁYMI, 211)

/** Najwyższa stawka, jaką teraz wolno postawić (0 = nie da się grać). */
function maksStawka(stan, akapit) {
  const reguly = akapit?.zaklady;
  if (!reguly || !stan.zaklad || stan.zaklad.koniec) return 0;
  return Math.min(reguly.stawka[1], stan.bohater.zloto ?? 0, stan.zaklad.zloto);
}

/**
 * Jeden zakład: rzut za siebie i za przeciwnika, wyższy wynik zabiera stawkę.
 * Remis – nikt nic nie traci. Gra kończy się, gdy przeciwnik zostaje bez złota
 * ("ograny") albo gdy bohater traci wszystko ("bankrut").
 */
function postawZaklad(stan, akapit, stawka, kostka = k6) {
  const maks = maksStawka(stan, akapit);
  const reguly = akapit?.zaklady;
  if (!maks || stawka < reguly.stawka[0] || stawka > maks) return stan;
  const ty = kostka();
  const on = kostka();
  const wynik = Math.sign(ty - on);                 // 1 wygrana, 0 remis, -1 przegrana
  const bohater = { ...stan.bohater, zloto: stan.bohater.zloto + wynik * stawka };
  const zaklad = {
    ...stan.zaklad,
    zloto: stan.zaklad.zloto - wynik * stawka,
    rundy: [...stan.zaklad.rundy, { ty, on, stawka, wynik }],
  };
  let liczniki = stan.liczniki ?? {};
  if (zaklad.zloto <= 0) {
    zaklad.koniec = "ograny";
    if (reguly.licznik_ogranych) liczniki = doliczDoLicznika(liczniki, reguly.licznik_ogranych, 1);
  } else if (bohater.zloto <= 0) {
    zaklad.koniec = "bankrut";
  }
  return { ...stan, bohater, zaklad, liczniki };
}

// ---------------------------------------------------------------- wędrujące potwory

// Potwory, które książka sama nazywa wędrującymi (paragraf 238), od najsłabszego.
// Im głębiej w podziemiach, tym groźniejsza trójka do wylosowania.
const WEDRUJACE = [
  { od: 4, potwory: [{ name: "GREMLIN", Z: 5, W: 3 }, { name: "ORKONIK", Z: 6, W: 4 }] },
  { od: 15, potwory: [{ name: "ORKONIK", Z: 6, W: 4 }, { name: "LICHA", Z: 6, W: 5 }, { name: "SAMASKÓRA", Z: 6, W: 5 }] },
  { od: 30, potwory: [{ name: "LICHA", Z: 6, W: 5 }, { name: "SAMASKÓRA", Z: 6, W: 5 }, { name: "BRONGO", Z: 8, W: 4 }] },
];
const SZANSA_SPOTKANIA = 1;   // spotkanie, gdy na kostce wypadnie 1 (czyli 1 na 6)

/**
 * Głębokość każdego paragrafu = najmniejsza liczba przejść od paragrafu 1.
 * Przeszukiwanie wszerz (BFS): kolejka, z której bierzemy od początku,
 * a nowe paragrafy dokładamy na koniec. Wynik pamiętamy – księga się nie zmienia.
 */
let pamiecGlebokosci = { ksiega: null, wynik: null };
function glebokosci(ksiega) {
  if (pamiecGlebokosci.ksiega === ksiega) return pamiecGlebokosci.wynik;
  const wynik = { [START]: 0 };
  const kolejka = [START];
  for (let i = 0; i < kolejka.length; i++) {          // i przesuwa się jak deque.popleft()
    const nr = kolejka[i];
    const a = ksiega[nr];
    const cele = (a?.edges ?? []).flatMap((e) => [e.target, e.return_to, ...(e.possible_targets ?? [])]);
    if (a?.combat?.escape) cele.push(a.combat.escape.target);
    for (const cel of cele.map(String)) {
      if (cel in ksiega && !(cel in wynik)) { wynik[cel] = wynik[nr] + 1; kolejka.push(cel); }
    }
  }
  pamiecGlebokosci = { ksiega, wynik };
  return wynik;
}

/** Potwór na ten korytarz albo null. Pierwszy rzut: czy w ogóle; drugi: który. */
function losujSpotkanie(ksiega, nr, kostka = k6) {
  if (!ksiega[nr]?.korytarz) return null;
  const glebokosc = glebokosci(ksiega)[nr] ?? 0;
  const pula = WEDRUJACE.filter((p) => glebokosc >= p.od).at(-1);   // najgłębsza pasująca pula
  if (!pula || kostka() > SZANSA_SPOTKANIA) return null;
  return { ...pula.potwory[(kostka() - 1) % pula.potwory.length] };
}

/** Opis trwającej walki: wędrujący potwór niesie go w stanie, reszta jest w księdze. */
function opisWalki(stan, akapit) {
  return stan.walka?.opis ?? akapit?.combat ?? null;
}

// ---------------------------------------------------------------- walka

/**
 * Tworzy stan walki dla paragrafu z polem "combat" (albo null).
 * "oslona": {"ma": ["hełm"], "W": 3} – jeśli bohater ma którąś z tych rzeczy,
 * dostaje na czas tej walki zapas punktów, który przyjmuje rany przed W.
 */
function rozpocznijWalke(akapit, bohater = null) {
  const opis = akapit?.combat;
  if (!opis?.monsters?.length) return null;
  const rzecz = (opis.oslona?.ma ?? []).find((r) => (bohater?.ekwipunek ?? []).includes(r));
  return {
    oslona: rzecz ? opis.oslona.W : 0,   // ile ran jeszcze przyjmie osłona
    oslonaZ: rzecz ?? null,              // z czego jest (do pokazania na ekranie)
    kara: bohater?.karaWalki ?? null,    // kara czekająca na tę walkę, np. {Z: -1, powod: "rękawice"}
    potwory: structuredClone(opis.monsters), // kopia – nie psujemy księgi
    indeks: 0,              // z którym potworem walczymy (walka po kolei)
    rundaPotwora: 0,        // rundy z bieżącym potworem
    rundy: 0,               // wszystkie rundy
    ostatniaWygrana: null,  // czy gracz wygrał ostatnią rundę
    zakonczona: false,
    dziennik: [],           // opis rund do pokazania na ekranie
  };
}

/**
 * Rana bohatera w walce: najpierw topnieje osłona, reszta idzie w W.
 * Zmienia podaną walkę i zwraca [nowy bohater, ile przyjęła osłona].
 */
function przyjmijRane(bohater, walka, rana) {
  const zOslony = Math.min(walka?.oslona ?? 0, rana);
  if (walka) walka.oslona = (walka.oslona ?? 0) - zOslony;
  return [{ ...bohater, W: Math.max(bohater.W - (rana - zOslony), 0) }, zOslony];
}

/**
 * Liczniki to słownik {nazwa: liczba} w stanie gry, np. {"jatka": 3, "grubasy": 1}.
 * Zwraca NOWY słownik – starego nie zmieniamy (jak dict(stary, **{nazwa: n}) w Pythonie).
 */
function doliczDoLicznika(liczniki, nazwa, ile) {
  return { ...liczniki, [nazwa]: (liczniki[nazwa] ?? 0) + ile };
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
  const silaBohatera = b.suma + bohater.Z + (opis.hero_Z_bonus ?? 0) + (opis.hero_attack_bonus ?? 0) + (walka.kara?.Z ?? 0);
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
  else [bohater, wpis.oslona] = przyjmijRane(bohater, walka, rana);

  wpis.wynik = wygrana ? "trafiasz" : "obrywasz";
  wpis.rana = rana;
  walka.dziennik.push(wpis);
  walka.rundy += 1;
  walka.rundaPotwora += 1;
  walka.ostatniaWygrana = wygrana;

  if (bohater.W <= 0) {
    return { ...stan, bohater, walka: { ...walka, zakonczona: true }, koniec: "porazka" };
  }
  let liczniki = stan.liczniki ?? {};
  if (potwor.W <= 0) {
    walka.indeks += 1;
    walka.rundaPotwora = 0;
    // "licznik": "jatka" – każdy zabity potwór liczy się do nagrody (193)
    for (const nazwa of [opis.licznik ?? []].flat()) liczniki = doliczDoLicznika(liczniki, nazwa, 1);
  }
  let pokonani = stan.pokonani ?? [];
  if (!biezacyPotwor(walka)) {
    walka.zakonczona = true;
    // wszystkie potwory tego paragrafu nie żyją (wędrujący nie należy do paragrafu)
    if (!opis.wedrujacy) pokonani = [...pokonani, stan.akapit];
  }
  if (opis.rounds && walka.rundy >= opis.rounds) walka.zakonczona = true;
  if (opis.until_round_won && wygrana) walka.zakonczona = true;

  return { ...stan, bohater, walka, pokonani, liczniki };
}

/**
 * Zapisy sprzed tej zmiany nie mają listy "pokonani". Odtwarzamy ją z historii:
 * jeśli po paragrafie z walką poszedłeś dalej (nie drogą ucieczki), to wygrałeś.
 */
function uzupelnijPokonanych(stan, ksiega) {
  if (stan.pokonani) return stan;
  const pokonani = [];
  stan.historia.forEach((nr, i) => {
    const dalej = stan.historia[i + 1];
    const opis = ksiega[nr]?.combat;
    if (!opis || dalej === undefined || pokonani.includes(nr)) return;
    if (opis.escape && String(opis.escape.target) === dalej) return;
    pokonani.push(nr);
  });
  return { ...stan, pokonani };
}

/** Czy w tym paragrafie potwory zostały już kiedyś pokonane? */
function potworyPokonane(stan, akapit) {
  return Boolean(akapit?.combat) && !stan.walka && (stan.pokonani ?? []).includes(stan.akapit);
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
  [bohater] = przyjmijRane(bohater, structuredClone(stan.walka), rana);
  if (bohater.W <= 0) return { ...stan, bohater, koniec: "porazka" };
  if (opis.wedrujacy) return { ...stan, bohater, walka: null };   // zostajesz w korytarzu, potwór odchodzi
  return wykonajPrzejscie({ ...stan, bohater, walka: null }, opis.escape, null, ksiega);
}

/**
 * Które przejścia pokazać? W czasie walki – żadne.
 * Po walce na określoną liczbę rund – według wyniku ostatniej rundy.
 */
/**
 * Pytania „czy już tu byłeś?” rozstrzyga gra – zna historię wędrówki.
 *   byl_w / nie_byl_w: "11"  – czy paragraf 11 jest w historii,
 *   pierwsza_wizyta: true/false – czy jesteśmy w tym paragrafie pierwszy raz.
 * Przejścia bez takich pól zawsze przechodzą.
 */
function pamiecPozwala(stan, przejscie) {
  const byl = (nr) => stan.historia.includes(String(nr));
  if (przejscie.byl_w !== undefined && !byl(przejscie.byl_w)) return false;
  if (przejscie.nie_byl_w !== undefined && byl(przejscie.nie_byl_w)) return false;
  if (przejscie.wizyty) {
    // "wizyty": ["115", 1] – paragraf 115 odwiedzony dokładnie raz (zbrojownia)
    const [nr, ile] = przejscie.wizyty;
    if (stan.historia.filter((x) => x === String(nr)).length !== ile) return false;
  }
  if (przejscie.pierwsza_wizyta !== undefined) {
    const ileRazy = stan.historia.filter((nr) => nr === stan.akapit).length;
    if (przejscie.pierwsza_wizyta !== (ileRazy === 1)) return false;
  }
  return true;
}

/** Czy gra ukryła jakąś odpowiedź, bo pamięta, gdzie byłeś? (do komentarza) */
function pamiecRozstrzyga(stan, akapit) {
  return (akapit?.edges ?? []).some((e) => !pamiecPozwala(stan, e));
}

// ---------------------------------------------------------------- SSS poza walką

/** Paragraf każe zrobić SSS, a test jeszcze się nie odbył. */
function czekaNaSSS(stan, akapit) {
  return Boolean(akapit?.test_sss) && stan.testSSS?.akapit !== stan.akapit;
}

/** Test szczęścia w paragrafie (zasady IV): wynik zostaje do wyjścia z paragrafu. */
function testSzczescia(stan, kostka = k6) {
  const proba = sss(stan.bohater, kostka);
  return {
    ...stan,
    bohater: proba.bohater,
    testSSS: { akapit: stan.akapit, szczescie: proba.szczescie, rzut: proba.rzut, poziom: stan.bohater.S },
  };
}

// ---------------------------------------------------------------- rzuty kością w paragrafie

/** Oczka rzucone w bieżącym paragrafie (każda kość rzucana osobno). */
function oczkaTutaj(stan) {
  return stan.kosci?.akapit === stan.akapit ? stan.kosci.oczka : [];
}

/** "rzut_kosci": {"ile": 4} – czy zostały jeszcze kości do rzucenia? */
function czekaNaKosci(stan, akapit) {
  const ile = akapit?.rzut_kosci?.ile ?? 0;
  return oczkaTutaj(stan).length < ile;
}

function rzucKoscia(stan, kostka = k6) {
  return { ...stan, kosci: { akapit: stan.akapit, oczka: [...oczkaTutaj(stan), kostka()] } };
}

/** Warunki na przejściu: suma oczek w przedziale, cecha co najmniej / poniżej. */
function warunkiPozwalaja(stan, e) {
  if (e.suma) {
    const suma = oczkaTutaj(stan).reduce((a, b) => a + b, 0);   // reduce ≈ sum()
    if (suma < e.suma[0] || suma > e.suma[1]) return false;
  }
  // Przedmiot i złoto: "ma": "lina z hakiem", "zloto_min": 10
  const rzeczy = stan.bohater?.ekwipunek ?? [];
  const lista = (x) => (Array.isArray(x) ? x : [x]);         // "lina" albo ["napój", "woda"]
  if (e.ma && !lista(e.ma).some((r) => rzeczy.includes(r))) return false;
  if (e.nie_ma && lista(e.nie_ma).some((r) => rzeczy.includes(r))) return false;
  if (e.ma_wszystkie && !e.ma_wszystkie.every((r) => rzeczy.includes(r))) return false;
  if (e.zloto_min && (stan.bohater?.zloto ?? 0) < e.zloto_min) return false;
  if (e.cecha_min && stan.bohater && stan.bohater[e.cecha_min[0]] < e.cecha_min[1]) return false;
  if (e.cecha_ponizej && stan.bohater && stan.bohater[e.cecha_ponizej[0]] >= e.cecha_ponizej[1]) return false;
  // Liczniki: "licznik_min": ["zle_grane", 3] – co najmniej trzy gry ze ZŁYMI.
  if (e.licznik_min && (stan.liczniki?.[e.licznik_min[0]] ?? 0) < e.licznik_min[1]) return false;
  // Zakłady: "gdy_bankrut": true – tylko gdy przeciwnik wygrał całe złoto.
  if (e.gdy_bankrut !== undefined && e.gdy_bankrut !== (stan.zaklad?.koniec === "bankrut")) return false;
  return true;
}

function dostepnePrzejscia(stan, akapit) {
  if (czekaNaSSS(stan, akapit) || czekaNaKosci(stan, akapit)) return [];
  const doWyboru = (akapit?.edges ?? [])
    .filter((e) => pamiecPozwala(stan, e))
    .filter((e) => e.sss === undefined || e.sss === stan.testSSS?.szczescie);
  const pasuje = doWyboru.filter((e) => warunkiPozwalaja(stan, e));
  // "inaczej": true – droga „w przeciwnym razie”: tylko gdy żadna inna nie pasuje (jak else).
  const zwykle = pasuje.filter((e) => !e.inaczej);
  const spelnione = zwykle.length ? zwykle : pasuje;
  // Zabezpieczenie przed „ślepą uliczką”: gdyby warunki przedmiotów odrzuciły
  // wszystko (np. brak przedmiotu, którego zdobycia gra jeszcze nie obsługuje),
  // pokaż przejścia bez tych warunków, zamiast zostawić gracza bez wyjścia.
  const wszystkie = spelnione.length ? spelnione : doWyboru;
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

/**
 * TRYB TESTOWY: po śmierci wracasz w to samo miejsce jako zwycięzca.
 * Potwory leżą pokonane, W wraca do poziomu początkowego, gra trwa dalej.
 * Licznik wskrzeszeń zostaje w stanie – uczciwie widać, ile razy oszukiwałeś.
 */
function wskrzes(stan) {
  const bohater = { ...stan.bohater, W: stan.bohater.start.W };
  let walka = stan.walka;
  if (walka) {
    walka = structuredClone(walka);
    walka.potwory.forEach((m) => { m.W = 0; });
    walka.indeks = walka.potwory.length;
    walka.zakonczona = true;
    walka.ostatniaWygrana = true;
  }
  const pokonani = walka ? [...(stan.pokonani ?? []), stan.akapit] : stan.pokonani;
  return { ...stan, bohater, walka, pokonani, koniec: null, wskrzeszenia: (stan.wskrzeszenia ?? 0) + 1 };
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
    const przed = b.zloto;
    b.zloto = Math.max(przed + efekt.zloto, 0);
    const naprawde = b.zloto - przed;   // przegrać można najwyżej tyle, ile się ma
    opisy.push(naprawde === 0 && efekt.zloto < 0 ? "nie masz złota"
      : `${naprawde >= 0 ? "+" : "−"}${Math.abs(naprawde)} złota`);
  }
  if (efekt.kara_w_walce) {
    // Nie zmienia cech od razu: czeka na bohaterze do najbliższej walki i tylko w niej działa.
    b.karaWalki = { ...efekt.kara_w_walce };
    opisy.push(`${efekt.kara_w_walce.Z} Z w najbliższej walce`.replace("-", "−"));
  }
  if (efekt.dodaj || efekt.usun || efekt.zuzyj) {
    let rzeczy = [...(b.ekwipunek ?? [])];
    // "zuzyj": [a, b] – zużywa pierwszą z tych rzeczy, którą masz (np. jeden z napojów)
    const pierwsza = (efekt.zuzyj ?? []).find((r) => rzeczy.includes(r));
    if (pierwsza) { rzeczy.splice(rzeczy.indexOf(pierwsza), 1); opisy.push(`− ${pierwsza}`); }
    for (const r of efekt.usun ?? []) {
      const i = rzeczy.indexOf(r);
      if (i !== -1) { rzeczy.splice(i, 1); opisy.push(`− ${r}`); }   // splice ≈ del lista[i]
    }
    for (const r of efekt.dodaj ?? []) { rzeczy.push(r); opisy.push(`+ ${r}`); }
    b.ekwipunek = rzeczy;
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
  // Efekty zależne od SSS ("gdy_sss") działają osobno – dopiero po teście.
  const poTescie = !czekaNaSSS(stan, akapit) && stan.testSSS?.akapit === stan.akapit;
  if (poTescie) stan = zastosujGrupe(stan, akapit, `${stan.akapit}:sss`,
    (e) => e.gdy_sss === stan.testSSS.szczescie);
  // Efekty zależne od rzutu ("gdy_suma": [od, do]) – dopiero gdy wszystkie kości
  // są rzucone. Klucz zawiera długość historii, więc przy każdej wizycie liczą się
  // od nowa (315 to pułapka, do której trafia się z kilku miejsc).
  if (akapit?.rzut_kosci && !czekaNaKosci(stan, akapit)) {
    stan = policzTrafienia(stan, akapit);
    const suma = oczkaTutaj(stan).reduce((a, b) => a + b, 0);
    stan = zastosujGrupe(stan, akapit, `${stan.akapit}:kosci:${stan.historia.length}`,
      (e) => e.gdy_suma && suma >= e.gdy_suma[0] && suma <= e.gdy_suma[1]
        && (e.gdy_parzysta === undefined || e.gdy_parzysta === (suma % 2 === 0)),
      (e) => zRzutu(e, suma, stan.bohater));
  }
  return zastosujGrupe(stan, akapit, stan.akapit, (e) => e.gdy_sss === undefined && !e.gdy_suma,
    (e) => zLicznika(e, stan.liczniki ?? {}));
}

/**
 * Próby na kościach (grubasy w 265, 359, 217):
 *   "rzut_kosci": {"ile": 4, "na_probe": 2, "trafienie": 5, "licznik": "grubasy"}
 * Kości dzielimy na próby po "na_probe" sztuk (domyślnie 1); próba jest udana,
 * gdy choć jedna kość pokazuje "trafienie". Udane próby dopisujemy do licznika.
 */
function ileTrafien(oczka, rzut) {
  const naProbe = rzut.na_probe ?? 1;
  let trafienia = 0;
  for (let i = 0; i < oczka.length; i += naProbe) {
    if (oczka.slice(i, i + naProbe).includes(rzut.trafienie)) trafienia += 1;   // slice ≈ oczka[i:i+n]
  }
  return trafienia;
}

function policzTrafienia(stan, akapit) {
  const rzut = akapit.rzut_kosci;
  const klucz = `${stan.akapit}:trafienia:${stan.historia.length}`;
  const zastosowane = stan.zastosowane ?? [];
  if (!rzut.licznik || zastosowane.includes(klucz)) return stan;
  const n = ileTrafien(oczkaTutaj(stan), rzut);
  return {
    ...stan,
    liczniki: doliczDoLicznika(stan.liczniki ?? {}, rzut.licznik, n),
    zmiany: [...(stan.zmiany ?? []), n ? `trafienia: ${n}` : "pudło"],
    zastosowane: [...zastosowane, klucz],
  };
}

/** {"zloto_za": {"licznik": "jatka", "po": 5}} → {"zloto": 5 × licznik} (nagroda w 193 i 26). */
function zLicznika(efekt, liczniki) {
  if (!efekt.zloto_za) return efekt;
  const { zloto_za: z, ...reszta } = efekt;          // reszta = efekt bez pola zloto_za
  const nagroda = (liczniki[z.licznik] ?? 0) * z.po;
  return nagroda ? { ...reszta, zloto: nagroda } : reszta;
}

/**
 * Wartość zależna od rzutu: "kosc" = tyle, ile wypadło; "-kosc" = minus tyle.
 *   {"zloto": "kosc"}  – wygrywasz tyle złota (201)
 *   {"zloto": "-kosc"} – przegrywasz tyle złota, najwyżej wszystko (145)
 *   {"W": "-kosc", "zostaw_W": 1} – tracisz tyle W, ale zostaje co najmniej 1 (240)
 * Zwraca zwykły efekt z liczbami, który rozumie zmienCechy().
 */
function zRzutu(efekt, suma, bohater) {
  const wynik = { ...efekt };
  for (const pole of ["W", "zloto"]) {
    if (efekt[pole] === "kosc") wynik[pole] = suma;
    if (efekt[pole] === "-kosc") wynik[pole] = -suma;
  }
  if ("zostaw_W" in efekt && wynik.W < 0) {
    wynik.W = -Math.min(-wynik.W, Math.max(bohater.W - efekt.zostaw_W, 0));
  }
  return wynik;
}

function zastosujGrupe(stan, akapit, klucz, pasuje, przelicz = (e) => e) {
  const efekty = (akapit?.efekty ?? []).filter(pasuje);
  const zastosowane = stan.zastosowane ?? [];
  if (!efekty.length || zastosowane.includes(klucz) || !efektyGotowe(stan)) return stan;
  let bohater = stan.bohater;
  const zmiany = [];
  for (const e of efekty.filter(czyAutomatyczny)) {
    const wynik = zmienCechy(bohater, przelicz(e));
    bohater = wynik.bohater;
    zmiany.push(...wynik.opisy);
  }
  const nowy = { ...stan, bohater, zmiany: [...(stan.zmiany ?? []), ...zmiany], zastosowane: [...zastosowane, klucz] };
  return bohater.W <= 0 ? { ...nowy, koniec: "porazka" } : nowy;
}

/** Efekty do wyboru („Możesz je wziąć”), jeszcze niewzięte. */
function dostepneOpcje(stan, akapit) {
  if (!efektyGotowe(stan)) return [];
  const wybrane = stan.wybrane ?? [];
  // "limit_opcji": 2 – „możesz wziąć najwyżej dwie z tych rzeczy” (np. 119)
  const wzieteTutaj = wybrane.filter((k) => k.startsWith(`${stan.akapit}:`)).length;
  if (akapit?.limit_opcji && wzieteTutaj >= akapit.limit_opcji) return [];
  const zloto = stan.bohater.zloto ?? 0;
  return (akapit?.efekty ?? [])
    .map((efekt, i) => ({ efekt, klucz: `${stan.akapit}:${i}` }))
    .filter(({ efekt, klucz }) => efekt.opcja && !wybrane.includes(klucz))
    .filter(({ efekt }) => !(efekt.zloto < 0 && zloto < -efekt.zloto))    // nie stać cię
    .filter(({ efekt }) => !efekt.wymaga || (stan.bohater.ekwipunek ?? []).includes(efekt.wymaga));
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

// ---------------------------------------------------------------- eliksir (zasady I i V)

const ELIKSIRY = { Z: "ZRĘCZNOŚCI", W: "WYTRZYMAŁOŚCI", S: "SZCZĘŚCIA" };

/** Jedna butelka na wyprawę; wystarcza na dwa łyki. Zwraca nowego bohatera. */
function wybierzEliksir(bohater, cecha) {
  if (!(cecha in ELIKSIRY)) throw new Error(`Nie ma eliksiru: ${cecha}`);
  return { ...bohater, eliksir: { cecha, lyki: 2 } };
}

function moznaPicEliksir(stan) {
  return Boolean(stan.bohater) && !stan.koniec && (stan.bohater.eliksir?.lyki ?? 0) > 0;
}

/**
 * Łyk eliksiru: cecha wraca do poziomu początkowego.
 * Eliksir SZCZĘŚCIA dodatkowo podnosi poziom początkowy o 1 – to jedyny
 * przypadek, gdy cecha może przekroczyć to, co wylosowałeś na starcie.
 */
function wypijEliksir(stan) {
  if (!moznaPicEliksir(stan)) return stan;
  const b = stan.bohater;
  const { cecha, lyki } = b.eliksir;
  const start = { ...b.start };
  if (cecha === "S") start.S += 1;
  const bohater = { ...b, start, [cecha]: start[cecha], eliksir: { cecha, lyki: lyki - 1 } };
  const zysk = bohater[cecha] - b[cecha];
  const opis = `eliksir ${ELIKSIRY[cecha]}: ${zysk > 0 ? `+${zysk} ${cecha}` : "bez zmian"}`;
  return { ...stan, bohater, zmiany: [...(stan.zmiany ?? []), opis] };
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

// ---------------------------------------------------------------- tryb tajemny

/**
 * Generator liczb losowych z ziarnem (algorytm mulberry32). To samo ziarno daje
 * zawsze ten sam ciąg – jak random.Random(ziarno) w Pythonie. Math.random()
 * ziarna nie ma, a my musimy odtworzyć tę samą numerację po wczytaniu zapisu.
 */
function losowaZZiarnem(ziarno) {
  let a = ziarno >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/**
 * Tajna numeracja: słownik {prawdziwy numer: numer na ekranie}. Numery są te same
 * (1…387), tylko przetasowane, więc książka i pamięć z poprzednich gier nie pomogą.
 * Tasowanie Fishera–Yatesa: idziemy od końca i zamieniamy z losowym wcześniejszym.
 */
function tajnaNumeracja(ziarno, numery) {
  const losuj = losowaZZiarnem(ziarno);
  const tajne = [...numery];
  for (let i = tajne.length - 1; i > 0; i--) {
    const j = Math.floor(losuj() * (i + 1));
    [tajne[i], tajne[j]] = [tajne[j], tajne[i]];     // zamiana miejscami, jak a, b = b, a
  }
  return Object.fromEntries(numery.map((nr, i) => [nr, tajne[i]]));
}

// Miejsca w tekście, gdzie stoi numer paragrafu: „patrz 35, 269 lub 110”,
// „patrz najpierw 315, a potem 274”, „Patrz - 15”, „do paragrafu 122”, „docierasz do 102”.
const ODSYLACZ = /(patrz(?:\s+najpierw)?(?:\s+-)?\s+|paragraf\p{L}*\s+|docierasz\s+do\s+|przeciskasz\s+się\s+do\s+)(\d+(?:(?:\s*,\s*|\s+lub\s+|\s+albo\s+|\s+i\s+|,?\s+a\s+potem\s+(?:patrz\s+)?)\d+)*)/giu;

/** Podmienia numery paragrafów w tekście na tajne. Inne liczby (cechy, złoto) zostają. */
function przepiszNumery(tekst, numeracja) {
  if (!numeracja) return tekst;
  return tekst.replace(ODSYLACZ, (_, wstep, lista) =>
    wstep + lista.replace(/\d+/g, (nr) => numeracja[nr] ?? nr));
}

// ---------------------------------------------------------------- potrząśnięcie telefonem

/**
 * Wykrywa potrząśnięcie na podstawie kolejnych odczytów czujnika ruchu.
 * Zwraca funkcję, która pamięta poprzedni odczyt (domknięcie – jak funkcja
 * wewnętrzna z "nonlocal" w Pythonie). Wywołujemy ją dla każdego odczytu:
 *   wykryj({x, y, z}, czasMs) → true, gdy właśnie rozpoznano potrząśnięcie.
 * Zasada: dwa mocne szarpnięcia (zmiana przyspieszenia ≥ prog) w ciągu "okno" ms.
 * Po rozpoznaniu przez "przerwa" ms nic nie zgłaszamy – jeden gest = jeden rzut.
 */
function wykrywaczPotrzasniecia({ prog = 15, okno = 600, przerwa = 1000 } = {}) {
  let poprzedni = null;       // ostatni odczyt
  let szarpniecie = -Infinity; // czas ostatniego mocnego szarpnięcia
  let ostatnie = -Infinity;    // czas ostatniego rozpoznanego potrząśnięcia
  return (odczyt, czas) => {
    if (!odczyt || odczyt.x == null) return false;
    const p = poprzedni;
    poprzedni = odczyt;
    if (!p || czas - ostatnie < przerwa) return false;
    const zmiana = Math.abs(odczyt.x - p.x) + Math.abs(odczyt.y - p.y) + Math.abs(odczyt.z - p.z);
    if (zmiana < prog) return false;
    if (czas - szarpniecie <= okno) {
      ostatnie = czas;
      szarpniecie = -Infinity;
      return true;
    }
    szarpniecie = czas;
    return false;
  };
}

// W Node.js (testy) udostępniamy funkcje przez module.exports,
// w przeglądarce są po prostu globalne.
if (typeof module !== "undefined") {
  module.exports = {
    START, k6, rzut2k, nowyBohater, sss, nowaGra, wykonajPrzejscie,
    rozpocznijWalke, przyjmijRane, biezacyPotwor, rundaWalki, moznaUciec, ucieczka, wskrzes, potworyPokonane, uzupelnijPokonanych,
    dostepnePrzejscia, tekstAkapitu, etykieta, czekaNaSSS, testSzczescia,
    oczkaTutaj, czekaNaKosci, rzucKoscia, ileTrafien, wykrywaczPotrzasniecia,
    losowaZZiarnem, tajnaNumeracja, przepiszNumery,
    glebokosci, losujSpotkanie, opisWalki, WEDRUJACE,
    maksStawka, postawZaklad,
    wyjscia, grafWedrowki, pierwszeZdanie, pamiecPozwala, pamiecRozstrzyga,
    ELIKSIRY, wybierzEliksir, moznaPicEliksir, wypijEliksir,
    zmienCechy, zastosujEfekty, dostepneOpcje, wezOpcje, moznaJesc, zjedzPosilek,
  };
}
