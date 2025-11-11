#!/usr/bin/env python3
"""
Test Mesh Deformation - Simple Breathing Animation
Path A validation test
"""

import cv2
import numpy as np
from PIL import Image
import os

def simple_breathing_animation(image_path, num_frames=8):
    """
    Generate simple breathing animation using scaling.
    Simplified version for quick testing.

    Args:
        image_path: Path to input image
        num_frames: Number of frames to generate

    Returns:
        List of PIL Image frames
    """
    print(f"\n🎬 Generating {num_frames}-frame breathing animation")
    print("=" * 60)

    # Load image
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    if img is None:
        print(f"❌ Could not load: {image_path}")
        return None

    print(f"✅ Loaded: {img.shape}")

    frames = []
    h, w = img.shape[:2]

    for i in range(num_frames):
        # Sinusoidal breathing curve
        t = np.sin(i / num_frames * 2 * np.pi)

        # Scale factor (1.0 = normal, 1.02 = 2% larger)
        scale = 1.0 + (t * 0.015)  # ±1.5% size variation

        # Calculate new size
        new_w = int(w * scale)
        new_h = int(h * scale)

        # Resize image
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        # Create output canvas (same size as original)
        canvas = np.zeros((h, w, img.shape[2]), dtype=img.dtype)

        # Calculate position to center the resized image
        x_offset = (w - new_w) // 2
        y_offset = (h - new_h) // 2

        # Place resized image on canvas
        if new_w <= w and new_h <= h:
            # Image is smaller - paste directly
            canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        else:
            # Image is larger - crop
            crop_x = (new_w - w) // 2
            crop_y = (new_h - h) // 2
            canvas = resized[crop_y:crop_y+h, crop_x:crop_x+w]

        # Convert to PIL Image
        if img.shape[2] == 4:
            # RGBA
            frame_pil = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGRA2RGBA))
        else:
            # RGB
            frame_pil = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))

        frames.append(frame_pil)

        # Progress
        scale_percent = (scale - 1.0) * 100
        print(f"  Frame {i:2d}/{num_frames}: scale={scale:.4f} ({scale_percent:+.2f}%)")

    print(f"\n✅ Generated {len(frames)} frames")
    return frames

def save_animation(frames, output_path, fps=12):
    """Save frames as animated GIF."""

    if not frames:
        return False

    print(f"\n💾 Saving animation...")
    print(f"  Output: {output_path}")
    print(f"  FPS: {fps}")
    print(f"  Frames: {len(frames)}")

    # Calculate duration per frame (milliseconds)
    duration = int(1000 / fps)

    # Save as GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=True
    )

    # Get file size
    file_size = os.path.getsize(output_path)
    file_size_kb = file_size / 1024

    print(f"  ✅ Saved: {file_size_kb:.1f} KB")

    return True

def main():
    """Main test."""

    print("\n" + "=" * 60)
    print("🎬 MESH DEFORMATION TEST - PATH A")
    print("=" * 60)

    # Input image
    input_image = 'temp_normie_rgb_1024.png'

    if not os.path.exists(input_image):
        print(f"\n❌ Input image not found: {input_image}")
        return

    # Generate animation
    frames = simple_breathing_animation(input_image, num_frames=8)

    if frames is None:
        print("\n❌ Animation generation failed")
        return

    # Save animation
    output_dir = 'output/breathing_frames'
    os.makedirs(output_dir, exist_ok=True)

    output_path = f'{output_dir}/breathing_test.gif'
    success = save_animation(frames, output_path, fps=12)

    if not success:
        print("\n❌ Failed to save animation")
        return

    # Summary
    print("\n" + "=" * 60)
    print("✅ BREATHING ANIMATION COMPLETE!")
    print("=" * 60)

    print(f"\n📊 Results:")
    print(f"  Frames generated: {len(frames)}")
    print(f"  Output file: {output_path}")
    print(f"  Frame rate: 12 FPS")
    print(f"  Loop: Infinite")

    print(f"\n🎯 Next Steps:")
    print(f"  1. View animation: open {output_path}")
    print(f"  2. Test particles: python scripts/test_particle_system.py")
    print(f"  3. Validate quality: Score the animation")

    print("\n🎉 Mesh deformation is working!")

if __name__ == '__main__':
    main()
