from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "work" / "plants" / "sproutlands" / "basic" / "Sprout Lands - Sprites - Basic pack"
OUT = ROOT / "outputs" / "assets"
PLANTS = OUT / "plants"

NEAREST = getattr(Image, "Resampling", Image).NEAREST
DIRECTIONS = ("front", "back", "left", "right")


def trim(img):
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def place(img, target_w=42, target_h=46, content_w=34, content_h=38):
    img = trim(img.convert("RGBA"))
    scale = min(content_w / img.width, content_h / img.height)
    img = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), NEAREST)
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    canvas.alpha_composite(img, ((target_w - img.width) // 2, target_h - img.height - 2))
    return canvas


def shifted(img, dx, dy):
    canvas = Image.new("RGBA", img.size, (0, 0, 0, 0))
    canvas.alpha_composite(img, (dx, dy))
    return canvas


def save(folder, mode, direction, frames):
    folder.mkdir(parents=True, exist_ok=True)
    for i, frame in enumerate(frames[:4]):
        frame.save(folder / f"{mode}_{direction}_frame_{i}.png")


def build_cat():
    sheet = Image.open(SRC / "Characters" / "Basic Charakter Spritesheet.png").convert("RGBA")
    actions = Image.open(SRC / "Characters" / "Basic Charakter Actions.png").convert("RGBA")
    folder = OUT / "sprout_cat"
    # Sheet is 4 columns by 4 rows at 48px cells: down, up, side-left, side-right.
    row_for = {"front": 0, "back": 1, "left": 2, "right": 3}
    for direction, row in row_for.items():
        base = [
            place(sheet.crop((col * 48, row * 48, col * 48 + 48, row * 48 + 48)))
            for col in range(4)
        ]
        idle = [base[0], shifted(base[0], 0, -1), base[0], shifted(base[0], 0, -1)]
        run = [base[i] for i in (0, 1, 2, 3)]
        # Use matching rows from the actions sheet when possible, otherwise nudge the idle frame.
        action_row = {"front": 0, "back": 1, "left": 2, "right": 3}[direction]
        action_source = [actions.crop((col * 48, action_row * 48, col * 48 + 48, action_row * 48 + 48)) for col in range(2)]
        attack = [place(action_source[i % 2], content_w=38, content_h=40) for i in range(4)]
        save(folder, "idle", direction, idle)
        save(folder, "run", direction, run)
        save(folder, "attack", direction, attack)


def build_chicken():
    sheet = Image.open(SRC / "Characters" / "Free Chicken Sprites.png").convert("RGBA")
    folder = OUT / "sprout_chicken"
    front = [place(sheet.crop((col * 16, 16, col * 16 + 16, 32)), target_w=34, target_h=34, content_w=28, content_h=28) for col in range(4)]
    back = [place(sheet.crop((col * 16, 0, col * 16 + 16, 16)), target_w=34, target_h=34, content_w=28, content_h=28) for col in range(2)]
    side = [front[i] for i in (1, 2, 3, 2)]
    frames = {
        "front": front,
        "back": [back[i % 2] for i in range(4)],
        "right": side,
        "left": [f.transpose(Image.FLIP_LEFT_RIGHT) for f in side],
    }
    for direction in DIRECTIONS:
        run = frames[direction]
        idle = [run[0], shifted(run[0], 0, -1), run[0], shifted(run[0], 0, -1)]
        attack = [run[0], shifted(run[1], 0, -2), run[2], run[0]]
        save(folder, "idle", direction, idle)
        save(folder, "run", direction, run)
        save(folder, "attack", direction, attack)


def build_cow():
    sheet = Image.open(SRC / "Characters" / "Free Cow Sprites.png").convert("RGBA")
    folder = OUT / "sprout_cow"
    side = [place(sheet.crop((col * 32, 0, col * 32 + 32, 32)), target_w=54, target_h=42, content_w=50, content_h=36) for col in range(3)]
    front = [place(sheet.crop((col * 32, 32, col * 32 + 32, 64)), target_w=54, target_h=42, content_w=50, content_h=36) for col in range(2)]
    frames = {
        "right": [side[i] for i in (0, 1, 2, 1)],
        "left": [side[i].transpose(Image.FLIP_LEFT_RIGHT) for i in (0, 1, 2, 1)],
        "front": [front[i % 2] for i in range(4)],
        "back": [front[i % 2] for i in (1, 0, 1, 0)],
    }
    for direction in DIRECTIONS:
        run = frames[direction]
        idle = [run[0], shifted(run[0], 0, -1), run[0], shifted(run[0], 0, -1)]
        attack = [run[0], shifted(run[1], 0, -2), run[2], run[0]]
        save(folder, "idle", direction, idle)
        save(folder, "run", direction, run)
        save(folder, "attack", direction, attack)


def write_prop(name, rel_path, box, out_w, out_h):
    sheet = Image.open(SRC / rel_path).convert("RGBA")
    img = place(sheet.crop(box), target_w=out_w, target_h=out_h, content_w=out_w - 2, content_h=out_h - 2)
    folder = PLANTS / name
    folder.mkdir(parents=True, exist_ok=True)
    img.save(folder / "frame_0.png")


def build_props():
    write_prop("prop_sprout_chicken_house", "Objects/Free_Chicken_House.png", (0, 0, 48, 48), 88, 88)
    write_prop("prop_sprout_nest", "Characters/Egg_And_Nest.png", (48, 0, 64, 16), 34, 30)
    write_prop("prop_sprout_egg", "Characters/Egg_And_Nest.png", (0, 0, 16, 16), 26, 28)
    write_prop("prop_sprout_chest", "Objects/Chest.png", (32, 0, 48, 16), 36, 34)
    write_prop("prop_sprout_seed_wheat", "Objects/Basic_Plants.png", (0, 0, 16, 16), 32, 32)
    write_prop("prop_sprout_seed_radish", "Objects/Basic_Plants.png", (0, 16, 16, 32), 32, 32)
    write_prop("prop_sprout_wheat_item", "Objects/Basic_Plants.png", (80, 0, 96, 16), 34, 34)
    write_prop("prop_sprout_radish_item", "Objects/Basic_Plants.png", (80, 16, 96, 32), 34, 34)
    write_prop("prop_sprout_apple", "Objects/Basic_Grass_Biom_things.png", (32, 32, 48, 48), 32, 32)
    write_prop("prop_sprout_big_apple", "Objects/Basic_Grass_Biom_things.png", (48, 32, 64, 48), 36, 36)
    write_prop("prop_sprout_chopped_log", "Objects/Basic_Grass_Biom_things.png", (80, 32, 112, 48), 54, 34)
    write_prop("prop_sprout_pink_mushrooms", "Objects/Basic_Grass_Biom_things.png", (80, 0, 96, 16), 36, 34)
    write_prop("prop_sprout_round_mushroom", "Objects/Basic_Grass_Biom_things.png", (96, 0, 112, 16), 34, 34)
    write_prop("prop_sprout_purple_mushroom", "Objects/Basic_Grass_Biom_things.png", (128, 0, 144, 16), 34, 34)
    write_prop("prop_sprout_blue_flower", "Objects/Basic_Grass_Biom_things.png", (80, 48, 96, 64), 34, 34)
    write_prop("prop_sprout_rose_flower", "Objects/Basic_Grass_Biom_things.png", (96, 48, 112, 64), 34, 34)
    write_prop("prop_sprout_tiny_rock", "Objects/Basic_Grass_Biom_things.png", (112, 64, 128, 80), 32, 28)
    write_prop("prop_sprout_big_rock", "Objects/Basic_Grass_Biom_things.png", (80, 64, 112, 80), 44, 32)
    write_prop("prop_sprout_lily_pad", "Objects/Basic_Grass_Biom_things.png", (112, 48, 144, 80), 46, 36)
    write_prop("prop_sprout_grass_clover", "Objects/Basic_Grass_Biom_things.png", (80, 16, 112, 32), 46, 30)
    write_prop("prop_sprout_small_fruit", "Objects/Basic_Grass_Biom_things.png", (0, 32, 16, 48), 28, 28)
    write_prop("prop_sprout_yellow_flower_small", "Objects/Basic_Grass_Biom_things.png", (96, 32, 112, 48), 32, 30)
    write_prop("prop_sprout_yellow_flower_large", "Objects/Basic_Grass_Biom_things.png", (112, 32, 128, 48), 34, 32)
    write_prop("prop_sprout_rock_pile", "Objects/Basic_Grass_Biom_things.png", (112, 16, 144, 32), 48, 34)
    write_prop("prop_sprout_fallen_log_left", "Objects/Basic_Grass_Biom_things.png", (0, 64, 32, 80), 54, 32)
    write_prop("prop_sprout_fallen_log_big", "Objects/Basic_Grass_Biom_things.png", (32, 64, 80, 80), 70, 34)
    write_prop("prop_sprout_path_tiles", "Objects/Paths.png", (0, 0, 64, 64), 78, 78)
    write_prop("prop_sprout_bridge", "Objects/Wood_Bridge.png", (0, 0, 80, 48), 100, 64)
    write_prop("prop_sprout_fence_set", "Tilesets/Fences.png", (0, 0, 64, 64), 82, 82)
    write_prop("prop_sprout_house", "Tilesets/Wooden House.png", (0, 0, 112, 80), 128, 96)
    write_prop("prop_sprout_door_set", "Tilesets/Doors.png", (0, 0, 16, 64), 28, 84)
    write_prop("prop_sprout_materials", "Objects/Basic_tools_and_meterials.png", (0, 0, 48, 32), 72, 48)
    write_prop("prop_sprout_tools", "Characters/Tools.png", (0, 0, 96, 96), 98, 98)
    write_prop("prop_sprout_furniture_top", "Objects/Basic_Furniture.png", (0, 0, 144, 32), 128, 48)
    write_prop("prop_sprout_beds", "Objects/Basic_Furniture.png", (0, 32, 64, 64), 96, 56)
    write_prop("prop_sprout_tables", "Objects/Basic_Furniture.png", (64, 32, 144, 64), 104, 56)
    write_prop("prop_sprout_rugs", "Objects/Basic_Furniture.png", (0, 80, 144, 96), 128, 34)


def main():
    build_cat()
    build_chicken()
    build_cow()
    build_props()
    print("built Sprout Lands cat, chicken, cow, and expanded props")


if __name__ == "__main__":
    main()
