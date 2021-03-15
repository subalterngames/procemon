from pkg_resources import get_distribution
from PIL import Image, ImageFont, ImageDraw
from PIL.PngImagePlugin import PngImageFile
import numpy as np
from perlin_numpy.perlin2d import generate_fractal_noise_2d
from procemon.paths import IMAGES_DIRECTORY, TEXT_FONT, SYMBOL_FONT


class CardBack:
    """
    Create an image of the back of a card.
    """

    @staticmethod
    def get(region: str, symbol: str) -> PngImageFile:
        """
        :param region: The name of the dex region.
        :param symbol: The region's symbol.

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
        font = ImageFont.truetype(str(TEXT_FONT.resolve()), 12)
        draw = ImageDraw.Draw(card)
        pad = 52
        draw.text((pad, card.size[1] - 80), "Copyright 2021 Subaltern Games", "white", font=font)
        version_y = card.size[1] - 80 + 16
        draw.text((pad, version_y), "https://subalterngames.com", "white", font=font)
        # Add the version.
        version = str(get_distribution("procemon")).split(" ")[1]
        version_x = int(card.size[0] - font.getsize(version)[0] - pad)
        draw.text((version_x, version_y), version, "white", font=font)

        # Draw the region.
        region = f"{region} Region"
        # Center the text.
        region_x = int(card.size[0] - font.getsize(region)[0] - pad)
        region_y = pad + 4
        draw.text((region_x, region_y), region, "white", font=font)
        # Draw a cool symbol.
        symbol_font = ImageFont.truetype(str(SYMBOL_FONT.resolve()), 24)
        symbol_x = region_x - symbol_font.getsize(symbol)[0] - 12
        symbol_y = pad
        draw.text((symbol_x, symbol_y), symbol, "white", font=symbol_font, encoding="symb")

        # Add the logo.
        logo = Image.open(str(IMAGES_DIRECTORY.joinpath("logo.png").resolve()))
        logo_x = int((card.size[0] / 2) - (logo.size[0] / 2))
        logo_y = int((card.size[1] / 2) - (logo.size[1] * 0.66))
        card.paste(logo, (logo_x, logo_y), mask=logo)
        return card
