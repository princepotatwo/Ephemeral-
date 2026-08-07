#!/usr/bin/env python3
import os
from PIL import Image, ImageOps

ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"
folders = ["bubu_highres", "bubu", "bubu_outlined", "bubu_pixel"]

print("Mirroring Bubu idle2 (alternate idle) in-place horizontally...")

for folder in folders:
    target_dir = os.path.join(ASSETS_DIR, folder)
    if not os.path.exists(target_dir):
        continue
    
    for i in range(25):
        left_path = os.path.join(target_dir, f"idle2_left_frame_{i}.png")
        right_path = os.path.join(target_dir, f"idle2_right_frame_{i}.png")
        
        if os.path.exists(left_path):
            img_left = Image.open(left_path).convert("RGBA")
            mirrored_left = ImageOps.mirror(img_left)
            mirrored_left.save(left_path)
            
        if os.path.exists(right_path):
            img_right = Image.open(right_path).convert("RGBA")
            mirrored_right = ImageOps.mirror(img_right)
            mirrored_right.save(right_path)

print("SUCCESS: Bubu idle2 mirrored in-place successfully!")
