from typing import List
from random import shuffle
from pathlib import Path
from fpdf import FPDF
from procemon.card_back import CardBack


class Zine:
    """
    Create a zine PDF from a dex.
    """

    @staticmethod
    def create(dex_path: Path, num_pages: int = 13, quiet: bool = False) -> None:
        """
        Create a zine from a dex of cards. To create the cards, see: `Dex.create_cards()`

        :param dex_path: The path to the cards directory.
        :param num_pages: Number of pages in the zine.
        :param quiet: If True, suppress console output.
        """

        if not quiet:
            print("Creating card back...")
        # Create a card back.
        card_back = CardBack.get()
        card_back_path = dex_path.joinpath("card_back.png")
        card_back.save(str(card_back_path.resolve()))
        print("...Done!")

        # Get the dimensions of the card on the page.
        w = 4.1
        r = card_back.size[1] / card_back.size[0]
        h = w * r
        left_x = 1
        right_x = 11 - w - 0.5

        # Create the zine.
        pdf = FPDF(unit="in", orientation="L")
        pdf.add_page()

        # Add the card back.
        pdf.image(str(card_back_path.resolve()), left_x, 1, w, h)
        pdf.image(str(card_back_path.resolve()), right_x, 1, w, h)
        # Delete the temporary file.
        card_back_path.unlink()

        # Get all of the card paths and randomize the order.
        card_paths: List[Path] = list()
        for f in dex_path.iterdir():
            if not f.is_file() or f.suffix != ".png":
                continue
            card_paths.append(f)
        shuffle(card_paths)

        if not quiet:
            print("Adding cards to zine...")
        i = 0
        page = 0
        while page < num_pages:
            # Add a new page.
            pdf.add_page()
            # Insert two cards.
            pdf.image(str(card_paths[i].resolve()), left_x, 1, w, h)
            pdf.image(str(card_paths[i + 1].resolve()), right_x, 1, w, h)
            page += 1
            i += 2
        zine_path = dex_path.joinpath("zine.pdf")
        pdf.output(str(zine_path.resolve()))
        if not quiet:
            print("...Done!")
            print(zine_path.resolve())