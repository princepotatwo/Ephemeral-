import os
from PIL import Image

def slice_grid_row(filepath, out_dir, row_idx, frame_w, frame_h, num_frames, reverse=False):
    if not os.path.exists(filepath):
        print("Missing file:", filepath)
        return
    os.makedirs(out_dir, exist_ok=True)
    im = Image.open(filepath).convert("RGBA")
    
    frames = []
    for i in range(num_frames):
        f = im.crop((i * frame_w, row_idx * frame_h, (i + 1) * frame_w, (row_idx + 1) * frame_h))
        frames.append(f)
        
    if reverse:
        frames.reverse()
        
    for i, frame in enumerate(frames):
        frame.save(os.path.join(out_dir, f"frame_{i}.png"))
    print(f"Sliced {filepath} row {row_idx} into {len(frames)} frames in {out_dir}")

def slice_strip(filepath, out_dir, frame_w, frame_h, reverse=False):
    if not os.path.exists(filepath):
        print("Missing file:", filepath)
        return
    os.makedirs(out_dir, exist_ok=True)
    im = Image.open(filepath).convert("RGBA")
    num_frames = im.width // frame_w
    
    frames = []
    for i in range(num_frames):
        f = im.crop((i * frame_w, 0, (i + 1) * frame_w, frame_h))
        frames.append(f)
        
    if reverse:
        frames.reverse()
        
    for i, frame in enumerate(frames):
        frame.save(os.path.join(out_dir, f"frame_{i}.png"))
    print(f"Sliced {filepath} into {len(frames)} frames in {out_dir}")

# 1. Spikes (32x32 cells, 6 frames each)
for v in [1, 2, 3, 4]:
    slice_strip(f"assets/magic_traps/1 Spikes/{v}.png", 
                f"assets/plants/magic_spike_{v}", 32, 32)

# 2. Lightning (160x160 cells, 4 frames each)
for v in [1, 2, 3, 4]:
    slice_strip(f"assets/magic_traps/3 Lightning/{v}.png", 
                f"assets/plants/magic_lightning_{v}", 160, 160)

# 3. Barricades (36x64 cells)
dirs_map = {"D": "down", "S": "side", "U": "up"}
for v in [1, 2, 3, 4]:
    for prefix, d_name in dirs_map.items():
        # Idle
        slice_strip(f"assets/magic_traps/2 Barricades/{prefix}_{v}.png", 
                    f"assets/plants/magic_barricade_{v}_{d_name}", 36, 64)
        # Build
        slice_strip(f"assets/magic_traps/2 Barricades/{prefix}_{v}_Build.png", 
                    f"assets/plants/magic_barricade_{v}_{d_name}_build", 36, 64)
        # Destroy
        slice_strip(f"assets/magic_traps/2 Barricades/{prefix}_{v}_Destroy.png", 
                    f"assets/plants/magic_barricade_{v}_{d_name}_destroy", 36, 64)

# 4. Single Magic Barrel (48x48 cells)
slice_strip("assets/magic_traps/4 Barrel/1.png", "assets/plants/magic_barrel_idle", 48, 48)
slice_strip("assets/magic_traps/4 Barrel/2.png", "assets/plants/magic_barrel_build", 48, 48)
slice_strip("assets/magic_traps/4 Barrel/3.png", "assets/plants/magic_barrel_destroy", 48, 48)
for v in [1, 2, 3]:
    slice_strip(f"assets/magic_traps/4 Barrel/Boom{v}.png", f"assets/plants/magic_barrel_boom_{v}", 48, 48)

# 5. Archer (48x48 cells)
for prefix, d_name in dirs_map.items():
    slice_strip(f"assets/magic_traps/2 Barricades/Archer/{prefix}_Idle.png", 
                f"assets/plants/trap_archer_{d_name}_idle", 48, 48)
    slice_strip(f"assets/magic_traps/2 Barricades/Archer/{prefix}_Attack.png", 
                f"assets/plants/trap_archer_{d_name}_attack", 48, 48)

# 6. Predator Plants (Plant 1, 2, 3) - Corrected 64x64 cell slicing in 4 directions
pred_dirs = ["down", "up", "left", "right"]
for v in [1, 2, 3]:
    for idx, d_name in enumerate(pred_dirs):
        slice_grid_row(f"assets/predator_plants/PNG/Plant{v}/Idle/Plant{v}_Idle_full.png", 
                       f"assets/plants/trap_predator_idle_{v}_{d_name}", idx, 64, 64, 4)
        slice_grid_row(f"assets/predator_plants/PNG/Plant{v}/Attack/Plant{v}_Attack_full.png", 
                       f"assets/plants/trap_predator_attack_{v}_{d_name}", idx, 64, 64, 7)
        slice_grid_row(f"assets/predator_plants/PNG/Plant{v}/Death/Plant{v}_Death_full.png", 
                       f"assets/plants/trap_predator_grow_{v}_{d_name}", idx, 64, 64, 10, reverse=True)

# 7. Missed Traps from Traps.zip
slice_strip("assets/animated_traps/Pit_Trap_Spikes.png", "assets/plants/trap_pit_spikes", 32, 32)
slice_strip("assets/animated_traps/Push_Trap_Front.png", "assets/plants/trap_push_front", 32, 32)
slice_strip("assets/animated_traps/Push_Trap_Right.png", "assets/plants/trap_push_right", 32, 32)

