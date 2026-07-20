import os
from PIL import Image

def slice_grid(filepath, out_dir, tile_w=32, tile_h=32):
    try:
        im = Image.open(filepath)
    except Exception as e:
        print(f"Could not open {filepath}: {e}")
        return

    os.makedirs(out_dir, exist_ok=True)
    
    cols = im.width // tile_w
    rows = im.height // tile_h
    count = 0
    
    for r in range(rows):
        for c in range(cols):
            left = c * tile_w
            upper = r * tile_h
            right = left + tile_w
            lower = upper + tile_h
            
            frame = im.crop((left, upper, right, lower))
            
            # Check if frame is completely transparent
            alpha = frame.split()[3] if frame.mode == 'RGBA' else None
            if alpha:
                extrema = alpha.getextrema()
                if extrema == (0, 0):
                    continue # Skip empty frames
                    
            frame.save(f"{out_dir}/frame_{count}.png")
            count += 1
            
    print(f"Sliced {filepath} into {count} non-empty frames in {out_dir}")

slice_grid("assets/ponk_plants/Plant.png", "assets/plants/ponk_plants_collection")
