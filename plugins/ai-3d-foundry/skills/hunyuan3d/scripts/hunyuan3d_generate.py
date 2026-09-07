#!/usr/bin/env python3
"""
Hunyuan3D-2.1 - 3D Model Generator via Hugging Face Gradio API

Generates 3D models from images using tencent/Hunyuan3D-2.1.
Supports geometry-only and geometry+texture generation with export to multiple formats.

Usage:
    # Shape only (geometry, no texture)
    python hunyuan3d_generate.py --image photo.png --mode shape

    # Full generation (geometry + texture)
    python hunyuan3d_generate.py --image photo.png --mode full

    # With custom parameters
    python hunyuan3d_generate.py --image photo.png --mode full --steps 50 --seed 42 --resolution 384

    # Export to specific format (after generation)
    python hunyuan3d_generate.py --image photo.png --mode full --export-format obj

    # Multi-view input
    python hunyuan3d_generate.py --front front.png --back back.png --left left.png --right right.png --mode full

Requirements:
    pip install gradio_client
"""

import argparse
import json
import sys
import os
from pathlib import Path

try:
    from gradio_client import Client, handle_file
except ImportError:
    print("ERROR: gradio_client not installed. Run: pip install gradio_client", file=sys.stderr)
    sys.exit(1)


SPACE_ID = "tencent/Hunyuan3D-2.1"

GENERATION_MODES = {
    "Turbo": 10,
    "Fast": 20,
    "Standard": 30,
}

DECODING_MODES = {
    "Low": 128,
    "Standard": 256,
    "High": 384,
}

EXPORT_FORMATS = ["glb", "obj", "ply", "stl"]


def extract_filepath(value):
    """Extract filepath from gradio_client response (may be str, dict, or FileData)."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        # gradio_client v2 returns {'value': '/path/...', '__type__': 'update'}
        # or {'path': '/path/...', ...}
        return value.get("value") or value.get("path") or str(value)
    # FileData object
    if hasattr(value, "path"):
        return value.path
    return str(value)


def prepare_file(path):
    """Prepare a file path for the Gradio client."""
    if path is None:
        return None
    p = Path(path).resolve()
    if not p.exists():
        print(f"ERROR: File not found: {p}", file=sys.stderr)
        sys.exit(1)
    return handle_file(str(p))


def generate_shape(client, args):
    """Generate geometry only (no texture)."""
    print(f"Generating shape from image(s)...")
    print(f"  Steps: {args.steps}, Guidance: {args.guidance_scale}, Seed: {args.seed}")
    print(f"  Octree Resolution: {args.resolution}, Chunks: {args.num_chunks}")

    result = client.predict(
        image=prepare_file(args.image),
        mv_image_front=prepare_file(args.front),
        mv_image_back=prepare_file(args.back),
        mv_image_left=prepare_file(args.left),
        mv_image_right=prepare_file(args.right),
        steps=args.steps,
        guidance_scale=args.guidance_scale,
        seed=args.seed,
        octree_resolution=args.resolution,
        check_box_rembg=args.rembg,
        num_chunks=args.num_chunks,
        randomize_seed=args.randomize_seed,
        api_name="/shape_generation",
    )

    file_path, html_output, mesh_stats, used_seed = result
    print(f"Shape generated successfully!")
    print(f"  Output file: {file_path}")
    print(f"  Seed used: {used_seed}")
    print(f"  Mesh stats: {json.dumps(mesh_stats, indent=2)}")
    return result


def generate_all(client, args):
    """Generate geometry + texture."""
    print(f"Generating shape + texture from image(s)...")
    print(f"  Steps: {args.steps}, Guidance: {args.guidance_scale}, Seed: {args.seed}")
    print(f"  Octree Resolution: {args.resolution}, Chunks: {args.num_chunks}")

    result = client.predict(
        image=prepare_file(args.image),
        mv_image_front=prepare_file(args.front),
        mv_image_back=prepare_file(args.back),
        mv_image_left=prepare_file(args.left),
        mv_image_right=prepare_file(args.right),
        steps=args.steps,
        guidance_scale=args.guidance_scale,
        seed=args.seed,
        octree_resolution=args.resolution,
        check_box_rembg=args.rembg,
        num_chunks=args.num_chunks,
        randomize_seed=args.randomize_seed,
        api_name="/generation_all",
    )

    file_out, file_out2, html_output, mesh_stats, used_seed = result
    print(f"Full generation completed!")
    print(f"  Shape file: {file_out}")
    print(f"  Textured file: {file_out2}")
    print(f"  Seed used: {used_seed}")
    print(f"  Mesh stats: {json.dumps(mesh_stats, indent=2)}")
    return result


def export_model(client, file_out, file_out2, args):
    """Export model to specified format."""
    fmt = args.export_format
    print(f"Exporting to {fmt.upper()} format...")

    result = client.predict(
        file_out=handle_file(file_out),
        file_out2=handle_file(file_out2),
        file_type=fmt,
        reduce_face=args.simplify,
        export_texture=args.export_texture,
        target_face_num=args.target_faces,
        api_name="/on_export_click",
    )

    html_output, download_path = result
    print(f"Exported successfully!")
    print(f"  Download: {download_path}")
    return result


def copy_output(src_path, output_dir):
    """Copy output file to specified directory."""
    if output_dir and src_path:
        import shutil
        dest = Path(output_dir)
        dest.mkdir(parents=True, exist_ok=True)
        src = Path(src_path)
        dest_file = dest / src.name
        shutil.copy2(src, dest_file)
        print(f"  Copied to: {dest_file}")
        return str(dest_file)
    return src_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate 3D models from images using Hunyuan3D-2.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --image photo.png --mode shape
  %(prog)s --image photo.png --mode full --export-format glb
  %(prog)s --front f.png --back b.png --left l.png --right r.png --mode full
  %(prog)s --image photo.png --mode full --steps 50 --seed 42 --output ./models/
        """,
    )

    # Input
    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--image", type=str, default=None, help="Single input image path")
    input_group.add_argument("--front", type=str, default=None, help="Front view image (multi-view)")
    input_group.add_argument("--back", type=str, default=None, help="Back view image (multi-view)")
    input_group.add_argument("--left", type=str, default=None, help="Left view image (multi-view)")
    input_group.add_argument("--right", type=str, default=None, help="Right view image (multi-view)")

    # Generation
    gen_group = parser.add_argument_group("Generation")
    gen_group.add_argument("--mode", choices=["shape", "full"], default="full",
                          help="'shape' = geometry only, 'full' = geometry + texture (default: full)")
    gen_group.add_argument("--steps", type=int, default=30, help="Inference steps (default: 30)")
    gen_group.add_argument("--guidance-scale", type=float, default=5.0, help="Guidance scale (default: 5.0)")
    gen_group.add_argument("--seed", type=int, default=1234, help="Random seed (default: 1234)")
    gen_group.add_argument("--randomize-seed", action="store_true", default=True, help="Randomize seed (default: True)")
    gen_group.add_argument("--no-randomize-seed", dest="randomize_seed", action="store_false")
    gen_group.add_argument("--resolution", type=int, default=256,
                          help="Octree resolution: 128=Low, 256=Standard, 384=High (default: 256)")
    gen_group.add_argument("--rembg", action="store_true", default=True, help="Remove background (default: True)")
    gen_group.add_argument("--no-rembg", dest="rembg", action="store_false")
    gen_group.add_argument("--num-chunks", type=int, default=8000, help="Number of chunks (default: 8000)")

    # Export
    export_group = parser.add_argument_group("Export")
    export_group.add_argument("--export-format", choices=EXPORT_FORMATS, default="glb",
                             help="Export format (default: glb)")
    export_group.add_argument("--simplify", action="store_true", default=False, help="Simplify mesh")
    export_group.add_argument("--export-texture", action="store_true", default=False, help="Include texture in export")
    export_group.add_argument("--target-faces", type=int, default=10000, help="Target face count for simplification")

    # Output
    parser.add_argument("--output", type=str, default=None, help="Output directory to copy results to")

    args = parser.parse_args()

    # Validate input
    has_single = args.image is not None
    has_multi = any(x is not None for x in [args.front, args.back, args.left, args.right])
    if not has_single and not has_multi:
        parser.error("Provide --image or multi-view images (--front, --back, --left, --right)")

    # Connect
    print(f"Connecting to {SPACE_ID}...")
    hf_token = os.environ.get("HF_TOKEN")
    import httpx
    timeout = httpx.Timeout(300.0, connect=60.0)
    client = Client(SPACE_ID, token=hf_token, httpx_kwargs={"timeout": timeout})
    print("Connected!")

    # Generate
    if args.mode == "shape":
        result = generate_shape(client, args)
        file_out = extract_filepath(result[0])
        file_out2 = file_out  # shape-only has single output
    else:
        result = generate_all(client, args)
        file_out = extract_filepath(result[0])
        file_out2 = extract_filepath(result[1])

    print(f"\nResolved output paths:")
    print(f"  file_out: {file_out}")
    print(f"  file_out2: {file_out2}")

    # Export
    export_result = export_model(client, file_out, file_out2, args)
    download_path = extract_filepath(export_result[1])

    # Copy to output directory
    if args.output:
        copy_output(download_path, args.output)

    print("\nDone!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
