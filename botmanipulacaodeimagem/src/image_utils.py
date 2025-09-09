import io
import re
from typing import Iterable, Tuple
from PIL import Image


ColorRGB = Tuple[int, int, int]


_NAMED_COLORS = {
    "red": (255, 0, 0),
    "green": (0, 200, 0),
    "blue": (0, 112, 244),
    "yellow": (255, 204, 0),
    "purple": (163, 73, 164),
    "magenta": (255, 0, 255),
    "cyan": (0, 255, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "orange": (255, 140, 0),
    "pink": (255, 105, 180),
    "teal": (0, 128, 128),
    "lime": (50, 205, 50),
}


def parse_color(color_value: str, default: ColorRGB = (114, 137, 218)) -> ColorRGB:
    """Parse a color string into an RGB tuple.

    Accepts formats:
    - Hex: #RRGGBB or RRGGBB
    - Named: 'blue', 'red', etc.
    """
    if not color_value:
        return default
    value = color_value.strip().lower()

    # Named color
    if value in _NAMED_COLORS:
        return _NAMED_COLORS[value]

    # Hex color
    m = re.fullmatch(r"#?([0-9a-f]{6})", value)
    if m:
        hex_value = m.group(1)
        r = int(hex_value[0:2], 16)
        g = int(hex_value[2:4], 16)
        b = int(hex_value[4:6], 16)
        return (r, g, b)

    return default


def read_image_from_bytes(data: bytes) -> Image.Image:
    buffer = io.BytesIO(data)
    image = Image.open(buffer)
    # Ensure loaded fully before buffer is GC'd
    image.load()
    return image


def save_image_to_bytes(image: Image.Image, format: str = "PNG") -> io.BytesIO:
    output = io.BytesIO()
    image.save(output, format=format)
    output.seek(0)
    return output


def ensure_rgba(image: Image.Image) -> Image.Image:
    return image.convert("RGBA")


def resize_to_square(image: Image.Image, size: int) -> Image.Image:
    return ensure_rgba(image).resize((size, size), Image.LANCZOS)
