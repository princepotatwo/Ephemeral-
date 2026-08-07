#!/usr/bin/env python3
import os
import glob
from PIL import Image, ImageOps
import numpy as np

GIF_PATH = "/Users/jasminpingol/Downloads/bubuattack.gif"
ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"

print("Extracting 36 clean watermark-free raw attack frames...")
gif = Image.open(GIF_PATH)
n_frames = gif.n_frames

raw_attack_dir = os.path.join(ASSETS_DIR, "bubu_highres", "raw_attack")
os.makedirs(raw_attack_dir, exist_ok=True)

for old_f in glob.glob(os.path.join(raw_attack_dir, "*.png")):
    os.remove(old_f)

for f_i in range(n_frames):
    gif.seek(f_i)
    raw = gif.copy().convert("RGBA")
    arr = np.array(raw)
    
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
        paste_y = 295 - target_h
        canvas.paste(resized, (paste_x, paste_y), resized)
    else:
        canvas = clean
        
    out_path = os.path.join(raw_attack_dir, f"frame_{f_i}.png")
    canvas.save(out_path)

print(f"Successfully saved all {n_frames} clean watermark-free raw frames!")
