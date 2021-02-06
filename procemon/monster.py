import re
from random import choice, randint
from typing import Tuple, List, Dict
from requests import get
from bs4 import BeautifulSoup
import markovify
from procemon.monster_type import MonsterType
from procemon.move import Move
from procemon.rarity import Rarity


class Monster:
    """
    A monster has a name, two types, two moves, and some flavor text.
    """

    """:class_var
    Wikipedia text per monster type or noun. Key = The type or noun. Value = Wikipedia text.
    """
    WIKIPEDIA: Dict[str, str] = dict()

    def __init__(self, types: Tuple[MonsterType, MonsterType], rarity: Rarity, strong_against: str):
        """
        :param types: The types associated with this monster.
        :param rarity: The rarity of this monster. Determines its overall strength and coolness.
        :param strong_against: The type of monster that this monster is strong against.
        """

        """:field
        The names of my two types as a tuple.
        """
        self.types: Tuple[str, str] = (types[0].monster_type, types[1].monster_type)

        """:field
        The rarity of this monster. Determines its overall strength and coolness.
        """
        self.rarity: Rarity = rarity
        """:field
        The type of monster that this monster is strong against.
        """
        self.strong_against: str = strong_against

        # Get a random word from each name.
        words = []
        for t in types:
            words.append(choice(t.nouns))

        """:field
        The name of the monster.
        """
        self.name: str = ""
        for i, w in enumerate(words):
            # If the word is small, just take all of it.
            if len(w) <= 5:
                self.name += w
            else:
                # Get a random slice of the beginning of the first word and the end of the second word.
                if i == 0:
                    start = 0
                    end = randint(4, 8)
                else:
                    start = randint(len(w) - 8, len(w) - 4)
                    end = len(w)
                self.name += w[start: end]
        # If the first few letters don't have a vowel, insert one at the beginning.
        needs_vowel = True
        vowels = ["a", "e", "i", "o", "u", "y"]
        for i in range(0, 4):
            if self.name[i] in vowels:
                needs_vowel = False
                break
        if needs_vowel:
            self.name = choice(vowels[:-1]) + self.name
        # Capitalize the name.
        self.name = self.name.lower().title()

        # Get a list of potential wiki words.
        wikipedia_pages: List[str] = words[:]
        for t in types:
            wikipedia_pages.append(t.wikipedia)

        txt = ""
        for c, w in zip(self.types, wikipedia_pages):
            # Try to get a wikipedia page of the word.
            txt += Monster.get_wiki_text(page=w)
        model = markovify.Text(txt)
        """:field
        A description of the monster.
        """
        self.description: str = model.make_short_sentence(80)
        # Make a few attempts.
        num_attempts = 0
        while num_attempts < 4 and self.description is None:
            num_attempts += 1
            self.description = model.make_short_sentence(80)
        if self.description is None:
            print(f"No description: {wikipedia_pages}")

        """:field
        The monster's moves as `Move` objects.
        """
        self.moves: List[Move] = list()
        for t in self.types:
            self.moves.append(Move(monster_type=t, rarity=rarity))

        if rarity == Rarity.common:
            """:field
            The monster's hitpoints.
            """
            self.hp: int = randint(2, 5)
        elif rarity == Rarity.uncommon:
            self.hp: int = randint(3, 7)
        else:
            self.hp: int = randint(5, 12)

    @staticmethod
    def get_wiki_text(page: str) -> str:
        """
        Given the name of the page, get text from Wikipedia.

        :param page: A word in a category that might be a Wikipedia page.

        :return: All of the paragraph text from a Wikipedia page if it exists. Otherwise, an empty string.
        """

        # Return the page if it's already been cached.
        if page in Monster.WIKIPEDIA:
            return Monster.WIKIPEDIA[page]
        url = f"https://en.wikipedia.org/wiki/{page}"
        resp = get(url)
        if resp.status_code != 200:
            return ""
        # Scrape all of the paragraphs.
        soup = BeautifulSoup(resp.content, 'html.parser')
        paragraphs = soup.select("p")
        wiki = ""
        for para in paragraphs:
            # Ignore lists of words.
            if max([len(p) for p in para.text.split("\n")]) < 80:
                continue
            # Remove footnotes and append the paragraph to the wiki text.
            wiki += re.sub(r"\[[0-9]{1,3}\]", "", para.text)
        # Cache the page.
        Monster.WIKIPEDIA[page] = wiki
        return wiki
