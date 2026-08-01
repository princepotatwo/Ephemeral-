# Changelog

## July 26, 2026
- Solved character/Knight visibility bug (dynamic sheet loading checks before offscreen caching).

## July 27, 2026
- Setup basic server.py utility and Bubu spritesheet preview tester.

## July 28, 2026
- Refactored character roster to remap standard Bubu and Dudu characters to 41x50 low-res variants for perfect size consistency.

## July 29, 2026
- Optimized offscreen cache thresholds, disabling on-the-fly cache allocations to eliminate frame-rate stutters.

## July 30, 2026
- Added directional, frame, and wall upgrade preview utility files to help trace sprite alignment.

## July 31, 2026
- Cleaned up duplicate/temporary asset filenames in local workspace to keep the structure clear.

## August 1, 2026
- Adjusted rendering layering: world-space rain now renders behind the night vignette, and screen-space gloom sits underneath biome filters.

