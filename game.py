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
    global save, v, visited
    if os.path.exists("save.txt"):
        with open("save.txt") as save:
            last_paragraph = save.read().strip()
            if os.path.exists("visited.json"):
                with open("visited.json") as v:
                    visited = json.load(v)
    else:
        start_new_game()


try:
    # open last saved or first
    while True:
        user_input = input("Nowa gra [n] czy wczytać ostatni zapis [l]?"
                           "[q] zawsze aby zakończyć: ")
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
            with open("save.txt", "w", encoding="utf-8") as save:
                save.write(last_valid_paragraph)
            with open("visited.json", "w") as v:
                json.dump(visited, v, indent=4)
            break
        elif paragraph.isdigit() and paragraph in book:
            last_valid_paragraph = paragraph
            if paragraph not in visited:
                # add paragraph to visited places
                visited[paragraph] = True
                # show actual paragraph
                print(f"[{paragraph}] [{'+' if visited[paragraph] else ''}]"
                      f" {book[paragraph]}")
        else:
            print("Nieprawidłowy numer paragrafu. Spróbuj ponownie.")

except FileNotFoundError:
    print("Nie znaleziono pliku gry.")