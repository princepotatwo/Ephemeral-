#!/usr/bin/env python3
import os
from PIL import Image, ImageSequence, ImageOps, ImageDraw
import numpy as np

SRC_GIF = "/Users/jasminpingol/Downloads/bubuidle1.gif"
ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"
TARGET_SIZE = (250, 300)
BG_COLOR = (252, 254, 252, 255)

folders = ["bubu_highres", "bubu", "bubu_outlined", "bubu_pixel"]

print(f"Loading GIF: {SRC_GIF}")
gif = Image.open(SRC_GIF)
raw_frames = list(ImageSequence.Iterator(gif))
print(f"Extracted {len(raw_frames)} frames from GIF.")

def clean_frame_background(frame_img):
    # Convert to RGBA
    img = frame_img.convert("RGBA")
    w, h = img.size
    
    # Flood fill from the four corners to make outer background transparent
    for corner in [(0, 0), (w-1, 0), (0, h-1), (w-1, h-1)]:
        ImageDraw.floodfill(img, corner, (0, 0, 0, 0), thresh=10)
        
    return img

print("Processing frames and saving...")

for folder in folders:
    target_dir = os.path.join(ASSETS_DIR, folder)
    if not os.path.exists(target_dir):
        continue
    
    saved = 0
    for i, raw in enumerate(raw_frames):
        # 1. Remove background
        clean_raw = clean_frame_background(raw)
        
        # 2. Resize to fit inside TARGET_SIZE
        clean_raw.thumbnail(TARGET_SIZE, Image.LANCZOS)
        
        # 3. Create a transparent canvas and paste Bubu centered
        canvas_l = Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))
        x = (TARGET_SIZE[0] - clean_raw.width) // 2
        y = (TARGET_SIZE[1] - clean_raw.height) // 2
        canvas_l.paste(clean_raw, (x, y))
        
        # Determine downscaling based on target folder
        box_sz = (250, 300) if ("outlined" in folder or "highres" in folder) else (41, 50)
        resamp = Image.Resampling.NEAREST if "pixel" in folder else Image.Resampling.LANCZOS
        
        # 4. Save Left Facing (Original GIF direction)
        img_left = canvas_l.resize(box_sz, resamp)
        img_left.save(os.path.join(target_dir, f"idle2_left_frame_{i}.png"))
        
        # 5. Save Right Facing (Mirrored GIF direction)
        img_right = ImageOps.mirror(canvas_l).resize(box_sz, resamp)
        img_right.save(os.path.join(target_dir, f"idle2_right_frame_{i}.png"))
        
        saved += 1
        
    print(f"  {folder}: compiled {saved} left and right transparent frames.")

print("All frames compiled successfully!")
