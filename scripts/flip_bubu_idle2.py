#!/usr/bin/env python3
import os
import glob
from PIL import Image, ImageOps

ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"
folders = ["bubu_highres", "bubu", "bubu_outlined", "bubu_pixel"]

print("Flipping Bubu idle2 (alternate idle) directions...")

for folder in folders:
    target_dir = os.path.join(ASSETS_DIR, folder)
    if not os.path.exists(target_dir):
        continue
    
    # Bubu idle2 has 25 frames
    for i in range(25):
        left_path = os.path.join(target_dir, f"idle2_left_frame_{i}.png")
        right_path = os.path.join(target_dir, f"idle2_right_frame_{i}.png")
        
        if os.path.exists(left_path) and os.path.exists(right_path):
            img_left = Image.open(left_path).convert("RGBA")
            img_right = Image.open(right_path).convert("RGBA")
            
            # Swap and mirror
            new_left = ImageOps.mirror(img_right)
            new_right = ImageOps.mirror(img_left)
            
            new_left.save(left_path)
            new_right.save(right_path)

print("SUCCESS: Bubu idle2 directions flipped successfully!")
