"""
Rewrite the vending-machine screens (menu + 8 project detail pages) with
Tianlang (Jackie) Chen's real projects. These textures are upright, 1024x1024.

    .venv/bin/python tools/make-projects.py <decoded-dir> <out-dir>
"""
import sys
import pathlib
from PIL import Image, ImageDraw, ImageFont

FUTURA = '/System/Library/Fonts/Supplemental/Futura.ttc'
MEDIUM, BOLD = 0, 2

# mean colours of the card / tile faces (they carry a fine dither pattern; the mean
# repaints them evenly with no visible patch seam)
TILE_BG = (155, 248, 217)
CARD_BG = (156, 247, 218)
INK = (47, 80, 72)
PREVIEW_BG = (33, 37, 68)
CHIP_BG = (55, 55, 55)

# card face, inset just inside its rounded border + drop shadow
CARD_FACE = (80, 450, 800, 740)
# small tile face on a project page (the label sits at its foot)
TILE_FACE = (72, 296, 234, 380)

# the two tile rows sit at slightly different offsets: (left edges, width, label y)
TILE_ROWS = [
    ([64, 256, 449, 642], 173, 308),
    ([72, 260, 449, 637], 169, 663),
]

# project detail page geometry
SMALL_TILE_LABEL = (81, 308, 235, 385)
PREVIEW = (258, 82, 812, 390)
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


# (menu label, detail title, blurb, skills)
PROJECTS = [
    ("Three.js Dim Sum Portfolio",
     "Three.js Dim Sum Shop",
     "A 3D, interactive take on the personal portfolio — the site you are standing in "
     "right now. Built with JavaScript and Three.js and optimized for both mobile and "
     "desktop. Forked from Jesse Zhou's open-source ramen shop and rebuilt around my "
     "own research and projects.",
     "JavaScript, Three.js, WebGL, Blender"),

    ("EPCOT Genomic Foundation Model",
     "EPCOT Foundation Model",
     "Scalable data preparation and training pipeline for TSS-to-expression prediction. "
     "Built an end-to-end pseudobulk pipeline from raw HPAP snMultiome data, implemented "
     "five bit-equivalent training optimizations for a 2-5x per-epoch speedup, and found "
     "and fixed a ~50 kb TSS-bin offset bug that improved interpretability.",
     "PyTorch, HDF5, Slurm / HPC, Python"),

    ("LLM Incentive Design for Mobility",
     "LLM Incentive Design",
     "Investigating how large language models can support incentive mechanism design for "
     "shared mobility systems — ridesharing, transit incentives and vehicle-sharing. "
     "Building LLM-guided workflows that generate and evaluate practical, interpretable "
     "incentive strategies.",
     "LLMs, Prompt Engineering, Optimization"),

    ("Microbial Genomic Representation",
     "Microbial Genomics",
     "A composable genomic representation framework that converts microbial genomes into "
     "interpretable, parameter-free functional encodings via proteogenic k-mer "
     "tokenization, integrating with pre-trained sequence models (Evo, ESM, ProtT5) and "
     "leakage-safe statistical validation.",
     "Python, scikit-learn, Foundation Models"),

    ("AI-Guided Environmental Sensing",
     "Environmental Sensing",
     "AI-guided sensing for the sparse, dynamic Great Lakes environment, under limited "
     "sensor coverage and high uncertainty. Reproducible workflows for data ingestion, "
     "baseline reconstruction, uncertainty quantification, and uncertainty-aware sensor "
     "placement strategies.",
     "Gaussian Processes, Python, UQ"),

    ("Materials Science Data Applets",
     "Materials Data Applets",
     "Web applets with a JavaScript front end and a Python back end supporting data "
     "analytics, curation and sharing for the materials research community. Interactive "
     "modules let users upload datasets and analyze them with state-of-the-art models "
     "and fitting methods, aligned with FAIR data principles.",
     "JavaScript, Python, Data Visualization"),

    ("WeCom Full-Stack Platform",
     "WeCom @ Mars",
     "Full-stack secondary development on WeCom (Enterprise WeChat) at the Mars Global IT "
     "Service Center, supporting internal enterprise communication and workflow tools. "
     "API implementation, interface development, data migration and automation workflows "
     "during a system migration.",
     "JavaScript, Node.js, Vue.js"),

    ("MCM Mathematical Modeling",
     "MCM-COMAP 2025",
     "Honorable Mention in the Mathematical Contest in Modeling. Built, validated and "
     "wrote up a complete mathematical model against a 96-hour deadline, covering the "
     "full modeling, sensitivity analysis and reporting cycle.",
     "MATLAB, Python, Mathematical Modeling"),
]


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

    # preview panel — project 1 keeps the render of this very shop
    if index != 0:
        d.rectangle(PREVIEW, fill=PREVIEW_BG)
        fnt = font(30, BOLD)
        lines = wrap(d, title, fnt, PREVIEW[2] - PREVIEW[0] - 80)
        ty = (PREVIEW[1] + PREVIEW[3]) // 2 - len(lines) * 20
        for line in lines:
            w = d.textlength(line, font=fnt)
            d.text(((PREVIEW[0] + PREVIEW[2] - w) / 2, ty), line, font=fnt, fill=(230, 240, 255))
            ty += 40

    d.rounded_rectangle(CARD_FACE, radius=20, fill=CARD_BG)
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
