from pathlib import Path
from PIL import Image, ImageSequence
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "assets" / "plants"
KARS = ROOT / "work" / "plants" / "karsiori" / "Pixel Art Spruce Tree Pack"
TAY = ROOT / "work" / "plants" / "tayziulei" / "Flowers and small plants pack" / "Flowers and small plants pack"
SHAADE = ROOT / "work" / "plants" / "shaade" / "Plants"
KARS_BUSH = ROOT / "work" / "plants" / "karsiori_bush" / "Pixel Art Bush Pack"
KETTO = ROOT / "work" / "plants" / "kettoman_farm" / "Pixel Farming Base Pack"
SPROUT = ROOT / "work" / "plants" / "sproutlands" / "basic" / "Sprout Lands - Sprites - Basic pack"

NEAREST = getattr(Image, "Resampling", Image).NEAREST
LANCZOS = getattr(Image, "Resampling", Image).LANCZOS


def safe(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def fit(img, box_w, box_h, resample=NEAREST):
    img = img.convert("RGBA")
    bbox = img.getbbox()
    if not bbox:
        return Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    crop = img.crop(bbox)
    scale = min(box_w / crop.width, box_h / crop.height)
    crop = crop.resize((max(1, round(crop.width * scale)), max(1, round(crop.height * scale))), resample)
    canvas = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    canvas.alpha_composite(crop, ((box_w - crop.width) // 2, box_h - crop.height))
    return canvas


def write_frames(name, frames, box_w, box_h, fps, label):
    folder = OUT / name
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("frame_*.png"):
        old.unlink()
    for i, frame in enumerate(frames):
        frame.save(folder / f"frame_{i}.png")
    return (name, label, len(frames), fps, box_w, box_h)


def bush_frames(name, label, path, box_w=54, box_h=42):
    src = fit(Image.open(path), box_w, box_h)
    frames = []
    for dx, dy in ((0, 0), (1, -1), (0, 0), (-1, -1), (0, 0), (-1, 0), (0, 0), (1, 0)):
        canvas = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
        canvas.alpha_composite(src, (dx, dy))
        frames.append(canvas)
    return write_frames(name, frames, box_w, box_h, 6, label)


def crop_frames(name, label, row, box=32):
    sheet = Image.open(KETTO / "Crops" / "spring-crops.png").convert("RGBA")
    frames = []
    for col in range(8):
        tile = sheet.crop((col * 16, row * 16, col * 16 + 16, row * 16 + 16))
        frames.append(fit(tile, box, box))
    return write_frames(name, frames, box, box, 3, label)


def sprout_static(name, label, rel_path, crop_box, box_w, box_h):
    sheet = Image.open(SPROUT / rel_path).convert("RGBA")
    frame = fit(sheet.crop(crop_box), box_w, box_h)
    return write_frames(name, [frame], box_w, box_h, 1, label)


def sprout_whole_sway(name, label, rel_path, crop_box, box_w, box_h):
    sheet = Image.open(SPROUT / rel_path).convert("RGBA")
    src = fit(sheet.crop(crop_box), box_w, box_h)
    frames = []
    for dx, dy in ((0, 0), (1, -1), (1, 0), (0, 0), (-1, -1), (-1, 0), (0, 0), (0, 0)):
        canvas = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
        canvas.alpha_composite(src, (dx, dy))
        frames.append(canvas)
    return write_frames(name, frames, box_w, box_h, 5, label)


def sprout_leaf_sway_tree(name, label, rel_path, crop_box, box_w, box_h, trunk_y):
    sheet = Image.open(SPROUT / rel_path).convert("RGBA")
    src = fit(sheet.crop(crop_box), box_w, box_h)
    frames = []
    for dx, squash in ((0, 0), (1, 0), (1, 2), (0, 0), (-1, 2), (-1, 0), (0, 0), (0, 0)):
        canopy = src.crop((0, 0, box_w, trunk_y))
        trunk = src.crop((0, trunk_y, box_w, box_h))
        canvas = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
        if squash:
            canopy = canopy.resize((box_w - squash, canopy.height), NEAREST)
            x = (box_w - canopy.width) // 2 + dx
        else:
            x = dx
        canvas.alpha_composite(canopy, (x, 0))
        canvas.alpha_composite(trunk, (0, trunk_y))
        frames.append(canvas)
    return write_frames(name, frames, box_w, box_h, 7, label)


def sprout_sequence(name, label, rel_path, crop_boxes, box=34, fps=3):
    sheet = Image.open(SPROUT / rel_path).convert("RGBA")
    frames = [fit(sheet.crop(crop_box), box, box) for crop_box in crop_boxes]
    return write_frames(name, frames, box, box, fps, label)


def write_sprout_soil():
    sheet = Image.open(SPROUT / "Tilesets/Tilled_Dirt.png").convert("RGBA")
    sheet.crop((0, 0, 16, 16)).save(OUT / "farm_soil.png")


def karsiori_frames(tree_type, color, limit=12):
    folder = KARS / tree_type / color / "Sprites"
    paths = sorted(folder.glob("*.png"), key=lambda p: int(re.search(r"(\d+)\.png$", p.name).group(1)))
    paths = paths[:limit]
    sample = Image.open(paths[0]).convert("RGBA")
    box_w = max(40, min(86, sample.width))
    box_h = max(54, min(118, sample.height))
    frames = [fit(Image.open(p), box_w, box_h) for p in paths]
    name = "plant_" + safe(f"{tree_type}_{color}")
    label = f"{tree_type} {color.title().replace('_', ' ')}"
    return write_frames(name, frames, box_w, box_h, 9, label)


def gif_frames(name, label, path, box=48, limit=12):
    im = Image.open(path)
    frames = []
    for frame in ImageSequence.Iterator(im):
        frames.append(fit(frame.convert("RGBA"), box, box, LANCZOS))
        if len(frames) >= limit:
            break
    return write_frames(name, frames, box, box, 7, label)


def static_sway_frames(name, label, path, box=42):
    src = fit(Image.open(path), box, box, LANCZOS)
    frames = []
    for dx in (0, 1, 0, -1, 0, -1, 0, 1):
        canvas = Image.new("RGBA", (box, box), (0, 0, 0, 0))
        canvas.alpha_composite(src, (dx, 0))
        frames.append(canvas)
    return write_frames(name, frames, box, box, 6, label)


def main():
    write_sprout_soil()
    objects = "Objects/Basic_Grass_Biom_things.png"
    plants = "Objects/Basic_Plants.png"
    manifest = [
        karsiori_frames("Tiny Spruce Tree", "GREEN"),
        karsiori_frames("Spruce Tree", "GREEN_TEAL"),
        karsiori_frames("Bubble Pine Tree", "GREEN"),
        karsiori_frames("Pico Pine Tree", "TEAL"),
        karsiori_frames("Small Pine Tree", "GREEN"),
        karsiori_frames("Triangle Spruce Tree", "YELLOW"),
        karsiori_frames("Slim Spruce Tree", "COLD"),
        karsiori_frames("Thick Spruce Tree", "GREEN_TEAL"),
        static_sway_frames("plant_shaade_leafy", "Leafy Plant", SHAADE / "Plant1.png", 44),
        static_sway_frames("plant_shaade_bush", "Round Plant", SHAADE / "Plant2.png", 44),
        static_sway_frames("plant_shaade_sapling", "Sapling Plant", SHAADE / "Plant3.png", 44),
        gif_frames("plant_flower_blue_glow", "Blue Glow Flower", TAY / "Flowers 6" / "Flowers 6.gif"),
        bush_frames("plant_box_bush_green", "Boxy Bush Green", KARS_BUSH / "Bush 3" / "Bush 3_GREEN.png", 70, 42),
        bush_frames("plant_box_bush_teal", "Boxy Bush Teal", KARS_BUSH / "Bush 1" / "Bush 1_TEAL.png", 64, 42),
        bush_frames("plant_round_bush_yellowish", "Round Bush Yellowish", KARS_BUSH / "Bush 8" / "Bush 8_YELLOWISH GREEN.png", 48, 42),
        bush_frames("plant_low_bush_green", "Low Bush Green", KARS_BUSH / "Bush 5" / "Bush 5_GREEN.png", 84, 36),
        crop_frames("plant_crop_radish", "Radish Crop Stages", 0),
        crop_frames("plant_crop_potato", "Potato Crop Stages", 1),
        crop_frames("plant_crop_strawberry", "Strawberry Crop Stages", 2),
        crop_frames("plant_crop_tree", "Tree Crop Stages", 3),
        sprout_leaf_sway_tree("plant_sprout_tall_box_tree", "Sprout Lands Tall Box Tree", objects, (0, 0, 16, 32), 40, 70, 50),
        sprout_leaf_sway_tree("plant_sprout_round_box_tree", "Sprout Lands Round Box Tree", objects, (16, 0, 48, 32), 66, 66, 50),
        sprout_leaf_sway_tree("plant_sprout_flower_box_tree", "Sprout Lands Flower Box Tree", objects, (48, 0, 80, 32), 66, 66, 50),
        sprout_whole_sway("plant_sprout_cube_berry_bush", "Sprout Lands Cube Berry Bush", objects, (0, 48, 32, 64), 66, 34),
        sprout_whole_sway("plant_sprout_cube_plain_bush", "Sprout Lands Cube Bush", objects, (16, 48, 48, 64), 66, 34),
        sprout_whole_sway("plant_sprout_blue_box_flower", "Sprout Lands Blue Box Flower", objects, (80, 48, 96, 64), 34, 34),
        sprout_whole_sway("plant_sprout_pink_box_flower", "Sprout Lands Pink Box Flower", objects, (96, 48, 112, 64), 34, 34),
        sprout_whole_sway("plant_sprout_sunflower", "Sprout Lands Sunflower", objects, (128, 32, 144, 64), 40, 68),
        sprout_sequence(
            "plant_sprout_wheat_growth",
            "Sprout Lands Wheat Growth",
            plants,
            [(16, 0, 32, 16), (32, 0, 48, 16), (48, 0, 64, 16), (64, 0, 80, 16)],
            34,
            3,
        ),
        sprout_sequence(
            "plant_sprout_radish_growth",
            "Sprout Lands Radish Growth",
            plants,
            [(16, 16, 32, 32), (32, 16, 48, 32), (48, 16, 64, 32), (64, 16, 80, 32), (80, 16, 96, 32)],
            34,
            3,
        ),
    ]
    (ROOT / "work" / "plants" / "manifest.tsv").write_text(
        "\n".join("\t".join(map(str, row)) for row in manifest) + "\n"
    )
    print(f"built {len(manifest)} plant animations")


if __name__ == "__main__":
    main()
