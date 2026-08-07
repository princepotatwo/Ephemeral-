#!/usr/bin/env python3
import os
import glob
from PIL import Image, ImageOps

DOWNLOAD_DIR = "/Users/jasminpingol/Downloads/duduframes"
ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"

print("Applying manual Dudu frames 19-23 as Dudu attack animation at 88% scale and CORRECT directions...")

extracted_key_frames = []

for idx, f_idx in enumerate(range(19, 24)):
    src_path = os.path.join(DOWNLOAD_DIR, f"dudu_attack_left_frame_{f_idx}.png")
    if not os.path.exists(src_path):
        print(f"ERROR: File {src_path} not found!")
        exit(1)
        
    # Open left-facing image (which is already facing LEFT)
    img_left = Image.open(src_path).convert("RGBA")
    
    # SCALE DOWN BY 88% (0.88)
    bbox = img_left.getbbox()
    if bbox:
        cropped = img_left.crop(bbox)
        new_w = int(cropped.width * 0.88)
        new_h = int(cropped.height * 0.88)
        resized = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        canvas = Image.new("RGBA", (250, 300), (0, 0, 0, 0))
        paste_x = (250 - new_w) // 2
        paste_y = 295 - new_h  # Dudu feet baseline aligned to y=295
        canvas.paste(resized, (paste_x, paste_y), resized)
        img_left = canvas
        
    extracted_key_frames.append(img_left)

directions = ["right", "left", "front", "back"]

# Save to dudu_highres
highres_dir = os.path.join(ASSETS_DIR, "dudu_highres")
os.makedirs(highres_dir, exist_ok=True)
for old_f in glob.glob(os.path.join(highres_dir, "attack_*.png")):
    os.remove(old_f)

for dir_name in directions:
    for idx, frame in enumerate(extracted_key_frames):
        # Left gets the original left-facing frame, Right gets mirrored
        img_to_save = frame if dir_name == "left" else ImageOps.mirror(frame)
        path = os.path.join(highres_dir, f"attack_{dir_name}_frame_{idx}.png")
        img_to_save.save(path)

print("Saved highres frames!")

# Downscale to dudu, dudu_outlined, dudu_pixel
for folder in ["dudu", "dudu_outlined", "dudu_pixel"]:
    target_dir = os.path.join(ASSETS_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)
    for old_f in glob.glob(os.path.join(target_dir, "attack_*.png")):
        os.remove(old_f)
    box_sz = (250, 300) if "outlined" in folder else (41, 50)
    resamp = Image.Resampling.NEAREST if "pixel" in folder else Image.Resampling.LANCZOS
    for dir_name in directions:
        for idx, frame in enumerate(extracted_key_frames):
            img_to_save = frame if dir_name == "left" else ImageOps.mirror(frame)
            resized = img_to_save.resize(box_sz, resamp)
            path = os.path.join(target_dir, f"attack_{dir_name}_frame_{idx}.png")
            resized.save(path)

print("SUCCESS: Dudu attack directions corrected on disk!")
