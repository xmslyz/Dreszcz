// Uruchomienie: node --test web/
// node:test działa jak unittest w Pythonie.
const test = require("node:test");
const assert = require("node:assert");
const { nowaGra, wykonajPrzejscie, etykieta } = require("./silnik.js");

test("zwykłe przejście zmienia paragraf i historię", () => {
  const stan = wykonajPrzejscie(nowaGra(), { target: "25" });
  assert.strictEqual(stan.akapit, "25");
  assert.deepStrictEqual(stan.historia, ["1", "25"]);
});

test("return_to i RETURN działają jak wywołanie i powrót", () => {
  let stan = { ...nowaGra(), akapit: "52" };
  stan = wykonajPrzejscie(stan, { target: "315", return_to: "274" });
  assert.strictEqual(stan.akapit, "315");
  stan = wykonajPrzejscie(stan, { target: "RETURN" });
  assert.strictEqual(stan.akapit, "274");
  assert.deepStrictEqual(stan.stos, []);
});

test("KEYS_SUM prowadzi do numeru podanego przez gracza", () => {
  const stan = wykonajPrzejscie(nowaGra(), { target: "KEYS_SUM" }, 204);
  assert.strictEqual(stan.akapit, "204");
});

test("END kończy grę, ending=victory to zwycięstwo", () => {
  assert.strictEqual(wykonajPrzejscie(nowaGra(), { target: "END" }).koniec, "porazka");
  assert.strictEqual(
    wykonajPrzejscie(nowaGra(), { target: "END", ending: "victory" }).koniec,
    "zwyciestwo"
  );
});

test("stary stan pozostaje bez zmian", () => {
  const stary = nowaGra();
  wykonajPrzejscie(stary, { target: "25", return_to: "9" });
  assert.deepStrictEqual(stary, nowaGra());
});

test("etykieta bez label to „Patrz N”", () => {
  assert.strictEqual(etykieta({ target: 25 }), "Patrz 25");
});

// ---------------------------------------------------------------- walka
const s = require("./silnik.js");

/** „Ustawiona” kostka: zwraca kolejne podane wyniki (jak mock w Pythonie). */
function kostka(...wyniki) {
  return () => wyniki.shift();
}

function stanWalki(opis, bohater = { Z: 8, W: 20, S: 9, start: { Z: 8, W: 20, S: 9 }, prowiant: 8 }) {
  return { ...s.nowaGra(bohater), walka: s.rozpocznijWalke({ combat: opis }) };
}

test("nowy bohater: Z=1K+6, W=2K+12, S=1K+6", () => {
  const b = s.nowyBohater(kostka(3, 2, 5, 6));
  assert.deepStrictEqual([b.Z, b.W, b.S], [9, 19, 12]);
});

test("wygrana runda zabiera potworowi 2 W", () => {
  const opis = { monsters: [{ name: "ORK", Z: 6, W: 4 }] };
  // potwór 1+1+6=8, bohater 6+6+8=20
  const st = s.rundaWalki(stanWalki(opis), opis, false, kostka(1, 1, 6, 6));
  assert.strictEqual(st.walka.potwory[0].W, 2);
  assert.strictEqual(st.bohater.W, 20);
});

test("przegrana runda zabiera bohaterowi 2 W", () => {
  const opis = { monsters: [{ name: "ORK", Z: 6, W: 4 }] };
  const st = s.rundaWalki(stanWalki(opis), opis, false, kostka(6, 6, 1, 1));
  assert.strictEqual(st.bohater.W, 18);
});

test("remis nie jest rundą", () => {
  const opis = { monsters: [{ name: "ORK", Z: 8, W: 4 }] };
  const st = s.rundaWalki(stanWalki(opis), opis, false, kostka(3, 3, 3, 3));
  assert.strictEqual(st.walka.rundy, 0);
});

test("SSS ze szczęściem: rana potwora 4, a S spada o 1", () => {
  const opis = { monsters: [{ name: "TROLL", Z: 6, W: 8 }] };
  // runda wygrana, SSS: 2+2=4 ≤ 9
  const st = s.rundaWalki(stanWalki(opis), opis, true, kostka(1, 1, 6, 6, 2, 2));
  assert.strictEqual(st.walka.potwory[0].W, 4);
  assert.strictEqual(st.bohater.S, 8);
});

test("zabicie ostatniego potwora kończy walkę i odsłania przejścia", () => {
  const opis = { monsters: [{ name: "ORK", Z: 6, W: 2 }] };
  const st = s.rundaWalki(stanWalki(opis), opis, false, kostka(1, 1, 6, 6));
  assert.strictEqual(st.walka.zakonczona, true);
  assert.strictEqual(s.dostepnePrzejscia(st, { edges: [{ target: "120" }] }).length, 1);
});

test("w trakcie walki nie ma przejść", () => {
  const opis = { monsters: [{ name: "ORK", Z: 6, W: 4 }] };
  assert.deepStrictEqual(s.dostepnePrzejscia(stanWalki(opis), { edges: [{ target: "120" }] }), []);
});

test("śmierć bohatera kończy grę", () => {
  const opis = { monsters: [{ name: "GIGANT", Z: 10, W: 12 }] };
  const b = { Z: 7, W: 2, S: 7, start: { Z: 7, W: 20, S: 7 }, prowiant: 8 };
  const st = s.rundaWalki(stanWalki(opis, b), opis, false, kostka(6, 6, 1, 1));
  assert.strictEqual(st.koniec, "porazka");
});

test("ucieczka po pierwszej rundzie kosztuje 2 W", () => {
  const opis = { monsters: [{ name: "GARAZAN", Z: 10, W: 10 }], escape: { target: "372", from_round: 1 } };
  let st = stanWalki(opis);
  assert.strictEqual(s.moznaUciec(st.walka, opis), false);
  st = s.rundaWalki(st, opis, false, kostka(1, 1, 6, 6));
  assert.strictEqual(s.moznaUciec(st.walka, opis), true);
  st = s.ucieczka(st, opis);
  assert.strictEqual(st.akapit, "372");
  assert.strictEqual(st.bohater.W, 18);
  assert.strictEqual(st.walka, null);
});

test("walka na jedną rundę: przejście zależy od wyniku (paragraf 109)", () => {
  const opis = { monsters: [{ name: "KROMAA", Z: 7, W: 8 }], rounds: 1 };
  const akapit = { edges: [{ target: "77", condition: "round_won" }, { target: "163", condition: "round_lost" }] };
  const st = s.rundaWalki(stanWalki(opis), opis, false, kostka(1, 1, 6, 6));
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit).map((e) => e.target), ["77"]);
});

test("tekst po „|” widać dopiero po walce", () => {
  const akapit = { text: "ORK naciera. ORK Z:6 W:4 | Rozglądasz się.", combat: { monsters: [{ name: "ORK", Z: 6, W: 2 }] } };
  let st = { ...s.nowaGra({ Z: 8, W: 20, S: 9, start: { Z: 8, W: 20, S: 9 }, prowiant: 8 }), walka: s.rozpocznijWalke(akapit) };
  assert.strictEqual(s.tekstAkapitu(st, akapit), "ORK naciera. ORK Z:6 W:4");
  st = s.rundaWalki(st, akapit.combat, false, kostka(1, 1, 6, 6));
  assert.strictEqual(s.tekstAkapitu(st, akapit), "ORK naciera. ORK Z:6 W:4 Rozglądasz się.");
});

// ---------------------------------------------------------------- efekty
const bohaterTestowy = () => ({ Z: 8, W: 15, S: 7, start: { Z: 9, W: 20, S: 9 }, prowiant: 8, zloto: 0 });

test("efekt nie przekracza poziomu początkowego", () => {
  const { bohater, opisy } = s.zmienCechy(bohaterTestowy(), { S: 5, zloto: 3 });
  assert.strictEqual(bohater.S, 9);
  assert.strictEqual(bohater.zloto, 3);
  assert.deepStrictEqual(opisy, ["+2 S", "+3 złota"]);  // przycięte do 9
});

test("efekty automatyczne działają raz na grę", () => {
  const akapit = { efekty: [{ S: 2 }] };
  let st = { ...s.nowaGra(bohaterTestowy()), akapit: "89" };
  st = s.zastosujEfekty(st, akapit);
  assert.strictEqual(st.bohater.S, 9);
  st = { ...st, bohater: { ...st.bohater, S: 5 } };
  assert.strictEqual(s.zastosujEfekty(st, akapit).bohater.S, 5);
});

test("efekty czekają na koniec walki", () => {
  const akapit = { efekty: [{ S: 1 }], combat: { monsters: [{ name: "TROLL", Z: 8, W: 8 }] } };
  const st = { ...s.nowaGra(bohaterTestowy()), walka: s.rozpocznijWalke(akapit) };
  assert.strictEqual(s.zastosujEfekty(st, akapit).bohater.S, 7);
});

test("złoto do wzięcia jest opcją, a posiłek daje +4 W", () => {
  const akapit = { efekty: [{ zloto: 3, opcja: "Weź" }, { posilek: true }] };
  let st = { ...s.nowaGra(bohaterTestowy()), akapit: "89" };
  const [opcja] = s.dostepneOpcje(st, akapit);
  st = s.wezOpcje(st, opcja);
  assert.strictEqual(st.bohater.zloto, 3);
  assert.deepStrictEqual(s.dostepneOpcje(st, akapit), []);
  assert.strictEqual(s.moznaJesc(st, akapit), true);
  st = s.zjedzPosilek(st);
  assert.deepStrictEqual([st.bohater.W, st.bohater.prowiant], [19, 7]);
  assert.strictEqual(s.moznaJesc(st, akapit), false);
});

test("połowa Wytrzymałości (paragraf 110)", () => {
  assert.strictEqual(s.zmienCechy(bohaterTestowy(), { W: "pol" }).bohater.W, 7);
});

// ---------------------------------------------------------------- mapa
test("graf wędrówki: odwiedziny, pętle i niezbadane wyjścia", () => {
  const ksiega = {
    "1": { text: "Start. Dalej.", edges: [{ target: "25" }] },
    "25": { text: "Skrzyżowanie T. Idź.", edges: [{ target: "64" }, { target: "90" }, { target: "END" }] },
    "64": { text: "Korytarz.", edges: [{ target: "25" }] },
  };
  const stan = { ...s.nowaGra(), historia: ["1", "25", "64", "25", "64"], akapit: "64" };
  const g = s.grafWedrowki(stan, ksiega);
  const w = Object.fromEntries(g.wezly.map((x) => [x.id, x]));
  assert.strictEqual(w["64"].odwiedzin, 2);
  assert.strictEqual(w["64"].biezacy, true);
  assert.strictEqual(w["25"].niezbadane, 1);           // tylko 90; END się nie liczy
  assert.strictEqual(g.krawedzie.length, 3);           // 1>25, 25>64, 64>25 – bez powtórek
  assert.strictEqual(s.pierwszeZdanie(ksiega["25"]), "Skrzyżowanie T.");
});

test("„czy już tu byłeś?” rozstrzyga historia (paragraf 331)", () => {
  const akapit = { edges: [{ target: "59", byl_w: "11" }, { target: "11", nie_byl_w: "11" }] };
  let st = { ...s.nowaGra(), historia: ["1", "331"], akapit: "331" };
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit).map((e) => e.target), ["11"]);
  assert.strictEqual(s.pamiecRozstrzyga(st, akapit), true);
  st = { ...st, historia: ["1", "331", "11", "40", "331"] };
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit).map((e) => e.target), ["59"]);
});

test("pierwsza wizyta w paragrafie (214, 350)", () => {
  const akapit = { edges: [{ target: "65", pierwsza_wizyta: true }, { target: "172", pierwsza_wizyta: false }] };
  let st = { ...s.nowaGra(), historia: ["1", "214"], akapit: "214" };
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit).map((e) => e.target), ["65"]);
  st = { ...st, historia: ["1", "214", "65", "214"] };
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit).map((e) => e.target), ["172"]);
});

// ---------------------------------------------------------------- ekwipunek
const zEkwipunkiem = () => ({ ...bohaterTestowy(), ekwipunek: ["miecz", "tarcza"] });

test("łupy do wyboru z limitem (paragraf 119: najwyżej dwie rzeczy)", () => {
  const akapit = {
    limit_opcji: 2,
    efekty: ["lina", "flasza", "skalp"].map((r) => ({ dodaj: [r], opcja: `Weź: ${r}` })),
  };
  let st = { ...s.nowaGra(zEkwipunkiem()), akapit: "119" };
  st = s.wezOpcje(st, s.dostepneOpcje(st, akapit)[0]);
  st = s.wezOpcje(st, s.dostepneOpcje(st, akapit)[0]);
  assert.deepStrictEqual(st.bohater.ekwipunek, ["miecz", "tarcza", "lina", "flasza"]);
  assert.deepStrictEqual(s.dostepneOpcje(st, akapit), []);
});

test("zakup tylko wtedy, gdy stać cię na niego (paragraf 55)", () => {
  const akapit = { efekty: [{ dodaj: ["pal"], zloto: -15, opcja: "Kup" }] };
  let st = { ...s.nowaGra({ ...zEkwipunkiem(), zloto: 10 }), akapit: "55" };
  assert.strictEqual(s.dostepneOpcje(st, akapit).length, 0);
  st = { ...st, bohater: { ...st.bohater, zloto: 20 } };
  st = s.wezOpcje(st, s.dostepneOpcje(st, akapit)[0]);
  assert.strictEqual(st.bohater.zloto, 5);
  assert.ok(st.bohater.ekwipunek.includes("pal"));
});

test("wymiana na przejściu: motyl za złoto (353 → 262)", () => {
  const st0 = s.nowaGra({ ...zEkwipunkiem(), ekwipunek: ["miecz", "blaszany motyl"] });
  const st = s.wykonajPrzejscie(st0, { target: "262", efekt: { zloto: 10, usun: ["blaszany motyl"] } });
  assert.deepStrictEqual(st.bohater.ekwipunek, ["miecz"]);
  assert.strictEqual(st.bohater.zloto, 10);
  assert.deepStrictEqual(st.zmiany, ["+10 złota", "− blaszany motyl"]);
});

test("zbrojownia: pierwsza czy druga rzecz (wizyty w 115)", () => {
  const akapit = { edges: [{ target: "115", wizyty: ["115", 1] }, { target: "68", wizyty: ["115", 2] }] };
  let st = { ...s.nowaGra(), historia: ["1", "115", "298", "324"], akapit: "324" };
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit).map((e) => e.target), ["115"]);
  st = { ...st, historia: ["1", "115", "298", "324", "115", "37", "324"] };
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit).map((e) => e.target), ["68"]);
});

test("tryb testowy: wskrzeszenie jako zwycięzca", () => {
  const akapit = { combat: { monsters: [{ name: "DEMON", Z: 8, W: 5 }] }, edges: [{ target: "297" }] };
  const b = { ...bohaterTestowy(), W: 2 };
  let st = { ...s.nowaGra(b), walka: s.rozpocznijWalke(akapit) };
  st = s.rundaWalki(st, akapit.combat, false, kostka(6, 6, 1, 1));
  assert.strictEqual(st.koniec, "porazka");
  st = s.wskrzes(st);
  assert.strictEqual(st.koniec, null);
  assert.strictEqual(st.bohater.W, 20);
  assert.strictEqual(st.wskrzeszenia, 1);
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit).map((e) => e.target), ["297"]);
});

// ---------------------------------------------------------------- SSS poza walką
test("SSS w paragrafie (242): najpierw test, potem tylko pasujące przejście", () => {
  const akapit = { test_sss: true, edges: [{ target: "233", sss: true }, { target: "111", sss: false }] };
  let st = { ...s.nowaGra(bohaterTestowy()), akapit: "242" };   // S = 7
  assert.strictEqual(s.czekaNaSSS(st, akapit), true);
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit), []);
  st = s.testSzczescia(st, kostka(3, 3));                        // 6 ≤ 7 → szczęście
  assert.strictEqual(st.bohater.S, 6);
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit).map((e) => e.target), ["233"]);
  st = s.wykonajPrzejscie(st, { target: "233" });
  assert.strictEqual(st.testSSS, null);                          // nowy paragraf – nowy test
});

test("efekt zależny od SSS (284: bez S −2 W)", () => {
  const akapit = { test_sss: true, efekty: [{ W: -2, gdy_sss: false }], edges: [{ target: "50" }] };
  let st = { ...s.nowaGra(bohaterTestowy()), akapit: "284" };
  assert.strictEqual(s.zastosujEfekty(st, akapit).bohater.W, 15);   // przed testem nic
  st = s.testSzczescia(st, kostka(6, 6));                          // 12 > 7 → pech
  st = s.zastosujEfekty(st, akapit);
  assert.strictEqual(st.bohater.W, 13);
  assert.strictEqual(s.zastosujEfekty(st, akapit).bohater.W, 13);   // tylko raz
});

// ---------------------------------------------------------------- rzuty kością w paragrafie
test("cztery kości rzucane osobno (112): przejście po sumie", () => {
  const akapit = { rzut_kosci: { ile: 4 }, edges: [{ target: "28", suma: [18, 24] }, { target: "291", suma: [4, 17] }] };
  let st = { ...s.nowaGra(bohaterTestowy()), akapit: "112" };
  for (const v of [6, 5, 4]) st = s.rzucKoscia(st, () => v);
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit), []);        // jeszcze jedna kość
  st = s.rzucKoscia(st, () => 3);                                     // 6+5+4+3 = 18
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit).map((e) => e.target), ["28"]);
  assert.strictEqual(s.wykonajPrzejscie(st, { target: "28" }).kosci, null);
});

test("warunek cechy (28: co najmniej 18 W)", () => {
  const akapit = { edges: [{ target: "177", cecha_min: ["W", 18] }, { target: "330", cecha_ponizej: ["W", 18] }] };
  const st = { ...s.nowaGra(bohaterTestowy()), akapit: "28" };       // W = 15
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit).map((e) => e.target), ["330"]);
});

test("pokonane potwory nie wstają po powrocie (pętla przez 69)", () => {
  const ksiega = { "69": { combat: { monsters: [{ name: "UPIÓR", Z: 5, W: 2 }] }, edges: [{ target: "291" }] } };
  let st = s.wykonajPrzejscie({ ...s.nowaGra(bohaterTestowy()), akapit: "319" }, { target: "69" }, null, ksiega);
  assert.ok(st.walka);
  st = s.rundaWalki(st, ksiega["69"].combat, false, kostka(1, 1, 6, 6));
  assert.deepStrictEqual(st.pokonani, ["69"]);
  st = s.wykonajPrzejscie({ ...st, akapit: "319" }, { target: "69" }, null, ksiega);
  assert.strictEqual(st.walka, null);
  assert.strictEqual(s.potworyPokonane(st, ksiega["69"]), true);
  assert.deepStrictEqual(s.dostepnePrzejscia(st, ksiega["69"]).map((e) => e.target), ["291"]);
});

test("stary zapis: pokonani odtworzeni z historii", () => {
  const ksiega = { "69": { combat: { monsters: [] } }, "2": { combat: { monsters: [], escape: { target: "372" } } } };
  const st = s.uzupelnijPokonanych({ ...s.nowaGra(), historia: ["1", "69", "305", "2", "372"] }, ksiega);
  assert.deepStrictEqual(st.pokonani, ["69"]);   // z 2 uciekłeś do 372
});

test("207: lina tylko z liną, smok tylko za 10 złota, woda tylko z naczyniem", () => {
  const akapit = {
    efekty: [{ W: 3, opcja: "Wypij", wymaga: "naczynie z zaczarowaną wodą" }],
    edges: [{ target: "35", zloto_min: 10 }, { target: "269", ma: "lina z hakiem" }, { target: "74" }],
  };
  let st = { ...s.nowaGra({ ...bohaterTestowy(), ekwipunek: ["miecz"], zloto: 5 }), akapit: "207" };
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit).map((e) => e.target), ["74"]);
  assert.deepStrictEqual(s.dostepneOpcje(st, akapit), []);
  st = { ...st, bohater: { ...st.bohater, zloto: 10, ekwipunek: ["miecz", "lina z hakiem", "naczynie z zaczarowaną wodą"] } };
  assert.deepStrictEqual(s.dostepnePrzejscia(st, akapit).map((e) => e.target), ["35", "269", "74"]);
  assert.strictEqual(s.dostepneOpcje(st, akapit).length, 1);
});
