# Monster

`from procemon.monster import Monster`

A monster has a name, two types, two moves, and some flavor text.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `WIKIPEDIA` | Dict[str, str] | Wikipedia text per monster type or noun. Key = The type or noun. Value = Wikipedia text. |
| `BAD_WIKIPEDIA_URLS_PATH ` |  | The path to the list of bad Wikipedia URLs. |
| `BAD_WIKIPEDIA_URLS` | List[str] | A list of known bad Wikipedia URLs. |
| `CONSONANT_SEQUENCES` | List[str] | A list of consonant sequences that appear in English.
    Scraped from here: http://www.ashley-bovan.co.uk/words/partsofspeech.html |
| `VOWELS` | List[str] | A list of vowels. |
| `VOWELS_NOT_Y` | List[str] | A list of vowels without Y. |

***

## Fields

- `types` The names of my two types as a tuple.

- `rarity` The rarity of this monster. Determines its overall strength and coolness.

- `strong_against` The type of monster that this monster is strong against.

- `name` The name of the monster.

- `description` A description of the monster.

- `moves` The monster's moves as `Move` objects.

- `hp` The monster's hitpoints.

***

## Functions

#### \_\_init\_\_

**`Monster(all_types, primary_type, type_adjectives, type_verbs, attack_verbs, rarity)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| all_types |  List[MonsterType] |  | All possible monster types in the dex. |
| primary_type |  MonsterType |  | The primary type of the monster. The monster will have a second type, chosen randomly. |
| type_adjectives |  Dict[str, List[str] |  | Adjectives per monster type. |
| type_verbs |  Dict[str, List[str] |  | Verbs per monster type. |
| attack_verbs |  List[str] |  | Type-agnostic verbs. |
| rarity |  Rarity |  | The rarity of this monster. Determines its overall strength and coolness. |

#### get_wiki_text

**`Monster.get_wiki_text(page)`**

_This is a static function._

Given the name of the page, get text from Wikipedia.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| page |  str |  | A word in a category that might be a Wikipedia page. |

_Returns:_  All of the paragraph text from a Wikipedia page if it exists. Otherwise, an empty string.

#### add_to_bad_urls

**`Monster.add_to_bad_urls(url)`**

_This is a static function._

Remember that this a bad Wikipedia URL.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| url |  str |  | The bad Wikipedia URL. |

