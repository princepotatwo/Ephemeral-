import os
import shutil

out = "assets/plants/magic_barricade"
os.makedirs(out, exist_ok=True)
count = 0
for src in ["D_1.png", "S_1.png", "U_1.png"]:
    filepath = f"assets/magic_traps/2 Barricades/{src}"
    if os.path.exists(filepath):
        shutil.copy(filepath, f"{out}/frame_{count}.png")
        count += 1
print(f"Copied {count} barricades")
