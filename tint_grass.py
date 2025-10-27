#!/usr/bin/env python3
import argparse
import os
import sys
from typing import Tuple
import numpy as np
from PIL import Image

def clamp01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))

def sample_biome_color(colormap_img: Image.Image, temperature: float, downfall: float) -> Tuple[int, int, int]:
    """
    Implements Minecraft-style grass colormap sampling with:
      - clamp temp, downfall to 0..1
      - project downfall by temperature (d' = d * t) to lower-left triangle
      - axes origin at bottom-right of the colormap (t→left, d'→up)
    Returns an (R,G,B) tuple (0..255).
    """
    t = clamp01(temperature)
    d = clamp01(downfall)
    d_proj = d * t

    # Convert to image coordinates (origin top-left). Bottom-right is (255,255).
    x_img = int(round(255 - (t * 255)))
    y_img = int(round(255 - (d_proj * 255)))
    x_img = max(0, min(255, x_img))
    y_img = max(0, min(255, y_img))

    cmap_np = np.asarray(colormap_img.convert("RGB"), dtype=np.uint8)
    return tuple(int(v) for v in cmap_np[y_img, x_img])

def tint_grayscale_rgba(img: Image.Image, biome_rgb: Tuple[int, int, int]) -> Image.Image:
    """
    Multiply a grayscale (or any) image by biome_rgb, using luminance from the image.
    Preserves original alpha. Returns RGBA.
    """
    rgba = img.convert("RGBA")
    arr = np.asarray(rgba, dtype=np.uint8)  # (H,W,4)
    rgb = arr[..., :3].astype(np.float32)
    a = arr[..., 3:4]

    # Rec.601 luma
    lum = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]).astype(np.float32)
    lum_norm = (lum / 255.0)[..., None]

    biome = (np.array(biome_rgb, dtype=np.float32)[None, None, :] / 255.0)
    tinted_rgb = np.clip(lum_norm * biome, 0.0, 1.0) * 255.0
    tinted_rgb = tinted_rgb.astype(np.uint8)

    out = np.concatenate([tinted_rgb, a], axis=-1)
    return Image.fromarray(out, mode="RGBA")

def composite_overlay_onto_base(base: Image.Image, overlay_rgba: Image.Image) -> Image.Image:
    """
    Alpha-composite overlay_rgba onto base (both RGBA). If sizes differ, resize overlay to base by NEAREST.
    """
    base_rgba = base.convert("RGBA")
    if overlay_rgba.size != base_rgba.size:
        overlay_rgba = overlay_rgba.resize(base_rgba.size, Image.NEAREST)
    return Image.alpha_composite(base_rgba, overlay_rgba)

def main():
    p = argparse.ArgumentParser(
        description="Tint Minecraft grass top + side overlay with a biome colormap, then composite onto side base."
    )
    p.add_argument("--top", default="grass_block_top_512.png", help="Top texture (grayscale) PNG. Default: grass_block_top_512.png")
    p.add_argument("--side-overlay", default="grass_block_side_overlay_512.png", help="Side overlay (grass only, transparent dirt). Default: grass_block_side_overlay_512.png")
    p.add_argument("--side-base", default="grass_block_side_512.png", help="Side base (dirt + grass). Default: grass_block_side_512.png")
    p.add_argument("--colormap", default="grass_colourmap.png", help="256x256 colormap PNG. Default: grass_colourmap.png")
    p.add_argument("--temperature", type=float, required=True, help="Biome temperature (0..1)")
    p.add_argument("--downfall", type=float, required=True, help="Biome downfall (0..1)")
    p.add_argument("--out-top", default=None, help="Output path for coloured top. Default: out/grass_block_top_<temp>_<downfall>.png")
    p.add_argument("--out-side", default=None, help="Output path for coloured side. Default: out/grass_block_side_<temp>_<downfall>.png")
    args = p.parse_args()

    # Check inputs exist
    for path in [args.top, args.side_overlay, args.side_base, args.colormap]:
        if not os.path.isfile(path):
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(1)

    cmap = Image.open(args.colormap).convert("RGB")
    if cmap.size != (256, 256):
        print(f"Error: colormap must be 256x256, got {cmap.size}", file=sys.stderr)
        sys.exit(1)

    biome_rgb = sample_biome_color(cmap, args.temperature, args.downfall)

    # Ensure output directory exists
    out_dir = "out"
    os.makedirs(out_dir, exist_ok=True)

    # Format temperature/downfall safely for filenames
    t_str = f"{args.temperature:.2f}".rstrip("0").rstrip(".")
    d_str = f"{args.downfall:.2f}".rstrip("0").rstrip(".")
    suffix = f"{t_str}_{d_str}"

    # ---- Top texture ----
    top_img = Image.open(args.top)
    top_coloured = tint_grayscale_rgba(top_img, biome_rgb)
    out_top = args.out_top or os.path.join(out_dir, f"grass_block_top_{suffix}.png")
    top_coloured.save(out_top, format="PNG")

    # ---- Side (overlay + base) ----
    side_overlay = Image.open(args.side_overlay)
    overlay_coloured = tint_grayscale_rgba(side_overlay, biome_rgb)

    side_base = Image.open(args.side_base)
    side_coloured = composite_overlay_onto_base(side_base, overlay_coloured)
    out_side = args.out_side or os.path.join(out_dir, f"grass_block_side_{suffix}.png")
    side_coloured.save(out_side, format="PNG")

    print(f"Biome RGB: {biome_rgb} (from temp={clamp01(args.temperature):.3f}, downfall={clamp01(args.downfall):.3f})", file=sys.stderr)
    print(f"Wrote top  -> {out_top}", file=sys.stderr)
    print(f"Wrote side -> {out_side}", file=sys.stderr)

if __name__ == "__main__":
    main()
