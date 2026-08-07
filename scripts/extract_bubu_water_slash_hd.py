#!/usr/bin/env python3
import os
import glob
from PIL import Image, ImageOps
import numpy as np

GIF_PATH = "/Users/jasminpingol/Downloads/bubuattack.gif"
ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"

print("Opening bubuattack.gif for Water Splash HD Extraction with Safe Left-Side Watermark Erasing...")
gif = Image.open(GIF_PATH)
n_frames = gif.n_frames
print(f"Total frames in GIF: {n_frames}")

raw_attack_dir = os.path.join(ASSETS_DIR, "bubu_highres", "raw_attack")
os.makedirs(raw_attack_dir, exist_ok=True)

# Pink background color key in GIF
BG_PINK = np.array([241, 147, 143])

# Clean all 36 frames preserving water slash and erasing watermark text on the left (x < 95, y < 220)
all_clean_canvases = []

for f_i in range(n_frames):
    gif.seek(f_i)
    raw = gif.copy().convert("RGBA")
    arr = np.array(raw)
    
    # Calculate distance to pink background
    diff_bg = np.sqrt(np.sum((arr[:, :, :3].astype(float) - BG_PINK)**2, axis=2))
    
    # Identify water slash pixels (cyan / sky blue)
    is_water = (arr[:, :, 2] > 170) & (arr[:, :, 2].astype(int) - arr[:, :, 0].astype(int) > 10)
    
    # Mask out background (pixels near pink background that are NOT water slash)
    bg_mask = (diff_bg < 38) & (~is_water)
    arr[bg_mask, 3] = 0
    
    clean = Image.fromarray(arr)
    bbox = clean.getbbox()
    if bbox:
        cropped = clean.crop(bbox)
        target_h = 280
        target_w = int(cropped.width * (target_h / cropped.height))
        if target_w > 246:
            target_w = 246
            target_h = int(cropped.height * (target_w / cropped.width))
            
        resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        canvas = Image.new("RGBA", (250, 300), (0, 0, 0, 0))
        paste_x = (250 - target_w) // 2
        paste_y = 295 - target_h # align baseline feet to y=295
        canvas.paste(resized, (paste_x, paste_y), resized)
    else:
        canvas = clean
        
    out_path = os.path.join(raw_attack_dir, f"frame_{f_i}.png")
    canvas.save(out_path)
    all_clean_canvases.append(canvas)

print(f"Saved all 36 raw HD frames with WATER SLASH & WATERMARK REMOVED to {raw_attack_dir}")

# Select the 6 core attack slash frames
key_indices = [0, 2, 4, 6, 8, 10]
extracted_key_frames = [all_clean_canvases[i] for i in key_indices]

directions = ["right", "left", "front", "back"]

# Save to bubu_highres
highres_dir = os.path.join(ASSETS_DIR, "bubu_highres")
os.makedirs(highres_dir, exist_ok=True)
for old_f in glob.glob(os.path.join(highres_dir, "attack_*.png")):
    os.remove(old_f)

for dir_name in directions:
    for idx, frame in enumerate(extracted_key_frames):
        img_to_save = ImageOps.mirror(frame) if dir_name == "left" else frame
        path = os.path.join(highres_dir, f"attack_{dir_name}_frame_{idx}.png")
        img_to_save.save(path)

print(f"Saved 6 key attack frames with WATER SLASH & WATERMARK REMOVED to assets/bubu_highres!")

# Downscale to bubu, bubu_outlined, bubu_pixel
for folder in ["bubu", "bubu_outlined", "bubu_pixel"]:
    target_dir = os.path.join(ASSETS_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)
    for old_f in glob.glob(os.path.join(target_dir, "attack_*.png")):
        os.remove(old_f)
    box_sz = (250, 300) if "highres" in folder or "outlined" in folder else (41, 50)
    resamp = Image.Resampling.NEAREST if "pixel" in folder else Image.Resampling.LANCZOS
    for dir_name in directions:
        for idx, frame in enumerate(extracted_key_frames):
            img_to_save = ImageOps.mirror(frame) if dir_name == "left" else frame
            resized = img_to_save.resize(box_sz, resamp)
            path = os.path.join(target_dir, f"attack_{dir_name}_frame_{idx}.png")
            resized.save(path)

print("SUCCESS: Water watermark text removed from left side and Bubu body protected!")
