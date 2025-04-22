from paragraph import Paragraph
from character import Hero as Player
from typing import List, Dict, Any


def get_available_edges(paragraph: Paragraph, player: Player) -> List[Dict[str, Any]]:
    """
    Returns a list of paragraph.edges that the player can take, based on conditions.

    Args:
        paragraph (Paragraph): The paragraph containing edges.
        player (Player): The player object for condition checks.

    Returns:
        List[Dict[str, Any]]: List of edge dicts that are available.

    Example:
        >>> edges = get_available_edges(paragraph, player)
        >>> for edge in edges:
        ...     print(edge['label'], '->', edge['target'])
    """
    available = []
    for edge in paragraph.edges:
        cond = edge.get('condition')
        if cond is None or check_condition(cond, player):
            available.append(edge)
    return available


def process_paragraph(
        paragraph: Paragraph,
        player: Player
) -> Dict[str, Any]:
    """
    Core logic to process a Paragraph and determine next steps.

    Applies effects, checks for combat, and computes available choices.

    Args:
        paragraph (Paragraph): The current Paragraph object.
        player (Player): The current player instance.

    Returns:
        Dict[str, Any]: A summary with keys:
            - 'effects_applied': List of effects applied to the player.
            - 'requires_combat': True if combat data is present.
            - 'next_edges': Available edges (List of edge dicts).
            - 'is_end': True if this paragraph ends the game (no edges & no combat).

    Example:
        >>> result = process_paragraph(paragraph, player)
        >>> if result['requires_combat']:
        ...     run_combat(paragraph, player)
        >>> choice = result['next_edges'][0]
    """
    # 1. Apply effects
    applied = []
    for effect in paragraph.effects:
        cond = effect.get('condition')
        if cond is None or check_condition(cond, player):
            # apply change
            attr = effect['attr']
            change = int(effect['change'])
            current = getattr(player, attr)
            setattr(player, attr, current + change)
            applied.append(effect)

    # 2. Check for combat
    needs_combat = paragraph.has_combat

    # 3. Compute available edges
    edges = get_available_edges(paragraph, player)

    # 4. Determine if end
    is_end = not needs_combat and len(edges) == 0

    return {
        'effects_applied': applied,
        'requires_combat': needs_combat,
        'next_edges': edges,
        'is_end': is_end
    }

def check_condition(condition: Dict[str, Any], player: Player) -> bool:
    """
    Evaluates whether the given condition dictionary is satisfied by the player's state.

    Supported keys in `condition`:
      - "in_inventory": Dict[str, bool] – item presence or absence requirement
      - "min_hp": int                   – minimum required hit points
      - "flag": str                     – game-flag that must be set

    Returns:
        bool: True if all specified sub-conditions are met, False otherwise.
    """
    # 1. Inventory requirements
    inv_req = condition.get("in_inventory")
    if inv_req:
        for item, required in inv_req.items():
            has = player.has_item(item)
            if required and not has:
                return False
            if not required and has:
                return False

    # 2. Minimum HP requirement
    min_hp = condition.get("min_hp")
    if min_hp is not None and player.hp < min_hp:
        return False

    # 3. Flag requirement
    flag = condition.get("flag")
    if flag:
        flags = getattr(player, "flags", {})
        if isinstance(flags, dict):
            if not flags.get(flag, False):
                return False
        else:
            if flag not in flags:
                return False

    return True