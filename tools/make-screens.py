"""
Rewrite the big-screen textures with Tianlang (Jackie) Chen's CV content.

The screen textures are stored rotated 90deg CW in texture space. We rotate each
decoded source upright, paint over just the text areas (leaving the gradient
bars, tabs, Back button and social icons untouched), then rotate back.

    .venv/bin/python tools/make-screens.py <decoded-dir> <out-dir>
"""
import sys
import pathlib
from PIL import Image, ImageDraw, ImageFont

FUTURA = '/System/Library/Fonts/Supplemental/Futura.ttc'
BG = (14, 14, 14)


def font(size, index=0):
    return ImageFont.truetype(FUTURA, size, index=index)


MEDIUM, BOLD = 0, 2  # Futura.ttc face indices


def wrap(draw, text, fnt, max_width):
    lines, line = [], ''
    for word in text.split():
        trial = f'{line} {word}'.strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def paragraph(draw, text, box, size, leading, fill=(255, 255, 255)):
    """Draw wrapped text into box=(x0, y0, x1, y1), clearing it first."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=BG)
    fnt = font(size, MEDIUM)
    y = y0
    for line in wrap(draw, text, fnt, x1 - x0):
        draw.text((x0, y), line, font=fnt, fill=fill)
        y += leading
    return y


ABOUT = (
    "I'm a Data Science student at the University of Michigan, working where "
    "machine learning, genomics and large language models meet. I build research "
    "pipelines — foundation-model fine-tuning, LLM-guided workflows and "
    "reproducible data infrastructure — and I care a lot about making them "
    "fast and correct. Previously Mechanical Engineering at Shanghai Jiao Tong "
    "University. Thanks for visiting!"
)

EXPERIENCE_INTRO = (
    "I study Data Science at the University of Michigan, after two years of "
    "Mechanical Engineering at Shanghai Jiao Tong University. Most of my time "
    "goes into research: genomic foundation models, LLM-guided incentive design, "
    "AI-guided environmental sensing, and data-analytics tooling for materials "
    "science. Before that I did full-stack work at Mars. See the vending machine "
    "for project details."
)

SKILLS_INTRO = (
    "My toolkit spans machine learning, LLM and agentic AI workflows, and "
    "full-stack web development. I am most at home in Python and PyTorch, "
    "fine-tuning foundation models and squeezing speed out of training loops on "
    "HPC clusters — but I also ship interactive front-ends like this one."
)

EXPERIENCE_CARDS = [
    ("University of Michigan", "Research — Genomics & LLMs",
     "EPCOT foundation model: pseudobulk data pipeline, 2–5x faster training, "
     "reset-head fine-tuning. Also LLM incentive design for mobility systems*"),
    ("Mars, Global IT Service Center", "Full-Stack Development Intern",
     "WeCom enterprise platform: JavaScript, Node.js and Vue.js. API and interface "
     "development, data migration, automation workflows*"),
    ("Teaching & Contests", "TA / MCM Honorable Mention",
     "TA for English Academic Writing and General Physics. Honorable Mention, "
     "Mathematical Contest in Modeling (MCM-COMAP) 2025*"),
]

SKILL_GROUPS = [
    ("CODING", ["Python", "C", "C++", "JavaScript", "SQL", "R", "MATLAB", "Java", "Bash", "Git"]),
    ("ML & DATA", ["PyTorch", "scikit-learn", "Gaussian Processes", "Fine-Tuning", "HDF5", "Slurm / HPC"]),
    ("LLM & AGENTIC AI", ["Prompt Engineering", "RAG", "LLM Workflows", "Agentic Coding", "Output Validation"]),
    ("WEB DEVELOPMENT", ["HTML", "CSS", "JavaScript", "Node.js", "Vue.js", "Three.js"]),
    ("TOOLS", ["Solidworks", "Blender", "MySQL", "SQLite"]),
]


def build_about(img):
    d = ImageDraw.Draw(img)
    d.rectangle((250, 1005, 1750, 1112), fill=BG)
    d.text((281, 1012), "Hi, I'm Jackie.", font=font(96, BOLD), fill=(255, 255, 255))
    paragraph(d, ABOUT, (279, 1210, 1590, 1692), 44, 54)
    return img


def build_skills(img):
    d = ImageDraw.Draw(img)
    # heading stops short of the right column
    d.rectangle((250, 1005, 1140, 1112), fill=BG)
    d.text((281, 1012), "Skills", font=font(96, BOLD), fill=(255, 255, 255))
    paragraph(d, SKILLS_INTRO, (279, 1210, 1000, 1692), 38, 46)

    # right column: wipe the old word cloud, lay out grouped tags
    d.rectangle((1060, 860, 1895, 1990), fill=BG)
    y = 950
    for title, items in SKILL_GROUPS:
        d.text((1100, y), title, font=font(32, BOLD), fill=(255, 255, 255))
        y += 46
        for line in wrap(d, '  '.join(items), font(27, MEDIUM), 760):
            d.text((1100, y), line, font=font(27, MEDIUM), fill=(90, 220, 220))
            y += 36
        y += 30
    return img


def build_experience(img):
    d = ImageDraw.Draw(img)
    d.rectangle((250, 1005, 1140, 1112), fill=BG)
    d.text((281, 1012), "Experience", font=font(96, BOLD), fill=(255, 255, 255))
    paragraph(d, EXPERIENCE_INTRO, (279, 1210, 1120, 1780), 38, 46)

    # reuse the three card panels already baked into the layout, on the right
    cards = [(929, 1213), (1230, 1541), (1559, 1897)]
    for (top, bottom), (org, role, blurb) in zip(cards, EXPERIENCE_CARDS):
        d.rectangle((1167, top, 1855, bottom), fill=(30, 30, 30))
        d.text((1200, top + 24), org, font=font(34, BOLD), fill=(90, 220, 220))
        d.text((1200, top + 68), role, font=font(26, MEDIUM), fill=(200, 200, 200))
        y = top + 112
        for line in wrap(d, blurb, font(24, MEDIUM), 620):
            d.text((1200, y), line, font=font(24, MEDIUM), fill=(175, 175, 175))
            y += 32
    return img


# ---- mobile: single narrow column, nav row on top ----

SKILLS_INTRO_SHORT = (
    "Machine learning, LLM and agentic AI workflows, and full-stack web "
    "development — most at home in Python and PyTorch."
)

EXPERIENCE_INTRO_SHORT = (
    "Data Science at the University of Michigan, previously Mechanical "
    "Engineering at Shanghai Jiao Tong University."
)

MOB_HEAD = (560, 992, 1500, 1062)
MOB_BODY = (553, 1140, 1500, 1850)


def mobile_heading(d, title):
    d.rectangle(MOB_HEAD, fill=BG)
    d.text((575, 992), title, font=font(62, BOLD), fill=(255, 255, 255))
    d.rectangle(MOB_BODY, fill=BG)


def build_about_mobile(img):
    d = ImageDraw.Draw(img)
    mobile_heading(d, "Hi, I'm Jackie.")
    paragraph(d, ABOUT, (575, 1150, 1480, 1840), 38, 47)
    return img


def build_skills_mobile(img):
    d = ImageDraw.Draw(img)
    mobile_heading(d, "Skills")
    y = paragraph(d, SKILLS_INTRO_SHORT, (575, 1150, 1480, 1400), 32, 40) + 24
    for title, items in SKILL_GROUPS:
        d.text((575, y), title, font=font(26, BOLD), fill=(255, 255, 255))
        y += 34
        for line in wrap(d, '  '.join(items), font(24, MEDIUM), 900):
            d.text((575, y), line, font=font(24, MEDIUM), fill=(90, 220, 220))
            y += 30
        y += 12
    return img


def build_experience_mobile(img):
    d = ImageDraw.Draw(img)
    mobile_heading(d, "Experience")
    y = paragraph(d, EXPERIENCE_INTRO_SHORT, (575, 1150, 1480, 1330), 32, 40) + 20
    for org, role, blurb in EXPERIENCE_CARDS:
        d.rectangle((575, y, 1480, y + 148), fill=(30, 30, 30))
        d.text((600, y + 12), org, font=font(28, BOLD), fill=(90, 220, 220))
        d.text((600, y + 48), role, font=font(22, MEDIUM), fill=(200, 200, 200))
        yy = y + 80
        for line in wrap(d, blurb, font(20, MEDIUM), 850)[:2]:
            d.text((600, yy), line, font=font(20, MEDIUM), fill=(175, 175, 175))
            yy += 26
        y += 168
    return img


BUILDERS = {
    'bigScreenAbout': build_about,
    'bigScreenSkills': build_skills,
    'bigScreenExperience': build_experience,
    'bigScreenAboutMobile': build_about_mobile,
    'bigScreenSkillsMobile': build_skills_mobile,
    'bigScreenExperienceMobile': build_experience_mobile,
}


def main():
    src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for name, build in BUILDERS.items():
        img = Image.open(src / f'{name}.png').convert('RGB').rotate(90, expand=True)
        img = build(img)
        img.rotate(-90, expand=True).save(out / f'{name}.png')
        img.save(out / f'{name}_preview.png')  # upright, for eyeballing
        print('wrote', out / f'{name}.png')


if __name__ == '__main__':
    main()
