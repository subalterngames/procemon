from procemon import Dex

if __name__ == "__main__":
    d = Dex(num_types=12, num_monsters_per_type=9, quiet=False)
    d.write_json()
    d.create_cards()
