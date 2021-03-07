# Changelog

## 1.4.0

- Each dex now has a random region name and symbol
  - Added Rosette font
  - Added `japan.txt` and `us.txt` place-name lists
  - Card backs include the region name and symbol
- Fixed: Sometimes, the text of the second move on the card overlaps with the flavor text (this is probably _actually_ fixed now)

## 1.3.0

- Moved changelog from README to this document
- Removed type: Metal (There aren't any valid images on ImageNet!)
- Removed some moods and verbs that we never want to include
- Fixed: Sometimes the flavor text of a card includes Unicode characters that the font doesn't support (this also happens very rarely if the card is a Sport-type). Now, unsupported characters are automatically replaced by supported characters.
  - (Backend): Added: `util/font_test.py` to check cached word lists for unsupported characters
  - (Backend): Added required modules: `Unidecode` and `fonttools`
- Fixed: Sometimes, the text of the second move on the card overlaps with the flavor text
- Fixed: Sometimes, a move without a conditional (i.e. "roll a die") can deal bonus damage (which doesn't make sense)
- Fixed: Crash if the dex has more monster types than colors in the palette
- Fixed: Monster names often have sequences of consonants that are impossible to pronounce. Now, when a name is generated, it is compared to a list of 3-letter consonant sequences; if it has an invalid sequence, the middle (second) consonant is replaced with a random vowel. It's still possible for a word to remain unpronounceable, just less likely.
  - (Backend): Added `data/types/consonant_sequences.txt`
  - (Backend) Added: `Monster.CONSONANT_SEQUENCES`, `Monster.VOWELS`, and `Monster.VOWELS_NOT_Y` class variables
- Fixed: Monster names sometimes include non-alphabetical characters (hyphens are still allowed)
- Fixed: Bad Wikipedia key for Boat type
- (Backend) Added: `image_url_test.py` Make sure that each monster type has enough images
- (Backend) Added: `Dex.get_all_types()` Returns all possible monster types


## 1.2.1

- Updated the image of the cards in the README

## 1.2.0

- Removed types: Antelope, Mollusk, Raptor
- Added MANY more adjectives and verbs.
- Move names tend to be much more closely associated with the primary monster type.
- Added `wv.py`. This script will pre-cache all of the verbs and adjectives per monster type rather than generating them at runtime with a word vector model.
  - `MonsterType` (and the associated .json files) now have pre-cached `verbs` and `adjectives` lists.
- Moves that deal damage generally prefer attack verbs (see below).
- Fixed: Sometimes a move says that you should roll a die and on "1 or greater" the effect happens. Now, the minimum number is 2.
- Fixed: The first double-quotation marks in the monster flavor text at the bottom of the card is facing the wrong way.
- (Backend) Added: `attack_verbs.txt` Pre-cached attack verbs.
- (Backend) Added: `src.txt` Sources for adjectives and verbs.
- (Backend) Moved most of the code related to verbs and adjecives from `dex.py` to `wv.py`

## 1.1.0

- Added a text file to the module to remember bad Wikipedia URLs so we don't test them again.
- Added monster types: Antelope, Antenna, Candy, Mollusk, Needlework, Sailor, Singer, Sphere, Tool, Tree.
- Fixed: Monster names sometimes end with `'S`.
- Fixed: Getting Wikipedia pages for flavor text and images for sprites is slow and your router might complain. Now, the HEAD headers are tested before the GET headers, which is a lot faster. 
- Fixed: Sometimes, images are marked as "bad" when they're actually valid.
- Backend: Moved image URL testing in `Dex` to `get_image_from_url()` so that this function can be tested externally.

## 1.0.2

- Minor update to README.

## 1.0.1

- Fixed: Data files aren't included.