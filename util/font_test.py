from json import loads
from procemon import Dex
from procemon.paths import TYPES_DIRECTORY, MOVES_DIRECTORY

"""
Test the cached text (nouns, verbs, adjectives) to make sure that their characters are supported by the card font.
This will print out any unsupported words.
"""

# Test the nouns.
print("Type nouns:")
for f in TYPES_DIRECTORY.iterdir():
    if f.is_file():
        d = loads(f.read_text(encoding="utf-8"))
        for n in d["nouns"]:
            if Dex.get_supported_string(n) != n:
                print(n, n.encode('utf-8'), f)
print("")
# Test the verbs.
for f in ["verbs.txt", "adjectives.txt"]:
    print(f)
    for w in MOVES_DIRECTORY.joinpath(f).read_text(encoding="utf-8").split("\n"):
        if Dex.get_supported_string(w) != w:
            print(w, w.encode('utf-8'))
    print("")
