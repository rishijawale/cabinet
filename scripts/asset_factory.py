"""Procedural, original seed artwork for Cabinet.

Everything produced here is authored for this project and released as CC0, so
the archive can be seeded honestly without scraping other people's work.
"""

from __future__ import annotations

import io
import os
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = 60_000_000

MEDIA_ROOT = Path(__file__).resolve().parents[1] / "backend" / "media"


@dataclass
class GeneratedArtwork:
    slug: str
    title: str
    description: str
    category: str
    media_type: str
    file_format: str
    width: int
    height: int
    orientation: str
    tags: list[str] = field(default_factory=list)
    original: bytes | None = None
    original_ext: str = "png"
    previews: dict[str, bytes] = field(default_factory=dict)
    external_only: bool = False
    style: str = ""


# ---------------------------------------------------------------------------
# Shared helpers


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in normalized.lower())
    return "-".join(part for part in cleaned.split("-") if part)


def _webp(image: Image.Image, *, quality: int = 82) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="WEBP", quality=quality, method=6)
    return buffer.getvalue()


def _scaled(image: Image.Image, max_dim: int, *, nearest: bool = False) -> Image.Image:
    largest = max(image.size)
    if largest <= max_dim:
        return image.copy()
    ratio = max_dim / largest
    size = (max(1, round(image.width * ratio)), max(1, round(image.height * ratio)))
    return image.resize(size, Image.Resampling.NEAREST if nearest else Image.Resampling.LANCZOS)


def make_previews(
    image: Image.Image,
    *,
    full_dim: int = 1600,
    nearest: bool = False,
) -> dict[str, bytes]:
    return {
        "thumb": _webp(_scaled(image, 320, nearest=nearest), quality=78),
        "card": _webp(_scaled(image, 800, nearest=nearest), quality=82),
        "full": _webp(_scaled(image, full_dim, nearest=nearest), quality=86),
    }


def _font_candidates() -> list[str]:
    return [
        os.environ.get("CABINET_ASCII_FONT", ""),
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\CascadiaMono.ttf",
        r"C:\Windows\Fonts\lucon.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
    ]


def load_mono_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in _font_candidates():
        if candidate and Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# ASCII


ASCII_RAMPS = [
    " .:-=+*#%@",
    " .'`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    " .oO@",
    " .,:;irsXA253hMHGS#9B&@",
    " \u00b7\u2591\u2592\u2593\u2588",
    "  123456789ABCDEF",
]

ASCII_STYLES = [
    "ripple",
    "diagonal",
    "plasma",
    "tunnel",
    "lattice",
    "spiral",
    "escape",
    "orbit",
    "bars",
    "vignette",
]

ASCII_TITLES = [
    "Quiet Observer",
    "Terminal Bloom",
    "Signal Garden",
    "Null Cathedral",
    "Soft Static",
    "Cold Index",
    "Slow Transmission",
    "Paper Machine",
    "Distant Chorus",
    "Analog Prayer",
    "Hollow Lattice",
    "Northern Circuit",
    "Silent Teletype",
    "Electric Orchard",
    "Faded Monolith",
    "Low Window",
    "Pale Ghost",
    "Vacant Room",
    "Amber Tape",
    "Drift Terminal",
    "Glass Field",
    "Monochrome Ghost",
    "Infinite Index",
    "Small Machine",
    "Warm Static",
    "Lunar Observer",
    "Signal Room",
    "After Image",
    "Static Bloom",
    "Sparse Cathedral",
    "Gentle Circuit",
    "Quiet Transmission",
    "Northern Window",
    "Terminal Field",
    "Analog Ghost",
    "Hollow Tape",
    "Distant Machine",
    "Pale Signal",
    "Slow Monolith",
    "Soft Index",
]


def _ascii_field(style: str, rows: int, cols: int, rng: np.random.Generator) -> np.ndarray:
    y, x = np.mgrid[0:rows, 0:cols]
    xn = x / max(cols - 1, 1)
    yn = y / max(rows - 1, 1)
    cx, cy = xn - 0.5, yn - 0.5
    radius = np.sqrt(cx**2 + cy**2)
    angle = np.arctan2(cy, cx)

    if style == "ripple":
        field = np.sin(radius * 34 - 1.2) * 0.5 + 0.5
        field *= np.clip(1.25 - radius, 0, 1) ** 0.5
    elif style == "diagonal":
        field = np.sin((xn * 2.2 + yn * 1.4) * 12) * 0.5 + 0.5
        field = field * 0.7 + yn * 0.3
    elif style == "plasma":
        field = (
            np.sin(xn * 8 + 0.4)
            + np.sin(yn * 7 - 1.1)
            + np.sin((xn + yn) * 6)
            + np.sin(np.sqrt((xn - 0.3) ** 2 + (yn - 0.6) ** 2) * 18)
        ) / 4
        field = field * 0.5 + 0.5
    elif style == "tunnel":
        field = np.sin(8 / (radius + 0.08)) * np.sin(angle * 5 + radius * 4)
        field = field * 0.5 + 0.5
    elif style == "lattice":
        field = (np.sin(xn * 28) * np.sin(yn * 20)) * 0.5 + 0.5
        field *= np.clip(1.4 - radius * 1.6, 0, 1)
    elif style == "spiral":
        field = np.sin(angle * 6 + radius * 28) * 0.5 + 0.5
        field *= np.clip(1.15 - radius, 0, 1)
    elif style == "escape":
        c = complex(-0.62, 0.42)
        z = (xn - 0.32) * 2.8 + 1j * (yn - 0.5) * 2.4
        counts = np.zeros(z.shape)
        with np.errstate(over="ignore", invalid="ignore"):
            for _ in range(28):
                z = z * z + c
                counts += np.abs(z) < 2
        field = counts / 28
    elif style == "orbit":
        field = np.sin(radius * 20 + angle * 3) * 0.5 + 0.5
        field = field * np.clip(1.2 - radius, 0, 1)
        field += 0.12 * np.sin(xn * 40)
    elif style == "bars":
        field = np.floor((yn * 9 + 0.12 * np.sin(xn * 7)) % 1 * 9) / 9
        field = field * 0.8 + 0.1 * np.sin(xn * 22)
    else:  # vignette
        noise = rng.random((rows, cols))
        smooth = noise
        for _ in range(3):
            smooth = (
                np.roll(smooth, 1, 0)
                + np.roll(smooth, -1, 0)
                + np.roll(smooth, 1, 1)
                + np.roll(smooth, -1, 1)
                + smooth
            ) / 5
        field = smooth * np.clip(1.3 - radius * 1.5, 0, 1)

    field = np.nan_to_num(field, nan=0.0, posinf=1.0, neginf=0.0)
    low, high = float(field.min()), float(field.max())
    if high - low < 1e-6:
        return np.zeros_like(field)
    return (field - low) / (high - low)


def _render_ascii(text: str, *, accent: tuple[int, int, int]) -> Image.Image:
    font = load_mono_font(18)
    probe = Image.new("RGB", (8, 8))
    draw = ImageDraw.Draw(probe)
    char_width = max(draw.textlength("M", font=font), 8)
    bbox = font.getbbox("M") if hasattr(font, "getbbox") else (0, 0, 8, 14)
    line_height = max((bbox[3] - bbox[1]) + 4, 16)

    lines = text.splitlines() or [""]
    cols = max(len(line) for line in lines)
    rows = len(lines)
    padding = 34
    width = int(cols * char_width + padding * 2)
    height = int(rows * line_height + padding * 2)

    image = Image.new("RGB", (width, height), (17, 17, 15))
    draw = ImageDraw.Draw(image)
    # A faint paper-like grain keeps the preview from looking like a screenshot.
    rng = np.random.default_rng(len(text))
    grain = rng.integers(0, 7, size=(height, width, 1), dtype=np.uint8)
    base = np.asarray(image).astype(np.uint8)
    image = Image.fromarray(np.clip(base + grain, 0, 255).astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(image)

    draw.rectangle((padding - 12, padding - 12, padding - 4, padding - 4), fill=accent)
    draw.multiline_text(
        (padding, padding),
        text,
        font=font,
        fill=(236, 233, 224),
        spacing=4,
    )
    return image


def make_ascii(index: int, title: str) -> GeneratedArtwork:
    style = ASCII_STYLES[index % len(ASCII_STYLES)]
    ramp = ASCII_RAMPS[index % len(ASCII_RAMPS)]
    rows = 48 if index % 3 else 40
    cols = 96 if index % 2 == 0 else 84
    rng = np.random.default_rng(20261117 + index)
    field = _ascii_field(style, rows, cols, rng)

    if style in {"lattice", "bars", "escape"}:
        field = field**0.75
    if index % 4 == 3:
        field = 1 - field

    indices = np.clip((field * (len(ramp) - 1)).round().astype(int), 0, len(ramp) - 1)
    lines = ["".join(ramp[value] for value in row).rstrip() for row in indices]
    text = "\n".join(lines) + "\n"

    accents = [(182, 93, 66), (177, 168, 148), (126, 139, 122), (196, 168, 109)]
    preview = _render_ascii(text, accent=accents[index % len(accents)])
    previews = make_previews(preview, full_dim=1600)
    original = text.encode("utf-8")

    return GeneratedArtwork(
        slug=slugify(title),
        title=title,
        description="",
        category="ascii",
        media_type="text",
        file_format="txt",
        width=cols,
        height=rows,
        orientation="landscape",
        tags=["ascii", "text", "generative", style],
        original=original,
        original_ext="txt",
        previews=previews,
        style=style,
    )


# ---------------------------------------------------------------------------
# Pixel art

PIXEL_PALETTES = [
    ["#12100e", "#f4ead5", "#c8553d", "#588b8b", "#f28f3b"],
    ["#0f0f12", "#e8e6e1", "#8f2d56", "#218380", "#d3b88c"],
    ["#1a1423", "#ede7d9", "#a15c6a", "#5c8001", "#f4d35e"],
    ["#0b132b", "#f0f3f5", "#5bc0be", "#3a506b", "#ffa69e"],
    ["#221d23", "#f5f1e3", "#d17b49", "#5c946e", "#d7cdb5"],
    ["#171614", "#f2efe9", "#7e6b5a", "#b65d42", "#8e9a7a"],
]

PIXEL_TITLES = [
    "Tiny Wanderer",
    "Moss Knight",
    "Low Village",
    "Pocket Planet",
    "Copper Sword",
    "Bitter Potion",
    "Quiet Forest",
    "Small Satellite",
    "Pale Ruin",
    "Night Creature",
    "Paper Tower",
    "Tiny Garden",
    "Amber Beacon",
    "Moss Shrine",
    "Little Island",
    "Soft Robot",
    "Dust Sprite",
    "Old Machine",
    "Warm Signal",
    "Hollow Keep",
    "Blue Wanderer",
    "Low Beacon",
    "Tiny Cathedral",
    "Red Planet",
    "Small Ruin",
    "Quiet Robot",
    "Green Sword",
    "Distant Village",
    "Pale Potion",
    "Slow Satellite",
]

PIXEL_STYLES = ["sprite", "landscape", "icon", "pattern"]


def _hex_color(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def _pixel_sprite(rng: np.random.Generator, palette: np.ndarray) -> np.ndarray:
    size = 32
    grid = np.zeros((size, size), dtype=int)
    # Build a vertically symmetric creature.
    body = rng.random((size, size // 2)) > 0.58
    body = body & (np.arange(size)[:, None] < size * 0.86)
    body[0:4, :] = False
    grid[:, : size // 2][body] = 2
    grid[:, size // 2 :] = np.flip(grid[:, : size // 2], axis=1)

    # Fill interior with a secondary tone for depth.
    interior = rng.random((size, size // 2)) > 0.72
    interior &= body
    grid[:, : size // 2][interior] = 3
    grid[:, size // 2 :] = np.flip(grid[:, : size // 2], axis=1)

    # Eyes.
    eye_y = int(size * rng.uniform(0.28, 0.45))
    grid[eye_y : eye_y + 2, 9:11] = 1
    grid[eye_y : eye_y + 2, size - 11 : size - 9] = 1

    # Ground shadow.
    grid[size - 4 :, 6 : size - 6] = 4 if len(palette) > 4 else 2
    return grid


def _pixel_landscape(rng: np.random.Generator, palette: np.ndarray) -> np.ndarray:
    size = 40
    grid = np.zeros((size, size), dtype=int)
    horizon = int(size * rng.uniform(0.48, 0.62))
    grid[:horizon, :] = 1
    grid[horizon - 3 : horizon, :] = 3

    sun_x = int(size * rng.uniform(0.2, 0.8))
    sun_y = int(horizon * rng.uniform(0.3, 0.6))
    radius = rng.integers(3, 6)
    y, x = np.mgrid[0:size, 0:size]
    sun = (x - sun_x) ** 2 + (y - sun_y) ** 2 <= radius**2
    grid[sun] = 4 if len(palette) > 4 else 2

    peaks = rng.integers(0, 4, size=size // 2)
    for i in range(size):
        peak = int(horizon - 2 - abs(peaks[i % len(peaks)])) + (i % 5)
        grid[max(peak, horizon - 10) : horizon, i] = 2

    grid[horizon:, :] = 2
    grid[horizon + 4 :, :] = 3
    return grid


def _pixel_icon(rng: np.random.Generator, palette: np.ndarray) -> np.ndarray:
    size = 32
    grid = np.zeros((size, size), dtype=int)
    shape = rng.integers(0, 3)

    if shape == 0:  # potion
        grid[8:12, 13:19] = 2
        grid[12:26, 9:23] = 3
        grid[16:24, 11:21] = 4 if len(palette) > 4 else 2
        grid[5:8, 14:18] = 1
    elif shape == 1:  # sword
        grid[6:24, 15:17] = 1
        grid[24:27, 12:20] = 2
        grid[20:22, 10:22] = 3
        grid[4:7, 15:17] = 2
    else:  # crystal
        grid[7:25, 11:21] = 3
        grid[10:22, 13:19] = 4 if len(palette) > 4 else 2
        grid[7:25, 11:13] = 2
        grid[7:9, 11:21] = 1

    grid[size - 4 :, 8 : size - 8] = 2
    return grid


def _pixel_pattern(rng: np.random.Generator, palette: np.ndarray) -> np.ndarray:
    size = 32
    grid = np.zeros((size, size), dtype=int)
    motif = rng.integers(1, min(len(palette), 5))
    for y in range(0, size, 8):
        for x in range(0, size, 8):
            if (x // 8 + y // 8) % 2 == 0:
                grid[y : y + 8, x : x + 8] = motif
            else:
                grid[y + 2 : y + 6, x + 2 : x + 6] = 4 if len(palette) > 4 else 2
    grid[0:2, :] = 1
    grid[:, 0:2] = 1
    return grid


def _grid_to_image(grid: np.ndarray, palette_hex: list[str]) -> Image.Image:
    palette = np.array([_hex_color(color) for color in palette_hex], dtype=np.uint8)
    grid = np.clip(grid, 0, len(palette) - 1)
    rgb = palette[grid]
    return Image.fromarray(rgb, "RGB")


def make_pixel(index: int, title: str) -> GeneratedArtwork:
    style = PIXEL_STYLES[index % len(PIXEL_STYLES)]
    palette_hex = PIXEL_PALETTES[index % len(PIXEL_PALETTES)]
    rng = np.random.default_rng(7717 + index)
    palette = np.array([_hex_color(color) for color in palette_hex], dtype=np.uint8)

    if style == "sprite":
        grid = _pixel_sprite(rng, palette)
    elif style == "landscape":
        grid = _pixel_landscape(rng, palette)
    elif style == "icon":
        grid = _pixel_icon(rng, palette)
    else:
        grid = _pixel_pattern(rng, palette)

    native = _grid_to_image(grid, palette_hex)
    preview = native.resize((1024, 1024), Image.Resampling.NEAREST)
    previews = make_previews(preview, full_dim=1024, nearest=True)

    buffer = io.BytesIO()
    native.save(buffer, format="PNG", optimize=True)

    return GeneratedArtwork(
        slug=slugify(title),
        title=title,
        description="",
        category="pixel-art",
        media_type="image",
        file_format="png",
        width=native.width,
        height=native.height,
        orientation="square",
        tags=["pixel art", "sprite", "retro", "16-bit", style],
        original=buffer.getvalue(),
        original_ext="png",
        previews=previews,
        style=style,
    )


# ---------------------------------------------------------------------------
# Wallpapers

WALLPAPER_PALETTES = [
    ["#0d0d0c", "#1c1c18", "#b65d42"],
    ["#f2ede4", "#d9cfc0", "#8a7968"],
    ["#101820", "#f2aa4c", "#f5f5f5"],
    ["#1b263b", "#415a77", "#e0e1dd"],
    ["#2b2d42", "#8d99ae", "#edf2f4"],
    ["#231f20", "#bb4430", "#f1e3d3"],
    ["#132a13", "#31572c", "#ecf39e"],
    ["#3d348b", "#7678ed", "#f7b801"],
    ["#001219", "#0a9396", "#e9d8a6"],
    ["#1a1a2e", "#16213e", "#e94560"],
    ["#f4f1de", "#e07a5f", "#3d405b"],
    ["#22223b", "#9a8c98", "#f2e9e4"],
]

WALLPAPER_TITLES = [
    "Digital Silence",
    "Quiet Horizon",
    "Meridian",
    "Slow Field",
    "Dusk Interval",
    "Paper Tide",
    "Soft Strata",
    "Low Aperture",
    "Amber Drift",
    "Northern Basin",
    "Pale Gradient",
    "Night Nocturne",
    "Distant Ridge",
    "Small Halo",
    "Warm Expanse",
    "Cold Meridian",
    "Silent Field",
    "Analog Horizon",
    "Low Tide",
    "Monochrome Interval",
    "Glass Basin",
    "Slow Aperture",
    "Faded Strata",
    "Distant Halo",
    "Amber Expanse",
    "Pale Nocturne",
    "Northern Drift",
    "Quiet Gradient",
    "Small Horizon",
    "Warm Meridian",
]

WALLPAPER_STYLES = ["mesh", "rings", "bands", "grain", "strata", "dotfield"]


def _rgb(value: str) -> np.ndarray:
    return np.array(_hex_color(value), dtype=float)


def _smooth_field(rng: np.random.Generator, height: int, width: int, cells: int = 6) -> np.ndarray:
    coarse = rng.random((cells, cells))
    image = Image.fromarray((coarse * 255).astype(np.uint8), "L").resize(
        (width, height), Image.Resampling.BICUBIC
    )
    return np.asarray(image, dtype=float) / 255.0


def _wallpaper_image(
    style: str,
    colors: list[str],
    width: int,
    height: int,
    rng: np.random.Generator,
) -> Image.Image:
    c0, c1, c2 = (_rgb(color) for color in colors[:3])
    y, x = np.mgrid[0:height, 0:width]
    xn = x / width
    yn = y / height

    if style == "mesh":
        image = np.tile(c0, (height, width, 1))
        weight_sum = np.ones((height, width))
        for _ in range(4):
            cx, cy = rng.uniform(0, 1), rng.uniform(0, 1)
            radius = rng.uniform(0.25, 0.75)
            color = [c0, c1, c2][int(rng.integers(0, 3))]
            distance = np.sqrt((xn - cx) ** 2 + (yn - cy) ** 2) / radius
            weight = np.clip(1 - distance, 0, 1) ** 2
            image += color * weight[..., None]
            weight_sum += weight
        image /= weight_sum[..., None]
    elif style == "rings":
        cx, cy = rng.uniform(0.35, 0.65), rng.uniform(0.35, 0.65)
        distance = np.sqrt((xn - cx) ** 2 + ((yn - cy) * height / width) ** 2)
        rings = np.sin(distance * 90 - 0.4) * 0.5 + 0.5
        image = c0 + (c1 - c0) * rings[..., None]
        image += (c2 - c1) * np.clip(0.5 - distance, 0, 0.5)[..., None]
    elif style == "bands":
        field = _smooth_field(rng, height, width, cells=10)
        bands = np.floor((yn * 7 + field * 0.35) % 1 * 4) / 4
        image = c0 + (c1 - c0) * bands[..., None]
        image = image * 0.85 + c2 * 0.15
    elif style == "grain":
        field = _smooth_field(rng, height, width, cells=5)
        image = c0 + (c1 - c0) * field[..., None]
        vignette = np.clip(1.25 - np.sqrt((xn - 0.5) ** 2 + (yn - 0.5) ** 2) * 1.6, 0, 1)
        image *= vignette[..., None]
        image = image * 0.9 + c2 * 0.1
    elif style == "strata":
        wave = np.sin(xn * 9 + 1.2) * 0.045 + np.sin(xn * 23) * 0.012
        bands = np.floor((yn + wave) * 11) / 11
        ramp = np.clip(bands * 1.35, 0, 1)
        image = c0 + (c1 - c0) * ramp[..., None]
        image = image * 0.75 + c2 * 0.25
    else:  # dotfield
        field = _smooth_field(rng, height, width, cells=8)
        image = np.tile(c0, (height, width, 1))
        spacing = max(10, width // 90)
        dots = ((x % spacing) - spacing / 2) ** 2 + ((y % spacing) - spacing / 2) ** 2
        radius = field * (spacing * 0.62)
        mask = dots < radius**2
        image[mask] = c1
        accent = np.clip(field - 0.72, 0, 1)[..., None] * 2.5
        image = image * (1 - accent) + c2 * accent

    grain = rng.normal(0, 2.6, size=(height, width, 1))
    image = np.clip(image + grain, 0, 255)
    return Image.fromarray(image.astype(np.uint8), "RGB")


def make_wallpaper(index: int, title: str) -> GeneratedArtwork:
    style = WALLPAPER_STYLES[index % len(WALLPAPER_STYLES)]
    colors = WALLPAPER_PALETTES[index % len(WALLPAPER_PALETTES)]
    portrait = index % 4 == 1
    rng = np.random.default_rng(4409 + index)

    if portrait:
        native_width, native_height = 1350, 2400
        render_width, render_height = 900, 1600
    else:
        native_width, native_height = 2400, 1350
        render_width, render_height = 1600, 900

    render = _wallpaper_image(style, colors, render_width, render_height, rng)
    native = render.resize((native_width, native_height), Image.Resampling.LANCZOS)
    previews = make_previews(native, full_dim=1600)

    buffer = io.BytesIO()
    native.save(buffer, format="JPEG", quality=90, optimize=True, progressive=True)

    return GeneratedArtwork(
        slug=slugify(title),
        title=title,
        description="",
        category="wallpapers",
        media_type="image",
        file_format="jpg",
        width=native_width,
        height=native_height,
        orientation="portrait" if portrait else "landscape",
        tags=["wallpaper", "abstract", "minimal", style],
        original=buffer.getvalue(),
        original_ext="jpg",
        previews=previews,
        style=style,
    )


# ---------------------------------------------------------------------------
# Descriptions


ASCII_DESCRIPTIONS = [
    "A dense field of glyphs that resolves into a shape only when you step back. Rendered with a fixed-width character ramp and no colour.",
    "An exercise in restraint: the whole image is built from punctuation, letters and whitespace.",
    "Rows of characters arranged until the noise became a horizon. Best viewed at full width.",
    "A small transmission from a machine that only knows how to draw with text.",
    "The kind of image that used to arrive over a slow connection, one line at a time.",
]

PIXEL_DESCRIPTIONS = [
    "A tiny scene drawn on a strict grid and scaled up without smoothing. Every visible detail is a single pixel.",
    "Hand-built from a five-colour palette, then exported at its native resolution so the grid remains intact.",
    "Small enough to fit in a pocket, stubborn enough to keep its edges.",
    "An object study in the language of early game hardware: limited colours, hard edges, careful silhouettes.",
    "A compact composition where each pixel has to justify its place in the palette.",
]

WALLPAPER_DESCRIPTIONS = [
    "A quiet abstract field composed for wide screens. Gradients and grain do the work; nothing competes for attention.",
    "Built from layered colour fields and a light film of noise. Available as an original file for personal use.",
    "An exercise in negative space: the composition is mostly the space between two tones.",
    "A minimal wallpaper study, generated at full desktop resolution and rendered for a calm screen.",
    "Soft colour strata with a fine grain, designed to sit behind windows without becoming a distraction.",
]


def attach_copy(pieces: list[GeneratedArtwork]) -> None:
    counters = {"ascii": 0, "pixel-art": 0, "wallpapers": 0}
    for piece in pieces:
        index = counters[piece.category]
        counters[piece.category] += 1
        if piece.category == "ascii":
            piece.description = ASCII_DESCRIPTIONS[index % len(ASCII_DESCRIPTIONS)]
        elif piece.category == "pixel-art":
            piece.description = PIXEL_DESCRIPTIONS[index % len(PIXEL_DESCRIPTIONS)]
        else:
            piece.description = WALLPAPER_DESCRIPTIONS[index % len(WALLPAPER_DESCRIPTIONS)]


def generate_archive() -> list[GeneratedArtwork]:
    pieces: list[GeneratedArtwork] = []
    for index, title in enumerate(ASCII_TITLES):
        pieces.append(make_ascii(index, title))
    for index, title in enumerate(PIXEL_TITLES):
        pieces.append(make_pixel(index, title))
    for index, title in enumerate(WALLPAPER_TITLES):
        pieces.append(make_wallpaper(index, title))
    attach_copy(pieces)
    return pieces


def write_asset(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
