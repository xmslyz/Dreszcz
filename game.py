import json
import os
import pathlib
from typing import Callable
import sys
import random

from colorama import Fore, Style, init
import game_mechanics
import character
import menu
import utils
from paragraph import Paragraph
from utils import load_book

init(autoreset=True)

def choose_game_mode(input_func) -> str:
    print(Fore.MAGENTA + "[1] " + Fore.GREEN + "Nowa gra")
    print(Fore.MAGENTA + "[2] " + Fore.GREEN + "Wczytaj zapis")
    print(Fore.MAGENTA + "[3] " + Fore.GREEN + "Usuń zapis")
    print(Fore.MAGENTA + "[0] " + Fore.GREEN + "Zakończ\n")
    print(Fore.MAGENTA + ">>> " + Style.RESET_ALL, end="")

    return input_func()


def choose_game_mode_gui() -> str:
    """
    Displays a graphical interface allowing the user to select a game mode.

    This function presents the user with a GUI-based menu containing options
    to start a new game, load a saved game, delete a save, or quit the game.
    It blocks until the user selects one of the available options.

    Returns:
        str: A string representing the user's choice. Possible return values are:
            - "1": Start a new game
            - "2": Load the last saved game
            - "3": Delete a saved game
            - "0": Quit the game


    Notes:
        TODO This function is a graphical replacement for the CLI input prompt in `choose_game_mode()`.
         It should be connected to a GUI framework such as PyQt, Tkinter, or Kivy.
    """
    ...


def get_game_over_choice(input_func=input) -> str:
    prompt = (
        Fore.GREEN + "I tak oto kończy się twoja przygoda Śmiałku! Zginąłeś!\n\n" +
        Fore.MAGENTA + "[1]" + Fore.GREEN + " Respawn?\n" +
        Fore.MAGENTA + "[2]" + Fore.GREEN + " Wczytać zapis gry?\n" +
        Fore.MAGENTA + "[0]" + Fore.GREEN + " Zakończyć grę?\n" +
        Fore.MAGENTA + ">>> " + Style.RESET_ALL
    )
    return input_func(prompt).strip()


def render_paragraph_cli(data: dict):
    print(Fore.CYAN + f"\n[{data['number']}]\n" + Style.RESET_ALL + data["text"])

    if data["is_end"]:
        print(Fore.RED + "\n🔚 To może być koniec twojej przygody...\n")
    elif data["has_exits"]:
        print(Fore.GREEN + "\nMożliwe przejścia: " + " / ".join(str(x) for x in data["edges"]))
    else:
        print(Fore.YELLOW + "\nBrak oczywistych dróg dalszych.\n")


def get_paragraph_data(paragraph) -> dict:
    """
    Returns a dictionary with content and interpretation of a paragraph.
    This function contains no display logic.
    """
    return {
        "number":    paragraph.number,
        "text": paragraph.text,
        "edges": paragraph.edges,
        "is_end": "END" in paragraph.edges if paragraph.edges else False,
        "has_exits": bool(paragraph.edges)
    }


class Shiver:
    def __init__(self):
        self.book_raw: dict[str, dict] = {}
        self.book_chapters: dict[str, Paragraph] = {}
        self.dev_mode: bool = False
        self.test = False
        self.last_valid_chapter: str = "1"
        self.book_chapters: dict[str, Paragraph] = {}
        self.visited_chapters: dict = {}
        self.hero = None
        self.bout = 0
        self.monsters_killed_counter = 0
        self.killed_monsters_dict = {}
        self._next_input_or_prompt = self._default_input

        self.COMMANDS: dict[str, Callable[[], bool]] = {
            "0": self.quit_game,
            "q": self.quit_game,
            "s": lambda: self.save_game(quicksave=True) or False,
            "h": lambda: print(self.hero) or False,
            "f": lambda: game_mechanics.combat_cli(self) or False,
            "v": lambda: print(sorted([int(x) for x in self.visited_chapters.keys()])) or False,
            "e": self._eat_provision,
            "i": lambda: print(self.hero.inventory) or False,
            "?": self._show_command_list,
            "help": self._show_command_list,
            "dev": lambda: self._toggle_dev_mode()
        }

        self.DEV_COMMANDS: dict[str, Callable[[], bool]] = {
            "t": self._toggle_test_mode,
            "k": lambda: game_mechanics.combat_cli(self, True) or False,
            "killself": self._hero_suicide,
            "sal": lambda: self.hero.change_attribute_level("stamina", 10) or False,
        }

    @staticmethod
    def _default_input(prompt: str = ">>> ") -> str:
        return input(prompt)

    def main_menu(self, replay_last_paragraph: bool = False, input_func=input):
        """
        Main game input loop for navigating through the game.

        Optionally re-displays the last paragraph (after a fight or other interruption).
        Then continuously asks the player for input and delegates processing
        to `handle_main_menu_command()`.

        Args:
            replay_last_paragraph (bool): If True, reprints the last visited paragraph at the start.
            input_func (callable): Function to receive user input (default: built-in `input()`).

        """
        if replay_last_paragraph:
            print("cd. ", end='')
            self.open_chapter(self.last_valid_chapter)

        while True:
            command = input_func(">>> ").strip()
            should_break = self.handle_main_menu_command(command)
            if should_break:
                break

    def handle_main_menu_command(self, cmd: str) -> bool:
        """
        Handles player input during the main menu loop.

        Args:
            cmd (str): The input command or chapter number entered by the player.

        Returns:
            bool: True if the game should exit the main loop, False otherwise.
        """
        paragraph = self.book_chapters.get(self.last_valid_chapter)

        # Walidacja przejścia: w trybie testowym zawsze pozwala, w przeciwnym razie sprawdza realnie
        is_valid = self.test or utils.is_valid_move(
            book_chapters=self.book_chapters,
            current=self.last_valid_chapter,
            target=cmd
        )

        if cmd in self.COMMANDS:
            return self.COMMANDS[cmd]()
        elif self.dev_mode and cmd in self.DEV_COMMANDS:
            return self.DEV_COMMANDS[cmd]()
        elif is_valid and cmd.isdigit() and cmd in self.book_chapters:
            self.open_chapter(cmd)
            return False
        else:
            if paragraph:
                possible_moves = [str(x) for x in paragraph.edges]
                print(Fore.YELLOW + f"Nieprawidłowy wybór. Możliwe ruchy: {', '.join(possible_moves)}")
            else:
                print(Fore.YELLOW + "Nieprawidłowy wybór i brak dostępu do aktualnego paragrafu.")
            return False

    def open_chapter(self, chapter: str):
        """
        Opens and displays the content of the specified chapter.

        This method updates the current chapter in the game state,
        marks the chapter as visited, and displays its content using the
        CLI renderer. If the chapter does not exist, an error message is shown.

        Args:
            chapter (str): The identifier (usually a number as string) of the paragraph to open.

        Side Effects:
            - Updates `self.last_valid_chapter` with the new chapter number.
            - Marks the chapter as visited in `self.visited_chapters`.
            - Prints the chapter content and its possible exits to the terminal.

        """

        # Ustaw nowy numer bieżącego paragrafu
        self.last_valid_chapter = chapter

        # Pobierz obiekt Paragraph z mapy rozdziałów
        paragraph = self.book_chapters.get(chapter)

        # Jeśli nie znaleziono paragrafu – pokaż błąd i zakończ
        if not paragraph:
            print(Fore.RED + f"Nie znaleziono paragrafu {chapter}.")
            return

        # Zaznacz paragraf jako odwiedzony
        self.visited_chapters[chapter] = True

        # Pobierz dane paragrafu i przekaż do funkcji renderującej interfejs CLI
        data = get_paragraph_data(paragraph)
        render_paragraph_cli(data)

    def start_game(self):
        """
        Initializes and starts the game loop from the main menu.

        This method loads the book content from file, then enters a loop allowing the
        player to choose between starting a new game, loading a saved game, deleting
        a save, or quitting. After a valid choice is made and the appropriate game state
        is initialized, it opens the corresponding paragraph and enters the main menu.

        The method uses `self._next_input_or_prompt()` to retrieve the user's choice,
        which allows for CLI or GUI-based input abstraction.

        Side Effects:
            - Loads and stores the game book into `self.book_raw` and `self.book_chapters`
            - Modifies game state: creates hero, loads save, opens paragraphs
            - Outputs to terminal (or GUI)
            - Enters `self.main_menu()` loop

        Exceptions:
            - Catches FileNotFoundError if the book file is missing

        Example:
            >>> my_game = Shiver()
            >>> my_game.start_game()
        """

        # Wczytaj dane z pliku książki paragrafowej (shiver.json)
        self.book_raw, self.book_chapters = load_book("shiver.json")

        try:
            # Główna pętla menu startowego
            while True:
                # Pobierz wybór użytkownika za pomocą CLI lub GUI
                choice = choose_game_mode(self._next_input_or_prompt)

                # Obsługa poszczególnych opcji menu
                match choice:
                    case "1":
                        # Nowa gra: stwórz bohatera i rozpocznij od paragrafu 1
                        self.create_new_hero()
                        self.save_game()
                        self.open_chapter("1")
                        break
                    case "2":
                        # Wczytaj ostatni zapis i otwórz ostatni rozdział
                        self.load_last_saved_game()
                        self.open_chapter(self.last_valid_chapter)
                        break
                    case "3":
                        # Usuń istniejący zapis gry
                        self.delete_game()
                    case "0":
                        # Zakończ grę
                        self.quit_game()
                    case _:
                        # Nieprawidłowy wybór – poproś o powtórzenie
                        print("Spróbuj jeszcze raz.")

            # Po wyborze – przejdź do głównego menu gry
            self.main_menu()

        except FileNotFoundError:
            print("Nie znaleziono pliku gry.")

    def quit_game(self):
        """
        Gracefully terminates the game session.

        This method displays a farewell message to the player, saves the current
        game state, and then exits the application.

        Side Effects:
            - Prints a farewell message to the standard output.
            - Persists the current game state by calling `self.save_game()`.
            - Terminates the Python process with `exit()`.

        See Also:
            - `self._handle_quit()`: Contains the non-terminal part of the quit logic.
            - `self.save_game()`: Responsible for writing game state to disk.
        """
        self._handle_quit()
        exit()

    def _handle_quit(self):
        print("Do zobaczenia wkrótce Śmiałku!")
        self.save_game()

    def save_game(self, quicksave: bool = False):
        """
        Saves the current game state to a JSON file.

        The game is saved using the hero's name as the filename and stored in the
        'SAVE' directory. If the hero does not exist, and `quicksave` is True,
        an error message is printed.

        Args:
            quicksave (bool, optional): If True, suppresses error if hero is None.
                                        Default is False.

        Side Effects:
            - Writes a JSON file to disk in the SAVE/ folder.
            - Prints a confirmation message or error if quicksave fails.

        """
        if self.hero is None:
            if quicksave:
                print("Nie można było zapisać pliku.")
            return

        # Utwórz strukturę danych do zapisania
        save_payload = {
            "NAME": self.hero.name,
            "TEST": self.test,
            "MAX_AGILITY": self.hero.max_agility,
            "MAX_STAMINA": self.hero.max_stamina,
            "MAX_LUCK": self.hero.max_luck,
            "AGILITY": self.hero.agility,
            "STAMINA": self.hero.stamina,
            "LUCK": self.hero.luck,
            "INVENTORY": {
                "SWORD": self.hero.inventory.sword,
                "SHIELD": self.hero.inventory.shield,
                "LANTERN": self.hero.inventory.lantern,
                "A_POTION": self.hero.inventory.agility_potion,
                "S_POTION": self.hero.inventory.stamina_potion,
                "L_POTION": self.hero.inventory.luck_potion,
                "FOOD": self.hero.inventory.food,
                "GOLD": self.hero.inventory.gold,
                "BAG": {}  # TODO: implement BAG serialization
            },
            "VISITED": self.visited_chapters,
            "LAST_CHAPTER": self.last_valid_chapter,
            "KILLS": self.hero.kills,
            "DEV": self.dev_mode
        }

        try:
            # Upewnij się, że folder SAVE istnieje
            dir_path = pathlib.Path.cwd() / "SAVE"
            dir_path.mkdir(parents=True, exist_ok=True)

            # Zapisz plik jako <hero_name>.json
            save_path = dir_path / f"{self.hero.name}.json"
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(save_payload, f, indent=4, ensure_ascii=False)

            print(f"✅ Zapisano grę jako: {self.hero.name}.json")

        except Exception as e:
            print(f"❌ Błąd zapisu pliku: {e}")

    def delete_game(self):
        """
        Allows the user to delete saved game files from the SAVE directory.

        This method presents a numbered list of available saved games and allows
        the user to select one to delete. It loops until the user chooses to exit
        the deletion menu or there are no files to delete.

        Side Effects:
            - Interacts with the filesystem to delete selected .json files.
            - Prints messages to the terminal (CLI interface).
            - Modifies contents of the SAVE folder.

        Example:
            >>> self.delete_game()
        """
        while True:
            # Pobierz ścieżkę do katalogu i listę plików zapisu
            directory_path, files = self.get_saved_files()

            # Jeśli są jakiekolwiek pliki zapisów
            if files:
                # Zbuduj tekst menu
                txt = "Wybierz zapis, który chcesz usunąć. [* aby wrócić do menu]\n"
                for i, file in enumerate(files):
                    txt += f"[{i + 1}] {file.strip('.json')}\n"
                txt += ">>> "

                file_index = input(txt).strip()

                # Wyjście z menu
                if file_index == "*":
                    break

                # Próba konwersji wyboru na numer i usunięcie pliku
                try:
                    idx = int(file_index) - 1
                    selected_file = files[idx]
                    full_path = directory_path / selected_file
                    if full_path.exists():
                        os.remove(full_path)
                        print(f"✅ Usunięto: {selected_file}")
                    else:
                        print("❌ Plik nie istnieje.")
                except (IndexError, ValueError):
                    print("❌ Nieprawidłowy wybór.")
            else:
                print("Nie ma plików do usunięcia.")
                break

    def create_new_hero(self):
        """
        Creates a new hero character and initializes the starting game state.

        This method instantiates a new `Hero` object, runs the interactive character
        creation process, and lets the user choose an initial potion. After the setup,
        it prints an introductory message and game intro text.

        Side Effects:
            - Modifies `self.hero` with a new Hero instance.
            - Interacts with the player via CLI for character creation and potion choice.
            - Prints introduction to the terminal.

        TODO:
            - Replace `choose_potion_cli()` with a GUI-based module in non-CLI environments.

        """
        # Utwórz nowego bohatera
        self.hero = character.Hero()

        # Interaktywne tworzenie postaci (atrybuty, imię, itp.)
        data = self.hero.create_from_user_input()
        self.hero = self.hero.from_data(data)

        # Wybór mikstury na start – na razie CLI
        self.hero.choose_potion_cli()  # TODO: Zastąpić GUI wersją w edytorze

        # Powitanie i wprowadzenie do gry
        print(Fore.RED + "\n *** ZACZYNAMY !!! *** " + Style.RESET_ALL)
        print(menu.intro(self.hero))

    def load_hero(self, hero_data):
        """
        Loads the game state and reconstructs the hero from saved data.

        Args:
            hero_data (dict): Dictionary of saved hero state and game metadata.
        """
        self.hero = character.Hero.from_dict(hero_data)
        self.test = hero_data["TEST"]
        self.last_valid_chapter = hero_data["LAST_CHAPTER"]
        self.visited_chapters = hero_data["VISITED"]
        self.dev_mode = hero_data["DEV"]

    def load_last_saved_game(self, default: int = None):
        """
        Prompts the user to select a saved game and loads it.

        This method lists all available save files in the SAVE directory,
        allows the user to select one, and loads its contents into the current game state.

        If the user chooses '*', it returns to the main game menu. If no files are found,
        or loading fails, an appropriate message is displayed and the user is redirected
        to the start menu.

        Args:
            default (int, optional): Reserved for automated tests or future GUI usage
                                     to auto-select a given file index.

        Side Effects:
            - Loads a JSON save file from disk
            - Updates hero and game state via `self.load_hero()`
            - Calls `self.start_game()` on failure or cancel

        """

        directory_path, files = self.get_saved_files()

        if not files:
            print("Nie ma żadnych zapisanych plików.")
            self.start_game()
            return

        # Buduj tekst wyboru
        txt = "Wybierz zapis. [* aby wrócić do poprzedniego menu]\n"
        for i, file in enumerate(files):
            txt += f"[{i + 1}] {file.strip('.json')}\n"
        txt += ">>> "

        while True:
            try:
                file_index = input(txt).strip()
                if file_index == "*":
                    self.start_game()
                    return

                idx = int(file_index) - 1
                if 0 <= idx < len(files):
                    selected_file = files[idx]
                    full_path = directory_path / selected_file

                    if full_path.exists():
                        with open(full_path, encoding="utf-8") as f:
                            load_data = json.load(f)
                        self.load_hero(load_data)
                        print(f"✅ Wczytano zapis: {selected_file}")
                        break
                    else:
                        print("❌ Plik nie istnieje.")
                else:
                    print("❌ Wybierz numer z listy.")
            except ValueError:
                print("❌ Wprowadź poprawny numer.")

    def respawn(self):
        print(Fore.YELLOW + "Powracasz do życia..." + Style.RESET_ALL)
        self.hero = self.hero.clone_hero()
        # Wybierz miejsce startowe — np. losowe z odwiedzonych:
        restart_point = random.choice(list(self.visited_chapters.keys()))
        self.open_chapter(restart_point)

    @staticmethod
    def get_saved_files() -> tuple[pathlib.Path, list[str]]:
        """
        Retrieves a list of saved game files from the SAVE directory.

        Returns:
            tuple:
                - directory_path (Path): Path to the SAVE directory
                - files (list of str): List of filenames in the SAVE directory

        Exceptions:
            - Prints an error message if the SAVE directory cannot be accessed.
              Returns an empty list in such a case.

        """
        directory_path = pathlib.Path.cwd() / "SAVE"

        try:
            files = [
                f for f in os.listdir(directory_path)
                if os.path.isfile(directory_path / f)
            ]
            return directory_path, files

        except FileNotFoundError:
            print("📂 Folder 'SAVE' nie istnieje.")
        except PermissionError:
            print("🚫 Brak uprawnień do odczytu folderu 'SAVE'.")
        except Exception as e:
            print(f"❌ Błąd podczas pobierania zapisów: {e}")

        return directory_path, []

    def game_over(self):
        while True:
            choice = get_game_over_choice()

            if choice == "1":
                self.respawn()
                break
            elif choice == "2":
                self.load_last_saved_game()
            elif choice == "0":
                self.quit_game()

    def _toggle_test_mode(self):
        self.test = not self.test
        print(f"TEST: {self.test}")
        return False

    def _hero_suicide(self):
        self.hero.stamina = 0
        print(f"{self.hero.name} zginął!")
        self.game_over()
        return True

    def _eat_provision(self):
        if "Prowiant" in self.book_chapters[self.last_valid_chapter]:
            healed, _ = game_mechanics.consume(self.hero)
            if healed > 0:
                print(f"Spożyłeś prowiant. W: +{healed}")
            else:
                print("Nie masz już Prowiantu albo jesteś najedzony.")
        else:
            print("Nie możesz w tej chwili zjeść Prowiantu")
        return False

    def _toggle_dev_mode(self) -> bool:
        self.dev_mode = not self.dev_mode
        print(Fore.MAGENTA + f"Tryb deweloperski: {self.dev_mode}")
        return False

    def _next_input_or_prompt(self, prompt: str) -> str:
        if hasattr(self, "_menu_sequence") and self._menu_sequence:
            return self._menu_sequence.pop(0)

        return input(prompt)

    def _show_command_list(self) -> bool:
        """
        Displays a grouped list of available command keys for the player.
        """
        print(Fore.CYAN + "\nDostępne komendy:" + Style.RESET_ALL)

        command_groups = {
            "🧱 System": [],
            "🧙‍♂️ Bohater": [],
            "⚔️ Walka": [],
            "🧪 Debug / Dev": []
        }

        label_map = {
            "0": "Zakończ grę",
            "q": "Zakończ grę",
            "s": "Zapisz grę",
            "dev": "Tryb developerski",
            "?": "Lista komend",
            "help": "Lista komend",

            "h": "Parametry bohatera",
            "i": "Plecak",
            "e": "Zjedz Prowiant",

            "f": "Walka",
            "k": "Walka testowa (1hp)",
            "v": "Odwiedzone paragrafy",

            "t": "Tryb testowy",
            "killself": "Zabij się",
            "sal": "Ulecz się"
        }

        group_map = {
            "0": "🧱 System",
            "q": "🧱 System",
            "s": "🧱 System",
            "dev": "🧱 System",
            "?": "🧱 System",
            "help": "🧱 System",

            "h": "🧙‍♂️ Bohater",
            "i": "🧙‍♂️ Bohater",
            "e": "🧙‍♂️ Bohater",

            "f": "⚔️ Walka",
            "k": "🧪 Debug / Dev",
            "v": "⚔️ Walka",

            "t": "🧪 Debug / Dev",
            "killself": "🧪 Debug / Dev",
            "sal": "🧪 Debug / Dev"
        }

        dev_items = []
        if self.dev_mode:
            dev_items = [
                ("test", "Tryb testowy"),
                ("k","Walka testowa z 1hp"),
                ("killself", "Zabij się"),
                ("sal", "Ulecz się"),
            ]

        printed = set()

        for key, func in self.COMMANDS.items():
            if func in printed:
                continue
            printed.add(func)

            group = group_map.get(key, "🧱 System")
            label = label_map.get(key, "<nieznana akcja>")
            command_groups[group].append((key, label))

        for group, items in command_groups.items():
            if items:
                print(Fore.BLUE + f"\n{group}" + Style.RESET_ALL)
                for key, label in sorted(items):
                    print(Fore.MAGENTA + f"[{key}]" + Fore.GREEN + f" {label}")

        if self.dev_mode:
            print(Fore.BLUE + "\n🧪 Debug / Dev" + Style.RESET_ALL)
            for key, label in sorted(dev_items):
                print(Fore.MAGENTA + f"[{key}]" + Fore.GREEN + f" {label}")
        return False


if __name__ == "__main__":
    args = sys.argv[1:]
    game = Shiver()
    game.start_game()