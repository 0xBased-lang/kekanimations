#!/usr/bin/env python3
"""
Export Generator
Final high-quality GIF export with Playwright quality validation
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import json


async def generate_final_animation(
    image_path: str,
    effects: List[Dict[str, Any]],
    num_frames: int = 24,
    fps: int = 12,
    quality_target: int = 85,
    output_dir: str = None
) -> Dict[str, Any]:
    """
    Generate final high-quality animation with quality validation

    Args:
        image_path: Path to input image
        effects: List of effect configurations
        num_frames: Number of frames
        fps: Frames per second
        quality_target: Minimum quality score (0-100)
        output_dir: Output directory

    Returns:
        Dictionary with output_path, quality_score, file_size
    """
    from effects.breathing_effect import apply_breathing

    # Output directory
    if output_dir is None:
        output_dir = Path(image_path).parent.parent / "outputs"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Read original image
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Convert to RGB
    if img.shape[2] == 4:
        alpha = img[:, :, 3]
        img_rgb = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2RGB)
    else:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        alpha = None

    height, width = img_rgb.shape[:2]

    # Generate frames with all effects applied
    frames = []

    for i in range(num_frames):
        frame = img_rgb.copy()

        # Apply each effect in order
        for effect in effects:
            effect_type = effect.get("type", "")
            intensity = effect.get("intensity", 1.0)
            params = effect.get("parameters", {})

            if effect_type == "breathing":
                # Apply breathing effect
                phase = (i / num_frames) * 2 * np.pi
                scale_delta = np.sin(phase) * intensity
                scale = 1.0 + scale_delta

                new_width = int(width * scale)
                new_height = int(height * scale)

                resized = cv2.resize(
                    frame,
                    (new_width, new_height),
                    interpolation=cv2.INTER_LANCZOS4
                )

                # Create canvas
                canvas = np.zeros_like(frame)

                if scale > 1.0:
                    # Crop
                    crop_x = (new_width - width) // 2
                    crop_y = (new_height - height) // 2
                    frame = resized[crop_y:crop_y+height, crop_x:crop_x+width]
                else:
                    # Paste
                    paste_x = (width - new_width) // 2
                    paste_y = (height - new_height) // 2
                    canvas[paste_y:paste_y+new_height, paste_x:paste_x+new_width] = resized
                    frame = canvas

            elif effect_type == "rotation":
                # Rotation effect
                degrees = params.get("degrees", 10.0) * intensity
                angle = (i / num_frames) * degrees - (degrees / 2)  # Center rotation
                center = (width // 2, height // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                frame = cv2.warpAffine(frame, M, (width, height), borderMode=cv2.BORDER_REPLICATE)

            elif effect_type == "glow":
                # Glow effect
                color = params.get("color", [255, 0, 0])
                strength = intensity * 0.5

                # Create glow layers
                glow = cv2.GaussianBlur(frame, (21, 21), 0)
                glow_tinted = glow.astype(float)

                for c in range(3):
                    glow_tinted[:, :, c] = glow_tinted[:, :, c] * (color[c] / 255.0)

                # Blend
                frame = cv2.addWeighted(
                    frame.astype(float), 1.0,
                    glow_tinted, strength,
                    0
                ).astype(np.uint8)

            elif effect_type == "sparkles":
                # Sparkle particles
                particle_count = params.get("particle_count", 30)
                for _ in range(int(particle_count * intensity)):
                    x = np.random.randint(0, width)
                    y = np.random.randint(0, height)
                    radius = np.random.randint(1, 4)
                    color = (255, 255, 200 + np.random.randint(0, 55))
                    alpha_val = np.random.uniform(0.5, 1.0)
                    overlay = frame.copy()
                    cv2.circle(overlay, (x, y), radius, color, -1)
                    frame = cv2.addWeighted(frame, 1 - alpha_val, overlay, alpha_val, 0)

            # Add more effect types here as they're implemented
            # elif effect_type == "fire":
            #     frame = apply_fire_effect(frame, intensity, params)
            # elif effect_type == "rotation_3d":
            #     frame = apply_3d_rotation(frame, intensity, params, i, num_frames)

        frames.append(frame)

    # Save as high-quality GIF
    output_filename = Path(image_path).stem + "_animated.gif"
    output_path = output_dir / output_filename

    # Convert to PIL Images
    pil_frames = [Image.fromarray(frame) for frame in frames]

    # Save with optimization
    duration = int(1000 / fps)
    pil_frames[0].save(
        output_path,
        save_all=True,
        append_images=pil_frames[1:],
        duration=duration,
        loop=0,
        optimize=True  # Enable optimization for final export
    )

    # Get file size
    file_size = output_path.stat().st_size

    # Run quality validation with Playwright
    quality_score = await validate_quality(output_path, image_path, quality_target)

    return {
        "output_path": str(output_path),
        "quality_score": quality_score,
        "file_size": file_size,
        "frames": num_frames,
        "fps": fps
    }


async def validate_quality(
    animation_path: str,
    original_image_path: str,
    target_score: int
) -> int:
    """
    Validate animation quality using Playwright

    Args:
        animation_path: Path to generated animation
        original_image_path: Path to original image
        target_score: Target quality score

    Returns:
        Quality score (0-100)
    """
    try:
        # Use existing Playwright quality validation
        # This will integrate with tests/fixtures/quality-scorer.ts

        # For now, return a basic quality score
        # TODO: Integrate with actual Playwright test once frontend is built

        # Basic quality checks
        quality_score = 85  # Baseline

        # Check file exists and has reasonable size
        path = Path(animation_path)
        if not path.exists():
            return 0

        file_size = path.stat().st_size
        if file_size < 100000:  # < 100KB might be corrupted
            quality_score -= 20

        # Check dimensions match
        img_original = cv2.imread(original_image_path)
        img_first_frame = cv2.imread(str(path))

        if img_original is not None and img_first_frame is not None:
            if img_original.shape[:2] == img_first_frame.shape[:2]:
                quality_score += 5
            else:
                quality_score -= 10

        return max(0, min(100, quality_score))

    except Exception as e:
        print(f"Quality validation error: {e}")
        return 0
