#!/usr/bin/env python3
"""
Preview Generator
Fast, low-res preview for real-time feedback in playground
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Tuple, Dict, Any


async def generate_preview(
    image_path: str,
    effects: List[Dict[str, Any]],
    num_frames: int = 8,
    size: Tuple[int, int] = (256, 256)
) -> str:
    """
    Generate low-res preview with effects for real-time feedback

    Args:
        image_path: Path to input image
        effects: List of effect configurations
        num_frames: Number of frames (fewer = faster)
        size: Output size (smaller = faster)

    Returns:
        Path to preview GIF
    """
    # Read and resize image for speed
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Resize to preview size
    img_resized = cv2.resize(img, size, interpolation=cv2.INTER_AREA)

    # Convert to RGB
    if img_resized.shape[2] == 4:
        alpha = img_resized[:, :, 3]
        img_rgb = cv2.cvtColor(img_resized[:, :, :3], cv2.COLOR_BGR2RGB)
    else:
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        alpha = None

    # Generate frames with effects
    frames = []
    for i in range(num_frames):
        frame = img_rgb.copy()

        # Apply each effect
        for effect in effects:
            effect_type = effect.get("type", "")
            intensity = effect.get("intensity", 1.0)
            params = effect.get("parameters", {})

            if effect_type == "breathing":
                # Simple breathing via scaling
                phase = (i / num_frames) * 2 * np.pi
                scale_delta = np.sin(phase) * intensity
                scale = 1.0 + scale_delta

                new_size = (int(size[0] * scale), int(size[1] * scale))
                frame_scaled = cv2.resize(frame, new_size, interpolation=cv2.INTER_LINEAR)

                # Center crop/pad to original size
                if scale > 1.0:
                    # Crop
                    crop_x = (new_size[0] - size[0]) // 2
                    crop_y = (new_size[1] - size[1]) // 2
                    frame = frame_scaled[crop_y:crop_y+size[1], crop_x:crop_x+size[0]]
                else:
                    # Pad
                    canvas = np.zeros_like(img_rgb)
                    paste_x = (size[0] - new_size[0]) // 2
                    paste_y = (size[1] - new_size[1]) // 2
                    canvas[paste_y:paste_y+new_size[1], paste_x:paste_x+new_size[0]] = frame_scaled
                    frame = canvas

            elif effect_type == "rotation":
                # Simple rotation
                degrees = params.get("degrees", 5.0) * intensity
                angle = (i / num_frames) * degrees
                center = (size[0] // 2, size[1] // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                frame = cv2.warpAffine(frame, M, size)

            elif effect_type == "glow":
                # Simple glow effect via Gaussian blur overlay
                color = params.get("color", [255, 0, 0])
                glow_strength = intensity * 0.3

                # Create glow layer
                glow = cv2.GaussianBlur(frame, (15, 15), 0)

                # Tint with color
                glow_tinted = glow.astype(float)
                for c in range(3):
                    glow_tinted[:, :, c] = glow_tinted[:, :, c] * (color[c] / 255.0)

                # Blend
                frame = cv2.addWeighted(
                    frame.astype(float), 1.0,
                    glow_tinted, glow_strength,
                    0
                ).astype(np.uint8)

            elif effect_type == "sparkles":
                # Simple random sparkle particles
                particle_count = params.get("particle_count", 20)
                for _ in range(int(particle_count * intensity)):
                    x = np.random.randint(0, size[0])
                    y = np.random.randint(0, size[1])
                    radius = np.random.randint(1, 3)
                    color = (255, 255, 255)
                    cv2.circle(frame, (x, y), radius, color, -1)

        frames.append(frame)

    # Create GIF
    preview_dir = Path(image_path).parent.parent / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)

    preview_path = preview_dir / f"preview_{Path(image_path).stem}.gif"

    # Convert to PIL Images
    pil_frames = [Image.fromarray(frame) for frame in frames]

    # Save as GIF
    pil_frames[0].save(
        preview_path,
        save_all=True,
        append_images=pil_frames[1:],
        duration=int(1000 / 12),  # 12 FPS
        loop=0,
        optimize=False  # Skip optimization for speed
    )

    return str(preview_path)
