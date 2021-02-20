from typing import List


class MonsterType:
    """
    A type of monster, as well as its associated keywords and nouns.
    """

    def __init__(self, monster_type: str, nouns: List[str], verbs: List[str], adjectives: List[str],
                 wikipedia: str, imagenet: str):
        """
        :param monster_type: The name of this type.
        :param nouns: The nouns associated with this type. Used for naming a monster.
        :param verbs: The verbs associated with this type. Used for naming a move.
        :param adjectives: The adjectives associated with this type. Used for naming a move.
        :param wikipedia: The name of the Wikipedia page corresponding to this type.
        :param imagenet: The ImageNet word corresponding to this type.
        """

        """:field
        The name of this type.
        """
        self.monster_type: str = monster_type
        """:field
        The nouns associated with this type. Used for naming a monster.
        """
        self.nouns: List[str] = nouns
        """:field
        The verbs associated with this type. Used for naming a move.
        """
        self.verbs: List[str] = verbs
        """:field
        The adjectives associated with this type. Used for naming a move.
        """
        self.adjectives: List[str] = adjectives
        """:field
        The name of the Wikipedia page corresponding to this type.
        """
        self.wikipedia: str = wikipedia
        """:field
        The ImageNet word corresponding to this type.
        """
        self.imagenet: str = imagenet
