#!/usr/bin/env python3
import os
import glob
from PIL import Image, ImageOps
import numpy as np

GIF_PATH = "/Users/jasminpingol/Downloads/bubuattack.gif"
ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"

print("Opening bubuattack.gif for smart text watermark removal...")
gif = Image.open(GIF_PATH)
n_frames = gif.n_frames
print(f"Total frames in GIF: {n_frames}")

raw_attack_dir = os.path.join(ASSETS_DIR, "bubu_highres", "raw_attack")
os.makedirs(raw_attack_dir, exist_ok=True)

# Clear old raw frames
for old_f in glob.glob(os.path.join(raw_attack_dir, "*.png")):
    os.remove(old_f)

extracted_hd_frames = []

for f_i in range(n_frames):
    gif.seek(f_i)
    raw = gif.copy().convert("RGBA")
    arr = np.array(raw)
    
    # 1. Background removal keyed to corner color
    bg_r, bg_g, bg_b = arr[0, 0, :3]
    diff = np.sqrt(
        (arr[:, :, 0].astype(float) - bg_r)**2 +
        (arr[:, :, 1].astype(float) - bg_g)**2 +
        (arr[:, :, 2].astype(float) - bg_b)**2
    )
    fg_mask = diff > 45
    arr[~fg_mask, 3] = 0
    
    # 2. Smart Text Watermark Removal (Erase text column x < 42, y >= 70 without cropping canvas)
    text_region = fg_mask & False
    text_region[70:350, 0:42] = True
    arr[text_region, 3] = 0
    
    clean = Image.fromarray(arr)
    
    # 3. Fit into 250x300 canvas preserving 280px body scale
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
        paste_y = 295 - target_h # align feet to baseline y=295
        canvas.paste(resized, (paste_x, paste_y), resized)
    else:
        canvas = clean
        
    out_path = os.path.join(raw_attack_dir, f"frame_{f_i}.png")
    canvas.save(out_path)
    extracted_hd_frames.append(canvas)

print(f"Successfully processed and saved all {n_frames} clean text-free raw HD attack frames!")

# Select 6 key frames [0, 2, 4, 6, 8, 10] for main game animation
key_indices = [0, 2, 4, 6, 8, 10]
key_frames = [extracted_hd_frames[idx] for idx in key_indices]

directions = ["right", "left", "front", "back"]

# Save to bubu_highres
highres_dir = os.path.join(ASSETS_DIR, "bubu_highres")
for old_f in glob.glob(os.path.join(highres_dir, "attack_*.png")):
    os.remove(old_f)

for dir_name in directions:
    for idx, frame in enumerate(key_frames):
        img_to_save = ImageOps.mirror(frame) if dir_name == "left" else frame
        path = os.path.join(highres_dir, f"attack_{dir_name}_frame_{idx}.png")
        img_to_save.save(path)

# Save to bubu, bubu_outlined, bubu_pixel
for folder in ["bubu", "bubu_outlined", "bubu_pixel"]:
    target_dir = os.path.join(ASSETS_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)
    for old_f in glob.glob(os.path.join(target_dir, "attack_*.png")):
        os.remove(old_f)
    box_sz = (250, 300) if "highres" in folder or "outlined" in folder else (41, 50)
    resamp = Image.Resampling.NEAREST if "pixel" in folder else Image.Resampling.LANCZOS
    for dir_name in directions:
        for idx, frame in enumerate(key_frames):
            img_to_save = ImageOps.mirror(frame) if dir_name == "left" else frame
            resized = img_to_save.resize(box_sz, resamp)
            path = os.path.join(target_dir, f"attack_{dir_name}_frame_{idx}.png")
            resized.save(path)

print("SUCCESS: Smart watermark removal complete across all 36 frames!")
