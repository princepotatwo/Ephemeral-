#!/usr/bin/env python3
import os
from PIL import Image
import numpy as np

GIF_PATH = "/Users/jasminpingol/Downloads/duduattack.gif"
ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"

print("Opening duduattack.gif for STRICT HD Extraction...")
gif = Image.open(GIF_PATH)
n_frames = gif.n_frames
print(f"Total frames in GIF: {n_frames}")

raw_attack_dir = os.path.join(ASSETS_DIR, "dudu_highres", "raw_attack")
os.makedirs(raw_attack_dir, exist_ok=True)

# Background color key in Dudu GIF - we use a strict threshold since the bg is solid!
BG_COLOR = np.array([212, 170, 147])

for f_i in range(n_frames):
    gif.seek(f_i)
    raw = gif.copy().convert("RGBA")
    arr = np.array(raw)
    
    # Calculate distance to background color
    diff_bg = np.sqrt(np.sum((arr[:, :, :3].astype(float) - BG_COLOR)**2, axis=2))
    
    # Strict background removal (threshold = 3) to keep Dudu's brown fur 100% safe
    bg_mask = (diff_bg < 3)
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

print(f"Saved all 24 raw HD Dudu frames to {raw_attack_dir}")
