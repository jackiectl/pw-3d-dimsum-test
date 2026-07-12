"""
Neon sign faces, drawn as transparent PNGs. They get mapped onto planes that sit
exactly where the old letter geometry was, once that geometry is stripped out.

    .venv/bin/python tools/make-signs.py <static/textures/signs>
"""
import sys
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


def main():
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)

    # main shop sign — replaces "JESSE'S RAMEN"
    shop = neon((2048, 352), "JACKIE'S DIM SUM", 190, PINK_CORE, PINK)
    shop.save(out / 'signShop.png')
    print('wrote signShop.png')

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
