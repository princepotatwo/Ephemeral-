#!/usr/bin/env python3
import os
import glob
import json
import traceback
from PIL import Image

ASSETS_DIR = "/Users/jasminpingol/Documents/Codex/assets"
META_PATH = os.path.join(ASSETS_DIR, "spritesheets_metadata.json")

def main():
    with open(META_PATH, "r") as f:
        meta = json.load(f)
        
    print("Starting synchronous pixel-perfect grid downscaling for large characters...", flush=True)

    optimized_count = 0
    skipped_count = 0
    
    for char_name in sorted(meta.keys()):
        try:
            char_dir = os.path.join(ASSETS_DIR, char_name)
            if not os.path.isdir(char_dir):
                continue
                
            anims = meta[char_name]["animations"]
            if not anims:
                continue
                
            # Quick check: original frame size
            canonical_w, canonical_h = None, None
            for priority in ["idle_front_frame_0.png", "idle_down_frame_0.png", "attack_front_frame_0.png"]:
                p_path = os.path.join(char_dir, priority)
                if os.path.exists(p_path):
                    try:
                        with Image.open(p_path) as test_img:
                            canonical_w, canonical_h = test_img.size
                        break
                    except Exception:
                        pass
                        
            if not canonical_w:
                # default fallback
                canonical_w, canonical_h = 210, 148

            max_count = max(a["count"] for a in anims.values())
            num_rows = max(a["row"] for a in anims.values()) + 1
            
            orig_sheet_w = max_count * canonical_w
            orig_sheet_h = num_rows * canonical_h
            orig_mp = (orig_sheet_w * orig_sheet_h) / 1000000.0
            
            # If the spritesheet is small, it does not need to be repacked because it is already at 100% scale!
            # Also check if scaleMult exists (meaning we downscaled it earlier and need to restore it)
            has_scale_mult = "scaleMult" in meta[char_name]
            
            if orig_mp <= 3.5 and not has_scale_mult:
                skipped_count += 1
                continue
                
            # Process large character
            frames = [f for f in glob.glob(os.path.join(char_dir, "*.png")) if not f.endswith("spritesheet.png")]
            if not frames:
                continue
                
            ratio = 1.0 # Restore to 100% scale
            
            target_fw = int(canonical_w * ratio)
            target_fh = int(canonical_h * ratio)
            
            sheet_w = max_count * target_fw
            sheet_h = num_rows * target_fh
            
            spritesheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
            
            for anim_name, a_info in anims.items():
                row_idx = a_info["row"]
                parts = anim_name.split("-")
                if len(parts) == 2:
                    mode, direction = parts
                    for col_idx in range(a_info["count"]):
                        frame_path = os.path.join(char_dir, f"{mode}_{direction}_frame_{col_idx}.png")
                        if os.path.exists(frame_path):
                            try:
                                with Image.open(frame_path) as img:
                                    dx = col_idx * target_fw
                                    dy = row_idx * target_fh
                                    # Copy directly at 100% scale
                                    spritesheet.paste(img, (dx, dy))
                            except Exception:
                                pass
                                
            sheet_path = os.path.join(char_dir, "spritesheet.png")
            spritesheet.save(sheet_path, "PNG")
            
            meta[char_name]["frameWidth"] = target_fw
            meta[char_name]["frameHeight"] = target_fh
            meta[char_name].pop("scaleMult", None) # Clean up scaleMult!
                
            print(f"  ✓ Restored {char_name:25s} to 100% scale grid: {target_fw}x{target_fh}", flush=True)
            optimized_count += 1
        except Exception as e:
            print(f"  ❌ Error processing {char_name}: {e}", flush=True)
            traceback.print_exc()

    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)
        
    print(f"\nSuccessfully repacked {optimized_count} characters, skipped {skipped_count} small characters!", flush=True)

if __name__ == "__main__":
    main()
