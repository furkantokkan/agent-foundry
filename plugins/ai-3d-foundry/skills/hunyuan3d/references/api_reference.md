# Hunyuan3D-2.1 API Reference

## Hugging Face Space

- **Space ID**: `tencent/Hunyuan3D-2.1`
- **Client library**: `gradio_client` (`pip install gradio_client`)

## Endpoints

### /shape_generation — Geometry Only

Generates a 3D mesh (geometry) from image input without texture.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| image | filepath \| None | None | Single input image |
| mv_image_front | filepath \| None | None | Front view (multi-view) |
| mv_image_back | filepath \| None | None | Back view (multi-view) |
| mv_image_left | filepath \| None | None | Left view (multi-view) |
| mv_image_right | filepath \| None | None | Right view (multi-view) |
| steps | float | 30 | Inference steps |
| guidance_scale | float | 5 | Guidance scale |
| seed | float | 1234 | Random seed |
| octree_resolution | float | 256 | Octree resolution (128/256/384) |
| check_box_rembg | bool | True | Remove background |
| num_chunks | float | 8000 | Number of chunks |
| randomize_seed | bool | True | Randomize seed |

**Returns** tuple of 4:
- `[0]` filepath — Output mesh file
- `[1]` str — HTML output
- `[2]` dict — Mesh stats (vertices, faces, etc.)
- `[3]` float — Seed used

### /generation_all — Geometry + Texture

Same parameters as `/shape_generation`. Generates mesh with texture applied.

**Returns** tuple of 5:
- `[0]` filepath — Shape file
- `[1]` filepath — Textured file
- `[2]` str — HTML output
- `[3]` dict — Mesh stats
- `[4]` float — Seed used

### /on_export_click — Export to Format

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| file_out | filepath | Required | Shape output from generation |
| file_out2 | filepath | Required | Textured output from generation |
| file_type | Literal | "glb" | Export format: glb, obj, ply, stl |
| reduce_face | bool | False | Simplify mesh |
| export_texture | bool | False | Include texture in export |
| target_face_num | float | 10000 | Target face count for simplification |

**Returns** tuple of 2:
- `[0]` str — HTML output
- `[1]` filepath — Download path

### /on_gen_mode_change — Get Steps for Mode

| Mode | Steps |
|------|-------|
| Turbo | 10 |
| Fast | 20 |
| Standard | 30 |

### /on_decode_mode_change — Get Resolution for Mode

| Mode | Resolution |
|------|-----------|
| Low | 128 |
| Standard | 256 |
| High | 384 |

## Quality Presets

| Preset | Steps | Resolution | Use Case |
|--------|-------|-----------|----------|
| Quick Draft | 10 | 128 | Fast preview, iteration |
| Balanced | 30 | 256 | Good quality, reasonable speed |
| High Quality | 50 | 384 | Best quality, slower |
