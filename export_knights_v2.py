#!/usr/bin/env python3
"""
Knight frame re-export v2.
- Exports all 7 actions: idle, run, attack, die, defense, hit, special_attack
- For each of 4 directions: front, back, left, right
- Crops all transparent padding (uniform crop across all frames per action+dir so feet stay consistent)
- Uses color-signature masking to prevent neighbor knight bleed
"""

import sys, os
from PIL import Image
import numpy as np

GIF_PATH = "/Users/jasminpingol/Downloads/sprite/knight1.gif"
OUT_DIRS = {
    "orange": "/Users/jasminpingol/Documents/Codex/assets/knight_orange",
    "green":  "/Users/jasminpingol/Documents/Codex/assets/knight_green",
    "blue":   "/Users/jasminpingol/Documents/Codex/assets/knight_blue",
}

# Frame dimensions (each cell in the sprite grid)
CELL_W, CELL_H = 210, 148
COLS = 4  # directions: right, left, front(down), back(up)

# Row offsets for each knight
KNIGHT_ROWS = {"orange": 0, "green": 1, "blue": 2}

# Direction mapping: column → game direction name
# Col 0=right, 1=left, 2=front, 3=back
COL_TO_DIR = {0: "right", 1: "left", 2: "front", 3: "back"}

# Action frame ranges (GIF frame indices, within the spritesheet row)
# These are GLOBAL frame indices into the GIF
# Each "row" in the spritesheet has 4 columns and N sprite-rows stacked vertically
# Actual GIF frames layout: The GIF has multiple frames, each frame is a horizontal strip
# of all 3 knights × 4 directions. Let's load and analyze.

# Frame slices: (action_name, start_frame_in_row, count)
# Based on the sprite analysis:
# Idle: 0-7 (8 frames)
# Run/Move: 9-16 (8 frames)
# Defense: 40-44 (5 frames)  
# Attack: 63-70 (8 frames)
# Hit: 79-86 (8 frames)
# Special Attack: 105-119 (15 frames)
ACTIONS = [
    ("idle",           0,  8),
    ("run",            9,  8),
    ("defense",       40,  5),
    ("attack",        63,  8),
    ("hit",           79,  8),
    ("special_attack",105, 15),
]

# --- Color signature cache for masking neighbor pixels ---
def get_knight_palette(gif_frames, knight_name):
    """Sample pixels from the FIRST idle frame of the knight to build a color signature."""
    knight_row = KNIGHT_ROWS[knight_name]
    frame_idx = 0  # first idle frame
    total_cols = 4
    # We need to figure out layout - load frame 0 and check total size
    f = gif_frames[frame_idx]
    arr = np.array(f.convert("RGBA"))
    h, w = arr.shape[:2]
    # Knight row = which vertical band
    y0 = knight_row * CELL_H
    y1 = y0 + CELL_H
    # Use front direction (col 2)
    x0 = 2 * CELL_W
    x1 = x0 + CELL_W
    cell = arr[y0:y1, x0:x1]
    alpha = cell[:,:,3]
    mask = alpha > 60
    if not mask.any():
        return set()
    rgb = cell[:,:,:3][mask]
    # Build a set of dominant colors (cluster)
    palette = set()
    for r,g,b in rgb:
        # Quantize to avoid noise
        palette.add((r//16*16, g//16*16, b//16*16))
    return palette

def is_neighbor_pixel(r, g, b, neighbor_palettes):
    """Returns True if this pixel color matches a neighbor knight's signature."""
    q = (r//16*16, g//16*16, b//16*16)
    for pal in neighbor_palettes:
        if q in pal:
            return True
    return False

def mask_neighbors(cell_rgba, knight_name, neighbor_palettes):
    """Mask out pixels that belong to neighbor knights."""
    arr = cell_rgba.copy()
    mask = arr[:,:,3] > 0
    ys, xs = np.where(mask)
    for y, x in zip(ys, xs):
        r, g, b = arr[y, x, :3]
        q = (int(r)//16*16, int(g)//16*16, int(b)//16*16)
        for pal in neighbor_palettes:
            if q in pal:
                arr[y, x, 3] = 0
                break
    return arr

def compute_uniform_crop(frames_for_action):
    """
    Given a list of RGBA arrays, find the tightest bounding box
    that fits ALL frames (so feet stay at same y across frames).
    Returns (top, bottom, left, right) — pixel indices to keep.
    """
    all_top = []
    all_bottom = []
    all_left = []
    all_right = []
    
    for arr in frames_for_action:
        alpha = arr[:,:,3]
        rows_with_content = np.any(alpha > 0, axis=1)
        cols_with_content = np.any(alpha > 0, axis=0)
        if not rows_with_content.any():
            continue
        all_top.append(np.where(rows_with_content)[0][0])
        all_bottom.append(np.where(rows_with_content)[0][-1])
        all_left.append(np.where(cols_with_content)[0][0])
        all_right.append(np.where(cols_with_content)[0][-1])
    
    if not all_top:
        return None
    
    # Use min top and max bottom to include all content
    top    = max(0, min(all_top) - 2)
    bottom = min(frames_for_action[0].shape[0]-1, max(all_bottom) + 4)
    left   = max(0, min(all_left) - 2)
    right  = min(frames_for_action[0].shape[1]-1, max(all_right) + 2)
    
    return top, bottom, left, right

def main():
    print(f"Loading GIF: {GIF_PATH}")
    gif = Image.open(GIF_PATH)
    frames = []
    try:
        while True:
            frames.append(gif.copy().convert("RGBA"))
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    
    print(f"Total GIF frames: {len(frames)}")
    
    # Check layout
    f0 = frames[0]
    print(f"Frame size: {f0.size}")
    
    # Build palettes for each knight
    palettes = {}
    for kname in ["orange", "green", "blue"]:
        palettes[kname] = get_knight_palette(frames, kname)
        print(f"{kname} palette size: {len(palettes[kname])}")
    
    for kname, out_dir in OUT_DIRS.items():
        os.makedirs(out_dir, exist_ok=True)
        k_row = KNIGHT_ROWS[kname]
        
        # Neighbor palettes (other knights to mask out)
        neighbor_pals = [v for kk, v in palettes.items() if kk != kname]
        
        print(f"\nExporting {kname}...")
        
        for action_name, start_frame, frame_count in ACTIONS:
            for col, dir_name in COL_TO_DIR.items():
                # Extract all frames for this action+direction
                raw_frames = []
                for fi in range(start_frame, start_frame + frame_count):
                    if fi >= len(frames):
                        print(f"  WARNING: frame {fi} out of range ({len(frames)} total)")
                        break
                    gif_frame = np.array(frames[fi])
                    # Crop the cell for this knight+direction
                    y0 = k_row * CELL_H
                    y1 = y0 + CELL_H
                    x0 = col * CELL_W
                    x1 = x0 + CELL_W
                    cell = gif_frame[y0:y1, x0:x1].copy()
                    # Mask neighbor pixels
                    cell = mask_neighbors(cell, kname, neighbor_pals)
                    raw_frames.append(cell)
                
                if not raw_frames:
                    continue
                
                # Compute uniform tight crop across all frames
                crop = compute_uniform_crop(raw_frames)
                if crop is None:
                    print(f"  SKIP {action_name}-{dir_name}: no content")
                    continue
                
                top, bottom, left, right = crop
                
                for fi, arr in enumerate(raw_frames):
                    cropped = arr[top:bottom+1, left:right+1]
                    img = Image.fromarray(cropped.astype(np.uint8), "RGBA")
                    fname = f"{action_name}_{dir_name}_frame_{fi}.png"
                    img.save(os.path.join(out_dir, fname))
                
                print(f"  {action_name}-{dir_name}: {len(raw_frames)} frames, size {right-left+1}x{bottom-top+1}")
    
    print("\nDone! All knight frames exported.")

if __name__ == "__main__":
    main()
