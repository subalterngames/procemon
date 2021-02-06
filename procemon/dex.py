from random import shuffle
from json import loads
from pathlib import Path
from secrets import token_urlsafe
from typing import List
from procemon.paths import TYPES_DIRECTORY, MOODS_PATH
from procemon.monster_type import MonsterType


class Dex:
    """
    A dex is a collection of Procemon.
    When created, the dex will randomly select types and moods, assign verbs and adjectives, and generate the Procemon.
    """

    def __init__(self, num_types: int = 12, num_monsters_per_type: int = 9, num_moods: int = 6, quiet: bool = False):
        """
        :param num_types: Number of types of monsters in the dex.
        :param num_monsters_per_type: Number of monsters per type.
        :param num_moods: Number of possible moods.
        :param quiet: If True, suppress console messages.
        """

        # Get all of the types.
        types: List[MonsterType] = list()
        for f in TYPES_DIRECTORY.iterdir():
            td = loads(f.read_text(encoding="utf-8"))
            types.append(MonsterType(**td))

        # Get a random subset of the types.
        shuffle(types)
        """:field
        A list of random types as `MonsterType` objects. Length = `num_types` (see constructor).
        """
        self.types: List[MonsterType] = types[:num_types]

        # Get all of the moods.
        moods = MOODS_PATH.read_text(encoding="utf-8").split("\n")

        # Get a random subset of the moods.
        shuffle(moods)
        """:field
        A list of random moods as strings. Length = `num_moods` (see constructor).
        """
        self.moods: List[str] = moods[:num_moods]

        """:field
        The output directory of the dex.
        """
        self.dst: Path = Path(f"dst/dex/{token_urlsafe(3)}")
        if not self.dst.exists():
            self.dst.mkdir(parents=True)
        if not quiet:
            print(f"Output directory: {self.dst}")
