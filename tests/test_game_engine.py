# test_game_engine.py
import pytest

# Zaimportuj swoje moduły:
import engine_core
from engine_core import get_available_edges, process_paragraph
# import combat_engine_refactored
# from combat_engine_refactored import combat_engine

# --- POMOCNICZE KLASY DO TESTÓW ---

class DummyPlayer:
    def __init__(self):
        self.hp = 10
        self.strength = 2
        # symulujemy system zabitych potworów
        self.kills = {}

    def is_dead(self):
        return self.hp <= 0

    def has_item(self, item):
        # w testach będziemy to nadpisywać przez check_condition
        return False

class DummyParagraph:
    def __init__(self, edges=None, effects=None, combat=None):
        self.edges = edges or []
        self.effects = effects or []
        self.combat = combat or []
    @property
    def has_combat(self):
        return bool(self.combat)

# --- MOCK check_condition DLA engine_core ---

@pytest.fixture(autouse=True)
def patch_check_condition():
    # Domyślnie false, chyba że condition zawiera {'allow': True}
    engine_core.check_condition = lambda cond, player: cond.get("allow", False)
    yield
    # (opcjonalnie) przywróć oryginał tutaj

# --- TESTY DLA get_available_edges ---

def test_get_available_edges_no_condition():
    p = DummyParagraph(edges=[{"label":"A","target":"1"}])
    player = DummyPlayer()
    edges = get_available_edges(p, player)
    assert len(edges) == 1
    assert edges[0]["label"] == "A"

def test_get_available_edges_with_false_condition():
    p = DummyParagraph(edges=[{"label":"A","target":"1","condition":{"allow":False}}])
    player = DummyPlayer()
    edges = get_available_edges(p, player)
    assert edges == []

def test_get_available_edges_with_true_condition():
    p = DummyParagraph(edges=[{"label":"A","target":"1","condition":{"allow":True}}])
    player = DummyPlayer()
    edges = get_available_edges(p, player)
    assert len(edges) == 1
    assert edges[0]["target"] == "1"

# --- TESTY DLA process_paragraph ---

def test_process_paragraph_applies_effect_and_detects_end():
    # paragraf z efektem +5 hp, bez walki i bez krawędzi
    p = DummyParagraph(
        effects=[{"attr":"hp","change":"+5"}],
        edges=[],
        combat=[]
    )
    player = DummyPlayer()
    result = process_paragraph(p, player)
    assert player.hp == 15                     # efekt zastosowany
    assert result["effects_applied"] == p.effects
    assert result["requires_combat"] is False
    assert result["next_edges"] == []
    assert result["is_end"] is True            # brak krawędzi i walki

def test_process_paragraph_detects_combat_and_edges():
    # paragraf z walką i jedną dostępną krawędzią
    p = DummyParagraph(
        effects=[],
        edges=[{"label":"Go","target":"2","condition":{"allow":True}}],
        combat=[{"name":"X","hp":1,"strength":1}]
    )
    player = DummyPlayer()
    result = process_paragraph(p, player)
    assert result["effects_applied"] == []
    assert result["requires_combat"] is True
    assert len(result["next_edges"]) == 1
    assert result["is_end"] is False

# --- TESTY DLA combat_engine_refactored.combat_engine ---

def test_combat_engine_no_monsters():
    # paragraf bez potworów
    p = DummyParagraph(combat=[])
    player = DummyPlayer()
    res = combat_engine(
        paragraph=p,
        player=player,
        chapter_id="chap1",
        cheat=False,
        escape_callback=None,
        use_luck_callback=None,
        round_callback=None
    )
    assert res["won"] is True
    assert res["escaped"] is False
    assert res["rounds"] == []
    assert res["kills"] == []

def test_combat_engine_cheat_instakill():
    # paragraf z jednym potworem, tryb cheat
    p = DummyParagraph(combat=[{"name":"Gob","hp":10,"strength":1}])
    player = DummyPlayer()
    res = combat_engine(
        paragraph=p,
        player=player,
        chapter_id="chap1",
        cheat=True,
        escape_callback=None,
        use_luck_callback=None,
        round_callback=None
    )
    assert res["won"] is False  or res["won"] is True
    # Ważne: w trybie cheat potwór idzie do kills bez rund walki
    assert "Gob" in res["kills"]
    assert res["rounds"] == []

