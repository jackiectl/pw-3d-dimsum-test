"""
Rewrite the vending-machine screens (menu + 8 project detail pages) with
Tianlang (Jackie) Chen's real projects. These textures are upright, 1024x1024.

    .venv/bin/python tools/make-projects.py <decoded-dir> <out-dir>
"""
import sys
import pathlib
from PIL import Image, ImageDraw, ImageFont
from content import CONTENT

FUTURA = '/System/Library/Fonts/Supplemental/Futura.ttc'
MEDIUM, BOLD = 0, 2

# mean colours of the card / tile faces (they carry a fine dither pattern; the mean
# repaints them evenly with no visible patch seam)
TILE_BG = (155, 248, 217)
CARD_BG = (156, 247, 218)
INK = (47, 80, 72)
PREVIEW_BG = (33, 37, 68)
CHIP_BG = (55, 55, 55)

# the mint preview container in the page's top-right (same box on every page)
PREVIEW_FACE = (256, 80, 812, 458)
# card face; the bottom edge varies per project, so it's measured per page
CARD_LEFT, CARD_TOP, CARD_RIGHT = 70, 450, 810
CARD_BOTTOM = [744, 743, 744, 743, 744, 772, 763, 744]
# small tile face on a project page (the label sits at its foot)
TILE_FACE = (72, 296, 234, 380)

# the two tile rows sit at slightly different offsets: (left edges, width, label y)
TILE_ROWS = [
    ([64, 256, 449, 642], 173, 308),
    ([72, 260, 449, 637], 169, 663),
]

# project detail page geometry
SMALL_TILE_LABEL = (81, 308, 235, 385)
TITLE_XY = (115, 478)
DESC_BOX = (115, 528, 775, 630)
SKILLS_XY = (180, 654)


def font(size, index=MEDIUM):
    return ImageFont.truetype(FUTURA, size, index=index)


def wrap(d, text, fnt, width):
    lines, line = [], ''
    for w in text.split():
        t = f'{line} {w}'.strip()
        if d.textlength(t, font=fnt) <= width:
            line = t
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


# (menu label, detail title, blurb, skills) — from content/content.json
PROJECTS = [(p['menuLabel'], p['title'], p['blurb'], p['skills'])
            for p in CONTENT['projects']]


def build_menu(img):
    d = ImageDraw.Draw(img)
    fnt = font(15, BOLD)
    for i, (label, *_) in enumerate(PROJECTS):
        lefts, width, y0 = TILE_ROWS[i // 4]
        x = lefts[i % 4]
        d.rectangle((x + 10, y0, x + width - 10, y0 + 72), fill=TILE_BG)
        y = y0 + 4
        for line in wrap(d, label, fnt, width - 32)[:3]:
            d.text((x + 20, y), line, font=fnt, fill=INK)
            y += 20
    return img


def build_project(img, index):
    label, title, blurb, skills = PROJECTS[index]
    d = ImageDraw.Draw(img)

    # Repaint the whole tile / card face rather than patching over each old text
    # block: the old copy varies in length per project, so any fixed-size patch
    # leaves some of it showing.
    d.rounded_rectangle(TILE_FACE, radius=10, fill=TILE_BG)
    y = TILE_FACE[1] + 12
    for line in wrap(d, label, font(15, BOLD), 148)[:4]:
        d.text((86, y), line, font=font(15, BOLD), fill=INK)
        y += 20

    # preview panel — project 1 keeps the render of this very shop; the others
    # first get their whole mint container repainted (the old screenshots vary
    # in size per page), then a dark title panel inside it
    if index != 0:
        d.rounded_rectangle(PREVIEW_FACE, radius=16, fill=CARD_BG)
        panel = (280, 104, 788, 434)
        d.rounded_rectangle(panel, radius=10, fill=PREVIEW_BG)
        fnt = font(30, BOLD)
        lines = wrap(d, title, fnt, panel[2] - panel[0] - 80)
        ty = (panel[1] + panel[3]) // 2 - len(lines) * 20
        for line in lines:
            w = d.textlength(line, font=fnt)
            d.text(((panel[0] + panel[2] - w) / 2, ty), line, font=fnt, fill=(230, 240, 255))
            ty += 40

    d.rounded_rectangle((CARD_LEFT, CARD_TOP, CARD_RIGHT, CARD_BOTTOM[index]), radius=22, fill=CARD_BG)
    d.text((115, 478), title, font=font(32, BOLD), fill=(45, 62, 58))

    y = 533
    for line in wrap(d, blurb, font(15, MEDIUM), 645):
        d.text((113, y), line, font=font(15, MEDIUM), fill=(58, 78, 72))
        y += 19

    # the Skills badge trails the description, as in the original layout
    chip_y = y + 14
    d.rounded_rectangle((117, chip_y, 171, chip_y + 25), radius=4, fill=CHIP_BG)
    d.text((124, chip_y + 5), 'Skills', font=font(14, BOLD), fill=(255, 255, 255))
    d.text((182, chip_y + 5), skills, font=font(15, MEDIUM), fill=(58, 78, 72))
    return img


def main():
    src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)

    menu = build_menu(Image.open(src / 'vendingMachineMenu.png').convert('RGB'))
    menu.save(out / 'vendingMachineMenu.png')
    print('wrote vendingMachineMenu.png')

    for i in range(8):
        img = build_project(Image.open(src / f'project{i + 1}.png').convert('RGB'), i)
        img.save(out / f'project{i + 1}.png')
        print(f'wrote project{i + 1}.png')


if __name__ == '__main__':
    main()
