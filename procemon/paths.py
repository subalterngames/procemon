from pathlib import Path
from pkg_resources import resource_filename

# The path to the data files.
DATA_DIRECTORY = Path(resource_filename(__name__, "data"))
# The path to the types files.
TYPES_DIRECTORY = DATA_DIRECTORY.joinpath("types")
# The path to the moves files.
MOVES_DIRECTORY = DATA_DIRECTORY.joinpath("moves")
# The path to the word vector file.
WORD_VEC_PATH = Path("D:/glove.txt")
