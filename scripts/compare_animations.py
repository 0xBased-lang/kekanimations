#!/usr/bin/env python3
"""
Animation Comparison Tool
Generate multiple animation variations and create visual comparison
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import os
import sys
import time
from pathlib import Path

def generate_animation_variant(image_path, num_frames=16, fps=12, scale_factor=0.02, output_path=None):
    """Generate animation with specific parameters."""

    # Load image
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None

    frames = []
    h, w = img.shape[:2]

    for i in range(num_frames):
        t = np.sin(i / num_frames * 2 * np.pi)
        scale = 1.0 + (t * scale_factor)

        new_w = int(w * scale)
        new_h = int(h * scale)

        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        channels = img.shape[2] if len(img.shape) == 3 else 1
        canvas = np.zeros((h, w, channels), dtype=img.dtype)

        x_offset = (w - new_w) // 2
        y_offset = (h - new_h) // 2

        if new_w <= w and new_h <= h:
            canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        else:
            crop_x = (new_w - w) // 2
            crop_y = (new_h - h) // 2
            canvas = resized[crop_y:crop_y+h, crop_x:crop_x+w]

        if channels == 4:
            frame_pil = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGRA2RGBA))
        elif channels == 3:
            frame_pil = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
        else:
            frame_pil = Image.fromarray(canvas)

        frames.append(frame_pil)

    # Save if output path provided
    if output_path:
        duration = int(1000 / fps)
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
            optimize=True
        )

    return frames

def create_comparison_set(image_path, output_dir='output/comparisons'):
    """
    Generate multiple animation variations for comparison.

    Creates variations with different:
    - Breathing intensities (subtle, normal, dramatic)
    - Frame counts (8, 16, 24)
    - FPS rates (10, 12, 15)
    """

    print("\n" + "=" * 60)
    print("🎨 ANIMATION COMPARISON GENERATOR")
    print("=" * 60)

    os.makedirs(output_dir, exist_ok=True)

    base_name = Path(image_path).stem

    # Test configurations
    configs = [
        # Intensity variations (16 frames, 12 fps)
        {'name': 'subtle', 'frames': 16, 'fps': 12, 'intensity': 0.015, 'desc': 'Subtle breathing (±1.5%)'},
        {'name': 'normal', 'frames': 16, 'fps': 12, 'intensity': 0.020, 'desc': 'Normal breathing (±2.0%)'},
        {'name': 'dramatic', 'frames': 16, 'fps': 12, 'intensity': 0.030, 'desc': 'Dramatic breathing (±3.0%)'},
        {'name': 'extreme', 'frames': 16, 'fps': 12, 'intensity': 0.050, 'desc': 'Extreme breathing (±5.0%)'},

        # Frame count variations (normal intensity, 12 fps)
        {'name': '8frames', 'frames': 8, 'fps': 12, 'intensity': 0.020, 'desc': '8 frames (faster)'},
        {'name': '24frames', 'frames': 24, 'fps': 12, 'intensity': 0.020, 'desc': '24 frames (smoother)'},

        # FPS variations (16 frames, normal intensity)
        {'name': '10fps', 'frames': 16, 'fps': 10, 'intensity': 0.020, 'desc': '10 FPS (slower)'},
        {'name': '15fps', 'frames': 16, 'fps': 15, 'intensity': 0.020, 'desc': '15 FPS (faster)'},
    ]

    results = []

    print(f"\n📊 Generating {len(configs)} variations...\n")

    for i, config in enumerate(configs, 1):
        print(f"[{i}/{len(configs)}] {config['desc']}...")

        output_path = os.path.join(output_dir, f"{base_name}_{config['name']}.gif")

        start = time.time()

        frames = generate_animation_variant(
            image_path,
            num_frames=config['frames'],
            fps=config['fps'],
            scale_factor=config['intensity'],
            output_path=output_path
        )

        elapsed = time.time() - start

        if frames:
            file_size = os.path.getsize(output_path)
            file_size_kb = file_size / 1024

            results.append({
                'name': config['name'],
                'description': config['desc'],
                'frames': config['frames'],
                'fps': config['fps'],
                'intensity': config['intensity'],
                'file': output_path,
                'size_kb': file_size_kb,
                'time': elapsed
            })

            print(f"  ✅ {file_size_kb:.1f} KB in {elapsed:.2f}s")

    # Create comparison HTML
    html_path = create_comparison_html(results, output_dir, base_name)

    print("\n" + "=" * 60)
    print("✅ COMPARISON SET COMPLETE")
    print("=" * 60)
    print(f"\n📁 Generated {len(results)} variations")
    print(f"📊 Total size: {sum(r['size_kb'] for r in results):.1f} KB")
    print(f"🌐 Comparison viewer: {html_path}")
    print(f"\n💡 Open in browser:")
    print(f"   open {html_path}")

    return results

def create_comparison_html(results, output_dir, base_name):
    """Create HTML viewer for side-by-side comparison."""

    html_path = os.path.join(output_dir, f"{base_name}_comparison.html")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NFT Animation Comparison - {base_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #1a1a1a;
            color: #ffffff;
            margin: 0;
            padding: 20px;
        }}

        .header {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            margin-bottom: 30px;
        }}

        h1 {{
            margin: 0;
            font-size: 2em;
        }}

        .subtitle {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}

        .card {{
            background: #2a2a2a;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }}

        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.4);
        }}

        .card h2 {{
            margin: 0 0 10px 0;
            color: #667eea;
            font-size: 1.3em;
        }}

        .description {{
            color: #aaa;
            margin-bottom: 15px;
            font-size: 0.95em;
        }}

        .animation-container {{
            background: #000;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 15px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 350px;
        }}

        .animation-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 5px;
        }}

        .stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 10px;
        }}

        .stat {{
            background: #1a1a1a;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }}

        .stat-label {{
            font-size: 0.8em;
            color: #888;
            margin-bottom: 5px;
        }}

        .stat-value {{
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
        }}

        .comparison-tips {{
            background: #2a2a2a;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 30px auto;
            max-width: 1400px;
            border-radius: 5px;
        }}

        .comparison-tips h3 {{
            margin-top: 0;
            color: #667eea;
        }}

        .comparison-tips ul {{
            line-height: 1.8;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 NFT Animation Comparison</h1>
        <p class="subtitle">{base_name} - {len(results)} Variations</p>
    </div>

    <div class="comparison-tips">
        <h3>💡 How to Compare</h3>
        <ul>
            <li><strong>Breathing Intensity:</strong> Compare subtle vs normal vs dramatic to find your preferred motion strength</li>
            <li><strong>Frame Count:</strong> More frames = smoother but larger file size</li>
            <li><strong>FPS:</strong> Higher FPS = faster playback, lower FPS = slower breathing</li>
            <li><strong>File Size:</strong> Balance quality with file size for web performance</li>
        </ul>
    </div>

    <div class="grid">
"""

    for result in results:
        # Make path relative to HTML file
        rel_path = os.path.basename(result['file'])

        html_content += f"""
        <div class="card">
            <h2>{result['name'].replace('_', ' ').title()}</h2>
            <p class="description">{result['description']}</p>

            <div class="animation-container">
                <img src="{rel_path}" alt="{result['name']}">
            </div>

            <div class="stats">
                <div class="stat">
                    <div class="stat-label">Frames</div>
                    <div class="stat-value">{result['frames']}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">FPS</div>
                    <div class="stat-value">{result['fps']}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Intensity</div>
                    <div class="stat-value">±{result['intensity']*100:.1f}%</div>
                </div>
                <div class="stat">
                    <div class="stat-label">File Size</div>
                    <div class="stat-value">{result['size_kb']:.0f} KB</div>
                </div>
            </div>
        </div>
"""

    html_content += """
    </div>

    <div class="comparison-tips" style="margin-top: 30px;">
        <h3>📊 Recommendations</h3>
        <ul>
            <li><strong>For most NFTs:</strong> Normal intensity (±2.0%), 16 frames, 12 FPS</li>
            <li><strong>For rare/legendary:</strong> Dramatic intensity (±3.0%), 24 frames, 15 FPS</li>
            <li><strong>For web optimization:</strong> Subtle intensity (±1.5%), 8 frames, 10 FPS</li>
            <li><strong>For maximum impact:</strong> Extreme intensity (±5.0%), 24 frames, 15 FPS</li>
        </ul>
    </div>
</body>
</html>
"""

    with open(html_path, 'w') as f:
        f.write(html_content)

    return html_path

def main():
    """Main comparison workflow."""

    if len(sys.argv) < 2:
        print("\nUsage: python compare_animations.py <image_path>")
        print("\nExample:")
        print("  python compare_animations.py temp_normie_rgb_1024.png")
        print("\nThis will generate:")
        print("  - 8 animation variations")
        print("  - Interactive HTML comparison viewer")
        print("  - Side-by-side visual comparison")
        sys.exit(1)

    image_path = sys.argv[1]

    if not os.path.exists(image_path):
        print(f"\n❌ Image not found: {image_path}")
        sys.exit(1)

    # Generate comparison set
    results = create_comparison_set(image_path)

    print("\n🎉 Ready to compare!")

if __name__ == '__main__':
    main()
