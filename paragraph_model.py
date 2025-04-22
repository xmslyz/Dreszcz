import re
from typing import Optional


class Paragraph:
    def __init__(self, number: int, text: str, meta: Optional[dict] = None):
        self.number = number
        self.text = text
        self.meta = meta or {}

        # Cechy wykrywane automatycznie
        self.has_monsters = self.detect_monsters()
        self.contains_choices = self.detect_choices()
        self.affects_stats = self.detect_stat_changes()
        self.requires_test = self.detect_test_requirement()
        self.can_escape = self.detect_escape()
        self.contains_items = self.detect_items()

    def detect_monsters(self) -> bool:
        return "combat" in self.meta or "monsters" in self.meta

    def detect_choices(self) -> bool:
        return "Jeśli chcesz" in self.text or bool(re.findall(r"\bpatrz (\d+)\b", self.text))

    def detect_stat_changes(self) -> bool:
        return any(kw in self.text.lower() for kw in ["tracisz", "zyskujesz", "dodaj", "odejmij", "zmniejsz", "zwiększ", "punkt"])

    def detect_test_requirement(self) -> bool:
        return any(kw in self.text.lower() for kw in ["rzuć", "test", "umiejętność"])

    def detect_escape(self) -> bool:
        return "uciec" in self.text.lower() or "możesz uciec" in self.text.lower() or "escape_rules" in self.meta

    def detect_items(self) -> bool:
        return "items" in self.meta or any(kw in self.text.lower() for kw in ["otrzymujesz", "znajdujesz", "dodaj do ekwipunku"])

    def get_links(self) -> list[int]:
        return list(map(int, re.findall(r"\bpatrz (\d+)\b", self.text)))

    def get_flags_set(self) -> set[str]:
        return set(self.meta.get("flags_set", []))

    def get_required_flags(self) -> set[str]:
        return set(self.meta.get("required_flags", []))

    def is_terminal(self) -> bool:
        return not self.contains_choices and not self.has_monsters

    def has_random_event(self) -> bool:
        return "losowo" in self.text.lower() or "rzut" in self.text.lower()

    def summary(self) -> str:
        flags = []
        if self.has_monsters:
            flags.append("Walka")
        if self.requires_test:
            flags.append("Test")
        if self.contains_choices:
            flags.append("Wybory")
        if self.contains_items:
            flags.append("Itemy")
        if self.affects_stats:
            flags.append("Statystyki")
        if self.is_terminal():
            flags.append("Koniec")
        return f"P{self.number}: {', '.join(flags)}"
