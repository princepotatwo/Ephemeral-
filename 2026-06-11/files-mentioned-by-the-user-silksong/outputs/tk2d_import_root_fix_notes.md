# TK2D / Unity Import Root Fix Notes

## What was actually wrong

The APK uses Unity Addressables/AssetBundles and 2D Toolkit (`tk2d`) sprite collections. The atlas PNG is not meant to be displayed directly. Unity/tk2d renders a mesh:

- `positions`: local sprite geometry.
- `uvs`: atlas coordinates per vertex.
- `indices`: sprite triangles.
- `flipped`: atlas region was packed rotated on its side.
- collection scale: `pixelsPerUnit = invOrthoSize * halfTargetHeight`.

For the Hornet `Knight` collection, `invOrthoSize = 2.0`, `halfTargetHeight = 32.0`, so `pixelsPerUnit = 64`.

The first extractor treated the UV rectangle like a normal crop. That ignores rotated atlas packing, so some frames came out sideways/upside down. The later v19 fix normalized individual frames, but the root fix is to bake the tk2d metadata correctly before any animation mapping.

## Correct sprite bake rule

For each `tk2dSpriteDefinition`:

1. Find the atlas texture from the sprite material `_MainTex`.
2. Crop the atlas AABB from the sprite `uvs`.
3. If `sprite.flipped == 1`, unrotate the crop. In this APK/Pillow coordinate space, `rotate(270, expand=True)` produced the consistent tk2d orientation.
4. Resize to the intended local sprite size:
   - `width = (max(position.x) - min(position.x)) * pixelsPerUnit`
   - `height = (max(position.y) - min(position.y)) * pixelsPerUnit`
5. Keep offset/pivot metadata from `positions`; do not blindly center every frame unless the target game intentionally wants a shared display canvas.
6. For a side-view character, generate one facing direction from the baked sprites and mirror at runtime or export mirrored copies consistently.

## Correct animation import rule

Do not rely only on sorted filenames.

The APK also has many `animations2_...controller` and `.anim` bundles. Controllers can contain state names, and `AnimationClip` assets may contain timing/events and sometimes sprite pointer curves. The real pipeline should:

1. Resolve Addressables dependencies for the character/controller bundle.
2. Read `AnimatorController` state names from `m_TOS`/controller data.
3. Read `AnimationClip` timing (`m_SampleRate`, events, curves).
4. When present, read sprite swaps from `m_PPtrCurves`.
5. Fall back to filename grouping only when no clip data exists, and then validate orientation/frame order with an audit sheet.

## Practical importer shape

Build a reusable importer with two phases:

```text
extractTk2dCollection(bundle):
  decode textures/materials
  ppu = invOrthoSize * halfTargetHeight
  for each spriteDefinition:
    bakedPng, metadata = bakeSprite(spriteDefinition, ppu)
  write sprite manifest by sprite name

extractAnimationBundles(apk, nameFilter):
  load related .controller/.anim/.prefab bundles
  resolve dependencies from Addressables catalog/bundle metadata
  emit animation manifest: state name -> ordered sprite names, fps, loop, events
```

Then the game should import from the manifest, not from ad hoc filename guesses.
