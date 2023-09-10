import json
import os

# game play
last_valid_paragraph: str = "1"
visited = {}
# open game file
with open("dreszcz.json") as f:
    book = json.load(f)


def start_new_game():
    print(f"[1] {book['1']}")


def load_last_saved_game():
    global visited
    if os.path.exists("save.txt"):
        with open("save.txt") as sv:
            last_paragraph = sv.read().strip()
            if os.path.exists("visited.json"):
                with open("visited.json") as vis:
                    visited = json.load(vis)
    else:
        start_new_game()


try:
    # open last saved or first
    while True:
        user_input = input("Nowa gra [N] czy wczytać ostatni zapis [L]?\n"
                           "Wybierz [Q] aby zakończyć w dowolnym momencie.\n"
                           ">>> ").lower()

        if user_input == "n":
            start_new_game()
            break
        elif user_input == "l":
            load_last_saved_game()
            break
        elif user_input == "q":
            exit()

        else:
            print("Zła komenda. Spróbuj jeszcze raz.")

    while True:
        paragraph = input("Podaj numer: ")

        if paragraph == "q":
            print("Do zobaczenia")
            with open("save.txt", "w", encoding="utf-8") as s:
                s.write(last_valid_paragraph)
            with open("visited.json", "w") as v:
                json.dump(visited, v, indent=4)
            exit()
        elif paragraph == "m":
            while True:
                menu_input = input("Menu:\n"
                                   "     [v] pokaż odwiedzone paragrafy\n"
                                   "     >>> ")
                if menu_input == "v":
                    print(sorted([int(x) for x in visited.keys()]))
                    break
                if menu_input == "q":
                    print("Do zobaczenia")
                    with open("save.txt", "w", encoding="utf-8") as s:
                        s.write(last_valid_paragraph)
                    with open("visited.json", "w") as v:
                        json.dump(visited, v, indent=4)
                    exit()
                else:
                    print("Nieprawidłowy znak. Spróbuj ponownie.")

        elif paragraph.isdigit() and paragraph in book:
            last_valid_paragraph = paragraph
            if paragraph not in visited:
                # show actual paragraph
                print(f"[{paragraph}] [] {book[paragraph]}")
                # add paragraph to visited places
                visited[paragraph] = True
            else:
                print(f"[{paragraph}] [+] {book[paragraph]}")
        else:
            print("Nieprawidłowy numer paragrafu. Spróbuj ponownie.")

except FileNotFoundError:
    print("Nie znaleziono pliku gry.")
