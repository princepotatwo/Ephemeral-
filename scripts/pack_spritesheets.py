#!/usr/bin/env python3
import os
import re
import json
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"
OUTPUT_METADATA_PATH = os.path.join(ASSETS_DIR, "spritesheets_metadata.json")

# Regex to match filenames like: idle_front_frame_0.png
FRAME_PATTERN = re.compile(r"^([a-z0-9_]+)_(front|back|left|right)_frame_([0-9]+)\.png$")

def pack_character_spritesheet(char_dir):
    char_name = os.path.basename(char_dir)
    
    # 1. Collect all frame files
    frames_by_anim = {} # (mode, direction) -> list of (index, filename)
    all_sizes = set()
    
    try:
        files = os.listdir(char_dir)
    except Exception as e:
        print(f"Error reading directory {char_name}: {e}")
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
        
        # Check size
        img_path = os.path.join(char_dir, f)
        try:
            with Image.open(img_path) as img:
                all_sizes.add(img.size)
        except Exception as e:
            pass

    if not frames_by_anim:
        return None

    # 2. Get frame size
    if not all_sizes:
        return None
    frame_w, frame_h = list(all_sizes)[0]
    
    # Sort frames within each animation by index
    for key in frames_by_anim:
        frames_by_anim[key].sort(key=lambda x: x[0])
        
    # Sort animations to make the row layout deterministic
    sorted_anims = sorted(frames_by_anim.keys())
    
    max_frames = max(len(frames_by_anim[k]) for k in frames_by_anim)
    rows_count = len(sorted_anims)
    
    # 3. Create sprite sheet canvas
    sheet_w = max_frames * frame_w
    sheet_h = rows_count * frame_h
    
    spritesheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    
    anim_meta = {}
    for row_idx, key in enumerate(sorted_anims):
        mode, direction = key
        anim_name = f"{mode}-{direction}"
        frames_list = frames_by_anim[key]
        
        for col_idx, (idx, filename) in enumerate(frames_list):
            img_path = os.path.join(char_dir, filename)
            try:
                with Image.open(img_path) as img:
                    dx = col_idx * frame_w
                    dy = row_idx * frame_h
                    if img.size != (frame_w, frame_h):
                        img = img.resize((frame_w, frame_h), Image.Resampling.LANCZOS)
                    spritesheet.paste(img, (dx, dy))
            except Exception as e:
                pass
                
        anim_meta[anim_name] = {
            "row": row_idx,
            "count": len(frames_list)
        }
        
    # 4. Save sprite sheet image
    output_png_path = os.path.join(char_dir, "spritesheet.png")
    spritesheet.save(output_png_path, "PNG")
    
    print(f"✓ Packed {char_name} ({frame_w}x{frame_h}, {rows_count} anims, {len(files)} total files)")
    
    # Return character metadata
    return char_name, {
        "frameWidth": frame_w,
        "frameHeight": frame_h,
        "animations": anim_meta
    }

def main():
    metadata = {}
    
    # Collect directories to process
    dirs_to_process = []
    for item in os.listdir(ASSETS_DIR):
        path = os.path.join(ASSETS_DIR, item)
        if not os.path.isdir(path):
            continue
        if item in ["forest", "magic_traps", "plants", "ponk_plants", "predator_plants", "raw_dudu_build"]:
            continue
        dirs_to_process.append(path)
        
    print(f"Starting parallel spritesheet packing for {len(dirs_to_process)} characters using 24 threads...")
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=24) as executor:
        results = executor.map(pack_character_spritesheet, dirs_to_process)
        
    for res in results:
        if res:
            char_name, char_meta = res
            metadata[char_name] = char_meta
            
    # Write metadata json
    with open(OUTPUT_METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"\nSuccessfully packed spritesheets!")
    print(f"Metadata file written to: {OUTPUT_METADATA_PATH}")
    print(f"Total characters processed: {len(metadata)}")

if __name__ == "__main__":
    main()
