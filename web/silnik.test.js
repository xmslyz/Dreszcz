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
