from game_mechanics import Paragraph
from character import Hero

def process_paragraph(paragraph: Paragraph, player: Hero) -> dict:
    """
    Processes a Paragraph: applies effects, checks for combat, and determines possible choices.

    Args:
        paragraph (Paragraph): The current paragraph to process.
        player (Player): The player instance to modify or evaluate.

    Returns:
        dict: Result of processing with keys:
            - 'next_edges': list of edges (choices) available to player
            - 'effects_applied': list of effects that were actually applied
            - 'requires_combat': bool, whether combat should be triggered
            - 'is_end': bool, whether this paragraph ends the game

    Example:
        >>> result = process_paragraph(current, player)
        >>> for edge in result['next_edges']:
        ...     print(edge['label'])
    """
    effects_applied = []

    for effect in paragraph.effects:
        condition = effect.get("condition")
        if condition and not check_condition(condition, player):
            continue

        attr = effect["attr"]
        change = int(effect["change"])

        if hasattr(player, attr):
            old_val = getattr(player, attr)
            setattr(player, attr, old_val + change)
            effects_applied.append(effect)

    available_edges = []
    for edge in paragraph.edges:
        condition = edge.get("condition")
        if not condition or check_condition(condition, player):
            available_edges.append(edge)

    return {
        "next_edges": available_edges,
        "effects_applied": effects_applied,
        "requires_combat": bool(paragraph.combat),
        "is_end": any(edge.get("target") == "END" for edge in paragraph.edges)
    }
