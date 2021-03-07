from pathlib import Path
from pkg_resources import resource_filename

# The path to the data files.
DATA_DIRECTORY = Path(resource_filename(__name__, "data"))
# The path to the types files.
TYPES_DIRECTORY = DATA_DIRECTORY.joinpath("types")
# The path to the moves files.
MOVES_DIRECTORY = DATA_DIRECTORY.joinpath("moves")
# The path to the images files.
IMAGES_DIRECTORY = DATA_DIRECTORY.joinpath("images")
# The path to the font files.
FONTS_DIRECTORY = DATA_DIRECTORY.joinpath("fonts")
# The path to the text font.
TEXT_FONT = FONTS_DIRECTORY.joinpath("pokemon-classic.ttf")
# The path to the symbol font.
SYMBOL_FONT = FONTS_DIRECTORY.joinpath("Rosette110621-4eVp.ttf")
# The path to the flavor text files.
FLAVOR_TEXT_DIRECTORY = DATA_DIRECTORY.joinpath("flavor_text")
# The path to the region placename files.
REGIONS_DIRECTORY = DATA_DIRECTORY.joinpath("regions")
# The directory of the word vector file.
WORD_VEC_DIRECTORY = Path.home().joinpath("procemon_wv")
