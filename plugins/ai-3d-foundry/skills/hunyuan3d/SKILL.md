---
name: hunyuan3d
description: "Generate 3D models from images using Tencent's Hunyuan3D-2.1 via Hugging Face Gradio API. Supports single-image and multi-view input, geometry-only or textured output, and GLB/OBJ/PLY/STL export. USE WHEN converting a 2D image or photo to a 3D mesh, or generating textured 3D assets."
cluster: media-gen
version: 1.0.0
---

# Hunyuan3D — Image-to-3D Model Generation

Generate 3D models from images using Tencent's Hunyuan3D-2.1 hosted on Hugging Face Spaces. Supports geometry-only and fully textured output with export to multiple 3D formats.

## Prerequisites

Ensure `gradio_client` is installed:

```bash
    python -m pip install gradio_client
```

## Workflow

### Quick Generation (Single Command)

To generate a 3D model from an image, run the bundled script:

```bash
# Geometry + Texture (default)
python scripts/hunyuan3d_generate.py --image <path-to-image> --mode full --output ./output/

# Geometry only (faster)
python scripts/hunyuan3d_generate.py --image <path-to-image> --mode shape --output ./output/
```

### Multi-View Generation

When multiple views of the subject are available, provide them for higher quality:

```bash
python scripts/hunyuan3d_generate.py \
    --front front.png --back back.png --left left.png --right right.png \
    --mode full --output ./output/
```

### Quality Presets

| Goal | Flags |
|------|-------|
| Quick draft / iteration | `--steps 10 --resolution 128` |
| Balanced (default) | `--steps 30 --resolution 256` |
| High quality | `--steps 50 --resolution 384` |

### Export Formats

To specify the output format, use `--export-format`:

```bash
python scripts/hunyuan3d_generate.py --image photo.png --mode full --export-format obj
```

Supported formats: `glb` (default), `obj`, `ply`, `stl`.

To include texture in the export, add `--export-texture`. To simplify the mesh, add `--simplify --target-faces 10000`.

If the hosted Space requires authentication, set `HF_TOKEN` in the execution
environment. Do not place a token in a prompt, source file, command history,
or a committed configuration file.

## Script Reference

The generation script is at `scripts/hunyuan3d_generate.py`. Key arguments:

| Argument | Default | Description |
|----------|---------|-------------|
| `--image` | None | Single input image path |
| `--front/back/left/right` | None | Multi-view image paths |
| `--mode` | full | `shape` (geometry) or `full` (geometry + texture) |
| `--steps` | 30 | Inference steps (10=Turbo, 20=Fast, 30=Standard) |
| `--guidance-scale` | 5.0 | Guidance scale for generation |
| `--seed` | 1234 | Random seed |
| `--resolution` | 256 | Octree resolution (128=Low, 256=Standard, 384=High) |
| `--rembg / --no-rembg` | True | Remove image background before generation |
| `--num-chunks` | 8000 | Number of processing chunks |
| `--export-format` | glb | Output format: glb, obj, ply, stl |
| `--simplify` | False | Reduce mesh face count |
| `--export-texture` | False | Include texture in exported file |
| `--target-faces` | 10000 | Target face count when simplifying |
| `--output` | None | Directory to copy final output to |

## Inline Usage (Without Script)

When integrating into other Python code or needing finer control, use `gradio_client` directly. Refer to `references/api_reference.md` for the full API endpoint documentation including parameter types, defaults, and return values.

```python
from gradio_client import Client, handle_file

client = Client("tencent/Hunyuan3D-2.1")

# Generate with texture
result = client.predict(
    image=handle_file("photo.png"),
    steps=30,
    guidance_scale=5,
    seed=1234,
    octree_resolution=256,
    check_box_rembg=True,
    num_chunks=8000,
    randomize_seed=True,
    api_name="/generation_all",
)
shape_file, textured_file, html, mesh_stats, seed_used = result
```

## Notes

- The Hugging Face Space may have queue times depending on load. The script blocks until generation completes.
- Single-image input works well for objects with relatively simple geometry. Multi-view input produces better results for complex shapes.
- Background removal (`--rembg`) is enabled by default and recommended for most inputs.
- GLB format is recommended for web/game use; OBJ for editing in DCC tools like Blender.
