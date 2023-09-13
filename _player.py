def choose_potion(self):
    potion = input("Jaki eliksir wybierasz [s]/[w]/[z]? :  ")
    match potion:
        case "s":
            self.inventory.potion.update({"luck": 1})
        case "w":
            self.inventory.potion.update({"stamina": 1})
        case "z":
            self.inventory.potion.update({"agility": 1})

def eat(self, extra=False):
    value = 5 if extra else 4
    food = self.inventory.food
    if food > 0:
        while not self.stamina > self.max_stamina:
            for _ in range(value):
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
            for _ in range(points):
                self.agility += 1
                if self.agility == self.max_agility:
                    break
                print(self.agility)
        self.inventory.potion.update({"agility": potion - 1})
        print(self.inventory.potion["agility"])
    else:
        print("Nie masz eliksiru zręczności")




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
                "Kiedy zacząłeś uciekać potwór zdążył w ostatniej chwili "
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

def use_object(self, attribute: str, in_plus: bool, value: int):
    attributes = ["stamina", "agility", "luck"]

    if not in_plus:
        value = value * -1

    if attribute in attributes:
        new_value = getattr(self, attribute) + value
        setattr(self, attribute, new_value)
    else:
        pass

def use_gold(self, in_plus: bool, value):

    if in_plus:
        for i in range(value):
            if self.inventory.gold > 0:
                self.inventory.gold += 1
    else:
        for i in range(value):
            if self.inventory.gold == 0:
                print("Nie masz więcej pieniędzy")
                break
            else:
                self.inventory.gold -= 1

def use_bag(self, object_name):
    self.inventory.bag.update({object_name: 1})

    print(self.inventory.bag)

def play_cards(self, with_luck: bool):
    k2 = Dice().d2()
    if with_luck:
        if self.am_i_lucky():
            self.inventory.gold += k2
        else:
            for i in range(k2):
                if self.inventory.gold == 0:
                    print("Nie masz więcej pieniędzy")
                    break
                else:
                    self.inventory.gold -= 1
    else:
        if k2 % 2 == 0:
            for i in range(k2):
                if self.inventory.gold == 0:
                    print("Nie masz więcej pieniędzy")
                    break
                else:
                    self.inventory.gold -= 1
        else:
            self.inventory.gold += k2

    print(self.inventory.gold)

def use_fireball(self):
    # *możesz dodać 2 do liczby uzyskanej na
    # kostkach przy określaniu siły ataku,
    # *każdy atak powoduje nie 2, lecz 3 rany,
    # *gdy STRAŻNIK zrani cię, rzuć kostką:
    # jeśli uzyskasz liczbę nieparzystą, zadaje
    # ci (jak normalnie) 2 rany;
    # jeśli wyrzucisz 2 lub 4 otrzymujesz 1 ranę; jeśli
    # masz 6, nie trafia cię w ogóle.
    ...


class Inventory:
    def __init__(self):
        self.sword = {"plain sword": 1}
        self.shield = {"plain shield": 1}
        self.bag = {}
        self.lantern = "lantern"
        self.potion = {"agility": 0, "stamina": 0, "luck": 0}
        self.food = 8
        self.gold = 5
