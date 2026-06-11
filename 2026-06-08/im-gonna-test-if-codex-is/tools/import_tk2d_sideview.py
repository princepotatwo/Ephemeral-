#!/usr/bin/env python3
"""Bake tk2d side-view frames from Unity asset bundles.

The Silksong APK stores many sprite frames rotated inside tk2d atlases. This
script reads tk2dSpriteDefinition metadata, crops by UV bounds, applies the
tk2d rotated-packing flag, and pastes the trimmed image back onto the original
untrimmed canvas so animation pivots stay stable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import UnityPy
from PIL import Image, ImageOps


DIRECTIONS = ("front", "back", "left", "right")
MODES = ("idle", "run", "attack")
DEFAULT_BUNDLE_ROOT = Path(
    os.environ.get("TK2D_BUNDLE_ROOT", "work/tk2d_bundles")
)


@dataclass(frozen=True)
class FrameGroup:
    prefix: str
    limit: int | None = None
    offset: int = 0


@dataclass(frozen=True)
class CharacterSpec:
    asset_id: str
    bundle: str
    groups: dict[str, FrameGroup]
    source_facing: str = "left"


CHARACTERS = (
    CharacterSpec(
        "silksong_hornet",
        "extract/tk2d_assets_assets_collections_knightdata_4e7b296df1048c2dd41251a3e1d42be7.bundle",
        {
            "idle": FrameGroup("idle", limit=6),
            "run": FrameGroup("Hornet_run_new", limit=10),
            "attack": FrameGroup("Hornet_slashes", limit=6),
        },
    ),
    CharacterSpec(
        "silksong_moss_creep",
        "candidate_extract/tk2d_assets_assets_collections_mosscreepclndata_348fc9b28ecde055616194914b48fe56.bundle",
        {
            "idle": FrameGroup("Creep_idle"),
            "run": FrameGroup("Creep_antic_turn"),
            "attack": FrameGroup("Creep_talk"),
        },
    ),
    CharacterSpec(
        "silksong_bone_worm",
        "candidate_extract/tk2d_assets_assets_collections_bonewormclndata_34458524125edbc76ff077d3431a703d.bundle",
        {
            "idle": FrameGroup("BW_crawl"),
            "run": FrameGroup("BW_crawl"),
            "attack": FrameGroup("BW_dig_away"),
        },
    ),
    CharacterSpec(
        "silksong_moss_crawler",
        "candidate_extract/tk2d_assets_assets_collections_hornetenemies_mossbonecrawlerclndata_12d8869c8484286d03a1b76eeaa3e995.bundle",
        {
            "idle": FrameGroup("MB_crawler_eat_idle"),
            "run": FrameGroup("MB_crawler"),
            "attack": FrameGroup("MB_crawler_sing"),
        },
    ),
    CharacterSpec(
        "silksong_staff_pilgrim",
        "candidate_extract/tk2d_assets_assets_collections_pilgrimstaffwielderclndata_a55acfcea772d97478576833807f3260.bundle",
        {
            "idle": FrameGroup("PS_idle"),
            "run": FrameGroup("PS_walk"),
            "attack": FrameGroup("PS_attack"),
        },
    ),
    CharacterSpec(
        "silksong_ladybug",
        "candidate_extract/tk2d_assets_assets_collections_hornetnpcs_a5d409f90ebec10ab2c8f5b27154e11e.bundle",
        {
            "idle": FrameGroup("Lady_Bug_small_rest_sing"),
            "run": FrameGroup("Lady_Bug_small_new"),
            "attack": FrameGroup("Lady_Bug_Small_new_turn"),
        },
    ),
    CharacterSpec(
        "silksong_pilgrim_hiker",
        "candidate_extract/tk2d_assets_assets_collections_hornetenemies_pilgrimhikerclndata_eec4a607c7d9b7fbc66c0a2ffde44e67.bundle",
        {
            "idle": FrameGroup("idle"),
            "run": FrameGroup("walk"),
            "attack": FrameGroup("attack_slash"),
        },
    ),
    CharacterSpec(
        "silksong_lifeblood_worm",
        "candidate_extract/tk2d_assets_assets_collections_bonewormbluebloodclndata_5a4f80b7c77aa54210919ba531ba4ec9.bundle",
        {
            "idle": FrameGroup("idle_wiggle"),
            "run": FrameGroup("charge_attack_dig_away"),
            "attack": FrameGroup("attack_spit"),
        },
    ),
    CharacterSpec(
        "silksong_shakra_rest",
        "candidate_extract/tk2d_assets_assets_collections_shakrarestclndata_e184a827689c02c5d9d363820135931b.bundle",
        {
            "idle": FrameGroup("Black_Thread_Rest"),
            "run": FrameGroup("Black_Thread_Rest"),
            "attack": FrameGroup("Black_Thread_Rest", limit=10),
        },
    ),
)


def main_texture_path_id(material_tree: dict) -> int:
    for key, val in material_tree.get("m_SavedProperties", {}).get("m_TexEnvs", []):
        if key == "_MainTex":
            return int(val["m_Texture"]["m_PathID"])
    return 0


def trailing_number(name: str) -> int:
    match = re.search(r"(\d+)$", name)
    return int(match.group(1)) if match else -1


def group_names(sprite_names: Iterable[str], group: FrameGroup) -> list[str]:
    names = [
        name
        for name in sprite_names
        if name
        and name.startswith(group.prefix)
        and (trailing_number(name) >= 0 or name == group.prefix)
    ]
    names.sort(key=lambda name: (trailing_number(name), name))
    names = names[group.offset :]
    if group.limit is not None:
        names = names[: group.limit]
    return names


def load_collection(bundle: Path) -> tuple[dict[str, Image.Image], dict]:
    env = UnityPy.load(str(bundle))
    textures = {}
    materials = {}
    metadata = {"bundle": str(bundle), "collections": []}

    for obj in env.objects:
        if obj.type.name == "Texture2D":
            texture = obj.read().image.convert("RGBA")
            textures[obj.path_id] = texture
        elif obj.type.name == "Material":
            materials[obj.path_id] = main_texture_path_id(obj.read_typetree())

    frames = {}
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        tree = obj.read_typetree()
        sprite_definitions = tree.get("spriteDefinitions") or []
        if not sprite_definitions:
            continue
        metadata["collections"].append(
            {
                "name": tree.get("spriteCollectionName", ""),
                "sprite_count": len(sprite_definitions),
                "flipped_count": sum(1 for sprite in sprite_definitions if sprite.get("flipped")),
            }
        )
        for sprite in sprite_definitions:
            name = sprite.get("name")
            if not name:
                continue
            material_id = sprite.get("material", {}).get("m_PathID")
            texture = textures.get(materials.get(material_id))
            if texture is None:
                continue
            baked = bake_sprite(texture, sprite)
            if baked is not None:
                frames[name] = baked

    return frames, metadata


def bake_sprite(texture: Image.Image, sprite: dict) -> Image.Image | None:
    uvs = sprite.get("uvs") or []
    if len(uvs) < 2:
        return None

    tex_w, tex_h = texture.size
    xs = [uv["x"] for uv in uvs]
    ys = [uv["y"] for uv in uvs]
    left = max(0, min(tex_w, round(min(xs) * tex_w)))
    right = min(tex_w, max(left + 1, round(max(xs) * tex_w)))
    top = max(0, min(tex_h, round((1 - max(ys)) * tex_h)))
    bottom = min(tex_h, max(top + 1, round((1 - min(ys)) * tex_h)))
    crop = texture.crop((left, top, right, bottom))

    if sprite.get("flipped"):
        crop = crop.rotate(90, expand=True)

    bounds = sprite.get("boundsData") or []
    untrimmed = sprite.get("untrimmedBoundsData") or []
    if len(bounds) < 2 or len(untrimmed) < 2:
        return crop

    world_per_pixel = sprite.get("texelSize", {}).get("x") or 0
    ppu = round(1 / world_per_pixel) if world_per_pixel else 64
    bw = max(1, round(bounds[1]["x"] * ppu))
    bh = max(1, round(bounds[1]["y"] * ppu))
    uw = max(bw, round(untrimmed[1]["x"] * ppu))
    uh = max(bh, round(untrimmed[1]["y"] * ppu))

    if crop.size != (bw, bh):
        crop = crop.resize((bw, bh), Image.Resampling.LANCZOS)

    bcx, bcy = bounds[0]["x"], bounds[0]["y"]
    ucx, ucy = untrimmed[0]["x"], untrimmed[0]["y"]
    trim_left = bcx - bounds[1]["x"] / 2
    trim_top = bcy + bounds[1]["y"] / 2
    untrim_left = ucx - untrimmed[1]["x"] / 2
    untrim_top = ucy + untrimmed[1]["y"] / 2
    paste_x = round((trim_left - untrim_left) * ppu)
    paste_y = round((untrim_top - trim_top) * ppu)

    canvas = Image.new("RGBA", (uw, uh), (0, 0, 0, 0))
    canvas.alpha_composite(crop, (paste_x, paste_y))
    return canvas


def write_character(spec: CharacterSpec, frames: dict[str, Image.Image], out_root: Path) -> dict:
    out_dir = out_root / spec.asset_id
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    counts = {}
    for mode in MODES:
        group = spec.groups[mode]
        names = group_names(frames.keys(), group)
        if not names and mode != "idle":
            names = group_names(frames.keys(), spec.groups["idle"])
        if not names:
            raise RuntimeError(f"{spec.asset_id}: no frames for {mode} prefix {group.prefix!r}")

        counts[mode] = len(names)
        for index, name in enumerate(names):
            source = frames[name]
            left = source if spec.source_facing == "left" else ImageOps.mirror(source)
            right = ImageOps.mirror(source) if spec.source_facing == "left" else source
            left.save(out_dir / f"{mode}_left_frame_{index}.png")
            right.save(out_dir / f"{mode}_right_frame_{index}.png")
            right.save(out_dir / f"{mode}_front_frame_{index}.png")
            right.save(out_dir / f"{mode}_back_frame_{index}.png")

    return {
        "id": spec.asset_id,
        "counts": counts,
        "groups": {mode: spec.groups[mode].prefix for mode in MODES},
    }


def make_preview(manifest: list[dict], out_root: Path, preview_path: Path) -> None:
    thumbs = []
    labels = []
    for item in manifest:
        asset_id = item["id"]
        for mode in MODES:
            path = out_root / asset_id / f"{mode}_right_frame_0.png"
            if path.exists():
                img = Image.open(path).convert("RGBA")
                img.thumbnail((88, 88), Image.Resampling.LANCZOS)
                tile = Image.new("RGBA", (96, 108), (246, 242, 232, 255))
                tile.alpha_composite(img, ((96 - img.width) // 2, 12 + (76 - img.height) // 2))
                thumbs.append(tile.convert("RGB"))
                labels.append(f"{asset_id.replace('silksong_', '')} {mode}")

    if not thumbs:
        return

    cols = 6
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 96, rows * 108), (32, 30, 28))
    for i, tile in enumerate(thumbs):
        sheet.paste(tile, ((i % cols) * 96, (i // cols) * 108))
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(preview_path, quality=92)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-root", type=Path, default=DEFAULT_BUNDLE_ROOT)
    parser.add_argument("--game-root", type=Path, required=True)
    parser.add_argument("--preview", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_roots = [args.game_root / "assets", args.game_root / "outputs" / "assets"]
    manifest = []
    cache: dict[Path, tuple[dict[str, Image.Image], dict]] = {}

    for spec in CHARACTERS:
        bundle = args.bundle_root / spec.bundle
        if bundle not in cache:
            cache[bundle] = load_collection(bundle)
        frames, metadata = cache[bundle]
        result = None
        for out_root in out_roots:
            result = write_character(spec, frames, out_root)
        assert result is not None
        result["bundle"] = spec.bundle
        result["collection_metadata"] = metadata["collections"]
        manifest.append(result)

    for out_root in out_roots:
        (out_root / "silksong_import_manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )

    if args.preview:
        make_preview(manifest, out_roots[-1], args.preview)

    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
