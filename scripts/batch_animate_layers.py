#!/usr/bin/env python3
"""
Batch Layer Animation Script
Processes all 43 layer templates and generates animated frame sequences

This script:
1. Discovers all layer PNG files in media_files/nft_layers/
2. Applies appropriate animation based on layer type
3. Saves frame sequences for later recombination
4. Generates preview GIFs for QA validation

Usage:
    python batch_animate_layers.py [options]

Options:
    --dry-run           Show what would be processed without animating
    --layer-type TYPE   Only process specific layer type (e.g., body, eyes)
    --frames N          Number of frames (default: 16)
    --fps N             Frames per second (default: 12)
    --output DIR        Output directory (default: output/animated_layers)
    --skip-previews     Don't generate preview GIFs
    --parallel N        Number of parallel processes (default: 1)
"""

import sys
import os
from pathlib import Path
import json
import time
from datetime import datetime
import subprocess
import concurrent.futures


class BatchLayerAnimator:
    """
    Batch processor for animating all layer templates
    """

    def __init__(self, layers_base_path="media_files/nft_layers", output_dir="output/animated_layers"):
        self.layers_base_path = Path(layers_base_path)
        self.output_dir = Path(output_dir)

        # Layer type to folder mapping
        self.layer_types = [
            "background",
            "body",
            "tattoo",
            "style",
            "clothes",
            "tools",
            "eyes",
            "glasses",
            "hat",
            "special",
            "glasses_for_xray",
            "style_for_xray",
            "tools_for_xray"
        ]

    def discover_layers(self, filter_layer_type=None):
        """
        Discover all layer PNG files

        Returns:
            List of tuples: (layer_path, layer_type, trait_name)
        """
        print("\n🔍 Discovering layers...")

        layers = []

        for layer_type in self.layer_types:
            if filter_layer_type and layer_type != filter_layer_type:
                continue

            layer_dir = self.layers_base_path / layer_type

            if not layer_dir.exists():
                print(f"  ⚠️  Directory not found: {layer_dir}")
                continue

            # Find all PNG files
            for layer_file in sorted(layer_dir.glob("*.png")):
                trait_name = layer_file.stem  # Filename without extension

                layers.append({
                    "path": layer_file,
                    "layer_type": layer_type,
                    "trait_name": trait_name,
                    "size_mb": layer_file.stat().st_size / (1024 * 1024)
                })

        print(f"  ✅ Found {len(layers)} layer files across {len(set(l['layer_type'] for l in layers))} layer types")

        return layers

    def animate_layer(self, layer_info, num_frames=16, fps=12, generate_preview=True):
        """
        Animate a single layer using the animate_layer.py script

        Args:
            layer_info: Dict with path, layer_type, trait_name
            num_frames: Number of frames
            fps: Frames per second
            generate_preview: Whether to generate preview GIF

        Returns:
            Dict with success status and metadata
        """
        layer_path = layer_info["path"]
        layer_type = layer_info["layer_type"]
        trait_name = layer_info["trait_name"]

        print(f"\n{'=' * 80}")
        print(f"🎬 Animating: {layer_type}/{trait_name}")
        print(f"{'=' * 80}")

        # Build command
        cmd = [
            "python3",
            "scripts/animate_layer.py",
            str(layer_path),
            layer_type,
            trait_name,
            "--frames", str(num_frames),
            "--fps", str(fps),
            "--output", str(self.output_dir)
        ]

        if generate_preview:
            cmd.append("--preview")

        # Execute
        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per layer
            )

            elapsed = time.time() - start_time

            if result.returncode == 0:
                print(f"✅ Success in {elapsed:.1f}s")

                return {
                    "success": True,
                    "layer_type": layer_type,
                    "trait_name": trait_name,
                    "elapsed_seconds": elapsed,
                    "frames": num_frames,
                    "output": result.stdout
                }
            else:
                print(f"❌ Failed (exit code {result.returncode})")
                print(f"Error: {result.stderr}")

                return {
                    "success": False,
                    "layer_type": layer_type,
                    "trait_name": trait_name,
                    "error": result.stderr
                }

        except subprocess.TimeoutExpired:
            print(f"❌ Timeout after 5 minutes")
            return {
                "success": False,
                "layer_type": layer_type,
                "trait_name": trait_name,
                "error": "Timeout"
            }

        except Exception as e:
            print(f"❌ Exception: {e}")
            return {
                "success": False,
                "layer_type": layer_type,
                "trait_name": trait_name,
                "error": str(e)
            }

    def batch_process(self, layers, num_frames=16, fps=12, generate_previews=True, parallel=1):
        """
        Process all layers in batch

        Args:
            layers: List of layer info dicts
            num_frames: Number of frames
            fps: Frames per second
            generate_previews: Generate preview GIFs
            parallel: Number of parallel processes (1 = sequential)

        Returns:
            Dict with summary statistics
        """
        print("\n" + "=" * 80)
        print(f"🚀 BATCH PROCESSING: {len(layers)} layers")
        print("=" * 80)
        print(f"Frames: {num_frames} @ {fps} FPS")
        print(f"Output: {self.output_dir}")
        print(f"Parallel processes: {parallel}")
        print(f"Preview GIFs: {'Yes' if generate_previews else 'No'}")

        start_time = time.time()
        results = []

        if parallel > 1:
            # Parallel processing
            print(f"\n⚡ Using {parallel} parallel processes...")

            with concurrent.futures.ProcessPoolExecutor(max_workers=parallel) as executor:
                futures = {
                    executor.submit(
                        self.animate_layer,
                        layer,
                        num_frames,
                        fps,
                        generate_previews
                    ): layer for layer in layers
                }

                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    layer = futures[future]
                    try:
                        result = future.result()
                        results.append(result)

                        print(f"\nProgress: {i+1}/{len(layers)} ({(i+1)/len(layers)*100:.1f}%)")

                    except Exception as e:
                        print(f"\n❌ Exception processing {layer['layer_type']}/{layer['trait_name']}: {e}")
                        results.append({
                            "success": False,
                            "layer_type": layer["layer_type"],
                            "trait_name": layer["trait_name"],
                            "error": str(e)
                        })
        else:
            # Sequential processing
            for i, layer in enumerate(layers):
                print(f"\nProgress: {i+1}/{len(layers)} ({(i+1)/len(layers)*100:.1f}%)")

                result = self.animate_layer(layer, num_frames, fps, generate_previews)
                results.append(result)

        total_elapsed = time.time() - start_time

        # Generate summary
        success_count = sum(1 for r in results if r["success"])
        failed_count = len(results) - success_count

        summary = {
            "total_layers": len(layers),
            "success_count": success_count,
            "failed_count": failed_count,
            "total_elapsed_seconds": total_elapsed,
            "avg_seconds_per_layer": total_elapsed / len(layers) if layers else 0,
            "timestamp": datetime.now().isoformat(),
            "results": results
        }

        return summary

    def print_summary(self, summary):
        """Print batch processing summary"""

        print("\n" + "=" * 80)
        print("📊 BATCH PROCESSING SUMMARY")
        print("=" * 80)

        print(f"\nTotal layers: {summary['total_layers']}")
        print(f"  ✅ Success: {summary['success_count']}")
        print(f"  ❌ Failed: {summary['failed_count']}")

        print(f"\nTime:")
        print(f"  Total: {summary['total_elapsed_seconds']:.1f}s ({summary['total_elapsed_seconds']/60:.1f} minutes)")
        print(f"  Average per layer: {summary['avg_seconds_per_layer']:.1f}s")

        if summary['failed_count'] > 0:
            print(f"\n⚠️  Failed layers:")
            for result in summary['results']:
                if not result['success']:
                    print(f"  - {result['layer_type']}/{result['trait_name']}: {result.get('error', 'Unknown error')}")

        # Save summary to JSON
        summary_path = Path(self.output_dir) / "batch_summary.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)

        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"\n💾 Summary saved to: {summary_path}")

    def dry_run(self, layers):
        """Print what would be processed without actually animating"""

        print("\n" + "=" * 80)
        print("🔍 DRY RUN - Layers to be processed:")
        print("=" * 80)

        # Group by layer type
        by_type = {}
        for layer in layers:
            layer_type = layer["layer_type"]
            if layer_type not in by_type:
                by_type[layer_type] = []
            by_type[layer_type].append(layer)

        total_size_mb = sum(l["size_mb"] for l in layers)

        for layer_type in sorted(by_type.keys()):
            layer_list = by_type[layer_type]
            type_size_mb = sum(l["size_mb"] for l in layer_list)

            print(f"\n{layer_type}: {len(layer_list)} layers ({type_size_mb:.1f} MB)")

            for layer in sorted(layer_list, key=lambda x: x["trait_name"]):
                print(f"  - {layer['trait_name']} ({layer['size_mb']:.2f} MB)")

        print(f"\n{'=' * 80}")
        print(f"Total: {len(layers)} layers ({total_size_mb:.1f} MB)")
        print(f"{'=' * 80}")


def main():
    """Main CLI"""

    print("\n" + "=" * 80)
    print("🎨 KEKTECH Batch Layer Animation")
    print("=" * 80)

    # Parse arguments
    dry_run = "--dry-run" in sys.argv
    skip_previews = "--skip-previews" in sys.argv

    # Filter layer type
    filter_layer_type = None
    if "--layer-type" in sys.argv:
        idx = sys.argv.index("--layer-type")
        if idx + 1 < len(sys.argv):
            filter_layer_type = sys.argv[idx + 1]

    # Frames
    num_frames = 16
    if "--frames" in sys.argv:
        idx = sys.argv.index("--frames")
        if idx + 1 < len(sys.argv):
            num_frames = int(sys.argv[idx + 1])

    # FPS
    fps = 12
    if "--fps" in sys.argv:
        idx = sys.argv.index("--fps")
        if idx + 1 < len(sys.argv):
            fps = int(sys.argv[idx + 1])

    # Output directory
    output_dir = "output/animated_layers"
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    # Parallel processing
    parallel = 1
    if "--parallel" in sys.argv:
        idx = sys.argv.index("--parallel")
        if idx + 1 < len(sys.argv):
            parallel = int(sys.argv[idx + 1])

    # Create batch animator
    animator = BatchLayerAnimator(output_dir=output_dir)

    # Discover layers
    layers = animator.discover_layers(filter_layer_type=filter_layer_type)

    if not layers:
        print("\n❌ No layers found!")
        sys.exit(1)

    # Dry run or actual processing
    if dry_run:
        animator.dry_run(layers)
        print("\n💡 Remove --dry-run to process layers")
        sys.exit(0)

    # Process layers
    summary = animator.batch_process(
        layers,
        num_frames=num_frames,
        fps=fps,
        generate_previews=not skip_previews,
        parallel=parallel
    )

    # Print summary
    animator.print_summary(summary)

    # Exit code
    if summary['failed_count'] > 0:
        print("\n⚠️  Some layers failed to process")
        sys.exit(1)
    else:
        print("\n✅ All layers processed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
