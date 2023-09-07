from main import Game


class Paragraphs:
    def __init__(self):
        self.game = Game()
        self.text = ""
        self.goto = []

    @staticmethod
    def par01(self):
        self.text = self.game.show_paragraph("1")
        self.goto = self.game.get_new_paths("1")

    def par02():
        txt = ("[2] Kopnij drzwi. Otwierają się i uderzają o skałę. Wchodzisz do środka z mieczem "
               "gotowym do zadania ciosu. Na pewno potwór nigdzie się nie ukrywa. Czuje się zbyt "
               "potężny. Tak, widzisz go przed sobą. Stoi na szeroko rozstawionych nogach. On "
               "też ma miecz. Czub wbił się w piasek. Opiera dłonie na rękojeści. Czeka. Ty nie "
               "czekaj! Jeśli masz hełm, załóż go koniecznie, zapewni ci +3W na czas trwania tej "
               "walki."
               "GARAZAN Z:10 W:10"
               "Po każdej rundzie możesz się ratować Ucieczką - patrz 372."
               "Jeśli zwyciężyłeś - patrz 380."
               )

        text = """
[2] Kopnij drzwi. Otwierają się i uderzają o skałę. Wchodzisz do środka z mieczem gotowym do zadania ciosu. Na pewno potwór nigdzie się nie ukrywa. Czuje się zbyt potężny. Tak, widzisz go przed sobą. Stoi na szeroko rozstawionych nogach. On też ma miecz. Czub wbił się w piasek. Opiera dłonie na rękojeści. Czeka. Ty nie czekaj! Jeśli masz hełm, załóż go koniecznie, zapewni ci +3W na czas trwania tej walki. GARAZAN Z:10 W:10 Po każdej rundzie możesz się ratować Ucieczką - patrz 372. Jeśli zwyciężyłeś - patrz 380.
[3] Twoja cierpliwość - a szczególnie zapasy złota - są na wyczerpaniu. A może inaczej? Starzy mieszkańcy podziemi mówią, że Smok ma swoje słabe strony. Szczególnie słaba jest jego lewa strona, gdzie nosi wór na pieniądze i złoto. Może by tak spróbować jeszcze raz, płacąc ponad taryfę (13 sztuk złota)? Jeśli chcesz spróbować i stać cię na to - patrz 136, jeśli nie - patrz 269, 74 lub 110.
[4] KRASNOLUDY prowadzą cię do stołu. Przynoszą na półmiskach czystą, zieloną sałatę. Stawiają pucharki. Rozlewasz napój. Kątem oka spostrzegasz, że dwa KRASNOLUDY wychodzą z pokoju wschodnimi drzwiami. Rozpinasz rzemień, ukradkiem wyciągasz miecz i kładziesz go przed sobą na stole. Zapada cisza. KRASNOLUDY bacznie cię obserwują. Ty patrzysz im prosto w oczy. Milczenie przeciąga się. Jeśli chwytasz za miecz i atakujesz - patrz 318. Jeśli postanawiasz czekać dalej - patrz 295.
[5] Lubisz walkę? Tak? To wspaniale. Przyjrzyj się więc dokładnie. Od lewej stoją: SZKIELET, ZOMBI i LUDOJAD. Wystarczy? Jeśli tak - patrz 312, jeśli nie - patrz 140.
[6] Możesz rozejrzeć się po komnacie. Ech, toż to prawdziwa zbrojownia. Na ścianach wiszą tarcze, niektóre ciężkie, u góry i u dołu zakończone ostrymi szpicami, inne ozdobne, obite czerwono-złotymi płytkami: są też lekkie tarcze skórzane. Na stojaku błyszczą miecze. Te najdłuższe, cienkie, to jedyna skuteczna broń przeciw wiedźmom. Miecze kamienne o gładkim brzeszczocie i ostrym jak igła czubie przeznaczone są do walki z płazurami. Nie wykonuje się nimi zamachów, lecz spuszcza z góry, by przeszywały cielska tych potworów. Przy samej ziemi widzisz poustawiane w rzędzie malutkie mieczyki gremlinów, krasnali ziemnych. Gdybyś widział jaki potrafią robić z nich użytek! Na ławie pod ścianą leżą rękawice: nabijane guzami do walki ciężkimi mieczami, skórzane do miotania włócznią. Są też rękawice futrzane (i tu zagląda zima!). Na wschodniej ścianie wiszą drewniane półki zastawione całą kolekcją hełmów. Są hełmy do pojedynków turniejowych, wyściełane żółtą trawą, są ciężkie hełmy z podnoszoną przyłbicą. Na najwyższej półce stoją trzy - chyba - garnki. Nie, to są hełmy do walki w pomieszczeniach albo korytarzach wypełnionych żrącym gazem. Czubkiem miecza podrzucasz jakieś skórzane płaty. To czapa, którą okrutne potwory zakładają na łeb torturowanym przez siebie istotom. Rozglądasz się dalej. Pod ścianami stoi, albo leży mnóstwo broni. Nawet nie wiesz komu i do czego służy. Widzisz ciężki młot na drewnianym stylisku, zapewne zdobyty kiedyś na goblinach, a także kościany kordelas w skórzanym futerale. Możesz zabrać dwie rzeczy - patrz 115.
[7] "Może ma Pan na składzie coś, co mógłbym ofiarować w prezencie?" - mówisz. "Jak mógłbym nie mieć? Jestem zawsze przygotowany na takie zachcianki. Mam uroczy drewniany pal i słój żrącego pyłu. Zapakować ze wstążeczką?". Patrz 219.
[8] Zaglądasz do komnaty. Drzwi lekko się uchylają. Co widzisz? Jakiś dziwny stwór biega jak oszalały od ściany do ściany. Nie wygląda groźnie. Za pas, w kieszenie, do cholew powtykane ma rozmaitej długości i różnego gatunku kości. Wchodzisz do środka. "Czemu tak biegasz, biedaku?" - pytasz. -"O, panie, co ja im zrobiłem? Taki raban o tych parę kostek! Moi bracia, gobliny upolowali kilka kocmołuchów. Jak pewnie wiesz, kocmołuchy to największy przysmak goblinów. Nie mogłem sobie odmówić. Podkradłem się i gwizdnąłem kilka kostek. Siadłem tu, by je sobie zjeść, a te bestie wyśledziły mnie i zaraz tu wpadną. O, już biegną". I goblin znów zaczyna szaleć. Bierzesz go za ramię i stajesz na środku komnaty. Za chwilę w drzwiach pojawia się stado goblinów. Jeśli będziesz walczył u boku prześladowanego stwora przeciw zgrai jego współplemieńców - patrz 98. Jeśli ratujesz się Ucieczką - patrz 210.
[9] Przygotowujesz się, by walnąć KRASNALA drewnianym palem. On spostrzega to. "Och, co za piękny pal" - mówi - "Sprzedaj mi go za 20 sztuk złota". Jeśli przystajesz na to patrz 289. Jeśli nie - patrz 375.
[10] KRASNOLUDY zapraszają cię, byś usiadł przy stole. Uśmiechają się. "Nareszcie jakiś kulturalny potwór" - mówią. "Wszyscy tylko wpadają tu, wyrywają główki sałaty i zwiewają. Ale nie mamy im tego za złe. Przynajmniej komuś przyda się nasze warzywko, he, he". Zamyśliłeś się chwilę nad tym "he, he", a tu już KRASNOLUDY zaczynają snuć opowieści. Niewielu z nich zapuszczało się kiedykolwiek w dalsze rejony podziemi. Ci, którzy wrócili, mówią, że najstraszniejszą rzeczą którą można spotkać jest ogień. Błąka się też po labiryncie tłusty Smok. Podobno jest bardzo groźny, choć niektórzy powiadają, że jest przekupny. Słuchasz tych opowieści, ale ciągle coś nie daje ci spokoju. Jeśli szedłeś ścieżką przez środek komnaty - patrz 257. Jeśli szedłeś przy ścianie - patrz 34.
"""
