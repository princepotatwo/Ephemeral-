from pathlib import Path
from PIL import Image
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "assets"
PIPOYA = ROOT / "work" / "pipoya" / "pipoya32" / "PIPOYA FREE RPG Character Sprites 32x32"
NEKONIN = ROOT / "work" / "pipoya" / "nekonin" / "PIPOYA FREE RPG Character Sprites NEKONIN"

# PIPOYA chara sheets are down, left, right, up.
ROW_TO_DIR = {0: "front", 1: "left", 2: "right", 3: "back"}
FRAME_ORDER = [0, 1, 2, 1]


def trim(img):
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def fit(img, scale, anchor):
    img = img.convert("RGBA")
    img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.NEAREST)
    canvas = Image.new("RGBA", (48, 54), (0, 0, 0, 0))
    x = round(24 - anchor[0] * scale)
    y = round(52 - anchor[1] * scale)
    canvas.alpha_composite(img, (x, y))
    return canvas


def shifted(img, dx, dy):
    canvas = Image.new("RGBA", img.size, (0, 0, 0, 0))
    canvas.alpha_composite(img, (dx, dy))
    return canvas


def export_sheet(src, out_name):
    sheet = Image.open(src).convert("RGBA")
    folder = OUT / out_name
    folder.mkdir(parents=True, exist_ok=True)
    boxes = []
    for row in range(4):
        for col in range(3):
            crop = sheet.crop((col * 32, row * 32, col * 32 + 32, row * 32 + 32))
            bbox = crop.getbbox()
            if bbox:
                boxes.append(bbox)
    left = min(box[0] for box in boxes)
    top = min(box[1] for box in boxes)
    right = max(box[2] for box in boxes)
    bottom = max(box[3] for box in boxes)
    content_w = right - left
    content_h = bottom - top
    scale = min(40 / content_w, 46 / content_h)
    anchor = ((left + right) / 2, bottom)

    for row, direction in ROW_TO_DIR.items():
        source_frames = [
            fit(sheet.crop((col * 32, row * 32, col * 32 + 32, row * 32 + 32)), scale, anchor)
            for col in range(3)
        ]
        for i, col in enumerate(FRAME_ORDER):
            run = source_frames[col]
            idle = source_frames[1]
            folder.joinpath(f"run_{direction}_frame_{i}.png").write_bytes(to_bytes(run))
            folder.joinpath(f"idle_{direction}_frame_{i}.png").write_bytes(to_bytes(idle if i % 2 == 0 else shifted(idle, 0, -1)))

            lx, ly = {"front": (0, 5), "back": (0, -5), "left": (-5, 0), "right": (5, 0)}[direction]
            attack = [idle, shifted(idle, lx, ly), shifted(idle, lx * 2, ly * 2), idle][i]
            folder.joinpath(f"attack_{direction}_frame_{i}.png").write_bytes(to_bytes(attack))


def to_bytes(img):
    from io import BytesIO
    b = BytesIO()
    img.save(b, format="PNG")
    return b.getvalue()


def safe_name(prefix, path):
    stem = path.stem.lower()
    stem = stem.replace("fmale", "female")
    stem = re.sub(r"[^a-z0-9]+", "_", stem).strip("_")
    return f"{prefix}_{stem}"


def main():
    files = []
    uniform = PIPOYA / "Japanese school characters" / "school uniform 1"
    teachers = PIPOYA / "Japanese school characters" / "teachers"
    xmas = PIPOYA / "Xmas"

    files.extend(("pipoya", p) for p in sorted(uniform.glob("*.png")))
    files.extend(("pipoya", p) for p in sorted(teachers.glob("*.png")))
    files.extend(("pipoya", p) for p in sorted(xmas.glob("*.png")))
    files.extend(("nekonin", p) for p in sorted(NEKONIN.glob("*.png")))

    manifest = []
    for prefix, path in files:
        out_name = safe_name(prefix, path)
        export_sheet(path, out_name)
        label = path.stem.replace("fmale", "female").replace("pipo-", "").replace("-", " ").title()
        manifest.append((out_name, label))

    (ROOT / "work" / "pipoya" / "manifest.tsv").write_text(
        "\n".join(f"{name}\t{label}" for name, label in manifest) + "\n"
    )


if __name__ == "__main__":
    main()
