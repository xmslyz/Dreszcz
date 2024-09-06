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
    ...
    # *możesz dodać 2 do liczby uzyskanej na
    # kostkach przy określaniu siły ataku,
    # *każdy atak powoduje nie 2, lecz 3 rany,
    # *gdy STRAŻNIK zrani cię, rzuć kostką:
    # jeśli uzyskasz liczbę nieparzystą, zadaje
    # ci (jak normalnie) 2 rany;
    # jeśli wyrzucisz 2 lub 4 otrzymujesz 1 ranę; jeśli
    # masz 6, nie trafia cię w ogóle.