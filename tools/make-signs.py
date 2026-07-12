"""
Neon sign faces, drawn as transparent PNGs. They get mapped onto planes that sit
exactly where the old letter geometry was, once that geometry is stripped out.

    .venv/bin/python tools/make-signs.py <static/textures/signs>
"""
import sys
import math
import pathlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FUTURA = '/System/Library/Fonts/Supplemental/Futura.ttc'
BOLD = 2

PINK = (255, 62, 165)
PINK_CORE = (255, 214, 240)
WHITE = (255, 255, 255)


def neon(size, text, size_px, core, glow, pad_scale=1.0):
    """Glowing text: a blurred colour halo with a bright core on top."""
    w, h = size
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    font = ImageFont.truetype(FUTURA, size_px, index=BOLD)

    halo = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.text((w / 2, h / 2), text, font=font, fill=glow + (255,), anchor='mm',
            stroke_width=int(10 * pad_scale), stroke_fill=glow + (255,))
    halo = halo.filter(ImageFilter.GaussianBlur(radius=14 * pad_scale))

    img.alpha_composite(halo)

    d = ImageDraw.Draw(img)
    d.text((w / 2, h / 2), text, font=font, fill=core + (255,), anchor='mm',
           stroke_width=int(5 * pad_scale), stroke_fill=glow + (255,))
    return img


CJK = '/System/Library/Fonts/Supplemental/Hiragino Sans GB.ttc'
CYAN = (94, 234, 240)
GREEN = (86, 240, 130)


def glow(img, colour, radius, width):
    """A blurred copy of the strokes, to fake the neon bleed."""
    halo = img.filter(ImageFilter.GaussianBlur(radius=radius))
    return halo


def food_icon(size=(1024, 924)):
    """A neon bamboo steamer with dumplings and steam, in place of the ramen bowl."""
    w, h = size
    strokes = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(strokes)

    lw = 14
    # steam curls
    for i, x in enumerate((330, 512, 694)):
        pts = []
        for t in range(0, 101, 5):
            k = t / 100
            pts.append((x + 46 * math.sin(k * math.pi * 2 + i), 300 - k * 210))
        d.line(pts, fill=CYAN + (255,), width=lw, joint='curve')

    # lid
    d.arc((250, 300, 774, 470), start=180, end=360, fill=PINK + (255,), width=lw)
    d.line((250, 386, 774, 386), fill=PINK + (255,), width=lw)
    d.ellipse((492, 300, 532, 340), outline=PINK + (255,), width=lw)   # lid knob

    # basket: two stacked bamboo tiers
    for top in (410, 540):
        d.rounded_rectangle((250, top, 774, top + 120), radius=26, outline=PINK + (255,), width=lw)
        for x in range(300, 760, 76):
            d.line((x, top + 22, x, top + 98), fill=PINK + (140,), width=6)

    # three dumplings peeking out of the top tier
    for x in (356, 512, 668):
        d.arc((x - 74, 344, x + 74, 470), start=180, end=360, fill=CYAN + (255,), width=lw)
        d.line((x - 40, 400, x - 16, 372), fill=CYAN + (200,), width=8)
        d.line((x + 40, 400, x + 16, 372), fill=CYAN + (200,), width=8)

    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    img.alpha_composite(strokes.filter(ImageFilter.GaussianBlur(radius=18)))
    img.alpha_composite(strokes)
    return img


def chinese_sign(size=(2048, 334)):
    """Replaces the old sign, which read 'delicious noodle soup'."""
    w, h = size
    strokes = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(strokes)
    font = ImageFont.truetype(CJK, 190, index=1)
    d.text((w / 2, h / 2), '美味点心屋', font=font, fill=GREEN + (255,), anchor='mm')

    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    img.alpha_composite(strokes.filter(ImageFilter.GaussianBlur(radius=16)))
    img.alpha_composite(strokes)
    return img


def main():
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)

    # main shop sign — replaces "JESSE'S RAMEN"
    shop = neon((2048, 352), "JACKIE'S DIM SUM", 190, PINK_CORE, PINK)
    shop.save(out / 'signShop.png')
    print('wrote signShop.png')

    food_icon().save(out / 'signFood.png')
    print('wrote signFood.png')

    chinese_sign().save(out / 'signChinese.png')
    print('wrote signChinese.png')

    # The pole sign carries its barcode + "j zhou" twice: as letter geometry AND
    # baked into the shop's misc texture. Hiding the geometry just uncovers the
    # baked copy, so this face is drawn opaque and covers the whole sign.
    w = h = 512
    pole = Image.new('RGBA', (w, h), (255, 47, 213, 255))   # #FF2FD5, the sign's pink
    d = ImageDraw.Draw(pole)

    ink = (20, 20, 20, 255)
    x = 96
    for width in (10, 22, 8, 14, 26, 10, 18, 8, 24, 12, 16, 10):
        d.rectangle((x, 120, x + width, 268), fill=ink)
        x += width + 14

    font = ImageFont.truetype(FUTURA, 104, index=BOLD)
    d.text((w / 2, 350), 'jackie', font=font, fill=ink, anchor='mm')

    pole.save(out / 'signPole.png')
    print('wrote signPole.png')


if __name__ == '__main__':
    main()
