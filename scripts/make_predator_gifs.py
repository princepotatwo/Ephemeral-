import os
from PIL import Image

def slice_and_gif(filepath, out_path, frame_w, frame_h, duration=100):
    try:
        if not os.path.exists(filepath):
            return
            
        im = Image.open(filepath).convert("RGBA")
        num_frames = im.width // frame_w
        
        frames = []
        for i in range(num_frames):
            frame = im.crop((i * frame_w, 0, (i + 1) * frame_w, frame_h))
            frame = frame.resize((frame_w * 3, frame_h * 3), Image.NEAREST)
            
            # Make background transparent for GIF
            alpha = frame.split()[3]
            frame_rgb = frame.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
            mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
            frame_rgb.paste(255, mask)
            frame_rgb.info['transparency'] = 255
            frames.append(frame_rgb)
            
        if frames:
            frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=duration, loop=0, disposal=2)
            print(f"Saved {out_path} ({num_frames} frames)")
            
    except Exception as e:
        print(f"Error making GIF for {filepath}: {e}")

artifact_dir = "/Users/jasminpingol/.gemini/antigravity/brain/8e0b068c-85f9-4213-a87a-da341f2e00f1"
# The predator plant sprites are usually 96x96 or 64x64. Let's check dimensions first.
im = Image.open("assets/predator_plants/PNG/Plant1/Idle/Plant1_Idle_full.png")
# If it's a strip of squares, frame_h is the height, and frame_w is also the height.
frame_h = im.height
frame_w = im.height
slice_and_gif("assets/predator_plants/PNG/Plant1/Idle/Plant1_Idle_full.png", f"{artifact_dir}/preview_predator_idle.gif", frame_w, frame_h, 150)
slice_and_gif("assets/predator_plants/PNG/Plant1/Attack/Plant1_Attack_full.png", f"{artifact_dir}/preview_predator_attack.gif", frame_w, frame_h, 100)
slice_and_gif("assets/predator_plants/PNG/Plant1/Death/Plant1_Death_full.png", f"{artifact_dir}/preview_predator_death.gif", frame_w, frame_h, 100)
