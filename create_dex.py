from procemon import Dex
from procemon.card_back import CardBack

if __name__ == "__main__":
    d = Dex(num_types=12, num_monsters_per_type=9, quiet=False)
    d.write_json()
    d.create_cards()
    card_back = CardBack.get()
    card_back.save(d.dst.joinpath("0_card_back.png"))
