from PIL import Image
import os

artifact_dir = "/Users/jasminpingol/.gemini/antigravity/brain/8e0b068c-85f9-4213-a87a-da341f2e00f1"

def test_slice(filename, frame_w, frame_h, out_gif):
    im = Image.open(filename).convert("RGBA")
    frames = []
    num_frames = im.width // frame_w
    for i in range(num_frames):
        f = im.crop((i * frame_w, 0, (i + 1) * frame_w, frame_h))
        # Scale up
        f = f.resize((f.width * 2, f.height * 2), Image.NEAREST)
        
        # Transparent background for GIF
        alpha = f.split()[3]
        f_rgb = f.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        mask = Image.eval(alpha, lambda a: 255 if a <= 128 else 0)
        f_rgb.paste(255, mask)
        f_rgb.info['transparency'] = 255
        frames.append(f_rgb)
    if frames:
        frames[0].save(out_gif, save_all=True, append_images=frames[1:], duration=150, loop=0, disposal=2)
        print(f"Saved {out_gif} with {num_frames} frames of {frame_w}x{frame_h}")

# Test both 54x64 (4 frames) and 36x64 (6 frames)
test_slice("assets/magic_traps/2 Barricades/D_1_Build.png", 54, 64, f"{artifact_dir}/barricade_test_54.gif")
test_slice("assets/magic_traps/2 Barricades/D_1_Build.png", 36, 64, f"{artifact_dir}/barricade_test_36.gif")
