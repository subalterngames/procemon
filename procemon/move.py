from random import shuffle, random, choice, randint
from typing import List, Dict
from gensim.models import KeyedVectors
from procemon.rarity import Rarity
from procemon.paths import WORD_VEC_PATH, MOVES_DIRECTORY


class Move:
    """
    A move that a Procemon can do. Moves have a name generated from verbs and adjectives associated with types.
    They also have costs and effects.
    """

    """:class_var
    All potential verbs.
    """
    VERBS: List[str] = MOVES_DIRECTORY.joinpath("verbs.txt").read_text(encoding="utf-8").split("\n")
    shuffle(VERBS)
    """:class_var
    All potential adjectives.
    """
    ADJECTIVES: List[str] = MOVES_DIRECTORY.joinpath("adjectives.txt").read_text(encoding="utf-8").split("\n")
    shuffle(ADJECTIVES)
    """:class_var
    A list of verbs that any move can use. This list is populated the first time it is used.
    """
    GENERIC_VERBS: List[str] = list()
    """:class_var
    The word vector model.
    """
    WV: KeyedVectors = KeyedVectors.load_word2vec_format(str(WORD_VEC_PATH.resolve()), binary=False)
    """:class_var
    A dictionary of verbs associated with each type. This is populated the first time it is used.
    Key = The monster type as a string. Value = A list of verbs.
    """
    TYPE_VERBS: Dict[str, List[str]] = dict()
    """:class_var
    A dictionary of adjectives associated with each type. This is populated the first time it is used.
    Key = The monster type as a string. Value = A list of adjectives.
    """
    TYPE_ADJECTIVES: Dict[str, List[str]] = dict()
    """:class_var
    A subset of all possible moods that is chosen randomly per dex. This is populated the first time it is used.
    """
    MOODS: List[str] = list()

    def __init__(self, monster_type: str, rarity: Rarity, force_damage: bool = False, force_no_special: bool = False):
        """
        :param monster_type: The type of move.
        :param rarity: The rarity of the monster this move belongs to. This is used to decide move's coolness.
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
        # Populate the list of generic verbs.
        if len(Move.GENERIC_VERBS) == 0:
            for v in Move.VERBS:
                # If the verb is nearby "attack" then it's a generic verb.
                try:
                    d = Move.WV.distance(v, "attack")
                # This word isn't isn't in the word vector model. Ignore it.
                except KeyError:
                    continue

                if d < 0.6:
                    Move.GENERIC_VERBS.append(v)

        # Assign type-specific words.
        for pos, lst, generic, num, d in zip([Move.TYPE_VERBS, Move.TYPE_ADJECTIVES], [Move.VERBS, Move.ADJECTIVES],
                                             [Move.GENERIC_VERBS, []], [12, 12], [0.7, 0.57]):
            if monster_type not in pos:
                pos[monster_type] = list()
                for w in lst:
                    # Ignore generic words.
                    if w in generic:
                        continue
                    if len(pos[monster_type]) >= 12:
                        break
                    # Get the distance between this word and the type.
                    try:
                        distance = Move.WV.distance(w, monster_type)
                    except KeyError:
                        continue
                    # If there is a close association, add the word.
                    if distance < d:
                        pos[monster_type].append(w)

        # Get an adjective.
        if random() < 0.75:
            adj = choice(Move.TYPE_ADJECTIVES[monster_type])
        else:
            adj = ""

        # Choose a type specific verb.
        if random() < 0.45:
            verb = choice(Move.TYPE_VERBS[monster_type])
        # Choose a generic verb.
        else:
            verb = choice(Move.VERBS)

        if adj != "":
            """:field 
            The name of the move.
            """
            self.name = f"{adj} {verb}".title()
        else:
            self.name = verb.title()

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
                conditional: str = f"Roll a die. If the roll is above a {randint(1, 5)}, "
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
