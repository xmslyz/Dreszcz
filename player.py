import json
import random


class Creature:
    def __init__(self):
        self.agility = None
        self.stamina = None

    def attack(self):
        return self.agility + Dice().d2()


class Dice:
    @staticmethod
    def d1():
        return random.randint(1, 6)

    def d2(self):
        return self.d1() + self.d1()


class Actions:
    def action_dialogue(self, player, monster):
        while True:
            dialogue = input("[1] Walczysz, [2] Ucieczkasz, [3] Jesz ... ")
            match dialogue:
                case "1":
                    self.fight_round_result(player, monster)
                case "2":
                    player.run()
                case "3":
                    player.eat()

    def fight_round_result(self, player, oponent):
        monster = Monster(oponent)
        self.fight_round(player, monster)

        if player.stamina <= 0:
            print("Giniesz")
        elif monster.stamina <= 0:
            print("Potwór ginie")
        else:
            print(
                f"Wytrzymałość gracza: {player.stamina} vs. "
                f"Wytrzymałość potwora: {monster.stamina}"
            )

    def fight_round(self, player, monster):
        got_luck = player.am_i_lucky()
        monster_attack_force = monster.attack()
        player_attack_force = player.attack()

        if monster_attack_force > player_attack_force:
            print(
                f"Monster's attack outcome: {monster.name} > Hero = Hero gets "
                f"injured."
            )
            if self.make_luck_test(player):
                if got_luck:
                    print("You were lucky! Hero stamina -1")
                    player.stamina -= 1
                else:
                    print("Luck was not on your side! Hero stamina -3")
                    player.stamina -= 3
                player.luck -= 1
            else:
                player.stamina -= 2

        elif player_attack_force > monster_attack_force:
            print(
                f"Monster's attack outcome: {monster.name} < Hero = Monster "
                f"gets hurt."
            )
            if self.make_luck_test(player):
                if got_luck:
                    print("You were lucky! Monster stamina -4")
                    monster.stamina -= 4
                else:
                    print("Luck wasn't with you! Monster stamina -1")
                    monster.stamina -= 1
                player.luck -= 1
            else:
                monster.stamina -= 2
        else:
            print("It's a tie!")

    @staticmethod
    def make_luck_test(player):
        luck_input = input(
            f"Do you want to test your luck? [t]/[n] Current LUCK level: "
            f"{player.luck}."
        )
        return luck_input == "t"

    @staticmethod
    def monster_attack_narrative():
        attacks_pl = [
            "Potwór rzucił się na Ciebie, rozszarpując Cię swoimi ostrymi "
            "pazurami.",
            "Potężny cios potwora spadł na Ciebie, powodując Ci druzgocące obrażenia.",
            "Potwór wystrzelił strumień ognia w Twoim kierunku, spalając wszystko na swojej drodze.",
            "Potwór chwycił Ciebie swoimi ogromnymi szczękami, miażdżąc Cię w swoim żelaznym uścisku.",
            "Potwór wypuścił przerażający ryk, który wstrząsnął Tobą, powodując dezorientację.",
            "Oszalały atak potwora zranił Ciebie wieloma szybkimi ciosami, zostawiając Cię w bolesnym szoku.",
            "Potwór wystrzelił groźne strzały kolców z ogona, przeszywając Ciebie i powodując Ci ciężkie rany.",
            "Potwór unosił się w powietrzu, spadając na Ciebie i atakując Cię z góry swoimi potężnymi łapami.",
            "Potwór wykorzystał swoją jadowitą truciznę, zatruwając Ciebie i osłabiając Cię w walce.",
            "Potwór wydobył dźwiękowy huk, który zmusił Ciebie do upadku, tracąc cenny czas w obronie.",
            "Potwór otoczył się chmurą ciemności, wysysając energię życiową Ciebie, osłabiając Cię z każdą sekundą.",
            "Potwór rzucił się na Ciebie z potężnym zamachem ogromnego młota, powodując wstrząsające wstrząsy.",
            "Potwór zwinął swoje ciało wokół Ciebie, dusząc Cię i pozbawiając Cię możliwości ruchu.",
            "Potwór wydał przerażający ryk, który sparaliżował Ciebie na chwilę, dając mu przewagę w ataku.",
        ]
        return random.choice(attacks_pl)

    @staticmethod
    def human_attacks_narrative():
        attacks_pl = [
            "Rzucasz się na potwora, zadając mu rany swoim ostrym mieczem.",
            "Zadajesz potworowi mocny cios, powodując mu bolesne obrażenia.",
            "Wyprowadzasz precyzyjne cięcie mieczem, sprawiając potworowi ból i dyskomfort.",
            "Przeprowadzasz serię szybkich ataków, siekając potwora z wściekłością.",
            "Twój płonący miecz przecina potwora, zadając mu poparzenia.",
            "Atakujesz potwora z determinacją, wbijając mu miecz w ciało i powodując rany.",
            "Mierzysz precyzyjne cięcie mieczem w kierunku potwora, sprawiając mu dyskomfort.",
            "Zaatakowałeś potwora potężnym zamachem miecza, powodując wstrząs.",
            "Zadajesz potworowi kolejne ciosy mieczem, osłabiając jego obronę.",
            "Przeszywasz potwora swoim ostrym mieczem, powodując mu ból i dezorientację.",
            "Twoje precyzyjne cięcie mieczem trafia potwora, zadając mu bolesne rany.",
            "Atakujesz potwora ze zwinnością i szybkością, wyprowadzając precyzyjne uderzenia mieczem.",
            "Twój miecz śmiercią pędzi w kierunku potwora, powodując mu cierpienie.",
            "Mierzysz potworowi precyzyjne ciosy mieczem, zadając mu obrażenia.",
            "Potwór zostaje przecięty przez twój ostry miecz, wydając przeraźliwy ryk.",
            "Twój nieustępliwy atak mieczem sprawia, że potwór traci równowagę i odczuwa ból.",
            "Zadajesz potworowi cięcie mieczem pełne determinacji, powalając go na kolana.",
            "Mierząc potwora wzrokiem, wbijasz mu miecz głęboko w ciało, powodując cierpienie.",
            "Twoje precyzyjne cięcia mieczem są nieustępliwe, doprowadzając potwora na skraj wyczerpania.",
            "Z impetem atakujesz potwora, siekając go bezlitosnymi ciosami miecza.",
            "Twój cios mieczem trafia potwora w kluczowe miejsce, sprawiając, że traci on siły i trudności w "
            "poruszaniu się.",
        ]

        return random.choice(attacks_pl)

    @staticmethod
    def tie_narrative():
        outcomes_pl = [
            "Po zaciętej walce potwór i ty macie jednakową siłę i determinację, co prowadzi do impasu.",
            "Potwór i ty kontynuujecie walkę, żaden z was nie ustępuje, utrzymując równą siłę i zdeterminowanie.",
            "Wciąż toczycie zaciętą walkę, potwór nie jest w stanie cię pokonać, ale ty również nie jesteś w stanie "
            "go pokonać.",
            "Potwór i ty nie dajecie za wygraną, niezależnie od liczby ciosów i ran, utrzymujecie się na równi.",
            "Walka między potworem a tobą trwa nadal, oboje nieustępliwi i zdeterminowani.",
            "Obaj nie odpuszczacie, kontynuując walkę z niezłomnym dążeniem do zwycięstwa.",
            "Potwór i ty nieustannie się staracie, nie dając sobie ani na moment oddechu.",
            "Twój upór i odwaga utrzymują cię w równorzędnej walce z potworem, nie pozwalając mu na przewagę.",
            "Starasz się z całych sił, potwór nie ustępuje, co prowadzi do sytuacji, "
            "w której nikt nie może przełamać impasu.",
            "Obaj pokazujecie swoje umiejętności i odwagę, nie pozwalając przeciwnikowi zyskać przewagi.",
            "Walka pomiędzy tobą a potworem trwa nadal, obaj nieustannie atakując i broniąc się.",
            "Nie masz zamiaru się poddawać, a potwór nieustannie stawia ci opór, utrzymując się w równorzędnej walce.",
            "Obaj nie dajecie za wygraną, trwając w zaciętej walce bez wyraźnego zwycięzcy.",
            "Walka toczy się dalej, potwór nie ustępuje, ale ty również nie ustępujesz przed przeciwnikiem.",
            "Potwór i ty kontynuujecie zaciętą walkę, nieustannie próbując przełamać siłę drugiej strony.",
            "Nie ma ani jednego zwycięzcy w starciu pomiędzy tobą a potworem, walka trwa nadal.",
            "Obaj trwacie w nieustępliwej walce, nie pozwalając przeciwnikowi zdobyć przewagi.",
            "Potwór i ty nadal zmierzacie się w walce, żaden z was nie ustępuje przed drugim.",
            "Walka między tobą a potworem trwa nadal, obaj niezłomnie dążycie do zwycięstwa.",
            "Potwór nie ustępuje, ale ty również nie rezygnujesz z walki, co prowadzi do utrzymania się impasu.",
        ]

        return random.choice(outcomes_pl)


class Player(Creature):
    def __init__(self):
        super().__init__()
        self.luck = 0
        self.name = self.set_name()
        self.inventory = Inventory()

        self.max_luck = None
        self.max_stamina = None
        self.max_agility = None

        self.max_luck_potion_usage = 2
        self.max_agility_potion_usage = 2
        self.max_stamina_potion_usage = 2

    def __str__(self):
        return (
            f"{self.name}:\n"
            f"ZRĘCZNOŚĆ: {self.agility}\n"
            f"WYTRZYMAŁOŚĆ: {self.stamina}\n"
            f"SZCZĘŚCIE: {self.luck}"
        )

    def set_level(self):
        dice = Dice()
        self.max_agility = dice.d1() + 6
        self.max_stamina = dice.d2() + 12
        self.max_luck = dice.d1() + 6

        self.agility = self.max_agility
        self.stamina = self.max_stamina
        self.luck = self.max_luck

    @staticmethod
    def set_name():
        fantasy_names = [
            "Eldrithia Stormrider",
            "Thalion Frostwind",
            "Seraphina Shadowcaster",
            "Draven Blackthorn",
            "Isolde Moonwhisper",
            "Magnus Ironheart",
            "Evelina Starshimmer",
            "Gryphon Stormcaller",
            "Orion Nightblade",
            "Lyra Silverleaf",
            "Asher Stormborne",
            "Morrigan Frostfall",
            "Aric Bloodfang",
            "Isadora Ravensong",
            "Zephyr Skywatcher",
            "Ember Darkfire",
            "Aveline Swiftarrow",
            "Darius Emberheart",
            "Seraphiel Dawnlight",
            "Ashlyn Shadowthorn",
            "Faelan Windrider",
            "Rhiannon Moonblade",
            "Zephyra Sunfire",
            "Cassian Frostborn",
            "Lunaire Stormweaver",
            "Ravenna Blackthistle",
            "Elysia Silvermoon",
            "Davian Shadowstrike",
            "Vespera Nightshade",
            "Aurora Dawnbreaker",
            "Lysander Starfrost",
            "Sylvana Whisperwind",
            "Cedric Stormheart",
            "Elara Emberwing",
            "Thorn Darkthorn",
            "Luna Shadowdancer",
            "Galen Ironwood",
            "Riven Stormrider",
            "Aria Moonlight",
            "Caelan Frostfire",
            "Nyx Shadowborn",
            "Valeria Silverstar",
            "Kaelen Windwalker",
            "Serenity Frostbloom",
            "Valek Darkbane",
            "Rowan Moonstrike",
            "Astrid Stormsinger",
            "Elysian Shadowbrook",
            "Lorien Moonshadow",
            "Cyrus Emberfall",
            "Selene Starblade",
            "Thaddeus Stormcrest",
            "Evelyn Ravenshadow",
            "Lucian Blackthorn",
            "Celestia Wintermoon",
            "Kieran Shadowsong",
            "Rosalind Sunfire",
            "Soren Ironbane",
            "Lilith Nightshade",
            "Zephyrus Stormchaser",
            "Elara Moonwhisper",
            "Gareth Frostfang",
            "Elysande Starwatcher",
            "Damian Shadowcaster",
            "Astraea Dawnsworn",
            "Rune Blackthistle",
            "Iris Silverbrook",
            "Dante Stormblade",
            "Ariella Emberheart",
            "Silas Moonwind",
            "Lyanna Frostglade",
            "Caspian Shadowstrike",
            "Eveline Stardust",
            "Lysander Thunderheart",
            "Arabella Swiftwind",
            "Drystan Frostthorn",
            "Vivienne Shadowborne",
            "Cassandra Starfall",
            "Kaelan Darkfire",
            "Aurelia Moonshadow",
            "Thorne Ironhelm",
            "Elysia Ravenshadow",
            "Leander Blackthorn",
            "Selene Frostbloom",
            "Nathaniel Stormchaser",
            "Ravenna Moonwhisper",
            "Zephyrus Frostfang",
            "Elara Starweaver",
            "Gideon Shadowthorn",
            "Seraphina Silvermoon",
            "Davian Stormrider",
            "Aria Nightshroud",
            "Lorenzo Emberstrike",
            "Celestia Frostfall",
            "Kieran Nightwind",
            "Rosalind Stormwatcher",
            "Soren Ironclaw",
            "Lilith Moonshade",
            "Zephyr Winterstorm",
            "Elara Moonshadow",
            "Gareth Frostheart",
            "Elysande Shadowdancer",
            "Damian Stormcaster",
            "Astraea Dawnbreaker",
            "Rune Blackthorn",
            "Iris Silverbrook",
            "Dante Stormblade",
            "Ariella Emberheart",
            "Silas Moonwind",
            "Lyanna Frostglade",
            "Caspian Shadowstrike",
            "Eveline Stardust",
            "Lysander Thunderheart",
            "Arabella Swiftwind",
            "Drystan Frostthorn",
            "Vivienne Shadowborne",
            "Cassandra Starfall",
            "Kaelan Darkfire",
            "Aurelia Moonshadow",
            "Thorne Ironhelm",
            "Elysia Ravenshadow",
            "Leander Blackthorn",
            "Selene Frostbloom",
            "Nathaniel Stormchaser",
            "Ravenna Moonwhisper",
            "Zephyrus Frostfang",
            "Elara Starweaver",
            "Gideon Shadowthorn",
            "Seraphina Silvermoon",
            "Davian Stormrider",
            "Aria Nightshroud",
            "Lorenzo Emberstrike",
            "Celestia Frostfall",
            "Kieran Nightwind",
            "Rosalind Stormwatcher",
            "Soren Ironclaw",
            "Lilith Moonshade",
            "Zephyr Winterstorm",
            "Eldrithia Stormrider",
            "Thalion Frostwind",
            "Seraphina Shadowcaster",
            "Draven Blackthorn",
            "Isolde Moonwhisper",
            "Magnus Ironheart",
            "Evelina Starshimmer",
            "Gryphon Stormcaller",
            "Orion Nightblade",
            "Lyra Silverleaf",
            "Asher Stormborne",
            "Morrigan Frostfall",
            "Aric Bloodfang",
            "Isadora Ravensong",
            "Zephyr Skywatcher",
            "Ember Darkfire",
            "Aveline Swiftarrow",
            "Darius Emberheart",
            "Seraphiel Dawnlight",
            "Ashlyn Shadowthorn",
        ]
        return random.choice(fantasy_names)

    def choose_potion(self):
        potion = input("Jaki eliksir wybierasz [s]/[w]/[z]? :  ")
        match potion:
            case "s":
                self.inventory.potion.update({"luck": 1})
            case "w":
                self.inventory.potion.update({"stamina": 1})
            case "z":
                self.inventory.potion.update({"agility": 1})

    def eat(self):
        food = self.inventory.food
        if food > 0:
            while not self.stamina > self.max_stamina:
                for n in range(4):
                    self.stamina += 1
                    if self.stamina == self.max_stamina:
                        break
            self.inventory.food -= 1
            print(self.inventory.food)
        else:
            print("Nie masz już jedzenia")

    def drink_agility_potion(self, points):
        potion = self.inventory.potion["agility"]
        if potion > 0:
            while not self.agility > self.max_agility:
                for n in range(points):
                    self.agility += 1
                    if self.agility == self.max_agility:
                        break
                    print(self.agility)
            self.inventory.potion.update({"agility": potion - 1})
            print(self.inventory.potion["agility"])
        else:
            print("Nie masz eliksiru zręczności")

    def wanna_check_sss(self):
        asking = input(
            f"Chcesz sprawdzić swoje szczęście? [t]/[n] "
            f"Obecny poziom SZCZĘŚCIA wynosi {self.luck}."
        )
        match asking:
            case "t":
                return True
            case "n":
                return False
            case _:
                print("[t]/[n]?")
                self.wanna_check_sss()

    def am_i_lucky(self):
        k2 = Dice().d2()
        return True if k2 <= self.luck else False

    def run(self):
        if self.wanna_check_sss():
            if self.am_i_lucky():
                print(
                    "Miałeś szczęście, potwór ledwo drasnął twoje plecy. "
                    "Wytrzymałość -1"
                )
                self.stamina -= 1
            else:
                print(
                    "Masz pecha. "
                    "Kiedy zacząłeś uciekać potwór zdążył w ostaniej chwili "
                    "zadać ci głęboką ranę."
                    "Wytrzymałość -3"
                )
                self.stamina -= 3
        else:
            print(
                "Kiedy odwróciłeś się aby uciec, potwór zdążył uderzyć po "
                "raz ostatni, zadając ci bolesną ranę."
                "Wytrzymałość -2"
            )
            self.stamina -= 2


class Inventory:
    def __init__(self):
        self.sword = {"plain sword": 1}
        self.shield = {"plain shield": 1}
        self.bag = {}
        self.lantern = "lantern"
        self.potion = {"agility": 0, "stamina": 0, "luck": 0}
        self.food = 8
        self.gold = 0


class Monster(Creature):
    def __init__(self, monster_data):
        super().__init__()
        with open("creature_data.json", encoding="utf-8") as f:
            self.monsters_list = json.load(f)

        self.monster_name = monster_data[1]
        self.paragraph = monster_data[0]
        self.name = monster_data[1]
        self.agility, self.stamina = self.monsters_list[self.monster_name][
            self.paragraph
        ]

    def __str__(self):
        return (
            f"{self.name}\n"
            f"ZRĘCZNOŚĆ: {self.agility}\n"
            f"WYTRZYMAŁOŚĆ: {self.stamina}"
        )
