# Monster

`from procemon.monster import Monster`

A monster has a name, two types, two moves, and some flavor text.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `WIKIPEDIA` | Dict[str, str] | Wikipedia text per monster type or noun. Key = The type or noun. Value = Wikipedia text. |

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

**`Monster(all_types, primary_type, type_adjectives, type_verbs, generic_verbs, rarity)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| all_types |  List[MonsterType] |  | All possible monster types in the dex. |
| primary_type |  MonsterType |  | The primary type of the monster. The monster will have a second type, chosen randomly. |
| type_adjectives |  Dict[str, List[str] |  | Adjectives per monster type. |
| type_verbs |  Dict[str, List[str] |  | Verbs per monster type. |
| generic_verbs |  List[str] |  | Type-agnostic verbs. |
| rarity |  Rarity |  | The rarity of this monster. Determines its overall strength and coolness. |

#### get_wiki_text

**`Monster.get_wiki_text(page)`**

_This is a static function._

Given the name of the page, get text from Wikipedia.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| page |  str |  | A word in a category that might be a Wikipedia page. |

_Returns:_  All of the paragraph text from a Wikipedia page if it exists. Otherwise, an empty string.
