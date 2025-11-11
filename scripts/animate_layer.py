#!/usr/bin/env python3
"""
Layer-Specific Animation Engine
Applies appropriate animation effects based on layer type and trait

This script is the core of the hybrid approach:
1. Animate each layer template (43 total) with layer-specific effects
2. Preserve 100% character fidelity through pure Python
3. Output frame sequences that can be recombined per-NFT

Layer Animation Strategies:
- Body: Subtle Y-axis breathing (2-3px sine wave)
- Eyes: Blinking animation (close on specific frames)
- Hat: Bouncing with spring physics
- Tools: Swing/rotate based on tool type
- Background: Parallax effect (slower motion)
- Special: Custom effects (glow, particles, etc.)
- Glasses, Tattoo, Clothes, Style: Subtle movements
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import json
import sys
import time


class LayerAnimator:
    """
    Handles layer-specific animation logic
    """

    def __init__(self, num_frames=16, fps=12, output_resolution=(2048, 2048)):
        self.num_frames = num_frames
        self.fps = fps
        self.output_resolution = output_resolution

        # Animation parameters per layer type
        self.animation_params = {
            "body": {
                "type": "breathing",
                "amplitude_px": 3,  # Y-axis movement
                "phase_offset": 0.0
            },
            "eyes": {
                "type": "blink",
                "blink_start": 7,  # Frame index
                "blink_duration": 3,  # Number of frames
                "blink_intensity": 0.9  # How much to close (0=fully open, 1=fully closed)
            },
            "hat": {
                "type": "bounce",
                "amplitude_px": 8,
                "spring_constant": 0.15,
                "damping": 0.92,
                "delay_frames": 2
            },
            "tools": {
                "type": "swing",
                "angle_degrees": 5,
                "pivot_point": "bottom_center"
            },
            "background": {
                "type": "parallax",
                "amplitude_px": 2,
                "speed_multiplier": 0.5  # Slower than foreground
            },
            "special": {
                "type": "glow",
                "intensity_variation": 0.15,
                "pulse_speed": 1.0
            },
            "glasses": {
                "type": "subtle_tilt",
                "angle_degrees": 1.5
            },
            "tattoo": {
                "type": "breathing",  # Same as body
                "amplitude_px": 2,
                "phase_offset": 0.2  # Slight delay
            },
            "clothes": {
                "type": "breathing",  # Same as body
                "amplitude_px": 2.5,
                "phase_offset": 0.1
            },
            "style": {
                "type": "breathing",  # Same as body
                "amplitude_px": 2,
                "phase_offset": 0.15
            }
        }

    def animate_layer(self, layer_image_path, layer_type, trait_name):
        """
        Main entry point: animate a single layer

        Args:
            layer_image_path: Path to layer PNG file
            layer_type: Type of layer (body, eyes, hat, etc.)
            trait_name: Specific trait name (e.g., "normie", "wrecked", "santa")

        Returns:
            List of PIL Image frames with alpha channel preserved
        """
        print(f"\n{'=' * 80}")
        print(f"🎬 Animating Layer: {layer_type}/{trait_name}")
        print(f"{'=' * 80}")

        # Load layer image
        layer_img = cv2.imread(str(layer_image_path), cv2.IMREAD_UNCHANGED)

        if layer_img is None:
            print(f"❌ Failed to load image: {layer_image_path}")
            return None

        print(f"  Image size: {layer_img.shape}")
        print(f"  Frames: {self.num_frames}")
        print(f"  Animation type: {self.animation_params.get(layer_type, {}).get('type', 'none')}")

        # Ensure RGBA format
        if len(layer_img.shape) == 2:
            # Grayscale -> RGBA
            layer_img = cv2.cvtColor(layer_img, cv2.COLOR_GRAY2RGBA)
        elif layer_img.shape[2] == 3:
            # RGB -> RGBA
            layer_img = cv2.cvtColor(layer_img, cv2.COLOR_RGB2RGBA)
        elif layer_img.shape[2] == 4:
            # Already RGBA, ensure correct channel order
            layer_img = cv2.cvtColor(layer_img, cv2.COLOR_BGRA2RGBA)

        # Route to specific animation method
        animation_type = self.animation_params.get(layer_type, {}).get("type", "static")

        if animation_type == "breathing":
            frames = self.animate_breathing(layer_img, layer_type)
        elif animation_type == "blink":
            frames = self.animate_blink(layer_img, trait_name)
        elif animation_type == "bounce":
            frames = self.animate_bounce(layer_img)
        elif animation_type == "swing":
            frames = self.animate_swing(layer_img, trait_name)
        elif animation_type == "parallax":
            frames = self.animate_parallax(layer_img)
        elif animation_type == "glow":
            frames = self.animate_glow(layer_img, trait_name)
        elif animation_type == "subtle_tilt":
            frames = self.animate_subtle_tilt(layer_img)
        else:
            # No animation - return static frames
            frames = [self.cv2_to_pil(layer_img)] * self.num_frames

        print(f"  ✅ Generated {len(frames)} frames")

        return frames

    def animate_breathing(self, img, layer_type):
        """
        Subtle Y-axis breathing animation
        Used for body, tattoo, clothes, style layers
        """
        params = self.animation_params.get(layer_type, {})
        amplitude = params.get("amplitude_px", 3)
        phase_offset = params.get("phase_offset", 0.0)

        frames = []
        h, w = img.shape[:2]

        for i in range(self.num_frames):
            # Sinusoidal breathing curve with phase offset
            t = (i / self.num_frames) + phase_offset
            y_offset = int(np.sin(t * 2 * np.pi) * amplitude)

            # Create canvas
            canvas = np.zeros((h, w, 4), dtype=np.uint8)

            # Shift image vertically
            if y_offset > 0:
                # Move down
                canvas[y_offset:, :] = img[:h-y_offset, :]
            elif y_offset < 0:
                # Move up
                canvas[:h+y_offset, :] = img[-y_offset:, :]
            else:
                canvas = img.copy()

            frames.append(self.cv2_to_pil(canvas))

            # Progress
            if (i + 1) % 4 == 0:
                print(f"    Progress: {(i+1)/self.num_frames*100:.0f}%", end='\r')

        print()  # New line after progress
        return frames

    def animate_blink(self, img, trait_name):
        """
        Blinking animation for eyes
        Closes eyes on specific frames
        """
        params = self.animation_params["eyes"]
        blink_start = params["blink_start"]
        blink_duration = params["blink_duration"]
        blink_intensity = params["blink_intensity"]

        frames = []
        h, w = img.shape[:2]

        for i in range(self.num_frames):
            # Check if we're in blink range
            blink_frame = i >= blink_start and i < blink_start + blink_duration

            if blink_frame:
                # Calculate blink progress (0 = start, 1 = peak, 0 = end)
                blink_progress = (i - blink_start) / blink_duration

                # Smooth blink curve (closes then opens)
                if blink_progress < 0.5:
                    # Closing
                    close_factor = (blink_progress * 2) * blink_intensity
                else:
                    # Opening
                    close_factor = ((1 - blink_progress) * 2) * blink_intensity

                # Vertical squeeze effect
                squeeze_height = int(h * (1 - close_factor))

                if squeeze_height < 10:
                    # Fully closed - just transparent
                    canvas = np.zeros((h, w, 4), dtype=np.uint8)
                else:
                    # Resize vertically
                    squeezed = cv2.resize(img, (w, squeeze_height), interpolation=cv2.INTER_LANCZOS4)

                    # Center on canvas
                    canvas = np.zeros((h, w, 4), dtype=np.uint8)
                    y_offset = (h - squeeze_height) // 2
                    canvas[y_offset:y_offset+squeeze_height, :] = squeezed
            else:
                # Eyes open
                canvas = img.copy()

            frames.append(self.cv2_to_pil(canvas))

            if (i + 1) % 4 == 0:
                print(f"    Progress: {(i+1)/self.num_frames*100:.0f}%", end='\r')

        print()
        return frames

    def animate_bounce(self, img):
        """
        Bouncing animation with spring physics for hats
        """
        params = self.animation_params["hat"]
        amplitude = params["amplitude_px"]
        spring_k = params["spring_constant"]
        damping = params["damping"]
        delay = params["delay_frames"]

        frames = []
        h, w = img.shape[:2]

        # Spring physics simulation
        position = 0.0
        velocity = 0.0

        positions = []

        for i in range(self.num_frames):
            if i < delay:
                # No movement during delay
                positions.append(0)
            else:
                # Apply spring force
                force = -spring_k * position
                velocity += force
                velocity *= damping
                position += velocity

                # Start with an impulse
                if i == delay:
                    position = amplitude

                positions.append(position)

        # Generate frames
        for i, y_offset in enumerate(positions):
            canvas = np.zeros((h, w, 4), dtype=np.uint8)

            y_shift = int(y_offset)

            if y_shift > 0:
                # Move down
                canvas[y_shift:, :] = img[:h-y_shift, :]
            elif y_shift < 0:
                # Move up
                canvas[:h+y_shift, :] = img[-y_shift:, :]
            else:
                canvas = img.copy()

            frames.append(self.cv2_to_pil(canvas))

            if (i + 1) % 4 == 0:
                print(f"    Progress: {(i+1)/self.num_frames*100:.0f}%", end='\r')

        print()
        return frames

    def animate_swing(self, img, trait_name):
        """
        Swing/rotate animation for tools
        Pivot point depends on tool type
        """
        params = self.animation_params["tools"]
        max_angle = params["angle_degrees"]

        frames = []
        h, w = img.shape[:2]
        center = (w // 2, h // 2)

        for i in range(self.num_frames):
            # Sinusoidal swing
            t = i / self.num_frames
            angle = np.sin(t * 2 * np.pi) * max_angle

            # Rotation matrix
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

            # Apply rotation with proper alpha handling
            rotated = cv2.warpAffine(
                img, rotation_matrix, (w, h),
                flags=cv2.INTER_LANCZOS4,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0, 0, 0, 0)
            )

            frames.append(self.cv2_to_pil(rotated))

            if (i + 1) % 4 == 0:
                print(f"    Progress: {(i+1)/self.num_frames*100:.0f}%", end='\r')

        print()
        return frames

    def animate_parallax(self, img):
        """
        Parallax effect for backgrounds (slower horizontal movement)
        """
        params = self.animation_params["background"]
        amplitude = params["amplitude_px"]
        speed = params["speed_multiplier"]

        frames = []
        h, w = img.shape[:2]

        for i in range(self.num_frames):
            # Sinusoidal horizontal movement
            t = (i / self.num_frames) * speed
            x_offset = int(np.sin(t * 2 * np.pi) * amplitude)

            # Shift image horizontally
            canvas = np.zeros((h, w, 4), dtype=np.uint8)

            if x_offset > 0:
                canvas[:, x_offset:] = img[:, :w-x_offset]
            elif x_offset < 0:
                canvas[:, :w+x_offset] = img[:, -x_offset:]
            else:
                canvas = img.copy()

            frames.append(self.cv2_to_pil(canvas))

        return frames

    def animate_glow(self, img, trait_name):
        """
        Glow/pulse effect for special layers
        Varies brightness/alpha over time
        """
        params = self.animation_params["special"]
        intensity_var = params["intensity_variation"]

        frames = []

        for i in range(self.num_frames):
            # Sinusoidal brightness variation
            t = i / self.num_frames
            brightness_factor = 1.0 + (np.sin(t * 2 * np.pi) * intensity_var)

            # Apply brightness adjustment
            adjusted = img.copy()
            adjusted[:, :, :3] = np.clip(
                adjusted[:, :, :3].astype(float) * brightness_factor,
                0, 255
            ).astype(np.uint8)

            frames.append(self.cv2_to_pil(adjusted))

        return frames

    def animate_subtle_tilt(self, img):
        """
        Subtle tilt animation for glasses
        """
        params = self.animation_params["glasses"]
        max_angle = params["angle_degrees"]

        frames = []
        h, w = img.shape[:2]
        center = (w // 2, h // 2)

        for i in range(self.num_frames):
            # Gentle sinusoidal tilt
            t = i / self.num_frames
            angle = np.sin(t * 2 * np.pi) * max_angle

            # Rotation matrix
            rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)

            # Apply rotation
            rotated = cv2.warpAffine(
                img, rotation_matrix, (w, h),
                flags=cv2.INTER_LANCZOS4,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0, 0, 0, 0)
            )

            frames.append(self.cv2_to_pil(rotated))

        return frames

    def cv2_to_pil(self, cv2_image):
        """Convert OpenCV RGBA image to PIL Image"""
        # cv2_image is already in RGBA format from our conversions
        return Image.fromarray(cv2_image)

    def save_frames(self, frames, output_dir, layer_type, trait_name):
        """
        Save frame sequence as individual PNG files

        Args:
            frames: List of PIL Images
            output_dir: Directory to save frames
            layer_type: Type of layer (for folder structure)
            trait_name: Trait name (for filename)
        """
        output_path = Path(output_dir) / layer_type / trait_name
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\n💾 Saving {len(frames)} frames to {output_path}")

        start_time = time.time()

        for i, frame in enumerate(frames):
            frame_filename = output_path / f"frame_{i:04d}.png"
            frame.save(frame_filename, "PNG", optimize=True)

            if (i + 1) % 4 == 0:
                print(f"    Saved: {i+1}/{len(frames)} frames", end='\r')

        elapsed = time.time() - start_time

        print(f"\n  ✅ Saved {len(frames)} frames in {elapsed:.2f}s")

        return output_path

    def save_as_gif(self, frames, output_path, optimize=True):
        """
        Save frames as animated GIF (for preview)
        """
        if not frames:
            print("❌ No frames to save")
            return False

        print(f"\n💾 Saving preview GIF: {output_path}")

        duration = int(1000 / self.fps)  # Duration per frame in ms

        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=0,
            optimize=optimize
        )

        # File size
        file_size_mb = Path(output_path).stat().st_size / (1024 * 1024)
        print(f"  ✅ Saved GIF: {file_size_mb:.2f} MB")

        return True


def main():
    """
    Command-line interface for layer animation
    """
    print("\n" + "=" * 80)
    print("🎨 KEKTECH Layer Animation Engine")
    print("=" * 80)

    if len(sys.argv) < 4:
        print("\nUsage: python animate_layer.py <layer_image> <layer_type> <trait_name> [options]")
        print("\nArguments:")
        print("  layer_image    Path to layer PNG file")
        print("  layer_type     Type of layer (body, eyes, hat, tools, etc.)")
        print("  trait_name     Trait name (normie, wrecked, santa, etc.)")
        print("\nOptions:")
        print("  --frames N     Number of frames (default: 16)")
        print("  --fps N        Frames per second (default: 12)")
        print("  --output DIR   Output directory (default: output/animated_layers)")
        print("  --preview      Save preview GIF")
        print("\nExamples:")
        print("  python animate_layer.py media_files/nft_layers/body/normie.png body normie")
        print("  python animate_layer.py media_files/nft_layers/eyes/wrecked.png eyes wrecked --preview")
        print("  python animate_layer.py media_files/nft_layers/hat/santa.png hat santa --frames 16 --fps 12")
        print("\nSupported layer types:")
        print("  body, eyes, hat, tools, background, special, glasses, tattoo, clothes, style")
        sys.exit(1)

    # Parse arguments
    layer_image_path = sys.argv[1]
    layer_type = sys.argv[2].lower()
    trait_name = sys.argv[3]

    # Defaults
    num_frames = 16
    fps = 12
    output_dir = "output/animated_layers"
    save_preview = False

    # Parse options
    i = 4
    while i < len(sys.argv):
        if sys.argv[i] == '--frames' and i + 1 < len(sys.argv):
            num_frames = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--fps' and i + 1 < len(sys.argv):
            fps = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--preview':
            save_preview = True
            i += 1
        else:
            i += 1

    # Validate inputs
    if not Path(layer_image_path).exists():
        print(f"❌ Image file not found: {layer_image_path}")
        sys.exit(1)

    # Create animator
    animator = LayerAnimator(num_frames=num_frames, fps=fps)

    # Animate layer
    frames = animator.animate_layer(layer_image_path, layer_type, trait_name)

    if not frames:
        print("❌ Animation failed")
        sys.exit(1)

    # Save frames
    output_path = animator.save_frames(frames, output_dir, layer_type, trait_name)

    # Save preview GIF if requested
    if save_preview:
        gif_path = Path(output_dir) / "previews" / f"{layer_type}_{trait_name}.gif"
        gif_path.parent.mkdir(parents=True, exist_ok=True)
        animator.save_as_gif(frames, gif_path)

    # Summary
    print("\n" + "=" * 80)
    print("✅ ANIMATION COMPLETE")
    print("=" * 80)
    print(f"\n📁 Frames saved to: {output_path}")
    print(f"🎬 Total frames: {num_frames} @ {fps} FPS")
    print(f"🎨 Animation type: {animator.animation_params.get(layer_type, {}).get('type', 'static')}")

    if save_preview:
        print(f"🖼️  Preview GIF: {gif_path}")

    print("\nNext steps:")
    print("1. Repeat for all 43 layer templates")
    print("2. Use frame sequences in recombination script")
    print("3. Generate full 4,200 NFT animations")

    return output_path


if __name__ == '__main__':
    main()
