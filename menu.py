import os


def intro(player):
    return (
        f"Hej, {player.name}!\n"
        "To o Tobie mówią, "
        "że w Twoich żyłach zamiast krwi płynie lodowata woda, "
        "a twoje mięśnie są z najszlachetniejszej stali?\n"
        "Jeśli tak, spójrz w stronę zachodzącego słońca. "
        "Tam, na rubieżach królestwa "
        "Almanhagor, rozpoczynają się niezbadane Podziemia. "
        "Tylko Ty możesz wydrzeć ich  Wielką Tajemnicę. Ruszaj!\n\n"
    )


def menu_options():
    print("*" * 30)
    print(
        "[1] WYPOSAŻENIE I CECHY\n"
        "[2] WALKA\n"
        "[3] UCIECZKA\n"
        "[4] SZCZĘŚCIE\n"
        "[5] PODWYŻSZANIE POZIOMU CECH\n"
        "[6] PROWIANT\n"
        "[7] ZAPIS\n"
        "[8] CEL WYPRAWY\n"
        "[0] OPCJE MENU\n"
    )
    print("*" * 30)


def rules():
    os.system("cls")
    menu_options()
    while True:
        menu_input = input("Wybierz opcje menu: ")
        match menu_input:
            case "0":
                menu_options()
            case "1":
                rules_1()
            case "2":
                rules_2()
            # case "3":
            # case "4":
            # case "5":
            # case "6":
            # case "7":
            # case "8":
            case "x":
                break
            case "_":
                print("Wpisz poprawny klucz menu.")
                rules()


def rules_1():
    print('''I. WYPOSAŻENIE I CECHY
Jesteś Śmiałkiem.

Twój ekwipunek to: miecz, tarcza, plecak na Prowiant, latarnia. Wędrując po
podziemiach będziesz znajdował inne rodzaje broni i przedmioty. Pamiętaj, że -
poza mieczem - każda broń może być wykorzystana tylko raz. Podobnie, znajdowane
przedmioty są "jednorazowego użytku".

Możesz zabrać ze sobą jedną butelkę eliksiru. Wybierasz spośród eliksirów:
ZRĘCZNOŚCI, WYTRZYMAŁOŚCI i SZCZĘŚCIA. Można wypić go w dowolnym momencie, ale
tylko dwukrotnie podczas przygody.
Twoje cechy to: ZRĘCZNOŚĆ (Z), WYTRZYMAŁOŚĆ (W) i SZCZĘŚCIE (S). Przed zejściem
do podziemi ustalasz początkowy poziom tych cech. Rzucasz zwykłą kostką
sześcienną (jeden rzut=1K, dwa rzuty=2K). Twoja ZRĘCZNOŚĆ to 1K+6 (czyli rzuć
raz kością sześcienną i do wyniku dodaj sześć). WYTRZYMAŁOŚĆ to 2K+12, a
SZCZĘŚCIE to 1K+6. Poziom cech będzie się nieustannie zmieniał podczas wędrówki.
Ale nie może przekroczyć poziomu początkowego.''')


def rules_2():
    print('''II. WALKA
Będziesz walczył z potworami. Ich cechy (ZRĘCZNOŚĆ i WYTRZYMAŁOŚĆ) określone są
w tekście. Oto sposób rozstrzygania walki:
1. określasz A, czyli SIŁĘ ATAKU potwora = 2K+jego ZRĘCZNOŚĆ,
2. określasz B, czyli swoją SIŁĘ ATAKU = 2K+twoja ZRĘCZNOŚĆ,
3. jeśli A>B, to otrzymujesz ranę: odejmij 2 od swojej WYTRZYMAŁOŚCI, jeśli A<B,
to potwór otrzymuje ranę: odejmij 2 od WYTRZYMAŁOŚCI potwora, jeśli A=B, to
powtórz 1 i 2.
4. możesz (lub musisz) zrobić SSS (patrz niżej).
5. powtórz 1-4 aż WYTRZYMAŁOŚĆ twoja lub potwora osiągnie 0 co oznacza śmierć.
Napotkawszy potwory musisz walczyć, chyba że tekst przewiduje możliwość
uniknięcia walki.
    ''')
