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
