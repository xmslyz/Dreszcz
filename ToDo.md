* problem z paragrafami, które polecają zapisać/zapamiętać numer. jeśli 
  włączę blokadę, nie będzie możliwe przeniesienie się do tej lokalizacji.
  - 52 -> 274,  
  - 195 -> 113, 
  - 273 -> 103,
  - 15 -> 113,
  - 20 -> 316,
  
* Błędy w scenariuszu (prawdopodobnie)
  - [174] odsyła do 200!

--- 

---

---
## 🧩 **2. Propozycja kategorii:**

### ⚔️ **Walka:**
- `combat`, `combat_disabled`, `combat_effect`, `pre_combat_penalty`
- `after_kill`, `can_escape`, `escape_rule`, `escape_possible`, `max_round`

### 🎲 **Testy i mechanika:**
- `requires_test`, `requires_attribute`, `requires_gold`, `requires_item`, `requires_keys`, `requires_math`
- `memory_test`, `requires_memory`, `requires_memory_test`, `test_type`, `roll`, `min`, `min_remaining`

### 🎁 **Nagrody i efekty:**
- `effects`, `effect`, `reward`, `rewards`, `stat_change`, `stat_changes`, `change`, `attr`
- `gold`, `luck`, `stamina`, `agility`, `Z`, `W`

### 🧳 **Ekwipunek i stan:**
- `add_to_inventory`, `inventory_add_optional`, `items`, `items_in`, `items_out`, `items_lost`, `items_found`, `items_flags`
- `requires_item`, `in_inventory`

### 🧠 **Zarządzanie historią i warunkami:**
- `flag`, `flags_set`, `note`, `condition`, `expected_input`, `any_of`, `special`

### 📜 **Narracja i struktura:**
- `label`, `text`, `target`, `edges`, `choices`, `name`, `action`, `actions`

---

## ⚠️ **3. Rzeczy do sprawdzenia / refaktoryzacji:**

- 🔍 **`stat_change` vs `stat_changes`** – czy to na pewno różne rzeczy?
- 🔍 `requires_memory` i `requires_memory_test` – może warto połączyć jako `requires_memory` + `type: test/other`?
- ❌ `hełm` jako klucz – wygląda jak specyficzny przypadek (`item: hełm`?) i być może powinien być tylko wartością.

---

- ??? 🔧 Stworzyć **słownik głównych kategorii**, np. `{"combat": {...}, "rewards": {...}}`
- ??? 📑 Albo nawet nową strukturę w JSON (np. `rules`, `conditions`, `narration`).
