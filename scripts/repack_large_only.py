#!/usr/bin/env python3
import os
import re
import json
from PIL import Image
from collections import Counter

ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"
META_PATH = os.path.join(ASSETS_DIR, "spritesheets_metadata.json")

# Regex to match filenames like: idle_front_frame_0.png
FRAME_PATTERN = re.compile(r"^([a-z0-9_]+)_(front|back|left|right|up|down|side)_frame_([0-9]+)\.png$")

LARGE_CHARS = [
    "bubu_highres", "bubu_outlined", "dudu_highres", "dudu_outlined",
    "silksong_lifeblood_worm", "silksong_ladybug", "silksong_staff_pilgrim",
    "silksong_pilgrim_hiker", "silksong_shakra_rest", "silksong_moss_creep",
    "silksong_bone_worm", "silksong_moss_crawler", "silksong_hornet",
    "creature_slasher", "creature_crawler", "knight_orange", "knight_green", "knight_blue"
]

def repack_character(char_name):
    path = os.path.join(ASSETS_DIR, char_name)
    if not os.path.isdir(path):
        return None
        
    frames_by_anim = {}
    frame_sizes = []
    
    try:
        files = os.listdir(path)
    except Exception:
        return None
        
    for f in files:
        m = FRAME_PATTERN.match(f)
        if not m:
            continue
        mode, direction, idx = m.group(1), m.group(2), int(m.group(3))
        key = (mode, direction)
        if key not in frames_by_anim:
            frames_by_anim[key] = []
        frames_by_anim[key].append((idx, f))
        
        img_path = os.path.join(path, f)
        try:
            with Image.open(img_path) as img:
                frame_sizes.append(img.size)
        except Exception:
            pass

    if not frames_by_anim or not frame_sizes:
        return None

    # Determine canonical frame size
    canonical_w, canonical_h = None, None
    for priority_frame in ["idle_front_frame_0.png", "idle_down_frame_0.png", "idle_side_frame_0.png"]:
        p_path = os.path.join(path, priority_frame)
        if os.path.exists(p_path):
            try:
                with Image.open(p_path) as img:
                    canonical_w, canonical_h = img.size
                    break
            except Exception:
                pass
                
    if not canonical_w:
        size_counts = Counter(frame_sizes)
        canonical_w, canonical_h = size_counts.most_common(1)[0][0]

    for key in frames_by_anim:
        frames_by_anim[key].sort(key=lambda x: x[0])
        
    sorted_anims = sorted(frames_by_anim.keys())
    max_frames = max(len(frames_by_anim[k]) for k in frames_by_anim)
    rows_count = len(sorted_anims)
    
    sheet_w = max_frames * canonical_w
    sheet_h = rows_count * canonical_h
    
    spritesheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    anim_meta = {}
    
    for row_idx, key in enumerate(sorted_anims):
        mode, direction = key
        anim_name = f"{mode}-{direction}"
        frames_list = frames_by_anim[key]
        
        for col_idx, (idx, filename) in enumerate(frames_list):
            img_path = os.path.join(path, filename)
            try:
                with Image.open(img_path) as img:
                    dx = col_idx * canonical_w
                    dy = row_idx * canonical_h
                    
                    if img.size == (canonical_w, canonical_h):
                        spritesheet.paste(img, (dx, dy))
                    else:
                        canvas = Image.new("RGBA", (canonical_w, canonical_h), (0, 0, 0, 0))
                        paste_x = max(0, (canonical_w - img.width) // 2)
                        paste_y = max(0, canonical_h - img.height)
                        canvas.paste(img, (paste_x, paste_y))
                        spritesheet.paste(canvas, (dx, dy))
            except Exception:
                pass
                
        anim_meta[anim_name] = {
            "row": row_idx,
            "count": len(frames_list)
        }
        
    output_png_path = os.path.join(path, "spritesheet.png")
    spritesheet.save(output_png_path, "PNG")
    
    return char_name, {
        "frameWidth": canonical_w,
        "frameHeight": canonical_h,
        "animations": anim_meta
    }

def main():
    with open(META_PATH, "r") as f:
        meta = json.load(f)
        
    print("Repacking large characters synchronously at 100% scale...", flush=True)

    repacked_count = 0
    for name in LARGE_CHARS:
        try:
            res = repack_character(name)
            if res:
                char_name, char_meta = res
                meta[char_name] = char_meta
                # Clean up any leftover scaleMult
                meta[char_name].pop("scaleMult", None)
                print(f"  ✓ Repacked {char_name:25s}: {char_meta['frameWidth']}x{char_meta['frameHeight']}", flush=True)
                repacked_count += 1
        except Exception as e:
            print(f"  ❌ Error repacking {name}: {e}", flush=True)

    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)
        
    print(f"\nSuccessfully repacked {repacked_count} characters at 100% scale!", flush=True)

if __name__ == "__main__":
    main()
