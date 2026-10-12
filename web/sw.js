// Service worker – „pośrednik” między grą a internetem.
// Przeglądarka uruchamia go w tle; przechwytuje każde zapytanie strony
// (fetch) i może odpowiedzieć kopią z pamięci telefonu (Cache Storage).
// Dzięki temu gra działa bez zasięgu.
//
// WERSJA podmienia skrypt budujący (web/zbuduj.py) – nowa wersja plików
// = nowa nazwa pamięci, a stara zostaje usunięta.
const WERSJA = "dev";
const PAMIEC = `dreszcz-${WERSJA}`;
const PLIKI = [
  "./",
  "index.html",
  "silnik.js",
  "shiver.json",
  "manifest.webmanifest",
  "ikona-192.png",
  "ikona-512.png",
];

// 1. Instalacja: zapisujemy wszystkie pliki gry w pamięci.
self.addEventListener("install", (zdarzenie) => {
  zdarzenie.waitUntil(
    caches.open(PAMIEC).then((pamiec) => pamiec.addAll(PLIKI)).then(() => self.skipWaiting())
  );
});

// 2. Aktywacja: sprzątamy pamięci poprzednich wersji.
self.addEventListener("activate", (zdarzenie) => {
  zdarzenie.waitUntil(
    caches.keys()
      .then((nazwy) => Promise.all(nazwy.filter((n) => n !== PAMIEC).map((n) => caches.delete(n))))
      .then(() => self.clients.claim())
  );
});

// 3. Każde zapytanie: najpierw pamięć (szybko, działa offline),
//    a w tle pobieramy świeżą kopię na następny raz.
//    Ta strategia nazywa się „stale-while-revalidate”.
self.addEventListener("fetch", (zdarzenie) => {
  if (zdarzenie.request.method !== "GET") return;
  zdarzenie.respondWith(
    caches.open(PAMIEC).then(async (pamiec) => {
      const zPamieci = await pamiec.match(zdarzenie.request);
      const zSieci = fetch(zdarzenie.request)
        .then((odpowiedz) => {
          if (odpowiedz.ok) pamiec.put(zdarzenie.request, odpowiedz.clone());
          return odpowiedz;
        })
        .catch(() => zPamieci);
      return zPamieci ?? zSieci;
    })
  );
});
