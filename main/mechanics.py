import random
import logging
from hero import Hero
from NPC import Enemy


logger = logging.getLogger(__name__)

def check_player_surprise(
    player: 'Hero',
    enemies_in_encounter: list['Enemy'],

    base_chance: float = 0.30,
    awareness_sensitivity: float = 0.05,
    luck_sensitivity: float = 0.025,
    min_chance: float = 0.05,
    max_chance: float = 0.95,
    environment_factors: dict | None = None # e.g., {'light': 'dim', 'cover': 'partial'}
) -> bool:
    """
    Checks if the player is surprised by an enemy group based on stats, luck,
    environment, and passed-in tuning parameters.

    Args:
        player: The player character object.
        enemies_in_encounter: A list of enemy objects in the encounter.
        base_chance: Base probability (0.0-1.0) player is surprised.
        awareness_sensitivity: How much chance changes per point of Aware vs Stealth diff.
        luck_sensitivity: How much chance changes per point of Luck diff.
        min_chance: Minimum possible surprise chance.
        max_chance: Maximum possible surprise chance.
        environment_factors: A dictionary describing relevant environmental conditions.

    Returns:
        bool: True if the player is surprised, False otherwise.
    """
    if not enemies_in_encounter:
        logger.debug("No enemies in encounter, player is not surprised.")
        return False

    highest_awareness = 0
    highest_luck = 0
    for enemy in enemies_in_encounter:
        highest_awareness = max(highest_awareness, getattr(enemy, 'get_awareness', lambda: 0)())
        highest_luck = max(highest_luck, getattr(enemy, 'get_luck', lambda: 0)())

    player_stealth = getattr(player, 'get_stealth_attribute', lambda: 0)()
    player_luck = getattr(player, 'get_luck', lambda: 0)()

    stat_diff = highest_awareness - player_stealth
    luck_diff = highest_luck - player_luck

    stealth_vs_awareness_mod = stat_diff * awareness_sensitivity
    luck_mod = luck_diff * luck_sensitivity

    environment_mod = 0.0
    if environment_factors:
        light = environment_factors.get('light', 'normal') 
        cover = environment_factors.get('cover', 'none') 

        if light == 'dim':
            environment_mod -= 0.10 
        elif light == 'dark':
            environment_mod -= 0.25 
        elif light == 'bright':
            environment_mod += 0.10 
        if cover == 'partial':
            environment_mod -= 0.15 
        elif cover == 'full':
            environment_mod -= 0.30 

        # TODO: Could add distance factor here if available
        logger.debug("Calculated environment modifier: %.2f (Light: %s, Cover: %s)",
                     environment_mod, light, cover)
   
    final_chance = base_chance + stealth_vs_awareness_mod + luck_mod + environment_mod

    final_chance = max(min_chance, min(max_chance, final_chance))

    is_surprised = (random.random() < final_chance)

    logger.debug(
        "Surprise Check: Roll < %.2f? Player(Stealth:%d Luck:%d) vs "
        "Enemy(HighAware:%d HighLuck:%d) | Mods(Aware:%.2f Luck:%.2f Env:%.2f) | Result: %s",
        final_chance, player_stealth, player_luck,
        highest_awareness, highest_luck,
        stealth_vs_awareness_mod, luck_mod, environment_mod,
        "SURPRISED" if is_surprised else "Not Surprised"
    )

    return is_surprised