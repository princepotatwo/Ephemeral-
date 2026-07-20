import os
import shutil

def copy_magic(src_dir, dest_name):
    out = f"assets/plants/{dest_name}"
    os.makedirs(out, exist_ok=True)
    count = 0
    for i in range(1, 5):
        src = f"{src_dir}/{i}.png"
        if os.path.exists(src):
            shutil.copy(src, f"{out}/frame_{count}.png")
            count += 1
    print(f"Copied {count} frames to {out}")

copy_magic("assets/magic_traps/1 Spikes", "magic_spike")
copy_magic("assets/magic_traps/2 Barricades", "magic_barricade")
copy_magic("assets/magic_traps/4 Barrel", "magic_barrel")
