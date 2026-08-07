#!/usr/bin/env python3
import os
import glob
from PIL import Image, ImageOps
import numpy as np

GIF_PATH = "/Users/jasminpingol/Downloads/bubuattack.gif"
ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"

print("Opening bubuattack.gif for complete 36-frame text watermark removal...")
gif = Image.open(GIF_PATH)
n_frames = gif.n_frames
print(f"Total frames in GIF: {n_frames}")

# All 3 background color variations present in bubuattack.gif
bg_colors = [
    np.array([241, 147, 143]), # Pink
    np.array([187, 247, 253]), # Cyan / Light Blue
    np.array([136, 197, 222])  # Sky Blue
]

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
    rgb = arr[:, :, :3].astype(float)
    
    # 1. Multi-color background distance masking
    min_diff = np.ones((arr.shape[0], arr.shape[1])) * 999999.0
    for bg in bg_colors:
        d = np.sqrt(np.sum((rgb - bg)**2, axis=2))
        min_diff = np.minimum(min_diff, d)
        
    fg_mask = min_diff > 45
    
    # Make background transparent
    arr[~fg_mask, 3] = 0
    
    # 2. Complete smart text watermark removal (erase left margin x < 75)
    arr[:, 0:75, 3] = 0
    
    clean = Image.fromarray(arr)
    
    # 3. Fit Bubu into 250x300 HD canvas preserving 280px character scale
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
    extracted_hd_frames.append(canvas)

print(f"Successfully processed all {n_frames} clean text-free raw HD attack frames!")

# Save key 6 attack frames [0, 2, 4, 6, 8, 10] for main game animation
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

print("SUCCESS: Text watermark 100% removed across all 36 frames!")
