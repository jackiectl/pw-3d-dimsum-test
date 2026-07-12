"""
Rebuild the shop's main screen: a cartooned portrait of Tianlang (Jackie) Chen
in place of the original owners, with dim sum branding.

The "cartoon" is a classic posterize + outline stylisation (smooth -> colour
quantise -> edge overlay), not an AI-generated illustration.

    .venv/bin/python tools/make-bigscreen.py <photo.jpg> <out.png>
"""
import sys
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from content import CONTENT

SIZE = 2048
FUTURA = '/System/Library/Fonts/Supplemental/Futura.ttc'
CJK = '/System/Library/Fonts/Supplemental/Hiragino Sans GB.ttc'
BOLD = 2

PURPLE = (106, 27, 224)
ORANGE = (255, 160, 20)
WHITE = (255, 255, 255)

FACE_CROP = (230, 20, 1020, 810)   # head + shoulders out of the 1206x1466 portrait
CIRCLE = (549, 549, 1499, 1499)     # portrait medallion, centred on the screen


def cartoonify(img, levels=7):
    """Smooth, flatten into colour bands, then lay dark outlines back on top."""
    img = img.convert('RGB')

    # knock out photographic noise / skin detail without losing the big shapes
    smooth = img.filter(ImageFilter.MedianFilter(size=9))
    smooth = smooth.filter(ImageFilter.GaussianBlur(radius=2))

    # flatten to a small palette -> the flat "cel" look
    flat = smooth.quantize(colors=levels, method=Image.MEDIANCUT, dither=Image.NONE)
    flat = flat.convert('RGB')

    # outlines from the smoothed image (not the noisy original)
    grey = smooth.convert('L')
    edges = grey.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
    edges = edges.point(lambda v: 255 if v > 28 else 0)
    ink = ImageChops.invert(edges).convert('RGB')

    return ImageChops.multiply(flat, ink)


def arc_text(canvas, text, centre, radius, font, fill, outline, start_deg, end_deg):
    """Lay text around an arc, one glyph at a time."""
    cx, cy = centre
    span = end_deg - start_deg
    step = span / max(len(text) - 1, 1)

    for i, ch in enumerate(text):
        if ch == ' ':
            continue
        angle = math.radians(start_deg + step * i)
        glyph = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glyph)
        gd.text((100, 100), ch, font=font, fill=fill, anchor='mm',
                stroke_width=8, stroke_fill=outline)
        glyph = glyph.rotate(-(start_deg + step * i) - 90, resample=Image.BICUBIC)
        x = cx + radius * math.cos(angle) - 100
        y = cy + radius * math.sin(angle) - 100
        canvas.alpha_composite(glyph, (int(x), int(y)))


def main():
    photo_path, out_path = sys.argv[1], sys.argv[2]

    canvas = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 255))
    d = ImageDraw.Draw(canvas)

    # --- medallion: purple disc, white ring, cartooned portrait ---
    d.ellipse(CIRCLE, fill=WHITE)
    inset = 22
    disc = (CIRCLE[0] + inset, CIRCLE[1] + inset, CIRCLE[2] - inset, CIRCLE[3] - inset)
    d.ellipse(disc, fill=PURPLE)

    diameter = disc[2] - disc[0]
    face = Image.open(photo_path).crop(FACE_CROP).resize((diameter, diameter), Image.LANCZOS)
    face = cartoonify(face)

    mask = Image.new('L', (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter - 1, diameter - 1), fill=255)
    canvas.paste(face, (disc[0], disc[1]), mask)

    # --- BEST DIM SUM IN TOWN, arced over the medallion ---
    arc_font = ImageFont.truetype(FUTURA, 86, index=BOLD)
    arc_text(canvas, CONTENT['bigScreen']['arcTagline'],
             centre=((CIRCLE[0] + CIRCLE[2]) // 2, (CIRCLE[1] + CIRCLE[3]) // 2),
             radius=(CIRCLE[2] - CIRCLE[0]) // 2 + 92,
             font=arc_font, fill=PURPLE, outline=WHITE,
             start_deg=200, end_deg=340)

    # big-screen textures are stored turned 90 degrees clockwise (the mesh UVs
    # expect it); drawing upright and saving directly shows up rotated in-game
    canvas.convert('RGB').rotate(-90, expand=True).save(out_path)
    print('wrote', out_path)


if __name__ == '__main__':
    main()
