from PIL import Image

def analyze(filepath):
    im = Image.open(filepath).convert("RGBA")
    print(f"File: {filepath}, Size: {im.size}")
    
    # We want to find the exact frame boundaries.
    # Let's check typical grid widths: 32, 48, 54, 72, etc.
    # Let's count how many distinct non-empty vertical strips we can find,
    # or print out where the transparency boundaries lie.
    width, height = im.size
    
    # Let's print the bounding box of the whole image
    print("Bounding Box:", im.getbbox())
    
    # Let's test frame divisions:
    for divs in [3, 4, 6]:
        frame_w = width // divs
        print(f"--- Division into {divs} frames (width {frame_w}) ---")
        for i in range(divs):
            frame = im.crop((i * frame_w, 0, (i + 1) * frame_w, height))
            bbox = frame.getbbox()
            print(f"  Frame {i}: Bbox={bbox}")

analyze("assets/magic_traps/2 Barricades/D_1_Build.png")
analyze("assets/magic_traps/2 Barricades/D_1.png")
