from PIL import Image, ImageDraw, ImageFont
import textwrap
import uuid
import os

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 1200, 675
MARGIN_X = 70
TOP_BAR_HEIGHT = 90

THEMES = {
    "NEWS": {
        "bg": (15, 23, 42),        # dark blue
        "accent": (251, 191, 36),  # amber
        "text": (255, 255, 255),
        "subtext": (203, 213, 225)
    },
    "HEALTH": {
        "bg": (20, 83, 45),
        "accent": (34, 197, 94),
        "text": (255, 255, 255),
        "subtext": (187, 247, 208)
    },
    "TECH": {
        "bg": (17, 24, 39),
        "accent": (96, 165, 250),
        "text": (255, 255, 255),
        "subtext": (191, 219, 254)
    },
    "ECONOMY": {
        "bg": (30, 41, 59),
        "accent": (250, 204, 21),
        "text": (255, 255, 255),
        "subtext": (226, 232, 240)
    }
}

# ---------------- FONT LOADER ----------------
def load_font(size, bold=False):
    try:
        if bold:
            return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except:
        return ImageFont.load_default()

# ---------------- AUTO FONT FIT ----------------
def fit_text(draw, text, max_width, start_size, bold=False):
    size = start_size
    while size > 20:
        font = load_font(size, bold)
        lines = textwrap.wrap(text, width=40)
        longest = max(draw.textlength(line, font=font) for line in lines)
        if longest <= max_width:
            return font, lines
        size -= 2
    return load_font(20, bold), textwrap.wrap(text, 40)

# ---------------- MAIN GENERATOR ----------------
def generate_banner(headline, summary, category="NEWS"):
    theme = THEMES.get(category.upper(), THEMES["NEWS"])

    img = Image.new("RGB", (WIDTH, HEIGHT), theme["bg"])
    draw = ImageDraw.Draw(img)

    # Top bar
    draw.rectangle((0, 0, WIDTH, TOP_BAR_HEIGHT), fill=theme["accent"])
    tag_font = load_font(28, bold=True)
    draw.text(
        (MARGIN_X, 28),
        f"{category.upper()} UPDATE",
        fill=(0, 0, 0),
        font=tag_font
    )

    # Headline (AUTO SCALE)
    headline_font, headline_lines = fit_text(
        draw,
        headline,
        WIDTH - 2 * MARGIN_X,
        start_size=60,
        bold=True
    )

    y = TOP_BAR_HEIGHT + 60
    for line in headline_lines:
        draw.text((MARGIN_X, y), line, fill=theme["text"], font=headline_font)
        y += headline_font.size + 10

    # Summary (AUTO SCALE)
    summary_font, summary_lines = fit_text(
        draw,
        summary,
        WIDTH - 2 * MARGIN_X,
        start_size=36,
        bold=False
    )

    y += 30
    for line in summary_lines[:3]:  # max 3 lines for clarity
        draw.text((MARGIN_X, y), line, fill=theme["subtext"], font=summary_font)
        y += summary_font.size + 8

    # Footer
    footer_font = load_font(22)
    draw.text(
        (MARGIN_X, HEIGHT - 50),
        "Verified news • Auto-generated banner",
        fill=theme["subtext"],
        font=footer_font
    )

    # Save
    os.makedirs("images", exist_ok=True)
    filename = f"images/news_{uuid.uuid4().hex}.png"
    img.save(filename, optimize=True)

    return filename
