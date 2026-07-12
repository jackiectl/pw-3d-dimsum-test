"""
Placeholder project cards for the two photo-wall screens, replacing the original
owner's personal photos. Deliberately minimal: a colour field, a few lines and the
project name — enough to hold the slot until real images exist.

    .venv/bin/python tools/make-photowall.py <out-dir>
"""
import sys
import math
import pathlib
from PIL import Image, ImageDraw, ImageFont

FUTURA = '/System/Library/Fonts/Supplemental/Futura.ttc'
MEDIUM, BOLD = 0, 2
SIZE = 256

# (title, kicker, background, accent)
CARDS = [
    ('EPCOT',       'GENOMIC FM',    (18, 22, 46),  (94, 234, 212)),
    ('LLM',         'INCENTIVES',    (40, 16, 44),  (244, 114, 182)),
    ('MICROBIAL',   'GENOMICS',      (14, 32, 30),  (163, 230, 53)),
    ('SENSING',     'GREAT LAKES',   (12, 26, 48),  (56, 189, 248)),
    ('MATERIALS',   'DATA APPLETS',  (44, 28, 12),  (251, 191, 36)),

    ('WECOM',       'FULL-STACK',    (16, 20, 44),  (129, 140, 248)),
    ('MCM',         'MODELING',      (38, 14, 22),  (248, 113, 113)),
    ('THREE.JS',    'THIS SHOP',     (30, 12, 46),  (192, 132, 252)),
    ('PYTORCH',     'FINE-TUNING',   (12, 30, 40),  (45, 212, 191)),
    ('MICHIGAN',    'DATA SCIENCE',  (20, 18, 38),  (250, 204, 21)),
]


def card(title, kicker, bg, accent):
    img = Image.new('RGB', (SIZE, SIZE), bg)
    d = ImageDraw.Draw(img)

    # a few lines: a sparse grid, plus an abstract data-ish polyline
    for i in range(1, 6):
        y = i * SIZE // 6
        d.line((0, y, SIZE, y), fill=tuple(int(c * 0.35 + b * 0.65) for c, b in zip(accent, bg)))

    points = []
    for i in range(9):
        x = 20 + i * (SIZE - 40) / 8
        y = 150 - 46 * math.sin(i * 0.9 + len(title)) * (0.4 + 0.1 * (i % 3))
        points.append((x, y))
    d.line(points, fill=accent, width=3, joint='curve')
    for x, y in points[::2]:
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=accent)

    d.rectangle((20, 196, 20 + 46, 200), fill=accent)
    d.text((20, 208), title, font=ImageFont.truetype(FUTURA, 26, index=BOLD), fill=(240, 245, 255))
    d.text((20, 236), kicker, font=ImageFont.truetype(FUTURA, 13, index=MEDIUM), fill=accent)
    return img


def main():
    out = pathlib.Path(sys.argv[1])
    for i, spec in enumerate(CARDS):
        screen = 'smallScreen1' if i < 5 else 'smallScreen2'
        folder = out / screen
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f'{i % 5 + 1}.png'
        card(*spec).save(path)
        print('wrote', path)


if __name__ == '__main__':
    main()
