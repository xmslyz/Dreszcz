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

test("napoje: 167 pyta o picie, 358 zużywa napój niewidzialności", () => {
  const napoje = ["flasza z napojem niewidzialności", "eliksir niewidzialności"];
  const a358 = { edges: [{ target: "343", ma: napoje, efekt: { zuzyj: napoje } }, { target: "162", nie_ma: napoje }] };
  let st = { ...s.nowaGra({ ...bohaterTestowy(), ekwipunek: ["miecz"] }), akapit: "358" };
  assert.deepStrictEqual(s.dostepnePrzejscia(st, a358).map((e) => e.target), ["162"]);
  st = { ...st, bohater: { ...st.bohater, ekwipunek: ["miecz", "eliksir niewidzialności"] } };
  const [przejscie] = s.dostepnePrzejscia(st, a358);
  assert.strictEqual(przejscie.target, "343");
  assert.deepStrictEqual(s.wykonajPrzejscie(st, przejscie).bohater.ekwipunek, ["miecz"]);
});

test("63: tylko broń, którą masz; użyta broń znika z plecaka", () => {
  const ksiega = JSON.parse(require("node:fs").readFileSync(require("node:path").join(__dirname, "..", "shiver.json"), "utf8"));
  let st = { ...s.nowaGra({ ...bohaterTestowy(), ekwipunek: ["miecz", "metalowa tarcza"] }), akapit: "63" };
  const wybory = s.dostepnePrzejscia(st, ksiega["63"]);
  assert.deepStrictEqual(wybory.map((e) => e.target), ["216"]);
  st = s.wykonajPrzejscie(st, wybory[0]);
  assert.deepStrictEqual(st.bohater.ekwipunek, ["miecz"]);
  st = { ...st, akapit: "63" };
  assert.deepStrictEqual(s.dostepnePrzejscia(st, ksiega["63"]).map((e) => e.target), ["275"]);
});

test("zabezpieczenie: gdy warunki odrzucą wszystko, gracz nie zostaje bez wyjścia", () => {
  const akapit = { edges: [{ target: "321", ma: "motyl" }, { target: "9", ma: "pal" }] };
  const st = { ...s.nowaGra({ ...bohaterTestowy(), ekwipunek: [] }), akapit: "22" };
  assert.strictEqual(s.dostepnePrzejscia(st, akapit).length, 2);
});

// ---------------------------------------------------------------- osłona (hełm w 2)
const GARAZAN = { combat: { monsters: [{ name: "GARAZAN", Z: 10, W: 10 }], escape: { target: "372", from_round: 1 },
  oslona: { ma: ["hełm", "hełm garnkowy"], W: 3 } } };
const zHelmem = (W = 20) => ({ Z: 8, W, S: 9, start: { Z: 8, W: 20, S: 9 }, prowiant: 8, ekwipunek: ["hełm"] });

test("osłona: bez hełmu nie ma zapasu, z hełmem są 3 punkty", () => {
  assert.strictEqual(s.rozpocznijWalke(GARAZAN, { ekwipunek: [] }).oslona, 0);
  assert.strictEqual(s.rozpocznijWalke(GARAZAN, zHelmem()).oslona, 3);
});

test("osłona: rany idą najpierw w hełm, potem w W", () => {
  let st = { ...s.nowaGra(zHelmem()), walka: s.rozpocznijWalke(GARAZAN, zHelmem()) };
  st = s.rundaWalki(st, GARAZAN.combat, false, kostka(6, 6, 1, 1));   // rana 2: cała w hełm
  assert.deepStrictEqual([st.bohater.W, st.walka.oslona], [20, 1]);
  st = s.rundaWalki(st, GARAZAN.combat, false, kostka(6, 6, 1, 1));   // rana 2: 1 w hełm, 1 w W
  assert.deepStrictEqual([st.bohater.W, st.walka.oslona], [19, 0]);
  st = s.rundaWalki(st, GARAZAN.combat, false, kostka(6, 6, 1, 1));   // hełm wyczerpany
  assert.strictEqual(st.bohater.W, 17);
});

test("osłona: działa też przy pełnej W i ratuje przy W=2", () => {
  const b = zHelmem(2);
  const st = s.rundaWalki({ ...s.nowaGra(b), walka: s.rozpocznijWalke(GARAZAN, b) }, GARAZAN.combat, false, kostka(6, 6, 1, 1));
  assert.strictEqual(st.bohater.W, 2);
  assert.notStrictEqual(st.koniec, "porazka");
});

test("osłona: wejście do paragrafu 2 z hełmem włącza ją samo", () => {
  const st = wykonajPrzejscie({ ...nowaGra(zHelmem()) }, { target: "2" }, null, { 2: GARAZAN });
  assert.strictEqual(st.walka.oslona, 3);
});

// ---------------------------------------------------------------- efekty zależne od rzutu
const PULAPKA = { text: "", rzut_kosci: { ile: 1 }, efekty: [{ gdy_suma: [4, 6], W: -3, Z: -1 }], edges: [{ target: "RETURN" }] };
const wPulapce = (W = 20) => ({ ...s.nowaGra({ Z: 8, W, S: 9, start: { Z: 8, W: 20, S: 9 }, prowiant: 8 }), akapit: "315", historia: ["1", "315"] });

test("rzut: przed rzutem efekt nie działa", () => {
  assert.strictEqual(s.zastosujEfekty(wPulapce(), PULAPKA).bohater.W, 20);
});

test("rzut: 315 – przy 1–3 nic, przy 4–6 −3 W i −1 Z", () => {
  const dobrze = s.zastosujEfekty(s.rzucKoscia(wPulapce(), kostka(3)), PULAPKA);
  assert.deepStrictEqual([dobrze.bohater.W, dobrze.bohater.Z], [20, 8]);
  const zle = s.zastosujEfekty(s.rzucKoscia(wPulapce(), kostka(4)), PULAPKA);
  assert.deepStrictEqual([zle.bohater.W, zle.bohater.Z], [17, 7]);
  // drugie wywołanie w tej samej wizycie niczego nie dolicza
  assert.strictEqual(s.zastosujEfekty(zle, PULAPKA).bohater.W, 17);
});

test("rzut: przy następnej wizycie pułapka działa od nowa", () => {
  let st = s.zastosujEfekty(s.rzucKoscia(wPulapce(), kostka(6)), PULAPKA);
  st = { ...st, historia: [...st.historia, "52", "315"], kosci: null };
  st = s.zastosujEfekty(s.rzucKoscia(st, kostka(5)), PULAPKA);
  assert.strictEqual(st.bohater.W, 14);
});

test("rzut: 240 – tracisz tyle W, ile wypadło, ale zostaje co najmniej 1", () => {
  const most = { text: "", rzut_kosci: { ile: 1 }, efekty: [{ gdy_suma: [1, 6], W: "-kosc", zostaw_W: 1 }], edges: [{ target: "288" }] };
  assert.strictEqual(s.zastosujEfekty(s.rzucKoscia(wPulapce(), kostka(5)), most).bohater.W, 15);
  const slaby = s.zastosujEfekty(s.rzucKoscia(wPulapce(3), kostka(6)), most);
  assert.strictEqual(slaby.bohater.W, 1);
  assert.notStrictEqual(slaby.koniec, "porazka");
});

// ---------------------------------------------------------------- hazard (145, 201, 334)
const przyStole = (zloto, nr = "334") => ({ ...s.nowaGra({ Z: 8, W: 20, S: 9, start: { Z: 8, W: 20, S: 9 }, prowiant: 8, zloto }), akapit: nr, historia: ["1", nr] });
const rzuc2 = (st, a, b) => s.rzucKoscia(s.rzucKoscia(st, kostka(a)), kostka(b));
const gra = (...efekty) => ({ text: "", rzut_kosci: { ile: 2 }, efekty, edges: [{ target: "19" }] });

test("hazard: 201 – wygrywasz tyle złota, ile oczek", () => {
  const st = s.zastosujEfekty(rzuc2(przyStole(5), 3, 4), gra({ gdy_suma: [2, 12], zloto: "kosc" }));
  assert.strictEqual(st.bohater.zloto, 12);
});

test("hazard: 145 – przegrywasz oczka, najwyżej wszystko", () => {
  const przegrana = gra({ gdy_suma: [2, 12], zloto: "-kosc" });
  assert.strictEqual(s.zastosujEfekty(rzuc2(przyStole(20), 3, 4), przegrana).bohater.zloto, 13);
  const bankrut = s.zastosujEfekty(rzuc2(przyStole(4), 6, 6), przegrana);
  assert.strictEqual(bankrut.bohater.zloto, 0);
  assert.deepStrictEqual(bankrut.zmiany, ["−4 złota"]);
});

test("hazard: 334 – parzysta przegrywa, nieparzysta wygrywa; po jednej kości nic", () => {
  const karty = gra({ gdy_suma: [2, 12], gdy_parzysta: true, zloto: "-kosc" }, { gdy_suma: [2, 12], gdy_parzysta: false, zloto: "kosc" });
  assert.strictEqual(s.zastosujEfekty(s.rzucKoscia(przyStole(10), kostka(3)), karty).bohater.zloto, 10);
  assert.strictEqual(s.zastosujEfekty(rzuc2(przyStole(10), 2, 4), karty).bohater.zloto, 4);
  assert.strictEqual(s.zastosujEfekty(rzuc2(przyStole(10), 2, 5), karty).bohater.zloto, 17);
});

test("hazard: 334 – „grasz jeszcze raz” daje nowy rzut i nowy wynik", () => {
  const karty = gra({ gdy_suma: [2, 12], gdy_parzysta: false, zloto: "kosc" });
  let st = s.zastosujEfekty(rzuc2(przyStole(10), 2, 5), karty);
  st = wykonajPrzejscie(st, { target: "334" }, null, { 334: karty });
  assert.deepStrictEqual(s.oczkaTutaj(st), []);
  st = s.zastosujEfekty(rzuc2(st, 1, 2), karty);
  assert.strictEqual(st.bohater.zloto, 20);
});

// ---------------------------------------------------------------- nagrody za potwory i grubasy (193, 26)
test("licznik: każdy zabity potwór z \"licznik\" jest liczony", () => {
  const opis = { licznik: "jatka", monsters: [{ name: "A", Z: 1, W: 2 }, { name: "B", Z: 1, W: 2 }] };
  let st = stanWalki(opis);
  st = s.rundaWalki(st, opis, false, kostka(1, 1, 6, 6));
  assert.strictEqual(st.liczniki.jatka, 1);
  st = s.rundaWalki(st, opis, false, kostka(1, 1, 6, 6));
  assert.strictEqual(st.liczniki.jatka, 2);
});

test("193: 5 sztuk złota za każdego pokonanego potwora, razem z +2 Z i +2 S", () => {
  const nagroda = { text: "", efekty: [{ Z: 2, S: 2 }, { zloto_za: { licznik: "jatka", po: 5 } }], edges: [{ target: "51" }] };
  const b = { Z: 6, W: 20, S: 5, start: { Z: 8, W: 20, S: 9 }, prowiant: 8, zloto: 1 };
  const st = s.zastosujEfekty({ ...s.nowaGra(b), akapit: "193", historia: ["1", "193"], liczniki: { jatka: 3 } }, nagroda);
  assert.deepStrictEqual([st.bohater.zloto, st.bohater.Z, st.bohater.S], [16, 8, 7]);
  const bez = s.zastosujEfekty({ ...s.nowaGra(b), akapit: "193", historia: ["1", "193"] }, nagroda);
  assert.strictEqual(bez.bohater.zloto, 1);
});

test("grubasy: trafia tylko 5; w 217 liczy się para kości", () => {
  assert.strictEqual(s.ileTrafien([5, 2, 5], { trafienie: 5 }), 2);
  assert.strictEqual(s.ileTrafien([1, 2, 3], { trafienie: 5 }), 0);
  assert.strictEqual(s.ileTrafien([5, 5, 1, 5], { trafienie: 5, na_probe: 2 }), 2);
  assert.strictEqual(s.ileTrafien([5, 5, 1, 2], { trafienie: 5, na_probe: 2 }), 1);
});

test("grubasy: trafienia z 265 i 359 sumują się, a 26 płaci po 5", () => {
  const sala = (ile) => ({ text: "", rzut_kosci: { ile, trafienie: 5, licznik: "grubasy" }, edges: [{ target: "26" }] });
  let st = { ...przyStole(0, "265") };
  for (const k of [5, 1, 5]) st = s.rzucKoscia(st, kostka(k));
  st = s.zastosujEfekty(st, sala(3));
  st = s.zastosujEfekty(st, sala(3));                       // drugi raz nic nie dolicza
  assert.strictEqual(st.liczniki.grubasy, 2);
  st = wykonajPrzejscie(st, { target: "359" });
  for (const k of [2, 5]) st = s.rzucKoscia(st, kostka(k));
  st = s.zastosujEfekty(st, sala(2));
  assert.strictEqual(st.liczniki.grubasy, 3);
  st = wykonajPrzejscie(st, { target: "26" });
  st = s.zastosujEfekty(st, { text: "", efekty: [{ zloto_za: { licznik: "grubasy", po: 5 } }], edges: [] });
  assert.strictEqual(st.bohater.zloto, 15);
});

// ---------------------------------------------------------------- potrząśnięcie telefonem
const spokoj = { x: 0, y: 9.8, z: 0 };
const szarp = { x: 12, y: 0, z: 9 };

test("potrząśnięcie: leżący telefon i pojedyncze szarpnięcie to nie rzut", () => {
  const wykryj = s.wykrywaczPotrzasniecia();
  assert.strictEqual(wykryj(spokoj, 0), false);
  assert.strictEqual(wykryj(spokoj, 16), false);
  assert.strictEqual(wykryj(szarp, 32), false);      // pierwsze szarpnięcie – jeszcze nic
  assert.strictEqual(wykryj(szarp, 2000), false);    // bez ruchu, i za późno
});

test("potrząśnięcie: dwa szarpnięcia w krótkim czasie to rzut, ale tylko jeden", () => {
  const wykryj = s.wykrywaczPotrzasniecia();
  wykryj(spokoj, 0);
  assert.strictEqual(wykryj(szarp, 20), false);
  assert.strictEqual(wykryj(spokoj, 120), true);
  assert.strictEqual(wykryj(szarp, 200), false);     // przerwa po rzucie
  assert.strictEqual(wykryj(spokoj, 300), false);
  wykryj(szarp, 1300);
  assert.strictEqual(wykryj(spokoj, 1400), true);    // po przerwie znowu działa
});

test("potrząśnięcie: brak danych z czujnika niczego nie psuje", () => {
  const wykryj = s.wykrywaczPotrzasniecia();
  assert.strictEqual(wykryj(null, 0), false);
  assert.strictEqual(wykryj({ x: null, y: null, z: null }, 10), false);
});
