from procemon import Dex
from procemon.zine import Zine


if __name__ == "__main__":
    # Create the dex.
    d = Dex(num_types=12, num_monsters_per_type=9, quiet=False)
    d.write_json()
    d.create_cards()
    # Create the zine.
    Zine.create(dex_path=d.dst)
