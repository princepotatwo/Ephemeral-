from pathlib import Path
import json
import re
import sys

import UnityPy


ROOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)


def clean(name: str) -> str:
    name = name or "unnamed"
    return re.sub(r"[^A-Za-z0-9._ -]+", "_", name)[:160]


summary = []

for bundle in sorted(ROOT.glob("*.bundle")):
    bundle_out = OUT / bundle.stem
    bundle_out.mkdir(parents=True, exist_ok=True)
    counts = {}
    saved = []
    try:
        env = UnityPy.load(str(bundle))
    except Exception as exc:
        summary.append({"bundle": bundle.name, "error": str(exc)})
        continue

    for obj in env.objects:
        typ = obj.type.name
        counts[typ] = counts.get(typ, 0) + 1
        if typ not in {"Texture2D", "Sprite"}:
            continue
        try:
            data = obj.read()
            image = getattr(data, "image", None)
            if image is None:
                continue
            name = clean(getattr(data, "name", typ))
            path = bundle_out / f"{name}_{obj.path_id}.png"
            image.save(path)
            saved.append(str(path.relative_to(OUT)))
        except Exception as exc:
            saved.append(f"FAILED {typ} {obj.path_id}: {exc}")

    summary.append({"bundle": bundle.name, "counts": counts, "saved": saved[:50], "saved_count": len(saved)})

(OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
