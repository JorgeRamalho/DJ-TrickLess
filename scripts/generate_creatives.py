"""Gera criativos, texturas e recortes a partir das fotos reais do TrickLess."""
from __future__ import annotations

import math
import os
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
IG = ROOT / "assets" / "instagram"
OUT = ROOT / "assets" / "creatives"
BRAND = ROOT / "assets" / "brand"
LP = ROOT / "assets" / "lp"
PHOTOS = ROOT / "assets" / "photos"

for folder in (OUT, BRAND, LP, PHOTOS):
    folder.mkdir(parents=True, exist_ok=True)

VOID = (7, 5, 6)
EMBER = (195, 18, 47)
GOLD = (230, 195, 74)
BONE = (244, 239, 230)
INK = (18, 9, 11)


def load_crop(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGB")
    width, height = image.size
    pixels = image.load()
    left, top, right, bottom = 0, 0, width, height
    threshold = 18

    def row_dark(y: int) -> bool:
        sample = [pixels[x, y] for x in range(0, width, max(1, width // 40))]
        return sum(sum(px) / 3 for px in sample) / len(sample) < threshold

    def col_dark(x: int) -> bool:
        sample = [pixels[x, y] for y in range(0, height, max(1, height // 40))]
        return sum(sum(px) / 3 for px in sample) / len(sample) < threshold

    while top < height - 8 and row_dark(top):
        top += 1
    while bottom > top + 8 and row_dark(bottom - 1):
        bottom -= 1
    while left < width - 8 and col_dark(left):
        left += 1
    while right > left + 8 and col_dark(right - 1):
        right -= 1
    pad = 4
    return image.crop((
        max(0, left - pad),
        max(0, top - pad),
        min(width, right + pad),
        min(height, bottom + pad),
    ))


def noise(size: tuple[int, int], amount: int = 28, seed: int = 11) -> Image.Image:
    rng = random.Random(seed)
    tiny = Image.new("L", (max(8, size[0] // 6), max(8, size[1] // 6)))
    pix = tiny.load()
    width, height = tiny.size
    for y in range(height):
        for x in range(width):
            pix[x, y] = rng.randint(0, amount)
    return tiny.resize(size, Image.Resampling.BILINEAR)


def vignette(size: tuple[int, int], strength: float = 0.72) -> Image.Image:
    layer = Image.new("L", size, 0)
    draw = ImageDraw.Draw(layer)
    width, height = size
    draw.ellipse((-width * 0.15, -height * 0.2, width * 1.15, height * 1.2), fill=255)
    layer = layer.filter(ImageFilter.GaussianBlur(max(width, height) * 0.12))
    return ImageEnhance.Brightness(layer).enhance(1.15 - strength)


def duotone(image: Image.Image, shadow: tuple[int, int, int], highlight: tuple[int, int, int]) -> Image.Image:
    gray = ImageOps.grayscale(image)
    color = ImageOps.colorize(gray, black=shadow, white=highlight)
    return Image.blend(image.convert("RGB"), color, 0.55)


def light_leaks(size: tuple[int, int]) -> Image.Image:
    layer = Image.new("RGB", size, VOID)
    draw = ImageDraw.Draw(layer, "RGBA")
    width, height = size
    draw.polygon(
        [(width * 0.55, -40), (width * 0.78, -40), (width * 0.42, height + 40), (width * 0.18, height + 40)],
        fill=(230, 195, 74, 42),
    )
    draw.ellipse((width * 0.62, -height * 0.2, width * 1.2, height * 0.45), fill=(195, 18, 47, 70))
    draw.ellipse((-width * 0.2, height * 0.45, width * 0.4, height * 1.2), fill=(255, 77, 109, 38))
    return layer.filter(ImageFilter.GaussianBlur(42))


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS, centering=(0.52, 0.42))


def save(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, quality=92, optimize=True)


def try_font(size: int, bold: bool = True) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/cinzel-bold.ttf",
        "C:/Windows/Fonts/Cinzel-Bold.ttf",
        "C:/Windows/Fonts/georgia.ttf",
        "C:/Windows/Fonts/times.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def draw_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, color: tuple[int, int, int], drip: bool = True) -> None:
    points = []
    for i in range(10):
        angle = math.radians(-90 + i * 36)
        r = radius if i % 2 == 0 else radius * 0.38
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, fill=color)
    if drip:
        draw.polygon(
            [(cx + radius * 0.08, cy + radius * 0.55), (cx + radius * 0.22, cy + radius * 0.55), (cx + radius * 0.15, cy + radius * 1.05)],
            fill=color,
        )


def draw_cross(draw: ImageDraw.ImageDraw, cx: int, cy: int, arm: int, color: tuple[int, int, int], thickness: int) -> None:
    draw.rectangle((cx - thickness // 2, cy - arm, cx + thickness // 2, cy + arm), fill=color)
    draw.rectangle((cx - arm, cy - thickness // 2, cx + arm, cy + thickness // 2), fill=color)


def make_cover() -> None:
    size = (1400, 1400)
    cover = Image.new("RGB", size, VOID)
    draw = ImageDraw.Draw(cover)
    for i in range(18):
        shade = 8 + i * 3
        draw.ellipse((80 - i * 18, 40 - i * 12, 980 - i * 10, 920 - i * 8), outline=(shade, 6, 8))
    grain = Image.merge("RGB", [noise(size, 46, 3)] * 3)
    cover = ImageChops.add(cover, grain, scale=3.2, offset=0)
    draw = ImageDraw.Draw(cover)
    draw_star(draw, 1180, 210, 92, GOLD)
    draw_cross(draw, 1180, 210, 18, EMBER, 8)
    font_big = try_font(210)
    font_mid = try_font(78)
    font_small = try_font(28)
    draw.text((96, 430), "ALTA", font=font_big, fill=BONE)
    draw.text((104, 660), "TRICKLESS", font=font_mid, fill=GOLD)
    draw.text((108, 1180), "NOVA FASE  ·  CURITIBA  ·  2026", font=font_small, fill=(185, 168, 164))
    draw.rectangle((96, 760, 420, 768), fill=EMBER)
    cover = ImageEnhance.Contrast(cover).enhance(1.08)
    save(cover, LP / "capa-alta.jpg")
    save(cover.resize((1080, 1080), Image.Resampling.LANCZOS), OUT / "capa-alta-ig.jpg")


def treat(image: Image.Image) -> Image.Image:
    treated = ImageEnhance.Brightness(image).enhance(1.18)
    treated = ImageEnhance.Color(treated).enhance(1.22)
    treated = ImageEnhance.Contrast(treated).enhance(1.16)
    treated = ImageEnhance.Sharpness(treated).enhance(1.25)
    leaks = light_leaks(treated.size).resize(treated.size)
    treated = Image.blend(treated, leaks, 0.12)
    grain = Image.merge("RGB", [noise(treated.size, 18, 7)] * 3)
    treated = ImageChops.add(treated, grain, scale=5.2, offset=0)
    mask = vignette(treated.size, 0.28)
    dark = Image.new("RGB", treated.size, VOID)
    return Image.composite(treated, dark, mask)


def main() -> None:
    pista = load_crop(IG / "circuito-2.jpg")
    save(pista, PHOTOS / "pista-circuito.jpg")
    save(fit(pista, (1920, 1080)), OUT / "hero-raw.jpg")
    hero = treat(fit(pista, (1920, 1080)))
    save(hero, OUT / "hero-cabine.jpg")
    save(fit(hero, (1200, 630)), OUT / "og-cover.jpg")
    save(fit(pista, (1080, 1350)), OUT / "retrato-pista.jpg")
    story = treat(fit(pista, (1080, 1920)))
    draw = ImageDraw.Draw(story)
    draw.rectangle((0, 0, 1080, 220), fill=(7, 5, 6, 0))
    font = try_font(72)
    draw.text((70, 1640), "TRICK", font=font, fill=BONE)
    draw.text((70, 1728), "LESS", font=font, fill=BONE)
    draw_cross(draw, 980, 1780, 34, EMBER, 14)
    save(story, OUT / "story-alta.jpg")

    nova = load_crop(IG / "nova-fase.jpg")
    save(nova, PHOTOS / "nova-fase-art.jpg")
    save(fit(nova, (1080, 1080)), OUT / "feed-nova-fase.jpg")

    duo = duotone(fit(pista, (1600, 1000)), (24, 6, 10), (244, 214, 150))
    save(treat(duo), OUT / "editorial-ouro.jpg")

    club = Image.new("RGB", (1600, 900), VOID)
    crowd = fit(pista, (1600, 900))
    crowd = ImageEnhance.Brightness(crowd).enhance(0.55)
    club = Image.blend(club, crowd, 0.9)
    club = treat(club)
    save(club, OUT / "club-crowd.jpg")

    make_cover()

    mark = Image.new("RGBA", (512, 512), (7, 5, 6, 255))
    draw = ImageDraw.Draw(mark)
    draw.rounded_rectangle((18, 18, 494, 494), radius=48, fill=INK)
    draw_star(draw, 256, 250, 148, GOLD)
    draw_cross(draw, 256, 250, 34, EMBER, 16)
    save(mark.convert("RGB"), BRAND / "logo-mark.png")
    fav = mark.resize((64, 64), Image.Resampling.LANCZOS).convert("RGB")
    save(fav, BRAND / "favicon-64.png")
    mark.save(BRAND / "apple-touch.png")

    banner = Image.new("RGB", (1500, 500), VOID)
    left = fit(pista, (780, 500))
    banner.paste(treat(left), (0, 0))
    draw = ImageDraw.Draw(banner)
    draw.rectangle((760, 0, 1500, 500), fill=VOID)
    font = try_font(64)
    draw.text((820, 150), "TRICKLESS", font=font, fill=BONE)
    draw.text((822, 230), "SERIES EDIT", font=try_font(32), fill=GOLD)
    draw.text((822, 300), "Tech House  ·  Bass House  ·  CWB", font=try_font(22), fill=(185, 168, 164))
    draw_star(draw, 1400, 90, 38, GOLD, drip=False)
    save(banner, OUT / "banner-soundcloud.jpg")
    save(fit(banner, (1500, 1500)), OUT / "spotify-pack.jpg")

    print("creatives ready")


if __name__ == "__main__":
    main()
