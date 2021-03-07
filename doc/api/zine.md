# Zine

`from procemon.zine import Zine`

Create a zine PDF from a dex.

***

#### create

**`Zine.create(dex_path, card_back)`**

**`Zine.create(dex_path, card_back, num_pages=13, quiet=False)`**

_This is a static function._

Create a zine from a dex of cards. To create the cards, see: `Dex.create_cards()`

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| dex_path |  Path |  | The path to the cards directory. |
| card_back |  PngImageFile |  | The image for the back of the card. |
| num_pages |  int  | 13 | Number of pages in the zine. |
| quiet |  bool  | False | If True, suppress console output. |

