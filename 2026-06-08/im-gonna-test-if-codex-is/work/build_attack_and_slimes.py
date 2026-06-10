from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "assets"
SLIME_SRC = ROOT / "work" / "slime_assets"
DIRECTIONS = ("front", "back", "left", "right")
ANIMALS = ("fox", "frog", "owl", "doe", "squirle", "bunny", "chicken", "turtle", "cow", "sheep", "pig")


def offset_for(direction, amount):
    return {
        "front": (0, amount),
        "back": (0, -amount),
        "left": (-amount, 0),
        "right": (amount, 0),
    }[direction]


def draw_impact(img, direction):
    px = img.load()
    color = (255, 244, 166, 205)
    w, h = img.size
    points = {
        "front": [(w // 2 - 8, h - 5), (w // 2, h - 1), (w // 2 + 8, h - 5)],
        "back": [(w // 2 - 8, 4), (w // 2, 0), (w // 2 + 8, 4)],
        "left": [(4, h // 2 - 6), (0, h // 2), (4, h // 2 + 6)],
        "right": [(w - 5, h // 2 - 6), (w - 1, h // 2), (w - 5, h // 2 + 6)],
    }[direction]
    for x, y in points:
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                xx, yy = x + dx, y + dy
                if 0 <= xx < w and 0 <= yy < h:
                    px[xx, yy] = color


def make_attack_for_animal(animal):
    folder = OUT / animal
    for direction in DIRECTIONS:
        srcs = [
            folder / f"run_{direction}_frame_0.png",
            folder / f"run_{direction}_frame_1.png",
            folder / f"run_{direction}_frame_2.png",
            folder / f"run_{direction}_frame_1.png",
        ]
        for frame, src in enumerate(srcs):
            base = Image.open(src).convert("RGBA")
            canvas = Image.new("RGBA", base.size, (0, 0, 0, 0))
            ox, oy = offset_for(direction, [0, 2, 5, 1][frame])
            canvas.alpha_composite(base, (ox, oy))
            if frame == 2:
                draw_impact(canvas, direction)
            canvas.save(folder / f"attack_{direction}_frame_{frame}.png")


def tint(img, color):
    alpha = img.getchannel("A")
    gray = ImageOps.grayscale(img)
    tinted = ImageOps.colorize(gray, black=(20, 24, 22), white=color).convert("RGBA")
    tinted.putalpha(alpha)
    return tinted


def recolor_slime(img, primary, secondary=None, split=False, invert=False):
    if invert:
        out = ImageOps.invert(img.convert("RGB")).convert("RGBA")
        out.putalpha(img.getchannel("A"))
        return out
    colored = tint(img, primary)
    if not split or not secondary:
        return colored

    alt = tint(img, secondary)
    out = colored.copy()
    px = out.load()
    alt_px = alt.load()
    for y in range(out.height):
        for x in range(out.width // 2, out.width):
            if alt_px[x, y][3]:
                px[x, y] = alt_px[x, y]
    return out


def resized(body, sx, sy):
    return body.resize((max(1, round(body.width * sx)), max(1, round(body.height * sy))), Image.NEAREST)


def paste_center(canvas, body, cx, bottom):
    canvas.alpha_composite(body, (round(cx - body.width / 2), round(bottom - body.height)))


def draw_crown(draw, x, y):
    gold = (255, 214, 82, 255)
    edge = (118, 80, 32, 255)
    draw.rectangle((x + 1, y + 8, x + 17, y + 12), fill=gold, outline=edge)
    draw.polygon([(x + 1, y + 8), (x + 4, y), (x + 8, y + 8)], fill=gold, outline=edge)
    draw.polygon([(x + 6, y + 8), (x + 10, y + 1), (x + 14, y + 8)], fill=gold, outline=edge)
    draw.polygon([(x + 11, y + 8), (x + 16, y + 2), (x + 17, y + 8)], fill=gold, outline=edge)


def draw_horns(draw, x, y):
    horn = (236, 228, 210, 255)
    edge = (68, 58, 62, 255)
    draw.polygon([(x, y + 9), (x + 5, y), (x + 8, y + 11)], fill=horn, outline=edge)
    draw.polygon([(x + 32, y + 11), (x + 35, y), (x + 40, y + 9)], fill=horn, outline=edge)


def draw_halo(draw, x, y):
    draw.ellipse((x, y, x + 30, y + 8), outline=(255, 238, 125, 230), width=2)


def draw_bow(draw, x, y):
    pink = (255, 112, 188, 255)
    edge = (92, 46, 78, 255)
    draw.polygon([(x, y + 4), (x + 8, y), (x + 8, y + 9)], fill=pink, outline=edge)
    draw.polygon([(x + 18, y + 4), (x + 10, y), (x + 10, y + 9)], fill=pink, outline=edge)
    draw.rectangle((x + 8, y + 3, x + 10, y + 6), fill=(255, 221, 232, 255), outline=edge)


def draw_stars(draw, frame):
    pts = [(12, 16), (48, 13), (52, 35), (9, 39)]
    for i, (x, y) in enumerate(pts):
        if (frame + i) % 2:
            draw.point((x, y), fill=(255, 245, 166, 245))
            draw.point((x + 1, y), fill=(255, 245, 166, 245))
            draw.point((x, y + 1), fill=(255, 245, 166, 245))


def draw_attack_burst(draw, direction, frame):
    if frame != 2:
        return
    color = (255, 245, 145, 230)
    if direction == "front":
        pts = [(30, 48), (24, 56), (36, 56), (20, 50), (40, 50)]
    elif direction == "back":
        pts = [(30, 12), (24, 4), (36, 4), (20, 10), (40, 10)]
    elif direction == "left":
        pts = [(12, 32), (4, 25), (4, 39), (10, 20), (10, 44)]
    else:
        pts = [(52, 32), (60, 25), (60, 39), (54, 20), (54, 44)]
    for x, y in pts:
        draw.line((30, 32, x, y), fill=color, width=2)


def decorate(canvas, variant, frame, mode, direction):
    draw = ImageDraw.Draw(canvas)
    if variant.get("stars"):
        draw_stars(draw, frame)
    if variant.get("halo"):
        draw_halo(draw, 17, 7)
    if variant.get("crown"):
        draw_crown(draw, 23, 6)
    if variant.get("horns"):
        draw_horns(draw, 12, 8)
    if variant.get("bow"):
        draw_bow(draw, 36, 13)
    if mode == "attack":
        draw_attack_burst(draw, direction, frame)
        if frame >= 1:
            drops = {
                "front": [(20, 50), (45, 47)],
                "back": [(21, 16), (43, 14)],
                "left": [(15, 24), (13, 39)],
                "right": [(49, 24), (51, 39)],
            }[direction]
            for x, y in drops:
                draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=variant["drop"])


def slime_frame(base, variant, mode, direction, frame):
    body = recolor_slime(base, variant["primary"], variant.get("secondary"), variant.get("split"), variant.get("invert"))
    huge = variant.get("huge", 1)
    if mode == "attack":
        sx, sy = [(1.0, .82), (1.18, .72), (1.42, .6), (.94, 1.18)][frame]
        ox, oy = {
            "front": (0, [0, 2, 6, 1][frame]),
            "back": (0, [0, -2, -6, -1][frame]),
            "left": ([0, -3, -8, -1][frame], 0),
            "right": ([0, 3, 8, 1][frame], 0),
        }[direction]
    elif mode == "run":
        sx, sy = [(1.05, .9), (.94, 1.1), (1.08, .86), (.98, 1.04)][frame]
        ox, oy = {
            "front": (0, [0, 1, 2, 1][frame]),
            "back": (0, [0, -1, -2, -1][frame]),
            "left": ([-1, -2, -3, -2][frame], 0),
            "right": ([1, 2, 3, 2][frame], 0),
        }[direction]
    else:
        sx, sy = [(1, 1), (1.04, .94), (1, 1.04), (.96, 1)][frame]
        ox, oy = (0, [0, 1, 0, -1][frame])

    body = resized(body, sx * huge, sy * huge)
    canvas = Image.new("RGBA", (64, 58), (0, 0, 0, 0))
    paste_center(canvas, body, 32 + ox, 50 + oy)
    decorate(canvas, variant, frame, mode, direction)
    return canvas


SLIME_VARIANTS = {
    "green_slime": {"primary": (78, 228, 55), "drop": (78, 228, 55, 235)},
    "blue_slime": {"primary": (105, 204, 255), "drop": (105, 204, 255, 235)},
    "pink_slime": {"primary": (255, 124, 198), "drop": (255, 124, 198, 235), "bow": True},
    "split_slime": {"primary": (86, 236, 95), "secondary": (105, 204, 255), "split": True, "drop": (160, 232, 190, 235)},
    "gold_slime": {"primary": (255, 211, 70), "drop": (255, 218, 90, 235), "crown": True},
    "shadow_slime": {"primary": (70, 60, 90), "drop": (145, 120, 200, 235), "invert": True, "horns": True},
    "galaxy_slime": {"primary": (126, 89, 255), "secondary": (70, 230, 255), "split": True, "drop": (150, 120, 255, 235), "halo": True, "stars": True},
    "huge_split_slime": {"primary": (255, 222, 70), "secondary": (165, 88, 255), "split": True, "drop": (255, 190, 110, 235), "crown": True, "huge": 1.24},
}


def save_slimes(sheet_name):
    src = Image.open(SLIME_SRC / sheet_name).convert("RGBA")
    base_frames = [src.crop((i * 36, row * 32, (i + 1) * 36, (row + 1) * 32)) for row in range(2) for i in range(10)]
    frame_sets = {
        "idle": [0, 1, 2, 3],
        "run": [4, 5, 6, 7],
        "attack": [8, 9, 18, 19],
    }
    for name, variant in SLIME_VARIANTS.items():
        folder = OUT / name
        folder.mkdir(parents=True, exist_ok=True)
        for mode, indexes in frame_sets.items():
            for direction in DIRECTIONS:
                for frame, idx in enumerate(indexes):
                    slime_frame(base_frames[idx], variant, mode, direction, frame).save(folder / f"{mode}_{direction}_frame_{frame}.png")
def main():
    for animal in ANIMALS:
        make_attack_for_animal(animal)
    save_slimes("greenslime_spritesheet_36x32.png")


if __name__ == "__main__":
    main()
