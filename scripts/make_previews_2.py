import os
from PIL import Image

artifact_dir = "/Users/jasminpingol/.gemini/antigravity/brain/8e0b068c-85f9-4213-a87a-da341f2e00f1"

def make_gif(frame_dir, out_path, num_frames, duration=100):
    try:
        frames = []
        for i in range(num_frames):
            frame_path = f"{frame_dir}/frame_{i}.png"
            if os.path.exists(frame_path):
                im = Image.open(frame_path).convert("RGBA")
                im = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
                alpha = im.split()[3]
                im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
                mask = Image.eval(alpha, lambda a: 255 if a <=128 else 0)
                im.paste(255, mask)
                im.info['transparency'] = 255
                frames.append(im)
        if frames:
            frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=duration, loop=0, disposal=2)
            print(f"Saved {out_path}")
    except Exception as e:
        print(f"Error making GIF for {frame_dir}: {e}")

def make_grid(frame_dir, out_path, max_frames=20):
    try:
        images = []
        for i in range(max_frames):
            frame_path = f"{frame_dir}/frame_{i}.png"
            if os.path.exists(frame_path):
                im = Image.open(frame_path).convert("RGBA")
                im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
                images.append(im)
        
        if not images: return
        
        # Make a 5x4 grid
        grid_w = images[0].width * 5
        grid_h = images[0].height * ((len(images) + 4) // 5)
        grid = Image.new('RGBA', (grid_w, grid_h), (0,0,0,0))
        
        for i, im in enumerate(images):
            x = (i % 5) * im.width
            y = (i // 5) * im.height
            grid.paste(im, (x, y), im)
            
        grid.save(out_path)
        print(f"Saved grid to {out_path}")
    except Exception as e:
        print(f"Error making grid for {frame_dir}: {e}")

make_gif("assets/plants/magic_spike", f"{artifact_dir}/preview_magic_spike.gif", 4, 150)
make_grid("assets/plants/magic_barricade", f"{artifact_dir}/preview_magic_barricade.png", 3)
make_grid("assets/plants/magic_barrel", f"{artifact_dir}/preview_magic_barrel.png", 3)
make_grid("assets/plants/ponk_plants_collection", f"{artifact_dir}/preview_ponk_plants.png", 20)
