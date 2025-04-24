# paragraph.py

ESCAPE_RULES = {
    "2": {"enabled": True, "max_round": None, "after_kill": False},
    "32": {"enabled": False, "max_round": 0, "after_kill": False},
    "69": {"enabled": False, "max_round": 0, "after_kill": False},
    "92": {"enabled": True, "max_round": None, "after_kill": False},
    "98": {"enabled": False, "max_round": 0, "after_kill": False},
    "107": {"enabled": False, "max_round": 0, "after_kill": False},
    "109": {"enabled": False, "max_round": 0, "after_kill": False},
    "116": {"enabled": False, "max_round": 0, "after_kill": False},
    "157": {"enabled": True, "max_round": 1, "after_kill": False},
    "169": {"enabled": True, "max_round": 1, "after_kill": False},
    "184": {"enabled": True, "max_round": 2, "after_kill": False},
    "213": {"enabled": False, "max_round": 0, "after_kill": False},
    "216": {"enabled": False, "max_round": 0, "after_kill": False},
    "238": {"enabled": True, "max_round": 0, "after_kill": True},
    "255": {"enabled": False, "max_round": 0, "after_kill": False},
    "277": {"enabled": True, "max_round": 0, "after_kill": True},
    "288": {"enabled": False, "max_round": 0, "after_kill": False},
    "307": {"enabled": False, "max_round": 0, "after_kill": False},
    "309": {"enabled": True, "max_round": 1, "after_kill": False},
    "312": {"enabled": True, "max_round": 0, "after_kill": True},
    "317": {"enabled": False, "max_round": 0, "after_kill": False},
    "332": {"enabled": False, "max_round": 0, "after_kill": False},
    "341": {"enabled": False, "max_round": 0, "after_kill": False},
    "344": {"enabled": False, "max_round": 0, "after_kill": False},
    "355": {"enabled": False, "max_round": 0, "after_kill": False},
    "361": {"enabled": False, "max_round": 0, "after_kill": False},
    "367": {"enabled": False, "max_round": 0, "after_kill": False}
}


class Paragraph:
    def __init__(self, number: str, text: dict):
        self.number: str = number
        self.text_raw: dict = text
        self.text: str = text.get("text", "")  # to tylko czysty tekst paragrafu
        self.edges: list[str] = self._detect_edges()
        self.can_escape: bool = self._detect_escape()
        self.escape_rule: dict | None = ESCAPE_RULES.get(number)
        self.has_monsters = self._detect_monsters()
        self.post_combat = self.text_raw.get("post_combat", {})

        if self.escape_rule:
            self.can_escape = self.escape_rule.get("enabled", False)

    def _detect_edges(self) -> list[str]:
        edges = self.text_raw.get("edges")
        if isinstance(edges, list):
            return [str(edge.get("target")) for edge in edges if "target" in edge]
        return []

    def _detect_escape(self) -> bool:
        return True

    def _detect_monsters(self) -> bool:
        return False

    @property
    def contains_choices(self) -> bool:
        return bool(self.edges)
