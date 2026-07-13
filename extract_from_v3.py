#!/usr/bin/env python3
"""Extract frames from v3 GIFs into game assets using the already-isolated sprites."""
import os
from PIL import Image

PREVIEWS_DIR = "/Users/jasminpingol/.gemini/antigravity/brain/8e0b068c-85f9-4213-a87a-da341f2e00f1/knight1_previews"
ASSETS_BASE  = "/Users/jasminpingol/Documents/Codex/assets"

COLOR_MAP  = {"orange": "knight_orange", "green": "knight_green", "blue": "knight_blue"}
ACTION_MAP = {"idle": "idle", "move": "run", "defense": "defense",
              "attack": "attack", "hit": "hit", "special": "special_attack"}
DIR_MAP    = {"right": "right", "left": "left", "down": "front", "up": "back"}

for fname in sorted(os.listdir(PREVIEWS_DIR)):
    if not fname.endswith("_v3.gif"):
        continue
    stem  = fname.replace("_v3.gif", "")   # e.g. orange_special_attack_right
    parts = stem.split("_")
    color = parts[0]
    if color not in COLOR_MAP:
        continue

    direction = parts[-1]
    if direction not in DIR_MAP:
        continue

    action_parts = parts[1:-1]                   # everything between color and direction
    # handle "special_attack" vs single-word actions
    action_key = action_parts[0] if len(action_parts) == 1 else action_parts[0]
    if action_parts == ["special", "attack"]:
        action_key = "special"
    elif len(action_parts) == 1:
        action_key = action_parts[0]
    else:
        action_key = "_".join(action_parts)      # fallback

    if action_key not in ACTION_MAP:
        print(f"SKIP (unknown action '{action_key}'): {fname}")
        continue

    game_base   = COLOR_MAP[color]
    game_action = ACTION_MAP[action_key]
    game_dir    = DIR_MAP[direction]
    out_dir     = os.path.join(ASSETS_BASE, game_base)
    os.makedirs(out_dir, exist_ok=True)

    gif = Image.open(os.path.join(PREVIEWS_DIR, fname))
    frame_idx = 0
    try:
        while True:
            frame = gif.copy().convert("RGBA")
            out_path = os.path.join(out_dir, f"{game_action}_{game_dir}_frame_{frame_idx}.png")
            frame.save(out_path)
            frame_idx += 1
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass

    print(f"  {fname} → {game_base}/{game_action}_{game_dir}_frame_*.png ({frame_idx} frames)")

print("\nDone.")
