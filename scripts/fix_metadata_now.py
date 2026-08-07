#!/usr/bin/env python3
import os
import glob
import json
from PIL import Image

ASSETS_DIR = "/Users/jasminpingol/Codex/assets"
META_PATH = os.path.join(ASSETS_DIR, "spritesheets_metadata.json")

with open(META_PATH, "r") as f:
    meta = json.load(f)

for char_name in ["knight_orange", "knight_green", "knight_blue", "dudu", "dudu_pixel", "dudu_highres", "dudu_outlined", "silksong_pilgrim_hiker", "silksong_hornet"]:
    char_dir = os.path.join(ASSETS_DIR, char_name)
    if not os.path.isdir(char_dir):
        continue
        
    frames = [f for f in glob.glob(os.path.join(char_dir, "*.png")) if not f.endswith("spritesheet.png")]
    if not frames:
        continue
        
    # Get max dimensions among frames (or idle_front)
    max_w, max_h = 0, 0
    for f in frames:
        try:
            w, h = Image.open(f).size
            if w > max_w: max_w = w
            if h > max_h: max_h = h
        except Exception:
            pass
            
    print(f"Fixing {char_name:25s}: Was ({meta[char_name]['frameWidth']}x{meta[char_name]['frameHeight']}) -> Now ({max_w}x{max_h})")
    
    meta[char_name]["frameWidth"] = max_w
    meta[char_name]["frameHeight"] = max_h

    # Rebuild spritesheet using max_w x max_h grid
    anims = meta[char_name]["animations"]
    max_count = max(a["count"] for a in anims.values())
    num_rows = max(a["row"] for a in anims.values()) + 1
    
    sheet_w = max_count * max_w
    sheet_h = num_rows * max_h
    
    spritesheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    
    for anim_name, a_info in anims.items():
        row_idx = a_info["row"]
        parts = anim_name.split("-")
        if len(parts) == 2:
            mode, direction = parts
            for col_idx in range(a_info["count"]):
                frame_path = os.path.join(char_dir, f"{mode}_{direction}_frame_{col_idx}.png")
                if os.path.exists(frame_path):
                    try:
                        with Image.open(frame_path) as img:
                            dx = col_idx * max_w
                            dy = row_idx * max_h
                            if img.size == (max_w, max_h):
                                spritesheet.paste(img, (dx, dy))
                            else:
                                canvas = Image.new("RGBA", (max_w, max_h), (0, 0, 0, 0))
                                px = max(0, (max_w - img.width) // 2)
                                py = max(0, max_h - img.height)
                                canvas.paste(img, (px, py))
                                spritesheet.paste(canvas, (dx, dy))
                    except Exception as e:
                        print(f"Skip frame error {frame_path}: {e}")
                        
    sheet_path = os.path.join(char_dir, "spritesheet.png")
    spritesheet.save(sheet_path, "PNG")
    print(f"  ✓ Clean spritesheet saved for {char_name} ({sheet_w}x{sheet_h})")

with open(META_PATH, "w") as f:
    json.dump(meta, f, indent=2)

print("\nSuccessfully updated metadata and regenerated spritesheets!")
