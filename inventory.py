

class Inventory(object):
    def __init__(self):
        self.sword = {"miecz": 1}
        self.shield = {"tarcza": 1}
        self.lantern = "latarnia"
        self.agility_potion = 0
        self.stamina_potion = 0
        self.luck_potion = 0
        self.food = 8
        self.gold = 5

        self.bag = {}

    def __str__(self):
        if self.agility_potion > 0:
            agility_potion = (f"     - eliksir zręczności: "
                              f"{self.agility_potion} szt.\n")
        else:
            agility_potion = ""

        if self.stamina_potion > 0:
            stamina_potion = (f"     - eliksir wytrzymałości: "
                              f"{self.stamina_potion} szt.\n")
        else:
            stamina_potion = ""

        if self.luck_potion > 0:
            luck_potion = (f"     - eliksir szczęścia: "
                           f"{self.luck_potion} szt.\n")
        else:
            luck_potion = ""

        return (
            "WYPOSAŻENIE\n"
            "* miecz\n"
            "* tarcza\n"
            "* latarnia\n"
            "* plecak:\n"
            f"{agility_potion}"
            f"{stamina_potion}"
            f"{luck_potion}"
            f"     - prowiant: {self.food} szt.\n"
            f"     - złoto: {self.gold} szt.\n"

        )

    def put_helmet(self):
        # 2
        ...

    def transactions(self, in_plus: bool, value):
        """ Buying or seling / eventualy loosing or finding gold """
        if in_plus:
            for i in range(value):
                self.gold += 1
        else:
            if value > self.gold:
                print("Nie masz tyle pieniędzy")
            else:
                for i in range(value):
                    if self.gold == 0:
                        print("Nie masz więcej pieniędzy")
                        break
                    else:
                        self.gold -= 1
