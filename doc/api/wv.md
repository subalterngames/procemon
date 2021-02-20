# WV

`from procemon.wv import WV`

Use a word vector model to assign verbs and adjectives to monster types.
These are stored in the .json monster type files.

***

## Fields

- `quiet` If True, suppress console output.

- `verbs` A list of all possible verbs.

- `adjectives` A list of all possible adjectives.

- `wv` The word vectors model.

***

## Functions

#### \_\_init\_\_

**`WV()`**

**`WV(quiet=False)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| quiet |  bool  | False | If True, suppress console output. |

#### get_word_vector_model

**`self.get_word_vector_model()`**

Get the loaded WordVector model. Download the file if it doesn't already exist.

_Returns:_  The word vector KeyedVectors model.

#### get_attack_verbs

**`self.get_attack_verbs()`**

**`self.get_attack_verbs(distance=0.5, write=False)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| distance |  float  | 0.5 | The verb must be this close to an "attack verb". |
| write |  bool  | False | If True, write the list to disk. |

_Returns:_  A list of all verbs that are nearby an "attack" verb.

#### get_type_verbs

**`self.get_type_verbs(monster_type)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| monster_type |  str |  | The monster type name string. |

_Returns:_  A list of verbs nearby the monster type word.

#### get_type_adjectives

**`self.get_type_adjectives(monster_type)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| monster_type |  str |  | The monster type name string. |

_Returns:_  A list of adjectives nearby the monster type word.

