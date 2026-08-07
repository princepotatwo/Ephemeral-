#!/usr/bin/env python3
import os
import json
import traceback
from PIL import Image

ASSETS_DIR = "/Users/jasminpingol/Codex/assets"
META_PATH = os.path.join(ASSETS_DIR, "spritesheets_metadata.json")

# Full dictionary of all large/modified characters that must be at 100% scale
CHAR_ORIGINAL_SIZES = {
    "bubu_highres": (250, 300),
    "bubu_outlined": (250, 300),
    "dudu_highres": (250, 300),
    "dudu_outlined": (250, 300),
    "knight_orange": (210, 148),
    "knight_green": (210, 148),
    "knight_blue": (210, 148),
    "silksong_hornet": (381, 249),
    "silksong_lifeblood_worm": (584, 480),
    "silksong_ladybug": (667, 245),
    "silksong_staff_pilgrim": (569, 460),
    "silksong_pilgrim_hiker": (261, 260),
    "silksong_shakra_rest": (319, 268),
    "silksong_moss_creep": (398, 386),
    "silksong_bone_worm": (312, 395),
    "silksong_moss_crawler": (190, 148),
    "creature_slasher": (435, 358),
    "creature_crawler": (403, 187)
}

def main():
    with open(META_PATH, "r") as f:
        meta = json.load(f)
        
    print("Starting ultra-fast pixel-perfect grid restoration at 100% scale...", flush=True)

    repacked_count = 0
    
    for char_name, orig_size in CHAR_ORIGINAL_SIZES.items():
        try:
            char_dir = os.path.join(ASSETS_DIR, char_name)
            if not os.path.isdir(char_dir):
                continue
                
            anims = meta[char_name]["animations"]
            if not anims:
                continue
                
            canonical_w, canonical_h = orig_size
            max_count = max(a["count"] for a in anims.values())
            num_rows = max(a["row"] for a in anims.values()) + 1
            
            sheet_w = max_count * canonical_w
            sheet_h = num_rows * canonical_h
            
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
                                    dx = col_idx * canonical_w
                                    dy = row_idx * canonical_h
                                    
                                    if img.size == (canonical_w, canonical_h):
                                        spritesheet.paste(img, (dx, dy))
                                    else:
                                        # Always paste at top-left (0,0) — the export_knights_v2.py
                                        # uses a uniform crop per action+direction, so the coordinate
                                        # system is already anchored correctly. Re-centering or
                                        # bottom-aligning would shift the character incorrectly.
                                        canvas = Image.new("RGBA", (canonical_w, canonical_h), (0, 0, 0, 0))
                                        canvas.paste(img, (0, 0))
                                        spritesheet.paste(canvas, (dx, dy))
                            except Exception:
                                pass
                                
            # Atomic save to bypass iCloud locking hangs
            temp_path = f"/tmp/temp_{char_name}_spritesheet.png"
            # Use compress_level=1 for fast PNG save
            spritesheet.save(temp_path, "PNG", compress_level=1)
            
            sheet_path = os.path.join(char_dir, "spritesheet.png")
            os.replace(temp_path, sheet_path)
            
            meta[char_name]["frameWidth"] = canonical_w
            meta[char_name]["frameHeight"] = canonical_h
            meta[char_name].pop("scaleMult", None)
            
            print(f"  ✓ Restored {char_name:25s}: {canonical_w}x{canonical_h}", flush=True)
            repacked_count += 1
        except Exception as e:
            print(f"  ❌ Error repacking {char_name}: {e}", flush=True)
            traceback.print_exc()

    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)
        
    print(f"\nSuccessfully repacked all {repacked_count} characters at 100% scale!", flush=True)

if __name__ == "__main__":
    main()
