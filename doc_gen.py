from pathlib import Path
from py_md_doc import PyMdDoc


"""
Create API documentation.
"""

if __name__ == "__main__":
    files = ["card_back.py",
             "dex.py",
             "monster.py",
             "monster_type.py",
             "move.py",
             "rarity.py"]
    md = PyMdDoc(input_directory=Path("procemon"), files=files)
    md.get_docs(output_directory=Path("doc/api"))
