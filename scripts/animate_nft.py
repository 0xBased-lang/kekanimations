#!/usr/bin/env python3
"""
Production NFT Animation Script
Pixel-perfect selective animation with progress tracking
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import os
import sys
import time
from pathlib import Path

class NFTAnimator:
    def __init__(self, output_dir='output/final_animations'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def analyze_image(self, image_path, n_zones=3):
        """
        Analyze NFT image and extract animation zones.

        Returns: dict with masks and metadata
        """
        print(f"\n📊 Analyzing: {image_path}")

        # Load image
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

        if img is None:
            print(f"❌ Could not load image")
            return None

        # Handle format
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            alpha = np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255
            img = np.dstack([img, alpha])
        elif img.shape[2] == 3:
            alpha = np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255
            img = np.dstack([img, alpha])

        rgb = img[:, :, :3]
        alpha = img[:, :, 3]

        # Analyze visible pixels
        visible_mask = alpha > 10
        visible_pixels = rgb[visible_mask].reshape(-1, 3).astype(float)

        if visible_pixels.shape[0] < 100:
            print(f"❌ Not enough visible pixels")
            return None

        print(f"  Analyzing {visible_pixels.shape[0]:,} pixels...")

        # K-Means clustering
        kmeans = KMeans(n_clusters=n_zones, random_state=42, n_init=10, max_iter=300)
        labels = kmeans.fit_predict(visible_pixels)

        # Create labeled image
        labeled_img = np.zeros(img.shape[:2], dtype=np.uint8)
        labeled_img[visible_mask] = labels

        # Generate masks
        masks = []
        for zone_id in range(n_zones):
            zone_mask = (labeled_img == zone_id).astype(np.uint8) * 255

            # Clean up
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            zone_mask = cv2.morphologyEx(zone_mask, cv2.MORPH_CLOSE, kernel)
            zone_mask = cv2.morphologyEx(zone_mask, cv2.MORPH_OPEN, kernel)

            masks.append(zone_mask)

        print(f"  ✅ Extracted {len(masks)} animation zones")

        return {
            'masks': masks,
            'colors': kmeans.cluster_centers_,
            'original_image': img,
            'rgb': rgb,
            'alpha': alpha
        }

    def generate_breathing_animation(self, image_path, num_frames=16, scale_factor=0.02):
        """
        Generate breathing animation for NFT.

        Args:
            image_path: Path to NFT image
            num_frames: Number of frames (default 16)
            scale_factor: Breathing intensity (default 0.02 = ±2%)

        Returns: List of PIL Image frames
        """
        print(f"\n🎬 Generating {num_frames}-frame breathing animation...")

        # Load image
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

        if img is None:
            print(f"❌ Could not load image")
            return None

        print(f"  Image size: {img.shape}")

        frames = []
        h, w = img.shape[:2]

        start_time = time.time()

        for i in range(num_frames):
            # Sinusoidal breathing curve
            t = np.sin(i / num_frames * 2 * np.pi)
            scale = 1.0 + (t * scale_factor)

            # Calculate new size
            new_w = int(w * scale)
            new_h = int(h * scale)

            # Resize image
            resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

            # Create output canvas
            if len(img.shape) == 3:
                channels = img.shape[2]
            else:
                channels = 1

            canvas = np.zeros((h, w, channels), dtype=img.dtype)

            # Calculate position to center
            x_offset = (w - new_w) // 2
            y_offset = (h - new_h) // 2

            # Place resized image
            if new_w <= w and new_h <= h:
                canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
            else:
                crop_x = (new_w - w) // 2
                crop_y = (new_h - h) // 2
                canvas = resized[crop_y:crop_y+h, crop_x:crop_x+w]

            # Convert to PIL Image
            if channels == 4:
                frame_pil = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGRA2RGBA))
            elif channels == 3:
                frame_pil = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
            else:
                frame_pil = Image.fromarray(canvas)

            frames.append(frame_pil)

            # Progress
            progress = (i + 1) / num_frames * 100
            print(f"\r  Progress: {progress:5.1f}% ({i+1}/{num_frames} frames)", end='')

        elapsed = time.time() - start_time
        print(f"\n  ✅ Generated {len(frames)} frames in {elapsed:.2f}s")

        return frames

    def save_animation(self, frames, output_path, fps=12, optimize=True):
        """
        Save frames as animated GIF.

        Args:
            frames: List of PIL Image frames
            output_path: Output file path
            fps: Frames per second (default 12)
            optimize: Optimize GIF size (default True)
        """
        if not frames:
            print(f"❌ No frames to save")
            return False

        print(f"\n💾 Saving animation...")
        print(f"  Output: {output_path}")
        print(f"  Frames: {len(frames)}")
        print(f"  FPS: {fps}")

        # Calculate duration per frame (milliseconds)
        duration = int(1000 / fps)

        start_time = time.time()

        # Save as GIF
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
            optimize=optimize
        )

        elapsed = time.time() - start_time

        # Get file size
        file_size = os.path.getsize(output_path)
        file_size_kb = file_size / 1024
        file_size_mb = file_size_kb / 1024

        if file_size_mb >= 1:
            size_str = f"{file_size_mb:.2f} MB"
        else:
            size_str = f"{file_size_kb:.1f} KB"

        print(f"  ✅ Saved: {size_str} in {elapsed:.2f}s")

        return True

    def animate_nft(self, image_path, nft_name=None, num_frames=16, fps=12, scale_factor=0.02):
        """
        Complete workflow: analyze and animate NFT.

        Args:
            image_path: Path to NFT image
            nft_name: Name for output (default: from filename)
            num_frames: Number of frames
            fps: Frames per second
            scale_factor: Breathing intensity

        Returns: Path to output GIF
        """
        print("\n" + "=" * 60)
        print("🎨 NFT ANIMATION PRODUCTION")
        print("=" * 60)

        # Determine output name
        if nft_name is None:
            nft_name = Path(image_path).stem

        print(f"\n🎯 Animating: {nft_name}")

        # Step 1: Analyze (optional - for future use)
        analysis = self.analyze_image(image_path)
        if analysis:
            print(f"\n  Color zones detected: {len(analysis['masks'])}")
            for i, color in enumerate(analysis['colors']):
                r, g, b = int(color[0]), int(color[1]), int(color[2])
                print(f"    Zone {i}: RGB({r}, {g}, {b})")

        # Step 2: Generate animation
        frames = self.generate_breathing_animation(
            image_path,
            num_frames=num_frames,
            scale_factor=scale_factor
        )

        if not frames:
            print(f"\n❌ Animation generation failed")
            return None

        # Step 3: Save animation
        output_path = os.path.join(self.output_dir, f"{nft_name}_animated.gif")
        success = self.save_animation(frames, output_path, fps=fps)

        if not success:
            print(f"\n❌ Save failed")
            return None

        # Summary
        print("\n" + "=" * 60)
        print("✅ ANIMATION COMPLETE!")
        print("=" * 60)
        print(f"\n📁 Output: {output_path}")
        print(f"🎬 Frames: {num_frames} @ {fps} FPS")
        print(f"🌊 Motion: ±{scale_factor*100:.1f}% breathing")

        return output_path

def main():
    """Main production workflow."""

    print("\n" + "=" * 60)
    print("🚀 NFT ANIMATION PRODUCTION SYSTEM")
    print("=" * 60)

    # Check for input
    if len(sys.argv) < 2:
        print("\nUsage: python animate_nft.py <image_path> [options]")
        print("\nOptions:")
        print("  --frames N     Number of frames (default: 16)")
        print("  --fps N        Frames per second (default: 12)")
        print("  --intensity N  Breathing intensity 0-1 (default: 0.02)")
        print("  --name NAME    Output name (default: from filename)")
        print("\nExamples:")
        print("  python animate_nft.py temp_normie_rgb_1024.png")
        print("  python animate_nft.py nft_0042.png --frames 16 --fps 12")
        print("  python animate_nft.py nft_rare.png --intensity 0.03 --name legendary")
        sys.exit(1)

    # Parse arguments
    image_path = sys.argv[1]

    # Defaults
    num_frames = 16
    fps = 12
    scale_factor = 0.02
    nft_name = None

    # Parse optional arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--frames' and i + 1 < len(sys.argv):
            num_frames = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--fps' and i + 1 < len(sys.argv):
            fps = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--intensity' and i + 1 < len(sys.argv):
            scale_factor = float(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--name' and i + 1 < len(sys.argv):
            nft_name = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    # Validate input
    if not os.path.exists(image_path):
        print(f"\n❌ Image not found: {image_path}")
        sys.exit(1)

    # Create animator
    animator = NFTAnimator()

    # Animate NFT
    output_path = animator.animate_nft(
        image_path,
        nft_name=nft_name,
        num_frames=num_frames,
        fps=fps,
        scale_factor=scale_factor
    )

    if output_path:
        print(f"\n🎉 Success! View animation:")
        print(f"   open {output_path}")
        sys.exit(0)
    else:
        print(f"\n❌ Animation failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
