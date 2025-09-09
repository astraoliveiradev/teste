from typing import Iterable, List, Tuple
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from .image_utils import ensure_rgba, resize_to_square, parse_color


def circular_crop(image: Image.Image) -> Image.Image:
    image = ensure_rgba(image)
    width, height = image.size
    size = min(width, height)
    image = image.crop(((width - size) // 2, (height - size) // 2, (width + size) // 2, (height + size) // 2))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)
    output = Image.new("RGBA", (size, size))
    output.paste(image, (0, 0))
    output.putalpha(mask)
    return output


def apply_ring(image: Image.Image, color_value: str = "#5865F2", thickness_ratio: float = 0.08) -> Image.Image:
    avatar = circular_crop(image)
    width, _ = avatar.size
    ring_layer = Image.new("RGBA", avatar.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(ring_layer)
    thickness = max(2, int(width * thickness_ratio))
    margin = thickness // 2
    rgb = parse_color(color_value)
    draw.ellipse((margin, margin, width - 1 - margin, width - 1 - margin), outline=(*rgb, 255), width=thickness)
    return Image.alpha_composite(avatar, ring_layer)


def _create_ring_mask(size: int, thickness: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size - 1, size - 1), fill=255)
    inner = thickness
    draw.ellipse((inner, inner, size - 1 - inner, size - 1 - inner), fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(1))
    return mask


def apply_gradient_ring(image: Image.Image, colors: Iterable[str] = ("#5865F2", "#00d4ff"), thickness_ratio: float = 0.1) -> Image.Image:
    avatar = circular_crop(image)
    size, _ = avatar.size
    thickness = max(3, int(size * thickness_ratio))

    # Create linear gradient layer (left->right) and mask it by ring
    gradient = Image.new("RGBA", (size, size))
    left_rgb = parse_color(next(iter(colors), "#5865F2"))
    right_rgb = parse_color(list(colors)[-1] if hasattr(colors, "__len__") and len(list(colors)) > 0 else "#00d4ff")

    for x in range(size):
        t = x / max(1, size - 1)
        r = int(left_rgb[0] * (1 - t) + right_rgb[0] * t)
        g = int(left_rgb[1] * (1 - t) + right_rgb[1] * t)
        b = int(left_rgb[2] * (1 - t) + right_rgb[2] * t)
        ImageDraw.Draw(gradient).line([(x, 0), (x, size)], fill=(r, g, b, 255))

    mask = _create_ring_mask(size, thickness)
    ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ring.paste(gradient, (0, 0), mask)
    return Image.alpha_composite(avatar, ring)


def apply_glow(image: Image.Image, color_value: str = "#5865F2", radius: int = 18) -> Image.Image:
    avatar = circular_crop(image)
    size, _ = avatar.size

    rgb = parse_color(color_value)
    # Create silhouette from alpha
    alpha = avatar.split()[-1]
    glow = Image.new("RGBA", (size, size), (*rgb, 0))
    glow.putalpha(alpha)
    glow = glow.filter(ImageFilter.GaussianBlur(radius))

    # Composite glow below avatar
    base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    base = Image.alpha_composite(base, glow)
    base = Image.alpha_composite(base, avatar)
    return base


def add_sticker(image: Image.Image, sticker: str = "estrela") -> Image.Image:
    avatar = circular_crop(image)
    size, _ = avatar.size
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    if sticker.lower() in ("estrela", "star"):
        # Simple 5-point star
        cx, cy = int(size * 0.78), int(size * 0.78)
        outer = int(size * 0.16)
        inner = int(outer * 0.5)
        points: List[Tuple[int, int]] = []
        import math
        for i in range(10):
            angle = i * math.pi / 5.0
            r = outer if i % 2 == 0 else inner
            x = cx + int(r * math.sin(angle))
            y = cy - int(r * math.cos(angle))
            points.append((x, y))
        draw.polygon(points, fill=(255, 223, 0, 230))
        draw.line(points + [points[0]], fill=(255, 180, 0, 255), width=2)
    else:
        # Heart
        cx, cy = int(size * 0.8), int(size * 0.78)
        r = int(size * 0.1)
        heart = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        hdraw = ImageDraw.Draw(heart)
        # Two circles and a triangle-ish bottom
        hdraw.ellipse((cx - r, cy - r - 5, cx, cy - 5 + r), fill=(255, 64, 129, 230))
        hdraw.ellipse((cx, cy - r - 5, cx + r, cy - 5 + r), fill=(255, 64, 129, 230))
        hdraw.polygon([(cx - r, cy), (cx + r, cy), (cx, cy + int(1.5 * r))], fill=(255, 64, 129, 230))
        layer = Image.alpha_composite(layer, heart)

    return Image.alpha_composite(avatar, layer)


def compose_profile_preview(image: Image.Image, display_name: str = "Display Name", bio_lines: Iterable[str] = None) -> Image.Image:
    if bio_lines is None:
        bio_lines = [
            "Look at me I'm a beautiful butterfly",
            "Fluttering in the moonlight ",
            "Waiting for the day when",
            "I get an avatar decoration",
        ]

    avatar = circular_crop(resize_to_square(image, 192))
    card_w, card_h = 600, 240
    bg = Image.new("RGBA", (card_w, card_h), (49, 51, 56, 255))  # Discord-like dark

    # Sidebar accent
    accent = Image.new("RGBA", (8, card_h), (88, 101, 242, 255))
    bg.paste(accent, (0, 0))

    # Paste avatar
    bg.paste(avatar, (24, (card_h - avatar.size[1]) // 2), avatar)

    # Text
    draw = ImageDraw.Draw(bg)
    font_title = ImageFont.load_default()
    font_text = ImageFont.load_default()

    # Display name
    draw.text((240, 28), display_name, font=font_title, fill=(255, 255, 255, 255))

    # Bio lines
    y = 60
    for line in bio_lines:
        draw.text((240, y), line, font=font_text, fill=(220, 221, 222, 255))
        y += 22

    return bg
