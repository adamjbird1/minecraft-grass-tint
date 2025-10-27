# Minecraft Grass Tinting Script

This repository contains a Python utility for generating biome-tinted Minecraft grass textures.  
Given grayscale base textures and a 256×256 biome colormap, the script reproduces Minecraft’s grass colour blending logic to create coloured top and side textures for use in resource packs or procedural map generation.

---

## Overview

The script reads a **grayscale** version of each grass texture and applies biome-specific tinting using the official grass colormap. It then composites the coloured grass overlay onto the dirt base for the block sides.

It follows the same algorithm Minecraft uses internally to map biome temperature and downfall values into a colour from the lower-left triangular region of the grass colormap.

You can read a full explanation of the biome colouring algorithm here:  
- [Wiki: Biome Colour Mapping Algorithm](https://minecraft.fandom.com/wiki/Color#Biome_colors)

And a full list of colour values for different biomes can be found here:
- [Wiki: Grass Biome colours](https://minecraft.fandom.com/wiki/Grass_Block#Color)

---

## Required files

The repository should include the following files:

| File | Description |
|------|--------------|
| `grass_block_top_512.png` | Grayscale top texture (grass only). |
| `grass_block_side_512.png` | Base side texture (includes dirt and the grass band at the top). |
| `grass_block_side_overlay_512.png` | Grayscale overlay used to tint the grass portion on the side; transparent where dirt should remain unchanged. |
| `grass_colourmap.png` | 256×256 biome grass colormap (used for colour sampling). |

---

## Running the script

The project is configured with a `pyproject.toml`, so you can run it directly using [uv](https://docs.astral.sh/uv/) — no manual installation required.


```bash
uv run python tint_grass.py --temperature 0.7 --downfall 0.8
```

This will:
- Sample the biome colour from grass_colourmap.png based on temperature and downfall.
- Tint the top and side overlay textures.
- Composite the tinted overlay onto the side base.
- Write both outputs to the out/ folder.

By default, filenames are based on the temperature and downfall values:
```
out/
├── grass_block_top_0.7_0.8.png
└── grass_block_side_0.7_0.8.png
```

---

## Optional arguments

| Argument         | Description                        | Default                                      |
| ---------------- | ---------------------------------- | -------------------------------------------- |
| `--top`          | Path to grayscale top texture      | `grass_block_top_512.png`                    |
| `--side-overlay` | Path to grayscale overlay texture  | `grass_block_side_overlay_512.png`           |
| `--side-base`    | Path to side base texture          | `grass_block_side_512.png`                   |
| `--colormap`     | Path to 256×256 biome colormap     | `grass_colourmap.png`                        |
| `--temperature`  | Biome temperature (0.0–1.0)        | *required*                                   |
| `--downfall`     | Biome downfall (0.0–1.0)           | *required*                                   |
| `--out-top`      | Custom output path for tinted top  | `out/grass_block_top_<temp>_<downfall>.png`  |
| `--out-side`     | Custom output path for tinted side | `out/grass_block_side_<temp>_<downfall>.png` |
