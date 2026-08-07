#!/usr/bin/env python3
import os
import glob
from PIL import Image, ImageOps
import numpy as np

GIF_PATH = "/Users/jasminpingol/Downloads/bubuattack.gif"
ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"

print("Opening bubuattack.gif for fast HD extraction...")
gif = Image.open(GIF_PATH)
n_frames = gif.n_frames
print(f"Total frames in GIF: {n_frames}")

# Sample 10 smooth attack frames
step = max(1, n_frames // 10)
frame_indices = list(range(0, n_frames, step))[:10]

extracted_frames = []
for idx, f_i in enumerate(frame_indices):
    gif.seek(f_i)
    raw = gif.copy().convert("RGBA")
    arr = np.array(raw)
    
    # Target pink/blue solid background colors in bubuattack.gif:
    # Corner pixels determine background color
    bg_r, bg_g, bg_b = arr[0, 0, :3]
    
    # Distance to corner background color
    diff = np.sqrt(
        (arr[:, :, 0].astype(float) - bg_r)**2 +
        (arr[:, :, 1].astype(float) - bg_g)**2 +
        (arr[:, :, 2].astype(float) - bg_b)**2
    )
    
    # Mask out background (pixels close to background color become transparent)
    bg_mask = (diff < 45) | (arr[:, :, 3] < 10)
    arr[bg_mask, 3] = 0
    
    clean = Image.fromarray(arr)
    bbox = clean.getbbox()
    if bbox:
        cropped = clean.crop(bbox)
        # Scale to fit 210x260 preserving HD aspect ratio
        cropped.thumbnail((210, 260), Image.Resampling.LANCZOS)
        
        canvas = Image.new("RGBA", (250, 300), (0, 0, 0, 0))
        paste_x = (250 - cropped.width) // 2
        paste_y = (300 - cropped.height) // 2 + 10 # Baseline feet align
        canvas.paste(cropped, (paste_x, paste_y), cropped)
        extracted_frames.append(canvas)
    else:
        extracted_frames.append(clean)

num_out = len(extracted_frames)
print(f"Extracted {num_out} clean HD frames instantly!")

# Kill any stuck task-510 if running
highres_dir = os.path.join(ASSETS_DIR, "bubu_highres")
os.makedirs(highres_dir, exist_ok=True)
for old_f in glob.glob(os.path.join(highres_dir, "attack_*.png")):
    os.remove(old_f)

directions = ["right", "left", "front", "back"]
for dir_name in directions:
    for idx, frame in enumerate(extracted_frames):
        img_to_save = ImageOps.mirror(frame) if dir_name == "left" else frame
        path = os.path.join(highres_dir, f"attack_{dir_name}_frame_{idx}.png")
        img_to_save.save(path)

print(f"Saved {num_out} HD full-color attack frames to assets/bubu_highres!")

# Save to bubu, bubu_outlined, bubu_pixel
for folder in ["bubu", "bubu_outlined", "bubu_pixel"]:
    target_dir = os.path.join(ASSETS_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)
    for old_f in glob.glob(os.path.join(target_dir, "attack_*.png")):
        os.remove(old_f)
    box_sz = (250, 300) if "highres" in folder or "outlined" in folder else (41, 50)
    resamp = Image.Resampling.NEAREST if "pixel" in folder else Image.Resampling.LANCZOS
    for dir_name in directions:
        for idx, frame in enumerate(extracted_frames):
            img_to_save = ImageOps.mirror(frame) if dir_name == "left" else frame
            resized = img_to_save.resize(box_sz, resamp)
            path = os.path.join(target_dir, f"attack_{dir_name}_frame_{idx}.png")
            resized.save(path)

print("SUCCESS: All HD full-color Bubu attack animation frames generated and saved!")
