#!/usr/bin/env python3
"""
Test Pixel Analysis - Quick Win Path A
Validates K-Means clustering and mask generation
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
import sys
import os

def analyze_layer(layer_path, n_zones=3):
    """
    Analyze layer and extract animation zones using K-Means.

    Args:
        layer_path: Path to layer image
        n_zones: Number of animation zones to extract

    Returns:
        dict with masks, colors, and statistics
    """
    print(f"\n📊 Analyzing: {layer_path}")
    print("=" * 60)

    # Load image
    img = cv2.imread(layer_path, cv2.IMREAD_UNCHANGED)

    if img is None:
        print(f"❌ Could not load image: {layer_path}")
        return None

    print(f"✅ Image loaded: {img.shape}")

    # Handle different image formats
    if len(img.shape) == 2:
        # Grayscale - convert to RGB
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        alpha = np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255
        img = np.dstack([img, alpha])
    elif img.shape[2] == 3:
        # RGB - add alpha channel
        alpha = np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255
        img = np.dstack([img, alpha])
    elif img.shape[2] == 4:
        # RGBA - perfect!
        pass
    else:
        print(f"❌ Unexpected image format: {img.shape}")
        return None

    rgb = img[:, :, :3]
    alpha = img[:, :, 3]

    # Only analyze visible pixels
    visible_mask = alpha > 10  # Threshold to ignore nearly transparent
    visible_pixels = rgb[visible_mask].reshape(-1, 3).astype(float)

    total_pixels = img.shape[0] * img.shape[1]
    visible_count = visible_pixels.shape[0]

    print(f"\n📈 Pixel Statistics:")
    print(f"  Total pixels: {total_pixels:,}")
    print(f"  Visible pixels: {visible_count:,} ({visible_count/total_pixels*100:.1f}%)")
    print(f"  Transparent pixels: {total_pixels - visible_count:,}")

    if visible_count < 100:
        print(f"❌ Too few visible pixels for analysis")
        return None

    # K-Means clustering
    print(f"\n🔬 Running K-Means clustering (k={n_zones})...")
    kmeans = KMeans(n_clusters=n_zones, random_state=42, n_init=10, max_iter=300)
    labels = kmeans.fit_predict(visible_pixels)

    print(f"✅ Clustering complete!")

    # Color centers
    print(f"\n🎨 Color Centers (RGB):")
    for i, color in enumerate(kmeans.cluster_centers_):
        r, g, b = int(color[0]), int(color[1]), int(color[2])
        print(f"  Zone {i}: RGB({r:3d}, {g:3d}, {b:3d}) - #{r:02x}{g:02x}{b:02x}")

    # Create labeled image
    labeled_img = np.zeros(img.shape[:2], dtype=np.uint8)
    labeled_img[visible_mask] = labels

    # Generate zone masks
    masks = []
    zones_info = []

    print(f"\n📐 Zone Statistics:")

    for zone_id in range(n_zones):
        zone_mask = (labeled_img == zone_id).astype(np.uint8) * 255

        # Clean up noise with morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        zone_mask = cv2.morphologyEx(zone_mask, cv2.MORPH_CLOSE, kernel)
        zone_mask = cv2.morphologyEx(zone_mask, cv2.MORPH_OPEN, kernel)

        pixel_count = np.sum(zone_mask > 0)

        # Calculate centroid
        moments = cv2.moments(zone_mask)
        if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])
        else:
            cx, cy = 0, 0

        # Bounding box
        contours, _ = cv2.findContours(zone_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            x, y, w, h = cv2.boundingRect(contours[0])
            bbox = [x, y, x+w, y+h]
        else:
            bbox = [0, 0, 0, 0]

        # Store info
        zone_info = {
            'id': zone_id,
            'pixel_count': int(pixel_count),
            'percentage': pixel_count / visible_count * 100,
            'centroid': [cx, cy],
            'bbox': bbox,
            'color': kmeans.cluster_centers_[zone_id].tolist()
        }

        masks.append(zone_mask)
        zones_info.append(zone_info)

        print(f"  Zone {zone_id}: {pixel_count:,} pixels ({zone_info['percentage']:.1f}%) - Center: ({cx}, {cy})")

    return {
        'masks': masks,
        'zones_info': zones_info,
        'original_shape': img.shape,
        'visible_pixels': visible_count
    }

def save_masks(result, layer_name):
    """Save masks to files."""

    if result is None:
        return False

    masks_dir = 'masks'
    os.makedirs(masks_dir, exist_ok=True)

    print(f"\n💾 Saving masks to {masks_dir}/...")

    for i, mask in enumerate(result['masks']):
        mask_path = f'{masks_dir}/{layer_name}_zone_{i}.png'
        cv2.imwrite(mask_path, mask)
        print(f"  ✅ {mask_path}")

    return True

def visualize_zones(result, layer_path, layer_name):
    """Create visualization of zones."""

    if result is None:
        return

    # Load original image
    img = cv2.imread(layer_path, cv2.IMREAD_UNCHANGED)

    if img.shape[2] == 4:
        # Convert RGBA to RGB for visualization
        rgb = img[:, :, :3]
    else:
        rgb = img

    # Create colored overlay
    overlay = rgb.copy()
    colors = [
        [255, 0, 0],    # Red
        [0, 255, 0],    # Green
        [0, 0, 255],    # Blue
        [255, 255, 0],  # Yellow
        [255, 0, 255],  # Magenta
    ]

    for i, mask in enumerate(result['masks']):
        color = colors[i % len(colors)]
        overlay[mask > 0] = overlay[mask > 0] * 0.5 + np.array(color) * 0.5

    # Save visualization
    vis_path = f'masks/{layer_name}_zones_visualization.png'
    cv2.imwrite(vis_path, overlay)
    print(f"\n🎨 Zone visualization saved: {vis_path}")

def main():
    """Main test execution."""

    print("\n" + "=" * 60)
    print("🔬 PIXEL-PERFECT ANALYSIS TEST - PATH A")
    print("=" * 60)

    # Test with normie RGB layer
    test_image = 'temp_normie_rgb_1024.png'

    if not os.path.exists(test_image):
        print(f"\n❌ Test image not found: {test_image}")
        print("Available images:")
        import glob
        for img in glob.glob('temp_*.png'):
            print(f"  - {img}")
        sys.exit(1)

    # Analyze
    result = analyze_layer(test_image, n_zones=3)

    if result is None:
        print("\n❌ Analysis failed")
        sys.exit(1)

    # Save masks
    layer_name = 'normie_body'
    save_masks(result, layer_name)

    # Create visualization
    visualize_zones(result, test_image, layer_name)

    # Summary
    print("\n" + "=" * 60)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  Total zones extracted: {len(result['masks'])}")
    print(f"  Visible pixels analyzed: {result['visible_pixels']:,}")
    print(f"  Masks saved to: masks/")

    print(f"\n🎯 Next Steps:")
    print(f"  1. Review masks: open masks/{layer_name}_zones_visualization.png")
    print(f"  2. Test mesh deformation: python scripts/test_mesh_deformation.py")
    print(f"  3. Test particles: python scripts/test_particle_system.py")

    print("\n🎉 Pixel-perfect system is working!")

if __name__ == '__main__':
    main()
