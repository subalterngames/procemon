import io
from random import shuffle
from json import loads, dumps
from pathlib import Path
from secrets import token_urlsafe
from typing import List, Dict, Optional
import re
import textwrap
import numpy as np
from requests import get, head
from requests.exceptions import ConnectionError, MissingSchema, TooManyRedirects, ChunkedEncodingError, ReadTimeout
from PIL import Image, ImageFont, ImageDraw, UnidentifiedImageError, ImageOps
from PIL.PngImagePlugin import PngImageFile
from fontTools.ttLib import TTFont
from unidecode import unidecode
from perlin_numpy.perlin2d import generate_fractal_noise_2d
from procemon.paths import TYPES_DIRECTORY, IMAGES_DIRECTORY, FONTS_DIRECTORY, MOVES_DIRECTORY
from procemon.monster_type import MonsterType
from procemon.monster import Monster
from procemon.rarity import Rarity
from procemon.dex_encoder import DexEncoder


class Dex:
    """
    A dex is a collection of Procemon.
    When created, the dex will randomly select types and moods, assign verbs and adjectives, and generate the Procemon.
    """

    """:class_var
    The path to the file of URLs that we know are bad.
    """
    BAD_IMAGE_URLS_PATH: Path = IMAGES_DIRECTORY.joinpath("bad_image_urls.txt")
    """:class_var
    A list of known bad URLs.
    """
    BAD_IMAGE_URLS: List[str] = BAD_IMAGE_URLS_PATH.read_text(encoding="utf-8").split("\n")
    """:class_var
    The path to the file of URLs that we know are bad.
    """
    BAD_WNIDS_PATH: Path = IMAGES_DIRECTORY.joinpath("bad_wnids.txt")
    """:class_var
    A list of known bad wnids.
    """
    BAD_WNIDS: List[str] = BAD_WNIDS_PATH.read_text(encoding="utf-8").split("\n")
    """:class_var
    Imagenet data. Key = A word. Value = The wnid corresponding to that word.
    """
    IMAGENET: Dict[str, str] = loads(IMAGES_DIRECTORY.joinpath("imagenet_wnids.json").read_text(encoding="utf-8"))
    """:class_var
    A numpy array of a color palette.
    """
    PALETTE: np.array = np.load(str(IMAGES_DIRECTORY.joinpath("palette.npy").resolve()))
    """:class_var
    The portion of the palette where there are light colors.
    """
    LIGHT_COLORS: np.array = PALETTE[-1][1:-3]
    """:class_var
    The portion of the palette where there are darker colors.
    """
    DARK_COLORS: np.array = PALETTE[-2][1:-3]
    """:class_var
    The path to the card template image.
    """
    CARD_PATH: Path = IMAGES_DIRECTORY.joinpath("card.png")
    """:class_var
    The path to the energy icons. 
    """
    ENERGY_DIRECTORY: Path = IMAGES_DIRECTORY.joinpath("energy")
    """:class_var
    The path to the font file.
    """
    FONT_FILE: str = str(FONTS_DIRECTORY.joinpath("pokemon-classic.ttf").resolve())
    with TTFont(FONT_FILE) as font:
        """:class_var
        A list of all Unicode characters supported by the font. Source: https://stackoverflow.com/a/58232763
        """
        SUPPORTED_CHARACTERS = list(set(chr(y[0]) for x in font["cmap"].tables for y in x.cmap.items()))

    def __init__(self, num_types: int = 12, num_monsters_per_type: int = 9, quiet: bool = False):
        """
        :param num_types: Number of types of monsters in the dex.
        :param num_monsters_per_type: Number of monsters per type.
        :param quiet: If True, suppress console messages.
        """

        # Get all of the types.
        all_types = Dex.get_all_types()
        # Get a random subset of the types.
        shuffle(all_types)
        all_types = all_types[:num_types]
        """:field
        A dictionary of monster types in this dex. Key = the name of the type. Value = a `MonsterType` object.
        """
        self.types: Dict[str, MonsterType] = dict()
        for t in all_types:
            self.types[t.monster_type] = t
        color_indices: List[int] = list(np.arange(len(Dex.LIGHT_COLORS)))
        shuffle(color_indices)
        """:field
        The indices of colors in the palette mapped to names of monster types.
        """
        self.color_indices: Dict[str, int] = dict()
        color_index: int = 0
        for t in all_types:
            self.color_indices[t.monster_type] = color_indices[color_index]
            color_index += 1
            # If there are more monster types than colors, go back to the start of the color index list.
            if color_index >= len(color_indices):
                color_index = 0
        attack_verbs = MOVES_DIRECTORY.joinpath("attack_verbs.txt").read_text(encoding="utf-8").split("\n")
        shuffle(attack_verbs)

        """:field
        The output directory of the dex.
        """
        self.dst: Path = Path(f"dst/dex/{token_urlsafe(3)}")
        if not self.dst.exists():
            self.dst.mkdir(parents=True)
        if not quiet:
            print(f"Output directory: {self.dst.resolve()}")

        """:field
        Monsters in the dex sorted by type name.
        """
        self.monsters: Dict[str, Dict[str, Monster]] = dict()

        # The number of monsters per type. Used for images.
        self.__num_monsters_per_type: int = num_monsters_per_type

        # Get and shuffle the type-specific verbs and adjectives.
        type_adjectives: Dict[str, List[str]] = dict()
        type_verbs: Dict[str, List[str]] = dict()
        for t in self.types:
            type_adjectives[t] = self.types[t].adjectives[:]
            type_verbs[t] = self.types[t].verbs[:]

        # Get the number of monsters per rarity.
        num_rare_per_type = int(num_monsters_per_type * 0.2)
        num_uncommon_per_type = int(num_monsters_per_type * 0.4)
        num_common_per_type = num_monsters_per_type - num_rare_per_type - num_uncommon_per_type
        if not quiet:
            print("Populating dex...")
        # Populate the dex.
        for t in self.types:
            if not quiet:
                print(t.title())
            self.monsters[t] = dict()
            rarities: List[Rarity] = []
            # Get monsters per rarity.
            for i in range(num_rare_per_type):
                rarities.append(Rarity.rare)
            for i in range(num_uncommon_per_type):
                rarities.append(Rarity.uncommon)
            for i in range(num_common_per_type):
                rarities.append(Rarity.common)
            for rarity in rarities:
                m = Monster(primary_type=self.types[t], all_types=all_types, rarity=rarity,
                            attack_verbs=attack_verbs, type_adjectives=type_adjectives, type_verbs=type_verbs)
                if not quiet:
                    print("\t" + m.name)
                self.monsters[t][m.name] = m

        """:field
        A dictionary of images per monster type. Key = The monster type. Value = The images.
        This is populated as-needed i.e. whenever we need images for a new type.
        """
        self.images_per_type: Dict[str, List[PngImageFile]] = dict()

    def write_json(self) -> None:
        """
        Save the dex as a JSON dictionary.
        """

        data = dict()
        for t in self.monsters:
            data[t] = dict()
            for n in self.monsters[t]:
                data[t][n] = self.monsters[t][n].__dict__
        self.dst.joinpath("dex.json").write_text(dumps(data, sort_keys=True, indent=2, cls=DexEncoder),
                                                 encoding="utf-8")

    def create_cards(self, quiet: bool = False) -> None:
        """
        Create images of each monster in the dex.

        :param quiet: If True, suppress console output.
        """

        if not quiet:
            print("Creating cards...")

        for t in self.monsters:
            if not quiet:
                print(t)
            for m in self.monsters[t]:
                # Generate the card.
                card = self.get_card(monster=self.monsters[t][m])
                # Save the card.
                card.save(str(self.dst.joinpath(f"{self.monsters[t][m].name}.png").resolve()))
                print(f"\t{m}")
        print("DONE!")

    def get_image(self, monster_type: str) -> PngImageFile:
        """
        Generate a sprite for a type of monster.

        If there are no images cached for `monster_type`, this function will cache and convert them.

        :param monster_type: The type of monster that needs an image.

        :return: A unique (to this dex) sprite-ish image converted from an ImageNet image.
        """
        # Get image URLs for the monster's primary type.
        if monster_type not in self.images_per_type:
            self.images_per_type[monster_type] = self.get_images(monster_type=monster_type)
        # Return the last image in the list. There might be duplicates.
        if len(self.images_per_type[monster_type]) == 1:
            return self.images_per_type[monster_type][0]
        # Pop the next image to avoid duplicates.
        else:
            return self.images_per_type[monster_type].pop(0)

    def get_images(self, monster_type: str) -> List[PngImageFile]:
        """
        :param monster_type: The name of the monster type.

        :return: A list of converted images for this type using ImageNet data.
        """

        # Get the wnids of the type name and the nouns. Some words might not have wnids.
        wnids = []
        for n in self.types[monster_type].nouns:
            if n in Dex.IMAGENET:
                wnids.append(Dex.IMAGENET[n])
        # Randomize the order of the wnids.
        shuffle(wnids)
        # Insert the root wnid at start.
        wnids.insert(0, Dex.IMAGENET[self.types[monster_type].imagenet])

        images: List[PngImageFile] = list()

        # Get a list of URLs from the list of wnids.
        wnid_index = 0
        while wnid_index < len(wnids) and len(images) < self.__num_monsters_per_type:
            wnid = wnids[wnid_index]
            # Get URLs from the wnid.
            urls = Dex.get_wnid_urls(wnid=wnid)
            if len(urls) == 0:
                wnid_index += 1
                if wnid not in Dex.BAD_WNIDS:
                    Dex.add_to_bad_urls(wnid)
                continue
            # We'll only test these and move on if they're no good.
            urls = urls[:20]
            # Test each URL.
            for url in urls:
                img = Dex.get_image_from_url(url=url)
                # Remember that this is a bad image so we never try it again.
                if img is None:
                    Dex.add_to_bad_urls(url)
                    continue
                # Convert to grayscale.
                img = ImageOps.grayscale(img)
                # Increase the contrast.
                img = ImageOps.autocontrast(img)
                # Resize.
                img = img.resize((32, 32), Image.LANCZOS)
                # Colorize using the palette color for this type.
                img = ImageOps.colorize(img, black="black",
                                        white=Dex.LIGHT_COLORS[self.color_indices[monster_type]])
                # Enlarge.
                img = img.resize((400, 400), Image.NEAREST)
                # Append the image.
                images.append(img)
            wnid_index += 1
        shuffle(images)
        return images

    def get_card(self, monster: Monster) -> PngImageFile:
        """
        :param monster: The monster.

        :return: A card image for this monster.
        """

        # Make sure that the monster's description string is supported by the card font.
        # We only check the description because we know that all names, types, verbs, and adjectives are ok.
        # See: `util/font_test.py` in the repo.
        if monster.description is None:
            monster.description = "None"
        monster.description = Dex.get_supported_string(monster.description)

        card = Image.open(str(Dex.CARD_PATH.resolve()))

        # Get Perlin noise.
        perlin_noise = generate_fractal_noise_2d(shape=(1056, 680), res=(4, 4))

        color_index = self.color_indices[monster.types[0]]

        # Set the background color.
        bg_color = list(Dex.LIGHT_COLORS[color_index])
        bg_color.append(255)
        bg_color = Dex.lighten(bg_color, 0.7)
        pixels = card.load()
        for y in range(card.size[1]):
            for x in range(card.size[0]):
                if pixels[x, y] == (255, 255, 255, 255):
                    # Add some Perlin noise.
                    pixels[x, y] = Dex.lighten(bg_color, (perlin_noise[y, x]))
        pad_x = 52
        # Add the name of the monster.
        f_header = ImageFont.truetype(Dex.FONT_FILE, 28)
        draw = ImageDraw.Draw(card)
        black = (0, 0, 0, 255)
        header_y = 52
        draw.text((pad_x, header_y), monster.name, black, font=f_header)
        # Add the HP.
        hp_text = f"{monster.hp} HP"
        hp_text_x = card.size[0] - pad_x - f_header.getsize(hp_text)[0]
        draw.text((hp_text_x, header_y), hp_text, black, font=f_header)

        # Add the types.
        f_type = ImageFont.truetype(Dex.FONT_FILE, 18)
        type_text_y = header_y + 50
        type_text_x = pad_x
        # Add the first type.
        type_text = monster.types[0].title()
        type_text_color = list(Dex.DARK_COLORS[color_index])
        type_text_color.append(255)
        draw.text((type_text_x, type_text_y), type_text, tuple(type_text_color), font=f_type)
        type_text_size = f_type.getsize(type_text)
        type_text_x += type_text_size[0]
        # Add a space.
        type_text = " & "
        draw.text((type_text_x, type_text_y), type_text, black, font=f_type)
        type_text_size = f_type.getsize(type_text)
        type_text_x += type_text_size[0]
        # Add the second type.
        type_text = monster.types[1].title()
        type_text_color = list(Dex.DARK_COLORS[self.color_indices[monster.types[1]]])
        type_text_color.append(255)
        draw.text((type_text_x, type_text_y), type_text, tuple(type_text_color), font=f_type)

        # Add rarity.
        if monster.rarity == Rarity.rare:
            rarity = "Rare"
            rarity_x = hp_text_x
        elif monster.rarity == Rarity.uncommon:
            rarity = "Uncommon"
            rarity_x = hp_text_x - 24
        else:
            rarity = "Common"
            rarity_x = hp_text_x
        f_rarity = ImageFont.truetype(Dex.FONT_FILE, 18)
        draw.text((rarity_x, type_text_y), rarity, black, font=f_rarity)

        # Draw a box for the image.
        img_box_shape_y = header_y + type_text_size[1] + 70
        img_box_shape_x = 135
        img_box_shape_d = 404
        image_box_shape = [(img_box_shape_x, img_box_shape_y), (img_box_shape_x + img_box_shape_d,
                                                                img_box_shape_y + img_box_shape_d)]
        draw.rectangle(image_box_shape, fill=None, outline=black, width=4)

        # Add the image.
        image = self.get_image(monster_type=monster.types[0])
        card.paste(image, (img_box_shape_x + 2, img_box_shape_y + 2))

        # Get the move energy icons.
        energy_icons = dict()
        for f in Dex.ENERGY_DIRECTORY.iterdir():
            if f.is_file() and f.suffix == ".png":
                energy_icons[int(f.name[0])] = Image.open(str(f.resolve()))

        move_x = pad_x
        move_text_x = img_box_shape_x
        move_y = img_box_shape_y + img_box_shape_d + 22

        # Remember where to put the strength.
        move_y_0 = move_y

        f_move_special = ImageFont.truetype(Dex.FONT_FILE, 18)
        f_move_damage = ImageFont.truetype(Dex.FONT_FILE, 28)
        last_line = None
        for i, m in enumerate(monster.moves):
            # Add the energy icon.
            energy_icon = energy_icons[m.cost]
            # Colorize the energy icon.
            energy_icon_color = list(Dex.DARK_COLORS[self.color_indices[monster.types[0]]])
            energy_icon_color.append(255)
            energy_icon_color = Dex.lighten(energy_icon_color, 0.8)
            pixels = energy_icon.load()
            for y in range(energy_icon.size[1]):
                for x in range(energy_icon.size[0]):
                    if pixels[x, y] == (255, 255, 255, 255):
                        pixels[x, y] = energy_icon_color
            energy_icon = energy_icon.resize((64, 64))
            energy_icon_y = move_y
            if m.special == "":
                energy_icon_y += 12
            # Paste the icon.
            card.paste(energy_icon, (move_x, energy_icon_y), mask=energy_icon)

            move_text_y = move_y

            if m.special == "":
                move_text_y += 26

            d_move_y = 95
            # Get the size of the name of the move.
            f_move_size = 24
            f_move = ImageFont.truetype(Dex.FONT_FILE, f_move_size)
            move_font_text_size = f_move.getsize(m.name)

            # The maximum width of the move text is the card minus the width of the damage text (if any).
            max_move_width = img_box_shape_d
            if m.damage > 0:
                max_move_width -= 32

            # Reset it to fit.
            while move_font_text_size[0] > max_move_width:
                f_move_size -= 2
                f_move = ImageFont.truetype(Dex.FONT_FILE, f_move_size)
                move_font_text_size = f_move.getsize(m.name)

            # Print the move.
            draw.text((move_text_x, move_text_y), m.name, black, font=f_move)
            lines = textwrap.wrap(m.special, width=24)
            line_y = d_move_y
            for line in lines:
                line_size = f_move_special.getsize(line)
                line_y += line_size[1] + 8
            # If there's too much special text, don't print it!
            if move_text_y + move_font_text_size[1] + 12 >= 930:
                m.special = ""
                m.damage = 1

            if m.damage > 0:
                damage_text = f"{m.damage}"
                damage_size = f_move_damage.getsize(damage_text)
                # Add the damage.
                damage_text_x = img_box_shape_x + img_box_shape_d - damage_size[0]
                draw.text((damage_text_x, move_text_y), damage_text, black, font=f_move_damage)
                move_text_y += damage_size[1] + 12
            else:
                move_text_y += move_font_text_size[1] + 12
            # Add the special text.
            for line in lines:
                draw.text((move_text_x, move_text_y), line, black, font=f_move_special)
                line_size = f_move_special.getsize(line)
                move_special_y = line_size[1] + 8
                d_move_y += move_special_y
                move_text_y += move_special_y

            if m.special == "":
                move_text_y += 8
            else:
                move_text_y -= 16

            # Move the y position down.
            move_y += d_move_y

            if m.special != "":
                move_y -= 8

            # Draw a line between the moves.
            last_line = [(img_box_shape_x, move_y), (img_box_shape_x + img_box_shape_d, move_y)]
            if i == 0:
                draw.line(last_line, fill=black, width=2)

            move_y += 12
        # Add the strength.
        f_strength = ImageFont.truetype(Dex.FONT_FILE, 22)
        strength_text = f"x2 vs. {monster.strong_against.title()}"
        strength = Image.new('RGBA', f_strength.getsize(strength_text))
        strength_color = list(Dex.DARK_COLORS[self.color_indices[monster.strong_against]])
        strength_color.append(255)
        draw_txt = ImageDraw.Draw(strength)
        draw_txt.text((0, 0), strength_text, font=f_strength, fill=tuple(strength_color))
        strength = strength.rotate(-90, expand=1)
        strength_text_x = card.size[0] - pad_x - 16
        strength_text_y = move_y_0
        # Draw a black box.
        strength_box_x = strength_text_x - 16
        strength_box_y = strength_text_y - 16
        strength_box_size = (strength_box_x + pad_x, strength_box_y + strength.size[1] + 24)
        draw.rectangle([(strength_box_x, strength_box_y), strength_box_size], fill=black)
        card.paste(strength, (strength_text_x, strength_text_y), mask=strength)

        # If the strength box goes really far down, then the rows of description text need to be shorter.
        if strength_box_size[1] > 920:
            desc_width = 30
        else:
            desc_width = 32
        # Add the description.
        desc_text_x = move_x
        f_desc = ImageFont.truetype(Dex.FONT_FILE, 18)
        desc = f'“{monster.description}”'
        desc_lines = textwrap.wrap(desc, width=desc_width)
        desc_height = 0
        desc_heights = []
        for line in desc_lines:
            line_size = f_desc.getsize(line)
            height = int(line_size[1] * 1.1)
            desc_height += height
            desc_heights.append(height)
        desc_text_y = card.size[1] - 52 - desc_height

        # Add a line if it's not too low.
        if desc_text_y - 8 > last_line[0][1]:
            # Draw a line.
            draw.line(last_line, fill=black, width=2)

        for line, height in zip(desc_lines, desc_heights):
            draw.text((desc_text_x, desc_text_y), line, black, font=f_desc)
            desc_text_y += height

        return card

    @staticmethod
    def add_to_bad_urls(url: str) -> None:
        """
        Remember that this a bad URL.

        :param url: The bad URL.
        """

        Dex.BAD_IMAGE_URLS.append(url)
        with io.open(str(Dex.BAD_IMAGE_URLS_PATH.resolve()), "at", encoding="utf-8") as f:
            f.write(url + "\n")

    @staticmethod
    def add_to_bad_wnids(wnid: str) -> None:
        """
        Remember that this a bad wnid.

        :param wnid: The wnid URL.
        """

        Dex.BAD_WNIDS.append(wnid)
        with io.open(str(Dex.BAD_WNIDS_PATH.resolve()), "at", encoding="utf-8") as f:
            f.write(wnid + "\n")

    @staticmethod
    def lighten(color, percent) -> tuple:
        """
        Lighten a color.

        Source: https://stackoverflow.com/questions/28015400/how-to-fade-color

        :param color: The color as an array-like.
        :param percent: Percent by which to lighten.

        :return: The lightened color as a tuple.
        """

        color = np.array(color)
        white = np.array([255, 255, 255, 255])
        vector = white - color
        arr = color + vector * percent
        return tuple([int(a) for a in arr])

    @staticmethod
    def get_image_from_url(url: str) -> Optional[PngImageFile]:
        """
        Get an image from a URL. The URL might be bad so this function will test it to make sure it's a valid image.

        :param url: The image URL.

        :return: If this is a valid image URL, the image. Otherwise, this returns None.
        """

        # Fix Wikimedia links.
        url = url.replace("http://upload.wikimedia.org/", "https://upload.wikimedia.org/")
        # Get the headers to quickly determine if this is an ok URL.
        try:
            # Set a short timeout because if it takes too long, we don't want the image anyway.
            image_header_resp = head(url, timeout=2)
            # Ignore if this is a text website.
            # Flickr's HEAD headers don't match its GET headers so we'll have to test them again.
            flickr = re.search(r"(.*)static\.flickr\.com", url)
            if flickr is None and ("Content-Type" not in image_header_resp.headers or
                                   "image" not in image_header_resp.headers["Content-Type"]):
                return None
        # If we can't connect, assume that the image doesn't exist.
        except ConnectionError:
            return None
        # If it takes too long to get the image, assume that it doesn't exist.
        except ReadTimeout:
            return None

        # Try to get the image.
        try:
            image_resp = get(url, timeout=10)
            # Check the header to see if this is an image before trying to load it with PIL.
            if "Content-Type" not in image_resp.headers or \
                    "image" not in image_resp.headers["Content-Type"]:
                return None
            else:
                # Try to load the image.
                try:
                    img = Image.open(io.BytesIO(image_resp.content))
                    return img
                except UnidentifiedImageError:
                    return None
        except ConnectionError:
            return None
        except MissingSchema:
            return None
        except TooManyRedirects:
            return None
        except ChunkedEncodingError:
            return None
        except ReadTimeout:
            return None

    @staticmethod
    def get_wnid_urls(wnid: str) -> List[str]:
        """
        Try to get image URLs from a wnid.

        :param wnid: The wnid.

        :return: A list of image URLs in the wnid. Can be empty.
        """
        if wnid.startswith("-"):
            wnid = wnid[1:]
        if wnid in Dex.BAD_WNIDS:
            return []
        got_resp = False
        resp = None
        num_attempts = 0
        while not got_resp and num_attempts < 10:
            # Try to get the data. We know all of these URLs are valid.
            try:
                resp = get(f"http://www.image-net.org/api/text/imagenet.synset.geturls.getmapping?wnid={wnid}")
                got_resp = True
            except ConnectionError:
                num_attempts += 1
                continue
        # If this wnid is totally bogus, remember not to try it again.
        if not got_resp or "Invalid" in resp.content.decode("utf-8"):
            Dex.add_to_bad_wnids(wnid)
            return []
        # Get all of the image URLs.
        urls = resp.content.decode("utf-8").split("\r\n")
        urls = [url.split(" ")[1].strip() for url in urls if len(url.strip()) > 0 and
                url.split(" ")[1].strip() not in Dex.BAD_IMAGE_URLS]
        # If there are no URLs, this is a bad wnid.
        if len(urls) == 0:
            Dex.add_to_bad_wnids(wnid)
        # Sometimes there's just whole wnids of bad URLs. We don't need to test them all. We've got places to be!
        shuffle(urls)
        return urls

    @staticmethod
    def get_supported_string(string: str) -> str:
        """
        :param string: A string that might have characters that the card font doesn't support.

        :return: A converted string in which all characters are supported by the card font.
        """

        return "".join([(c if c in Dex.SUPPORTED_CHARACTERS else unidecode(c)) for c in string])

    @staticmethod
    def get_all_types() -> List[MonsterType]:
        """
        :return: A list of all available `MonsterTypes`.
        """

        all_types: List[MonsterType] = list()
        for f in TYPES_DIRECTORY.iterdir():
            if f.is_file() and f.suffix == ".json":
                td = loads(f.read_text(encoding="utf-8"))
                all_types.append(MonsterType(**td))
        return all_types
