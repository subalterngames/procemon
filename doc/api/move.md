# Move

`from procemon.move import Move`

A move that a Procemon can do. Moves have a name generated from verbs and adjectives associated with types.
They also have costs and effects.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `MOODS` | List[str] | A subset of all possible moods that is chosen randomly per dex. This is populated the first time it is used. |

***

## Fields

- `type` The type of move.

- `damage` The damage this move will deal.

- `cost` The energy cost of this move.

- `special` A special effect of the move.

- `name` The name of the move.

***

## Functions

#### \_\_init\_\_

**`Move(monster_type, rarity, type_adjectives, type_verbs, attack_verbs)`**

**`Move(monster_type, rarity, type_adjectives, type_verbs, attack_verbs, force_damage=False, force_no_special=False)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| monster_type |  str |  | The type of move. |
| rarity |  Rarity |  | The rarity of the monster this move belongs to. This is used to decide move's coolness. |
| type_adjectives |  Dict[str, List[str] |  | Adjectives per monster type. |
| type_verbs |  Dict[str, List[str] |  | Verbs per monster type. |
| attack_verbs |  List[str] |  | Type-agnostic verbs that are nearby "attack verbs". |
| force_damage |  bool  | False | If True, this move will always deal damage. If False, it might deal damage. |
| force_no_special |  bool  | False | If True, this move will never have a special effect. |

