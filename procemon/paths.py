from pathlib import Path
from pkg_resources import resource_filename

# The path to the data files.
DATA_DIRECTORY = Path(resource_filename(__name__, "data"))
# The path to the types data.
TYPES_DIRECTORY = DATA_DIRECTORY.joinpath("types")
# The path to the mood file.
MOODS_PATH = DATA_DIRECTORY.joinpath("moods.txt")
