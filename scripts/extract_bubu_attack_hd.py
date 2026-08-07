#!/usr/bin/env python3
import os
import glob
from PIL import Image, ImageOps
import numpy as np
from rembg import remove

GIF_PATH = "/Users/jasminpingol/Downloads/bubuattack.gif"
ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"

print("Opening bubuattack.gif...")
gif = Image.open(GIF_PATH)
n_frames = gif.n_frames
print(f"Total frames in GIF: {n_frames}")

# Subsample to 8-12 crisp attack animation frames for optimal 60fps game performance
step = max(1, n_frames // 10)
frame_indices = list(range(0, n_frames, step))[:10]
print(f"Extracting {len(frame_indices)} key frames: {frame_indices}")

extracted_frames = []
for idx, f_i in enumerate(frame_indices):
    gif.seek(f_i)
    raw = gif.copy().convert("RGBA")
    clean = remove(raw)
    
    # Fit into 250x300 canvas centered
    bbox = clean.getbbox()
    if bbox:
        cropped = clean.crop(bbox)
        # Scale to fit inside 210x260 preserving aspect ratio
        cropped.thumbnail((210, 260), Image.Resampling.LANCZOS)
        
        canvas = Image.new("RGBA", (250, 300), (0, 0, 0, 0))
        paste_x = (250 - cropped.width) // 2
        paste_y = (300 - cropped.height) // 2 + 10 # align feet to baseline
        canvas.paste(cropped, (paste_x, paste_y), cropped)
        extracted_frames.append(canvas)
    else:
        extracted_frames.append(clean)
    print(f"  Processed frame {idx+1}/{len(frame_indices)}")

num_out = len(extracted_frames)
print(f"Extracted {num_out} clean HD frames!")

# Save to bubu_highres
highres_dir = os.path.join(ASSETS_DIR, "bubu_highres")
os.makedirs(highres_dir, exist_ok=True)

# Remove old low-res/sketch attack frames
for old_f in glob.glob(os.path.join(highres_dir, "attack_*.png")):
    os.remove(old_f)

directions = ["right", "left", "front", "back"]
for dir_name in directions:
    for idx, frame in enumerate(extracted_frames):
        if dir_name == "left":
            img_to_save = ImageOps.mirror(frame)
        else:
            img_to_save = frame
        
        path = os.path.join(highres_dir, f"attack_{dir_name}_frame_{idx}.png")
        img_to_save.save(path)

print(f"Saved {num_out} HD attack frames per direction to assets/bubu_highres!")

# Downscale for bubu (41x50 box)
bubu_dir = os.path.join(ASSETS_DIR, "bubu")
os.makedirs(bubu_dir, exist_ok=True)
for old_f in glob.glob(os.path.join(bubu_dir, "attack_*.png")):
    os.remove(old_f)

for dir_name in directions:
    for idx, frame in enumerate(extracted_frames):
        img_to_save = ImageOps.mirror(frame) if dir_name == "left" else frame
        small = img_to_save.resize((41, 50), Image.Resampling.LANCZOS)
        path = os.path.join(bubu_dir, f"attack_{dir_name}_frame_{idx}.png")
        small.save(path)

print(f"Saved {num_out} attack frames per direction to assets/bubu!")

# Downscale for bubu_outlined and bubu_pixel
for folder in ["bubu_outlined", "bubu_pixel"]:
    target_dir = os.path.join(ASSETS_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)
    for old_f in glob.glob(os.path.join(target_dir, "attack_*.png")):
        os.remove(old_f)
    for dir_name in directions:
        for idx, frame in enumerate(extracted_frames):
            img_to_save = ImageOps.mirror(frame) if dir_name == "left" else frame
            box_sz = (250, 300) if "highres" in folder or "outlined" in folder else (41, 50)
            resamp = Image.Resampling.NEAREST if "pixel" in folder else Image.Resampling.LANCZOS
            resized = img_to_save.resize(box_sz, resamp)
            path = os.path.join(target_dir, f"attack_{dir_name}_frame_{idx}.png")
            resized.save(path)

print("Done processing HD Bubu attack animation!")
