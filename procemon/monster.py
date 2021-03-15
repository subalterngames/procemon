import io
import re
from random import choice, randint, shuffle
from typing import Tuple, List, Dict
from requests import get, head
from requests.exceptions import ConnectionError, ReadTimeout
from bs4 import BeautifulSoup
import markovify
from procemon.monster_type import MonsterType
from procemon.move import Move
from procemon.rarity import Rarity
from procemon.paths import FLAVOR_TEXT_DIRECTORY, TYPES_DIRECTORY


class Monster:
    """
    A monster has a name, two types, two moves, and some flavor text.
    """

    """:class_var
    Wikipedia text per monster type or noun. Key = The type or noun. Value = Wikipedia text.
    """
    WIKIPEDIA: Dict[str, str] = dict()
    """:class_var
    The path to the list of bad Wikipedia URLs.
    """
    BAD_WIKIPEDIA_URLS_PATH = FLAVOR_TEXT_DIRECTORY.joinpath("bad_wikipedia_urls.txt")
    """:class_var
    A list of known bad Wikipedia URLs.
    """
    BAD_WIKIPEDIA_URLS: List[str] = BAD_WIKIPEDIA_URLS_PATH.read_text(encoding="utf-8").split("\n")
    """:class_var
    A list of consonant sequences that appear in English.
    Scraped from here: http://www.ashley-bovan.co.uk/words/partsofspeech.html
    """
    CONSONANT_SEQUENCES: List[str] = TYPES_DIRECTORY.joinpath("consonant_sequences.txt").read_text(encoding="utf-8").\
        split("\n")
    """:class_var
    A list of vowels.
    """
    VOWELS: List[str] = ["a", "e", "i", "o", "u", "y"]
    """:class_var
    A list of vowels without Y.
    """
    VOWELS_NOT_Y: List[str] = VOWELS[:-1]

    def __init__(self, primary_type: MonsterType, all_types: List[MonsterType], attack_verbs: List[str],
                 type_verbs: Dict[str, List[str]], type_adjectives: Dict[str, List[str]], rarity: Rarity):
        """
        :param all_types: All possible monster types in the dex.
        :param primary_type: The primary type of the monster. The monster will have a second type, chosen randomly.
        :param type_adjectives: Adjectives per monster type.
        :param type_verbs: Verbs per monster type.
        :param attack_verbs: Type-agnostic verbs.
        :param rarity: The rarity of this monster. Determines its overall strength and coolness.
        """

        types: List[MonsterType] = [primary_type]
        # Get a random second type.
        possible_types = [t for t in all_types if t.monster_type != primary_type.monster_type]
        types.append(choice(possible_types))

        """:field
        The names of my two types as a tuple.
        """
        self.types: Tuple[str, str] = (types[0].monster_type, types[1].monster_type)

        """:field
        The rarity of this monster. Determines its overall strength and coolness.
        """
        self.rarity: Rarity = rarity

        # Get the index of the type I am strong against.
        strength_index = 0
        for i in range(len(all_types)):
            if all_types[i].monster_type == primary_type.monster_type:
                if i == len(all_types) - 1:
                    strength_index = 0
                else:
                    strength_index = i + 1
        """:field
        The type of monster that this monster is strong against.
        """
        self.strong_against: str = all_types[strength_index].monster_type

        """:field
        The words used to generate the name.
        """
        self.words: List[str] = []
        for t in types:
            self.words.append(choice(t.nouns))

        """:field
        The name of the monster.
        """
        self.name: str = ""
        for i, w in enumerate(self.words):
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
        for i in range(0, 4):
            if self.name[i] in Monster.VOWELS:
                needs_vowel = False
                break
        if needs_vowel:
            self.name = choice(Monster.VOWELS_NOT_Y) + self.name
        self.name = self.name.lower()
        # Look for 3-letter sequences of consequences that probably don't appear often in English.
        for seq in re.findall(r"([b-df-hj-np-tv-xz]{3})", self.name):
            if seq not in Monster.CONSONANT_SEQUENCES:
                # Replace the second consonant with a vowel.
                seq_list = [s for s in seq]
                seq_list[1] = choice(Monster.VOWELS)
                self.name = self.name.replace(seq, "".join(seq_list))
        # Capitalize the name.
        self.name = self.name.title()

        # Get a list of potential wiki words.
        wikipedia_pages: List[str] = self.words[:]
        shuffle(wikipedia_pages)
        for t in types:
            wikipedia_pages.insert(0, t.wikipedia)

        txt = ""
        num_pages = 0
        for w in wikipedia_pages:
            # Try to get a wikipedia page of the word.
            wiki_text = Monster.get_wiki_text(page=w)
            if wiki_text is not None:
                txt += wiki_text + "\n"
                num_pages += 1
            if num_pages >= 4:
                break
        try:
            model = markovify.Text(txt)
        except KeyError:
            raise Exception(wikipedia_pages, txt)
        """:field
        A description of the monster.
        """
        self.description: str = model.make_short_sentence(80)
        # Make a few attempts.
        num_attempts = 0
        while num_attempts < 20 and self.description is None:
            num_attempts += 1
            self.description = model.make_short_sentence(80)
        if self.description is None:
            print(f"No description: {wikipedia_pages}")

        """:field
        The monster's moves as `Move` objects.
        """
        self.moves: List[Move] = list()
        for i in range(2):
            self.moves.append(Move(monster_type=self.types[0], rarity=rarity, type_adjectives=type_adjectives,
                                   type_verbs=type_verbs, attack_verbs=attack_verbs))

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
        # If this is a known bad page, ignore it.
        if url in Monster.BAD_WIKIPEDIA_URLS:
            return ""
        # Test the HEAD header to see if the page exists.
        try:
            resp = head(url, timeout=20)
            if resp.status_code != 200 and resp.status_code != 301:
                Monster.add_to_bad_urls(url)
                return ""
        except ConnectionError:
            Monster.add_to_bad_urls(url)
            return ""
        except ReadTimeout:
            Monster.add_to_bad_urls(url)
            return ""

        resp = get(url)
        if resp.status_code != 200 and resp.status_code != 301:
            Monster.add_to_bad_urls(url)
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

    @staticmethod
    def add_to_bad_urls(url: str) -> None:
        """
        Remember that this a bad Wikipedia URL.

        :param url: The bad Wikipedia URL.
        """

        Monster.BAD_WIKIPEDIA_URLS.append(url)
        with io.open(str(Monster.BAD_WIKIPEDIA_URLS_PATH.resolve()), "at", encoding="utf-8") as f:
            f.write(url + "\n")
