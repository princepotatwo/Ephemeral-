#!/usr/bin/env python3
import os
import glob
from PIL import Image, ImageOps
import numpy as np

GIF_PATH = "/Users/jasminpingol/Downloads/bubuattack.gif"
ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"

print("Extracting clean watermark-free 6-frame HD attack animation...")
gif = Image.open(GIF_PATH)
n_frames = gif.n_frames

# 6 key attack slash frames
frame_indices = [0, 2, 4, 6, 8, 10]

extracted_frames = []
for idx, f_i in enumerate(frame_indices):
    gif.seek(f_i)
    raw = gif.copy().convert("RGBA")
    arr = np.array(raw)
    
    # Corner background color removal
    bg_r, bg_g, bg_b = arr[0, 0, :3]
    diff = np.sqrt(
        (arr[:, :, 0].astype(float) - bg_r)**2 +
        (arr[:, :, 1].astype(float) - bg_g)**2 +
        (arr[:, :, 2].astype(float) - bg_b)**2
    )
    
    mask = (diff > 45) & (arr[:, :, 3] > 10)
    
    # Strip watermark text on left border (x < 52) and top-right text (x > 320, y < 260)
    clean_mask = mask.copy()
    clean_mask[:, :52] = False
    clean_mask[:260, 320:] = False
    
    arr[~clean_mask, 3] = 0
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
        extracted_frames.append(canvas)
    else:
        extracted_frames.append(clean)

num_out = len(extracted_frames)
directions = ["right", "left", "front", "back"]

# Save to bubu_highres
highres_dir = os.path.join(ASSETS_DIR, "bubu_highres")
os.makedirs(highres_dir, exist_ok=True)
for old_f in glob.glob(os.path.join(highres_dir, "attack_*.png")):
    os.remove(old_f)

for dir_name in directions:
    for idx, frame in enumerate(extracted_frames):
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
        for idx, frame in enumerate(extracted_frames):
            img_to_save = ImageOps.mirror(frame) if dir_name == "left" else frame
            resized = img_to_save.resize(box_sz, resamp)
            path = os.path.join(target_dir, f"attack_{dir_name}_frame_{idx}.png")
            resized.save(path)

print("SUCCESS: Watermark text stripped from all attack frames!")
