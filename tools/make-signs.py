"""
Neon sign faces, drawn as transparent PNGs. They get mapped onto planes that sit
exactly where the old letter geometry was, once that geometry is stripped out.

    .venv/bin/python tools/make-signs.py <static/textures/signs>
"""
import sys
import math
import pathlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from content import CONTENT

SHOP = CONTENT['shop']

FUTURA = '/System/Library/Fonts/Supplemental/Futura.ttc'
MEDIUM, BOLD = 0, 2

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
    d.text((w / 2, h / 2), SHOP['chineseSign'], font=font, fill=GREEN + (255,), anchor='mm')

    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    img.alpha_composite(strokes.filter(ImageFilter.GaussianBlur(radius=16)))
    img.alpha_composite(strokes)
    return img



def floor_signature(size=(2048, 1496)):
    """The ground signature: it read 'Jesse Zhou / Management Consultant'.

    Drawn landscape; Signs.js turns it 90 degrees on the plane so the text runs
    along Z like the original. 2048 x 1496 keeps the pixels square on the
    2.33 x 3.19 m plane after that turn.
    """
    w, h = size
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    name = ImageFont.truetype(FUTURA, 250, index=BOLD)
    role = ImageFont.truetype(FUTURA, 100, index=MEDIUM)
    d.text((w / 2, h / 2 - 260), SHOP['floorName1'], font=name, fill=(255, 255, 255, 255), anchor='mm')
    d.text((w / 2, h / 2 - 10), SHOP['floorName2'], font=name, fill=(255, 255, 255, 255), anchor='mm')
    d.text((w / 2, h / 2 + 200), SHOP['floorRole'], font=role, fill=(235, 240, 255, 235), anchor='mm')
    return img



def vertical_sign(size=(512, 1824)):
    """The tall sign on the shop's flank; it read RAMEN top to bottom."""
    w, h = size
    strokes = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(strokes)

    d.rounded_rectangle((28, 28, w - 28, h - 28), radius=40, outline=CYAN + (255,), width=16)

    font = ImageFont.truetype(FUTURA, 168, index=BOLD)
    words = SHOP['verticalSign'].split()
    letters = []
    for i, word in enumerate(words):
        if i:
            letters.append('')
        letters.extend(list(word))
    top, step = 150, 210
    for i, ch in enumerate(letters):
        if not ch:
            continue
        d.text((w / 2, top + i * step), ch, font=font, fill=PINK_CORE + (255,),
               anchor='mm', stroke_width=9, stroke_fill=PINK + (255,))

    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    img.alpha_composite(strokes.filter(ImageFilter.GaussianBlur(radius=15)))
    img.alpha_composite(strokes)
    return img


def main():
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)

    # main shop sign — replaces "JESSE'S RAMEN"
    shop = neon((2048, 352), SHOP['name'], 190, PINK_CORE, PINK)
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
    d.text((w / 2, 350), SHOP['poleLabel'], font=font, fill=ink, anchor='mm')

    pole.save(out / 'signPole.png')
    print('wrote signPole.png')

    floor_signature().save(out / 'signFloor.png')
    print('wrote signFloor.png')

    vertical_sign().save(out / 'signVertical.png')
    print('wrote signVertical.png')


if __name__ == '__main__':
    main()
