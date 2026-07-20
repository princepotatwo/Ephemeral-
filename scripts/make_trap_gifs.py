import os
from PIL import Image

def make_gif(frame_dir, out_path, num_frames, duration=100):
    try:
        frames = []
        for i in range(num_frames):
            frame_path = f"{frame_dir}/frame_{i}.png"
            if os.path.exists(frame_path):
                # Scale it up 3x for easier viewing
                im = Image.open(frame_path).convert("RGBA")
                im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
                
                # Convert to palette for GIF
                # Background needs to be transparent
                alpha = im.split()[3]
                im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
                mask = Image.eval(alpha, lambda a: 255 if a <=128 else 0)
                im.paste(255, mask)
                im.info['transparency'] = 255
                frames.append(im)
                
        if frames:
            frames[0].save(
                out_path,
                save_all=True,
                append_images=frames[1:],
                duration=duration,
                loop=0,
                disposal=2
            )
            print(f"Saved {out_path}")
    except Exception as e:
        print(f"Error making GIF for {frame_dir}: {e}")

artifact_dir = "/Users/jasminpingol/.gemini/antigravity/brain/8e0b068c-85f9-4213-a87a-da341f2e00f1"
make_gif("assets/plants/trap_spike", f"{artifact_dir}/preview_trap_spike.gif", 14, 100)
make_gif("assets/plants/trap_bear", f"{artifact_dir}/preview_trap_bear.gif", 4, 150)
make_gif("assets/plants/trap_fire", f"{artifact_dir}/preview_trap_fire.gif", 14, 100)
