from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "work" / "kenney_animals" / "extracted" / "PNG" / "Round (outline)"
OUT = ROOT / "outputs" / "assets"

ANIMALS = [
    "bear", "buffalo", "chick", "chicken", "cow", "crocodile", "dog", "duck",
    "elephant", "frog", "giraffe", "goat", "gorilla", "hippo", "horse",
    "monkey", "moose", "narwhal", "owl", "panda", "parrot", "penguin",
    "pig", "rabbit", "rhino", "sloth", "snake", "walrus", "whale", "zebra",
]
DIRECTIONS = ("front", "back", "left", "right")
MODES = ("idle", "run", "attack")


def trim(img):
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def fit_base(img):
    img = trim(img.convert("RGBA"))
    scale = min(34 / img.width, 34 / img.height)
    img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", (42, 42), (0, 0, 0, 0))
    canvas.alpha_composite(img, ((42 - img.width) // 2, 42 - img.height - 3))
    return canvas


def shifted(img, dx=0, dy=0, angle=0):
    frame = Image.new("RGBA", (42, 42), (0, 0, 0, 0))
    work = img.rotate(angle, resample=Image.BICUBIC, expand=False)
    frame.alpha_composite(work, (dx, dy))
    return frame


def make_frames(base, direction, mode):
    flip = direction == "left"
    img = base.transpose(Image.FLIP_LEFT_RIGHT) if flip else base
    if direction == "back":
        img = img.point(lambda p: p)
        overlay = Image.new("RGBA", img.size, (34, 45, 52, 0))
        px = overlay.load()
        for y in range(0, 17):
            for x in range(42):
                px[x, y] = (32, 45, 54, 54)
        img = Image.alpha_composite(img, overlay)

    if mode == "idle":
        steps = [(0, 0, 0), (0, -1, 0), (0, 0, 0), (0, 1, 0)]
    elif mode == "run":
        lean = -5 if direction == "left" else 5 if direction == "right" else 0
        steps = [(-1, 0, -lean), (0, -3, 0), (1, 0, lean), (0, 1, 0)]
    else:
        lunge = {"front": (0, 4), "back": (0, -4), "left": (-5, 0), "right": (5, 0)}[direction]
        steps = [(0, 0, 0), (*lunge, 0), (lunge[0] * 2, lunge[1] * 2, 0), (0, 0, 0)]
    return [shifted(img, dx, dy, angle) for dx, dy, angle in steps]


def main():
    for animal in ANIMALS:
        src = SRC / f"{animal}.png"
        base = fit_base(Image.open(src))
        folder = OUT / f"kenney_{animal}"
        folder.mkdir(parents=True, exist_ok=True)
        for mode in MODES:
            for direction in DIRECTIONS:
                for i, frame in enumerate(make_frames(base, direction, mode)):
                    frame.save(folder / f"{mode}_{direction}_frame_{i}.png")


if __name__ == "__main__":
    main()
