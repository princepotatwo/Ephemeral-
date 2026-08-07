#!/usr/bin/env python3
import os
import json
from PIL import Image

ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"
META_PATH = os.path.join(ASSETS_DIR, "spritesheets_metadata.json")

with open(META_PATH, "r") as f:
    meta = json.load(f)

print("Starting intelligent spritesheet texture optimization for 60 FPS performance...")

optimized_count = 0
total_saved_vram_mb = 0

# Base scales ratio dictionary to store in metadata or adjust
for base, char_meta in sorted(meta.items()):
    char_dir = os.path.join(ASSETS_DIR, base)
    sheet_path = os.path.join(char_dir, "spritesheet.png")
    
    if not os.path.exists(sheet_path):
        continue
        
    try:
        sheet_img = Image.open(sheet_path)
    except Exception:
        continue
        
    w, h = sheet_img.size
    mp = (w * h) / 1000000.0
    
    # If spritesheet is > 4 Megapixels, it needs texture optimization!
    if mp > 3.5:
        # Determine downscale ratio: 0.5 (for 3.5 - 20 MP) or 0.25 (for > 20 MP)
        ratio = 0.25 if mp > 20.0 else 0.5
        
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        
        old_vram = (w * h * 4) / (1024 * 1024)
        new_vram = (new_w * new_h * 4) / (1024 * 1024)
        saved_vram = old_vram - new_vram
        total_saved_vram_mb += saved_vram
        
        # High quality Lanczos downsample
        resized_sheet = sheet_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        resized_sheet.save(sheet_path, "PNG")
        
        # Update metadata frameWidth, frameHeight and record scaleMultiplier
        old_fw = char_meta["frameWidth"]
        old_fh = char_meta["frameHeight"]
        
        new_fw = max(1, int(old_fw * ratio))
        new_fh = max(1, int(old_fh * ratio))
        
        char_meta["frameWidth"] = new_fw
        char_meta["frameHeight"] = new_fh
        # Store scale multiplier so index.html multiplies scale by (1 / ratio)
        char_meta["scaleMult"] = 1.0 / ratio
        
        print(f"  ⚡ Optimized {base:28s}: {w}x{h} ({mp:.1f}MP) ➔ {new_w}x{new_h} ({new_w*new_h/1e6:.1f}MP) | VRAM saved: {saved_vram:.1f}MB")
        optimized_count += 1

with open(META_PATH, "w") as f:
    json.dump(meta, f, indent=2)

print(f"\nOptimization complete!")
print(f"Total characters optimized: {optimized_count}")
print(f"Total GPU VRAM freed: {total_saved_vram_mb:.1f} MB!")
