from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap
import uuid
import os

WIDTH, HEIGHT = 1200, 675

FONT_BOLD = "Roboto-Bold.ttf"
FONT_REGULAR = "Roboto-Regular.ttf"

THEMES = {
    "TECH": ((88, 80, 200), (20, 24, 45)),
    "POLITICS": ((220, 38, 38), (30, 15, 15)),
    "FINANCE": ((16, 185, 129), (6, 78, 59)),
    "WORLD": ((59, 130, 246), (15, 23, 42)),
    "NEWS": ((139, 92, 246), (17, 24, 39))
}

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def gradient_bg(c1, c2):
    base = Image.new("RGB", (WIDTH, HEIGHT), c1)
    top = Image.new("RGB", (WIDTH, HEIGHT), c2)
    mask = Image.new("L", (WIDTH, HEIGHT))
    mask.putdata([int((x+y)/(WIDTH+HEIGHT)*255)
                  for y in range(HEIGHT) for x in range(WIDTH)])
    base.paste(top, (0,0), mask)
    return base

def generate_banner(headline, summary, category="NEWS"):
    headline = (headline or "").strip()
    summary = (summary or "").strip()

    if not headline:
        headline = "Latest News Update"

    c1, c2 = THEMES.get(category.upper(), THEMES["NEWS"])
    img = gradient_bg(c1, c2).convert("RGBA")

    overlay = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle((80,100,1120,575), radius=24, fill=(15,20,35,215))
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)

    tag_font = load_font(FONT_BOLD, 22)
    draw.rounded_rectangle((120,130,300,170), radius=10, fill=c1)
    draw.text((135,136), f"{category.upper()} UPDATE", fill="white", font=tag_font)

    h_font = load_font(FONT_BOLD, 60)
    lines = textwrap.wrap(headline, width=32)[:3]

    y = 200
    for line in lines:
        draw.text((120,y), line, fill="white", font=h_font)
        y += 70

    draw.line((120,y+10,220,y+10), fill=c1, width=4)

    if summary:
        s_font = load_font(FONT_REGULAR, 30)
        y += 35
        for line in textwrap.wrap(summary, width=60)[:2]:
            draw.text((120,y), line, fill=(210,215,225), font=s_font)
            y += 42

    os.makedirs("images", exist_ok=True)
    path = f"images/news_{uuid.uuid4().hex}.png"
    img.convert("RGB").save(path, optimize=True)
    return path
