
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Dict, List, Optional, Tuple
import math
import os

# ---------- Utility ----------

def _rounded_rectangle(draw: ImageDraw.ImageDraw, xy, radius, fill=None, outline=None, width=1):
    """
    Draw a rounded rectangle on the provided ImageDraw object.
    """
    x1, y1, x2, y2 = xy
    w = x2 - x1
    h = y2 - y1
    r = min(radius, w // 2, h // 2)
    draw.rounded_rectangle([x1, y1, x2, y2], radius=r, fill=fill, outline=outline, width=width)

from PIL import ImageFont, ImageDraw
import os

def _load_font(size: int):
    """Load a font with fallback support"""
    candidates = [
        "./DejaVuSans.ttf",  # local project font (recommended: copy DejaVuSans.ttf here)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    # Last fallback
    return ImageFont.load_default()


# ---------- Coloring ----------
# Color palette: (fill, text)
PALETTE = {
    "awesome": ((20, 150, 70), (255, 255, 255)),   # dark-ish green
    "great":   ((34, 197, 94), (0, 0, 0)),         # green
    "good":    ((234, 179, 8), (0, 0, 0)),         # yellow
    "regular": ((249, 115, 22), (0, 0, 0)),        # orange
    "bad":     ((239, 68, 68), (255, 255, 255)),   # red
    "garbage": ((139, 92, 246), (255, 255, 255)),  # purple
    "chip_bg": ((24, 24, 27), (255, 255, 255)),    # neutral chip
    "panel":   (12, 12, 17),                       # background panel
    "bg":      (10, 10, 12),                       # overall bg
    "muted":   (180, 183, 188),                    # muted text
    "white":   (245, 245, 245),
    "card":    (18, 18, 22),
}

def rating_bucket(score: float) -> str:
    if score is None:
        return "chip_bg"
    if score >= 9.0:
        return "awesome"
    if score >= 8.0:
        return "great"
    if score >= 7.0:
        return "good"
    if score >= 6.0:
        return "regular"
    if score >= 3.5:
        return "bad"
    return "garbage"

# ---------- Main Renderer ----------

def generate_episode_grid(
    out_path: str,
    title: str,
    overall_rating: Optional[float],
    years: str,
    season_to_ratings: Dict[str, List[Optional[float]]],
    poster_path: Optional[str] = None,
    canvas_size: Tuple[int, int] = (1080, 1920),  # 9:16
    caption: Optional[str] = None
) -> str:
    W, H = canvas_size
    img = Image.new("RGB", (W, H), PALETTE["bg"])
    draw = ImageDraw.Draw(img)

    # Top caption
    top_pad = 46
    side_pad = 40
    caption_pad_bottom = 20
    if caption:
        cap_font = _load_font(44)
        w = draw.textlength(caption, font=cap_font)
        draw.text(((W - w)/2, top_pad), caption, font=cap_font, fill=PALETTE["white"])
        y_cursor = top_pad + 60 + caption_pad_bottom
    else:
        y_cursor = top_pad

    # Left card (poster + title + meta)
    card_w = int(W * 0.40)
    card_h = int(H * 0.40)
    card_x1 = side_pad
    card_y1 = y_cursor + 20
    card_x2 = card_x1 + card_w
    card_y2 = card_y1 + card_h

    _rounded_rectangle(draw, (card_x1, card_y1, card_x2, card_y2), 28, fill=PALETTE["card"])

    inner_pad = 18
    inner_x1 = card_x1 + inner_pad
    inner_y1 = card_y1 + inner_pad

    # Poster area
    poster_h = int(card_h * 0.62)
    poster_w = card_w - 2*inner_pad
    poster_x1 = inner_x1
    poster_y1 = inner_y1
    poster_x2 = poster_x1 + poster_w
    poster_y2 = poster_y1 + poster_h
    _rounded_rectangle(draw, (poster_x1, poster_y1, poster_x2, poster_y2), 18, fill=(30,30,35))

    if poster_path and os.path.exists(poster_path):
        try:
            poster = Image.open(poster_path).convert("RGB").resize((poster_w, poster_h))
            img.paste(poster, (poster_x1, poster_y1))
        except Exception:
            pass
    else:
        # Placeholder text
        pfont = _load_font(28)
        draw.text((poster_x1+16, poster_y1+16), "Poster\nplaceholder", font=pfont, fill=PALETTE["muted"])

    # Title & meta
    tfont = _load_font(42)
    mfont = _load_font(28)
    draw.text((inner_x1, poster_y2 + 16), title, font=tfont, fill=PALETTE["white"])

    meta_y = poster_y2 + 16 + 54
    meta = f"{overall_rating:.1f}" if overall_rating is not None else "-"
    # Star icon as simple text
    draw.text((inner_x1, meta_y), f"★ {meta}    {years}", font=mfont, fill=PALETTE["muted"])

    # Legend
        # Legend (split into 2 rows of 3 items each, top-right)
    legend_items = [
        ("Awesome", "awesome"), ("Great", "great"), ("Good", "good"),
        ("Regular", "regular"), ("Bad", "bad"), ("Garbage", "garbage")
    ]
    lfont = _load_font(28)  # bigger font
    box_size = 28
    spacing_x = 160   # horizontal spacing between legend items
    spacing_y = 50    # vertical spacing between rows
    margin_top = 20   # distance from top
    margin_right = 40 # distance from right edge

    # Start position (top-right corner)
    legend_x_start = W - side_pad - (3 * spacing_x)
    legend_y_start = margin_top

    for i, (label, key) in enumerate(legend_items):
        row = i // 3
        col = i % 3

        lx = legend_x_start + col * spacing_x
        ly = legend_y_start + row * spacing_y

        color = PALETTE[key][0] if isinstance(PALETTE[key], tuple) else PALETTE[key]
        _rounded_rectangle(draw, (lx, ly, lx + box_size, ly + box_size), 6, fill=color)
        draw.text((lx + box_size + 10, ly - 2), label, font=lfont, fill=PALETTE["muted"])




    # Episode chips area (right side)
    chips_x1 = card_x2 + 60
    chips_w = W - chips_x1 - side_pad
    chips_y = y_cursor + 60

    sfont = _load_font(28)
    cfont = _load_font(34)

    # We place seasons vertically; each season label then a column of chips
    season_gap = 28
    chip_w = 120
    chip_h = 50
    chip_radius = 16
    row_gap = 15

    for s_idx, (season_label, ratings) in enumerate(season_to_ratings.items()):
        # Season header
        draw.text((chips_x1, chips_y), season_label, font=sfont, fill=PALETTE["white"])
        chips_y += 36

        # Draw chips (E1..En)
        max_eps_per_col = 25
        col_gap = 180   # more gap so labels don’t overlap
        base_y = chips_y

        for e_idx, score in enumerate(ratings, start=1):
            col = (e_idx - 1) // max_eps_per_col
            row = (e_idx - 1) % max_eps_per_col

            # Position based on col & row
            x1 = chips_x1 + col * (chip_w + col_gap)
            y1 = base_y + row * (chip_h + row_gap)
            x2 = x1 + chip_w
            y2 = y1 + chip_h

            # Skip drawing if API returned None
            if score is None:
                continue

            # Draw chip
            bucket = rating_bucket(score)
            fill, text_color = PALETTE[bucket]
            _rounded_rectangle(draw, (x1, y1, x2, y2), chip_radius, fill=fill)

            # Episode label (drawed with more spacing so it doesn't overlap chip)
            elabel = f"E{e_idx}"
            label_w = draw.textlength(elabel, font=sfont)
            draw.text(
                (x1 - label_w - 12, y1 + (chip_h - sfont.size) // 2),  # shift left by label width + margin
                elabel,
                font=sfont,
                fill=PALETTE["muted"]
            )
            # Rating text
            val = f"{score:.1f}"
            tw = draw.textlength(val, font=cfont)
            draw.text((x1 + (chip_w - tw)/2, y1 + 8), val, font=cfont, fill=text_color)

        # after finishing all eps of season
        chips_y = base_y + min(len(ratings), max_eps_per_col) * (chip_h + row_gap) + season_gap

    # Export
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    return out_path
