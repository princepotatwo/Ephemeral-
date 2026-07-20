import os
from PIL import Image

artifact_dir = "/Users/jasminpingol/.gemini/antigravity/brain/8e0b068c-85f9-4213-a87a-da341f2e00f1"

def slice_and_gif(filepath, out_path, frame_w, frame_h, duration=150):
    try:
        im = Image.open(filepath).convert("RGBA")
        num_frames = im.width // frame_w
        frames = []
        for i in range(num_frames):
            f = im.crop((i * frame_w, 0, (i + 1) * frame_w, frame_h))
            f = f.resize((f.width * 2, f.height * 2), Image.NEAREST)
            
            alpha = f.split()[3]
            f_rgb = f.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
            mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
            f_rgb.paste(255, mask)
            f_rgb.info['transparency'] = 255
            frames.append(f_rgb)
        if frames:
            frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=duration, loop=0, disposal=2)
            print(f"Saved {out_path} ({num_frames} frames)")
    except Exception as e:
        print(f"Error: {e}")

slice_and_gif("assets/magic_traps/2 Barricades/Archer/D_Idle.png", f"{artifact_dir}/archer_idle_down.gif", 48, 48)
slice_and_gif("assets/magic_traps/2 Barricades/Archer/D_Attack.png", f"{artifact_dir}/archer_attack_down.gif", 48, 48)
