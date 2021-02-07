# Dex

`from procemon import Dex`

A dex is a collection of Procemon.
When created, the dex will randomly select types and moods, assign verbs and adjectives, and generate the Procemon.

***

## Class Variables

| Variable | Type | Description |
| --- | --- | --- |
| `BAD_IMAGE_URLS_PATH` | Path | The path to the file of URLs that we know are bad. |
| `BAD_IMAGE_URLS` | List[str] | A list of known bad URLs. |
| `BAD_WNIDS_PATH` | Path | The path to the file of URLs that we know are bad. |
| `BAD_WNIDS` | List[str] | A list of known bad wnids. |
| `IMAGENET` | Dict[str, str] | Imagenet data. Key = A word. Value = The wnid corresponding to that word. |
| `PALETTE` | np.array | A numpy array of a color palette. |
| `LIGHT_COLORS` | np.array | The portion of the palette where there are light colors. |
| `DARK_COLORS` | np.array | The portion of the palette where there are darker colors. |
| `CARD_PATH` | Path | The path to the card template image. |
| `ENERGY_DIRECTORY` | Path | The path to the energy icons. |

***

## Fields

- `types` A dictionary of monster types in this dex. Key = the name of the type. Value = a `MonsterType` object.

- `dst` The output directory of the dex.

- `monsters` Monsters in the dex sorted by type name.

- `images_per_type` A dictionary of images per monster type. Key = The monster type. Value = The images.
This is populated as-needed i.e. whenever we need images for a new type.

- `color_indices` The indices of colors in the palette mapped to names of monster types.

***

## Functions

#### \_\_init\_\_

**`Dex()`**

**`Dex(num_types=12, num_monsters_per_type=9, quiet=False)`**

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| num_types |  int  | 12 | Number of types of monsters in the dex. |
| num_monsters_per_type |  int  | 9 | Number of monsters per type. |
| quiet |  bool  | False | If True, suppress console messages. |

#### write_json

**`self.write_json()`**

Save the dex as a JSON dictionary.

#### create_cards

**`self.create_cards()`**

**`self.create_cards(quiet=False)`**

Create images of each monster in the dex.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| quiet |  bool  | False | If True, suppress console output. |

#### get_image

**`self.get_image(monster_type)`**

Generate a sprite for a type of monster.

If there are no images cached for `monster_type`, this function will cache and convert them.


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| monster_type |  str |  | The type of monster that needs an image. |

_Returns:_  A unique (to this dex) sprite-ish image converted from an ImageNet image.

#### get_images

**`self.get_images(monster_type)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| monster_type |  str |  | The name of the monster type. |

_Returns:_  A list of converted images for this type using ImageNet data.

#### get_card

**`self.get_card(monster)`**


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| monster |  Monster |  | The monster. |

_Returns:_  A card image for this monster.

#### add_to_bad_urls

**`Dex.add_to_bad_urls(url)`**

_This is a static function._

Remember that this a bad URL.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| url |  str |  | The bad URL. |

#### add_to_bad_wnids

**`Dex.add_to_bad_wnids(wnid)`**

_This is a static function._

Remember that this a bad wnid.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| wnid |  str |  | The wnid URL. |

#### lighten

**`Dex.lighten(color, percent)`**

_This is a static function._

Lighten a color.

Source: https://stackoverflow.com/questions/28015400/how-to-fade-color


| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| color |  |  | The color as an array-like. |
| percent |  |  | Percent by which to lighten. |

_Returns:_  The lightened color as a tuple.

