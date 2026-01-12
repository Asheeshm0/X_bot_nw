from PIL import Image, ImageDraw, ImageFont, ImageFilter
import textwrap
import uuid
import os

WIDTH, HEIGHT = 1200, 675

FONT_BOLD = "Roboto-Bold.ttf"
FONT_REGULAR = "Roboto-Regular.ttf"

THEMES = {
    "NEWS": {
        "bg_grad": [(15, 23, 42), (59, 130, 246)],
        "accent": (255, 200, 0),
        "tag_bg": (255, 200, 0),
        "tag_text": (0, 0, 0)
    },
    "ALERT": {
        "bg_grad": [(40, 0, 0), (220, 38, 38)],
        "accent": (255, 255, 255),
        "tag_bg": (220, 38, 38),
        "tag_text": (255, 255, 255)
    },
    "TECH": {
        "bg_grad": [(17, 24, 39), (139, 92, 246)],
        "accent": (56, 189, 248),
        "tag_bg": (139, 92, 246),
        "tag_text": (255, 255, 255)
    },
    "FINANCE": {
        "bg_grad": [(6, 78, 59), (16, 185, 129)],
        "accent": (250, 204, 21),
        "tag_bg": (250, 204, 21),
        "tag_text": (0, 0, 0)
    }
}

def load_font(name, size):
    try:
        return ImageFont.truetype(name, size)
    except:
        return ImageFont.load_default()

def create_gradient_background(width, height, start, end):
    base = Image.new("RGB", (width, height), start)
    top = Image.new("RGB", (width, height), end)
    mask = Image.new("L", (width, height))
    mask.putdata([
        int(255 * (x + y) / (width + height))
        for y in range(height) for x in range(width)
    ])
    base.paste(top, (0, 0), mask)
    return base

def draw_glass_card(img, x, y, w, h):
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle((x, y, x+w, y+h), radius=20, fill=(20, 25, 35, 210))
    d.line((x+20, y, x+w-20, y), fill=(255, 255, 255, 100), width=2)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x+10, y+10, x+w+10, y+h+15), radius=20, fill=(0, 0, 0, 100))
    shadow = shadow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, shadow)
    img = Image.alpha_composite(img, overlay)
    return img

def draw_glow(img, color, x, y, r):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(glow)
    d.ellipse((x-r, y-r, x+r, y+r), fill=(*color, 80))
    glow = glow.filter(ImageFilter.GaussianBlur(r / 1.5))
    return Image.alpha_composite(img, glow)

def generate_banner(headline, summary, category="NEWS"):
    headline = (headline or "Breaking News Update").strip()
    summary = (summary or "Details are emerging.").strip()

    theme = THEMES.get(category.upper(), THEMES["NEWS"])

    img = create_gradient_background(WIDTH, HEIGHT, *theme["bg_grad"]).convert("RGBA")
    img = draw_glow(img, theme["bg_grad"][1], WIDTH, 0, 400)
    img = draw_glow(img, theme["accent"], 0, HEIGHT, 300)

    img = draw_glass_card(img, 60, 100, WIDTH-120, HEIGHT-160)
    draw = ImageDraw.Draw(img)

    tag_font = load_font(FONT_BOLD, 22)
    tag_text = f"  {category.upper()} UPDATE  "
    bx = tag_font.getbbox(tag_text)
    draw.rounded_rectangle((100, 140, 100+bx[2]+20, 140+bx[3]+20), radius=10, fill=theme["tag_bg"])
    draw.text((110, 150), tag_text, fill=theme["tag_text"], font=tag_font)

    font_size = 65
    wrapper = textwrap.TextWrapper(width=30)

    while font_size > 30:
        font = load_font(FONT_BOLD, font_size)
        lines = wrapper.wrap(headline)
        if lines and max(draw.textlength(l, font=font) for l in lines) < 900:
            break
        font_size -= 4

    y = 220
    for l in lines[:3]:
        draw.text((100, y), l, fill="white", font=font)
        y += font_size + 10

    draw.line((100, y+10, 220, y+10), fill=theme["accent"], width=4)
    y += 40

    sum_font = load_font(FONT_REGULAR, 32)
    for l in textwrap.wrap(summary, 60)[:3]:
        draw.text((100, y), l, fill=(200, 210, 220), font=sum_font)
        y += 40

    

    os.makedirs("images", exist_ok=True)
    path = f"images/viral_{uuid.uuid4().hex}.png"
    img.convert("RGB").save(path, optimize=True)
    return path
