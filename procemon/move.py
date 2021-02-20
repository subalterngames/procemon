from random import shuffle, random, choice, randint
from typing import List, Dict
from procemon.rarity import Rarity
from procemon.paths import MOVES_DIRECTORY


class Move:
    """
    A move that a Procemon can do. Moves have a name generated from verbs and adjectives associated with types.
    They also have costs and effects.
    """

    """:class_var
    A subset of all possible moods that is chosen randomly per dex. This is populated the first time it is used.
    """
    MOODS: List[str] = list()

    def __init__(self, monster_type: str, rarity: Rarity, attack_verbs: List[str], type_verbs: Dict[str, List[str]],
                 type_adjectives: Dict[str, List[str]], force_damage: bool = False, force_no_special: bool = False):
        """
        :param monster_type: The type of move.
        :param rarity: The rarity of the monster this move belongs to. This is used to decide move's coolness.
        :param type_adjectives: Adjectives per monster type.
        :param type_verbs: Verbs per monster type.
        :param attack_verbs: Type-agnostic verbs that are nearby "attack verbs".
        :param force_damage: If True, this move will always deal damage. If False, it might deal damage.
        :param force_no_special: If True, this move will never have a special effect.
        """

        if len(Move.MOODS) == 0:
            # Get all of the moods.
            moods: List[str] = MOVES_DIRECTORY.joinpath("moods.txt").read_text(encoding="utf-8").split("\n")

            # Get a random subset of the moods.
            shuffle(moods)
            Move.MOODS = moods[:6]

        """:field
        The type of move.
        """
        self.type: str = monster_type

        # Get an adjective.
        if random() < 0.75:
            adj = choice(type_adjectives[monster_type])
        else:
            adj = ""

        # Get the odds of dealing no damage.
        if force_damage:
            no_damage = 0.0
        elif rarity == Rarity.common:
            no_damage = 0.3
        elif rarity == Rarity.uncommon:
            no_damage = 0.2
        else:
            no_damage = 0.1
        # This attack won't deal damage and will be cheaper. It will have a special effect.
        if random() < no_damage:
            """:field
            The damage this move will deal.
            """
            self.damage: int = 0
            """:field
            The energy cost of this move.
            """
            self.cost: int = randint(1, 2)
            special = True
        # Get the damage, the cost, and whether there's a special effect.
        else:
            if rarity == Rarity.common:
                self.damage = randint(1, 3)
                self.cost: int = randint(1, 4)
                special = random() < 0.2
            elif rarity == Rarity.uncommon:
                if random() < 0.75:
                    self.damage = randint(1, 3)
                    self.cost: int = randint(1, 4)
                    special = random() < 0.4
                # Occasionally, a really good move.
                else:
                    self.damage = randint(2, 4)
                    self.cost: int = randint(1, 3)
                    special = random() < 0.6
            else:
                if random() < 0.75:
                    self.damage = randint(2, 5)
                    self.cost: int = randint(2, 5)
                # Occasionally, a really good move.
                else:
                    self.damage = randint(2, 6)
                    self.cost: int = randint(1, 5)
                special = random() < 0.4
        if force_no_special:
            special = False
        """:field
        A special effect of the move.
        """
        self.special: str = ""
        if special:
            # Add a conditional.
            if random() < 0.4:
                conditional: str = f"Roll a die. On a {randint(2, 5)} or above, "
            else:
                conditional: str = ""

            effect = ""
            # Deal extra damage.
            if self.damage > 0 and random() < 0.3:
                if random() > 0.66:
                    effect = f"+{randint(1, 3)} damage."
                else:
                    effect = f"This Proćemon deals {randint(1, 3)} to itself."

            # Set a mood.
            if effect == "" and random() < 0.7:
                if random() < 0.33:
                    effect = f"This Proćemon is now {choice(Move.MOODS)}."
                else:
                    effect = f"The defending Proćemon is now {choice(Move.MOODS)}."

            # Add counters.
            if effect == "":
                num_counters = randint(1, 4)
                effect = f"Add {num_counters} {monster_type.title()} counter"
                # Pluralize.
                if num_counters == 1:
                    effect += "."
                else:
                    effect += "s."

            # Combine the effect with the conditional.
            if conditional == "":
                self.special = effect
            else:
                self.special = conditional + effect[0].lower() + effect[1:]
        # Choose a type specific verb.
        if self.damage == 0 or random() < 0.5:
            verb = choice(type_verbs[monster_type])
        # Choose a generic attack verb.
        else:
            verb = choice(attack_verbs)

        if adj != "":
            """:field 
            The name of the move.
            """
            self.name = f"{adj} {verb}".title()
        else:
            self.name = verb.title()
