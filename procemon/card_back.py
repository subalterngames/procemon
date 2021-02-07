from pkg_resources import get_distribution
from PIL import Image, ImageFont, ImageDraw
from PIL.PngImagePlugin import PngImageFile
import numpy as np
from perlin_numpy.perlin2d import generate_fractal_noise_2d
from procemon.paths import IMAGES_DIRECTORY, FONTS_DIRECTORY


class CardBack:
    """
    Create an image of the back of a card.
    """

    @staticmethod
    def get() -> PngImageFile:
        """
        :return: An image of a card back.
        """

        # Load the card template.
        card = Image.open(str(IMAGES_DIRECTORY.joinpath("card_back.png").resolve()))

        light_color: np.array = np.array([92, 99, 140, 255])
        dark_color: np.array = np.array([35, 57, 107, 255])
        # Get some perlin noise
        perlin_noise = generate_fractal_noise_2d(shape=(1056, 680), res=(8, 8))
        pixels = card.load()
        for y in range(card.size[1]):
            for x in range(card.size[0]):
                if pixels[x, y] == (255, 255, 255, 255):
                    # Get a color interpolated with perlin noise.
                    color = (light_color - dark_color) * perlin_noise[y, x] + dark_color
                    pixels[x, y] = tuple([int(ch) for ch in color])

        # Add Subaltern Games text.
        font_file: str = str(FONTS_DIRECTORY.joinpath("pokemon-classic.ttf").resolve())
        font = ImageFont.truetype(font_file, 12)
        draw = ImageDraw.Draw(card)
        draw.text((52, card.size[1] - 80), "Copywrite 2021 Subaltern Games", "white", font=font)
        draw.text((52, card.size[1] - 80 + 16), "https://subalterngames.com", "white", font=font)

        # Add the version.
        draw.text((card.size[0] - 116, card.size[1] - 80 + 16), str(get_distribution("procemon")).split(" ")[1],
                  "white", font=font)

        # Add the logo.
        logo = Image.open(str(IMAGES_DIRECTORY.joinpath("logo.png").resolve()))
        logo_x = int((card.size[0] / 2) - (logo.size[0] / 2))
        logo_y = int((card.size[1] / 2) - (logo.size[1] * 0.66))
        card.paste(logo, (logo_x, logo_y), mask=logo)
        return card
