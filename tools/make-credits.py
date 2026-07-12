"""
Rewrite the arcade credits screen.

Jesse Zhou built the 3D scene, models and illustrations this whole site runs on —
that credit stays. Jackie is added as the person who adapted and extended it.
Renaming the model credit would simply be false.

Arcade screens are stored rotated the opposite way to the big screens: rotate -90
to work upright, +90 to write back.

    .venv/bin/python tools/make-credits.py <decoded-dir> <out-dir>
"""
import sys
import pathlib
from PIL import Image, ImageDraw, ImageFont

MONO = '/System/Library/Fonts/Supplemental/Courier New Bold.ttf'
ORANGE = (255, 166, 38)
WHITE = (255, 255, 255)
FIELD = (29, 5, 54)
GRID = (62, 5, 112)

WIPE = (108, 180, 800, 870)     # old credit block + old copyright; keeps the "Next" hint
GRID_H = [8, 54, 101, 148, 194, 241, 288, 334, 381, 428, 474, 521, 568, 615, 662,
          708, 755, 802, 848, 895]
GRID_V_STEP = 59.8
GRID_V_START = 4

LINES = [
    ('label', 'Original design,'),
    ('label', '3D models & art:'),
    ('value', 'JESSE ZHOU'),
    ('gap', ''),
    ('label', 'Adapted & extended by:'),
    ('value', 'TIANLANG (JACKIE) CHEN'),
    ('gap', ''),
    ('label', 'Inspirations:'),
    ('value', "@BJGDESIGN, RU'S"),
    ('value', 'BLENDER DIARY,'),
    ('value', 'NATALIA TSY'),
    ('gap', ''),
    ('value', '(C) 2022 JESSE ZHOU'),
    ('value', '2026 ADAPTATION'),
]


def main():
    src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)

    img = Image.open(src / 'arcadeScreenCredits.png').convert('RGB').rotate(-90, expand=True)
    d = ImageDraw.Draw(img)

    # wipe the old credits, then put the grid back so it doesn't read as a patch
    d.rectangle(WIPE, fill=FIELD)
    for y in GRID_H:
        if WIPE[1] <= y <= WIPE[3]:
            d.line((WIPE[0], y, WIPE[2], y), fill=GRID, width=2)
    x = GRID_V_START
    while x < WIPE[2]:
        if x >= WIPE[0]:
            d.line((x, WIPE[1], x, WIPE[3]), fill=GRID, width=2)
        x += GRID_V_STEP

    font = ImageFont.truetype(MONO, 26)
    y = WIPE[1] + 20
    for kind, text in LINES:
        if kind == 'gap':
            y += 20
            continue
        d.text((130, y), text, font=font, fill=ORANGE if kind == 'label' else WHITE)
        y += 34

    img.rotate(90, expand=True).save(out / 'arcadeScreenCredits.png')
    img.save(out / 'arcadeScreenCredits_preview.png')
    print('wrote arcadeScreenCredits.png')


if __name__ == '__main__':
    main()
