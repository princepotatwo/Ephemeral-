from pathlib import Path
import json
import re
import sys

import UnityPy


ROOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)


def clean(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._ -]+", "_", name or "frame")[:140]


def main_texture_path_id(material_tree: dict) -> int:
    for key, val in material_tree.get("m_SavedProperties", {}).get("m_TexEnvs", []):
        if key == "_MainTex":
            return val["m_Texture"]["m_PathID"]
    return 0


summary = []
for bundle in sorted(ROOT.glob("tk2d*.bundle")):
    env = UnityPy.load(str(bundle))
    textures = {}
    materials = {}
    for obj in env.objects:
        if obj.type.name == "Texture2D":
            textures[obj.path_id] = obj.read().image.convert("RGBA")
        elif obj.type.name == "Material":
            materials[obj.path_id] = main_texture_path_id(obj.read_typetree())

    bundle_out = OUT / bundle.stem
    bundle_out.mkdir(parents=True, exist_ok=True)
    saved = 0
    names = []

    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        tree = obj.read_typetree()
        for idx, sprite in enumerate(tree.get("spriteDefinitions", [])):
            mat_id = sprite.get("material", {}).get("m_PathID")
            tex = textures.get(materials.get(mat_id))
            if tex is None:
                continue

            uvs = sprite.get("uvs") or []
            if len(uvs) < 2:
                continue
            xs = [uv["x"] for uv in uvs]
            ys = [uv["y"] for uv in uvs]
            w, h = tex.size
            left = max(0, min(w, round(min(xs) * w)))
            right = min(w, max(left + 1, round(max(xs) * w)))
            top = max(0, min(h, round((1 - max(ys)) * h)))
            bottom = min(h, max(top + 1, round((1 - min(ys)) * h)))
            crop = tex.crop((left, top, right, bottom))

            name = clean(sprite.get("name"))
            out = bundle_out / f"{idx:04d}_{name}.png"
            crop.save(out)
            saved += 1
            if len(names) < 20:
                names.append(out.name)

    summary.append({"bundle": bundle.name, "frames_saved": saved, "sample": names})

(OUT / "tk2d_crop_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
