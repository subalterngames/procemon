from json import JSONEncoder
import numpy as np
from procemon.rarity import Rarity
from procemon.move import Move


class DexEncoder(JSONEncoder):
    """
    Use this class to encode a dex.

    Source: https://stackoverflow.com/questions/27050108/convert-numpy-type-to-python
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, Move):
            return obj.__dict__
        elif isinstance(obj, Rarity):
            return obj.name
        else:
            print(obj)
            return super(DexEncoder, self).default(obj)
