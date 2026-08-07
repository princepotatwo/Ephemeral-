#!/usr/bin/env python3
import os
import glob
from PIL import Image, ImageOps

DOWNLOAD_DIR = "/Users/jasminpingol/Downloads/bubuframes"
ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"

print("Applying manual frames 16-25 as Bubu attack animation scaled to 88%...")

extracted_key_frames = []

for idx, f_idx in enumerate(range(16, 26)):
    src_path = os.path.join(DOWNLOAD_DIR, f"bubu_attack_left_frame_{f_idx}.png")
    if not os.path.exists(src_path):
        print(f"ERROR: File {src_path} not found!")
        exit(1)
        
    # Open left-facing image
    img_left = Image.open(src_path).convert("RGBA")
    
    # Mirror horizontally to get the base right-facing image
    img_right = ImageOps.mirror(img_left)
    
    # SCALE DOWN BY 88% (0.88) to match run/idle scale!
    bbox = img_right.getbbox()
    if bbox:
        cropped = img_right.crop(bbox)
        new_w = int(cropped.width * 0.88)
        new_h = int(cropped.height * 0.88)
        resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        canvas = Image.new("RGBA", (250, 300), (0, 0, 0, 0))
        paste_x = (250 - new_w) // 2
        paste_y = 285 - new_h  # Bubu feet baseline aligned to y=285
        canvas.paste(resized, (paste_x, paste_y), resized)
        img_right = canvas
        
    extracted_key_frames.append(img_right)

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

print("Saved highres frames!")

# Downscale to bubu, bubu_outlined, bubu_pixel
for folder in ["bubu", "bubu_outlined", "bubu_pixel"]:
    target_dir = os.path.join(ASSETS_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)
    for old_f in glob.glob(os.path.join(target_dir, "attack_*.png")):
        os.remove(old_f)
    box_sz = (250, 300) if "outlined" in folder else (41, 50)
    resamp = Image.Resampling.NEAREST if "pixel" in folder else Image.Resampling.LANCZOS
    for dir_name in directions:
        for idx, frame in enumerate(extracted_key_frames):
            img_to_save = ImageOps.mirror(frame) if dir_name == "left" else frame
            resized = img_to_save.resize(box_sz, resamp)
            path = os.path.join(target_dir, f"attack_{dir_name}_frame_{idx}.png")
            resized.save(path)

print("SUCCESS: 10 attack frames applied to Bubu at 88% scale!")
