from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "work" / "online_animals"
OUT = ROOT / "outputs" / "assets"
DIRECTIONS = ("front", "back", "left", "right")


def transparent_keyed(img):
    img = img.convert("RGBA")
    bg = img.getpixel((0, 0))
    if bg[3] == 0:
        return img
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) == bg[:3]:
                px[x, y] = (r, g, b, 0)
    return img


def trim(img):
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img


def fit(img, size, max_size):
    img = trim(img)
    scale = min(max_size[0] / img.width, max_size[1] / img.height)
    resized = img.resize((max(1, round(img.width * scale)), max(1, round(img.height * scale))), Image.NEAREST)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    x = (size[0] - resized.width) // 2
    y = size[1] - resized.height - 1
    canvas.alpha_composite(resized, (x, y))
    return canvas


def save_frame(animal, mode, direction, frame, img, size, max_size):
    folder = OUT / animal
    folder.mkdir(parents=True, exist_ok=True)
    fit(img, size, max_size).save(folder / f"{mode}_{direction}_frame_{frame}.png")


def extract_grid(animal, filename, cell, size, max_size):
    sheet = transparent_keyed(Image.open(SRC / filename))
    rows = {"back": 0, "left": 1, "front": 2, "right": 3}
    for direction in DIRECTIONS:
        row = rows[direction]
        first = None
        for frame in range(4):
            crop = sheet.crop((frame * cell, row * cell, (frame + 1) * cell, (row + 1) * cell))
            if first is None:
                first = crop
            save_frame(animal, "run", direction, frame, crop, size, max_size)
            save_frame(animal, "idle", direction, frame, first, size, max_size)


def bunny_boxes():
    return {
        "back": [(29, 52, 48, 78), (62, 51, 81, 78), (103, 47, 122, 78), (139, 50, 158, 75)],
        "front": [(31, 138, 50, 166), (64, 136, 83, 167), (104, 135, 123, 170), (143, 140, 162, 167)],
        "left": [(28, 218, 53, 245), (59, 216, 85, 244), (91, 217, 124, 245), (134, 218, 163, 243)],
        "right": [(27, 289, 52, 316), (61, 288, 87, 316), (96, 288, 129, 316), (138, 291, 167, 316)],
    }


def extract_bunny():
    sheet = transparent_keyed(Image.open(SRC / "bunny_lpc.png"))
    for direction, boxes in bunny_boxes().items():
        first = None
        for frame, box in enumerate(boxes):
            crop = sheet.crop(box)
            if first is None:
                first = crop
            save_frame("bunny", "run", direction, frame, crop, (42, 42), (36, 36))
            save_frame("bunny", "idle", direction, frame, first, (42, 42), (36, 36))


def main():
    extract_bunny()
    extract_grid("chicken", "chicken_lpc.png", 32, (36, 36), (31, 31))
    extract_grid("turtle", "turtle_16.png", 16, (30, 30), (24, 24))
    extract_grid("cow", "cow_lpc.png", 128, (64, 52), (58, 46))
    extract_grid("sheep", "sheep_lpc.png", 128, (58, 50), (52, 44))
    extract_grid("pig", "pig_lpc.png", 128, (54, 46), (48, 40))


if __name__ == "__main__":
    main()
