from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "assets"

AXULART_SHEET = ROOT / "work" / "axulart" / "extracted" / "Small-8-Direction-Characters_by_AxulArt" / "Small-8-Direction-Characters_by_AxulArt.png"
RGS_ROOT = ROOT / "work" / "rgs" / "extracted" / "Square characters animated 8 directions top down free cc0" / "Sprites"

DIRECTIONS = ("front", "back", "left", "right")
NEAREST = getattr(Image, "Resampling", Image).NEAREST
LANCZOS = getattr(Image, "Resampling", Image).LANCZOS


def to_bytes(img):
    from io import BytesIO

    b = BytesIO()
    img.save(b, format="PNG")
    return b.getvalue()


def place(img, target_w=48, target_h=54, content_w=42, content_h=48, resample=NEAREST):
    img = img.convert("RGBA")
    bbox = img.getbbox()
    if not bbox:
        return Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    crop = img.crop(bbox)
    scale = min(content_w / crop.width, content_h / crop.height)
    crop = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), resample)
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    canvas.alpha_composite(crop, ((target_w - crop.width) // 2, target_h - crop.height - 2))
    return canvas


def shifted(img, dx, dy):
    canvas = Image.new("RGBA", img.size, (0, 0, 0, 0))
    canvas.alpha_composite(img, (dx, dy))
    return canvas


def write_frames(folder, mode, direction, frames):
    folder.mkdir(parents=True, exist_ok=True)
    for i, frame in enumerate(frames[:4]):
        folder.joinpath(f"{mode}_{direction}_frame_{i}.png").write_bytes(to_bytes(frame))


def build_axulart():
    sheet = Image.open(AXULART_SHEET).convert("RGBA")
    # AxulArt sheet: columns are UL-ish 8 directions, rows are arrow + 3 walk frames per character.
    col_for_dir = {"back": 0, "right": 2, "front": 4, "left": 6}
    chars = [
        ("axulart_blue_girl", "Axul Blue Girl", 1),
        ("axulart_cap_boy", "Axul Cap Boy", 5),
        ("axulart_orange_girl", "Axul Orange Girl", 9),
    ]
    manifest = []
    for name, label, row_start in chars:
        folder = OUT / name
        for direction, col in col_for_dir.items():
            base = [
                sheet.crop((col * 16, (row_start + row) * 24, col * 16 + 16, (row_start + row) * 24 + 24))
                for row in range(3)
            ]
            run = [place(base[i], content_w=34, content_h=46) for i in (0, 1, 2, 1)]
            idle = [run[1], shifted(run[1], 0, -1), run[1], shifted(run[1], 0, -1)]
            dx, dy = {"front": (0, 5), "back": (0, -5), "left": (-5, 0), "right": (5, 0)}[direction]
            attack = [idle[0], shifted(idle[0], dx, dy), shifted(idle[0], dx * 2, dy * 2), idle[0]]
            write_frames(folder, "run", direction, run)
            write_frames(folder, "idle", direction, idle)
            write_frames(folder, "attack", direction, attack)
        manifest.append((name, label))
    return manifest


def rgs_frame(char_dir, anim, direction, number):
    src_dir = {"front": "down", "back": "up", "right": "right", "left": "right"}[direction]
    path = char_dir / f"{anim}_{src_dir} ({number}).png"
    img = Image.open(path).convert("RGBA")
    if direction == "left":
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return place(img, content_w=44, content_h=46, resample=LANCZOS)


def build_rgs():
    chars = [
        ("rgs_base_square", "RGS Base Square", "Base Character"),
        ("rgs_hero_square", "RGS Hero Square", "Hero"),
        ("rgs_skeleton_square", "RGS Skeleton Square", "Skeleton"),
        ("rgs_monster_square", "RGS Monster Square", "Monster"),
    ]
    manifest = []
    for name, label, dirname in chars:
        src = RGS_ROOT / dirname
        folder = OUT / name
        for direction in DIRECTIONS:
            idle = [rgs_frame(src, "idle", direction, i) for i in (1, 2, 3, 4)]
            run = idle
            attack = [rgs_frame(src, "jump", direction, i) for i in (1, 3, 5, 7)]
            write_frames(folder, "idle", direction, idle)
            write_frames(folder, "run", direction, run)
            write_frames(folder, "attack", direction, attack)
        manifest.append((name, label))
    return manifest


def main():
    manifest = build_axulart() + build_rgs()
    (ROOT / "work" / "itch_extra_manifest.tsv").write_text(
        "\n".join(f"{name}\t{label}" for name, label in manifest) + "\n"
    )
    print(f"built {len(manifest)} characters")


if __name__ == "__main__":
    main()
