import os
from PIL import Image

def slice_trap(filepath, output_name, frame_width=32, frame_height=32):
    try:
        im = Image.open(filepath)
    except Exception as e:
        print(f"Could not open {filepath}: {e}")
        return

    out_dir = f"assets/plants/{output_name}"
    os.makedirs(out_dir, exist_ok=True)
    
    # If the trap height is more than 32 (e.g. 41), use the actual height
    frame_height = im.height
    
    num_frames = im.width // frame_width
    for i in range(num_frames):
        left = i * frame_width
        right = left + frame_width
        frame = im.crop((left, 0, right, frame_height))
        frame.save(f"{out_dir}/frame_{i}.png")
    
    print(f"Sliced {filepath} into {num_frames} frames in {out_dir}")

slice_trap("assets/animated_traps/Spike Trap.png", "trap_spike")
slice_trap("assets/animated_traps/Bear_Trap.png", "trap_bear")
slice_trap("assets/animated_traps/Fire_Trap.png", "trap_fire")
