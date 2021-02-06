from pathlib import Path
from pkg_resources import resource_filename

# The path to the data files.
DATA_DIRECTORY = Path(resource_filename(__name__, "data"))
# The paths to the types data.
TYPES_DIRECTORY = DATA_DIRECTORY.joinpath("types")
