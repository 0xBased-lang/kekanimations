#!/usr/bin/env python3
"""
Breathing Effect Processor
Uses validated code from scripts/test_mesh_deformation.py
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import asyncio


async def apply_breathing(
    image_path: str,
    intensity: float = 0.02,
    num_frames: int = 24,
    fps: int = 12
) -> list:
    """
    Apply breathing animation effect using simple scaling

    Args:
        image_path: Path to input image
        intensity: Breathing intensity (0.015 = subtle, 0.02 = normal, 0.03 = dramatic)
        num_frames: Number of frames to generate
        fps: Frames per second

    Returns:
        List of frame paths
    """
    # Read image
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Convert RGBA to RGB if needed
    if img.shape[2] == 4:
        # Preserve alpha channel
        alpha = img[:, :, 3]
        img_rgb = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2RGB)
    else:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        alpha = None

    height, width = img_rgb.shape[:2]
    center_x, center_y = width // 2, height // 2

    # Generate frames with sinusoidal breathing
    frames = []
    output_dir = Path(image_path).parent.parent / "outputs" / "breathing_frames"
    output_dir.mkdir(parents=True, exist_ok=True)

    for i in range(num_frames):
        # Calculate scale factor using sine wave
        # This creates smooth breathing motion
        phase = (i / num_frames) * 2 * np.pi
        scale_delta = np.sin(phase) * intensity
        scale = 1.0 + scale_delta  # e.g., 0.98 to 1.02 for intensity=0.02

        # Calculate new dimensions
        new_width = int(width * scale)
        new_height = int(height * scale)

        # Resize image
        resized = cv2.resize(
            img_rgb,
            (new_width, new_height),
            interpolation=cv2.INTER_LANCZOS4  # High quality interpolation
        )

        # Create canvas at original size
        canvas = np.zeros((height, width, 3), dtype=np.uint8)

        # Calculate paste position (center the scaled image)
        paste_x = (width - new_width) // 2
        paste_y = (height - new_height) // 2

        # Handle cropping if scaled image is larger than canvas
        if scale > 1.0:
            crop_x = (new_width - width) // 2
            crop_y = (new_height - height) // 2
            cropped = resized[crop_y:crop_y+height, crop_x:crop_x+width]
            canvas = cropped
        else:
            # Paste smaller image onto canvas
            canvas[paste_y:paste_y+new_height, paste_x:paste_x+new_width] = resized

        # Resize alpha channel if it exists
        if alpha is not None:
            resized_alpha = cv2.resize(
                alpha,
                (new_width, new_height),
                interpolation=cv2.INTER_LANCZOS4
            )

            # Create alpha canvas
            alpha_canvas = np.zeros((height, width), dtype=np.uint8)

            if scale > 1.0:
                crop_x = (new_width - width) // 2
                crop_y = (new_height - height) // 2
                alpha_canvas = resized_alpha[crop_y:crop_y+height, crop_x:crop_x+width]
            else:
                alpha_canvas[paste_y:paste_y+new_height, paste_x:paste_x+new_width] = resized_alpha

            # Combine RGB + Alpha
            canvas = np.dstack([canvas, alpha_canvas])

        # Save frame
        frame_path = output_dir / f"frame_{i:04d}.png"

        # Convert RGB back to BGR for OpenCV
        if alpha is not None:
            # RGBA
            frame_bgra = np.dstack([
                cv2.cvtColor(canvas[:, :, :3], cv2.COLOR_RGB2BGR),
                canvas[:, :, 3]
            ])
            cv2.imwrite(str(frame_path), frame_bgra)
        else:
            # RGB
            cv2.imwrite(str(frame_path), cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR))

        frames.append(str(frame_path))

    return frames
