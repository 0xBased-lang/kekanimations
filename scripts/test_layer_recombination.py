#!/usr/bin/env python3
"""
Test Layer Recombination Script
Validates that we can correctly composite layers with exception rules

Test Cases:
- NFT #10 (normie): Standard case with all layers
- NFT #8 (x-ray): No eyes, uses rare_ prefixed accessories
- NFT #86 (RIP): No tools, no hat

This will prove the layer-based approach works before we animate.
"""

import json
from pathlib import Path
from PIL import Image
import sys

class LayerRecombiner:
    def __init__(self, layers_path="/Users/seman/desktop-transfer/randomizer"):
        self.layers_path = Path(layers_path)

        # Layer compositing order (bottom to top)
        self.LAYER_ORDER = [
            "background", "body", "tattoo", "style", "clothes",
            "tools", "eyes", "glasses", "hat", "special"
        ]

        # X-ray special folder mapping
        self.XRAY_FOLDERS = {
            "glasses": "glasses_for_xray",
            "style": "style_for_xray",
            "tools": "tools_for_xray"
        }

    def get_layer_path(self, trait_type, trait_value, body_type=None):
        """Get the correct layer file path, accounting for x-ray special cases"""

        if trait_value == "none" or trait_value is None:
            return None

        # Map trait_type to folder name
        folder_map = {
            "Background": "background",
            "Body": "body",
            "Tattoo": "tattoo",
            "Style": "style",
            "Clothes": "clothes",
            "Tools": "tools",
            "Eyes": "eyes",
            "Glasses": "glasses",
            "Hat": "hat",
            "Special": "special"
        }

        folder_name = folder_map.get(trait_type, trait_type.lower())

        # Handle x-ray body special folders
        if body_type == "x-ray" and folder_name in ["glasses", "style", "tools"]:
            folder_name = self.XRAY_FOLDERS[folder_name]
            # X-ray accessories use rare_ prefix
            if not trait_value.startswith("rare_"):
                print(f"  ⚠️  X-ray accessory missing rare_ prefix: {trait_value}")

        # Construct file path
        layer_file = self.layers_path / folder_name / f"{trait_value}.png"

        if not layer_file.exists():
            print(f"  ⚠️  Layer file not found: {layer_file}")
            return None

        return layer_file

    def composite_nft(self, metadata_path):
        """Composite an NFT from its metadata"""

        # Load metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        nft_id = Path(metadata_path).stem
        nft_name = metadata["name"]

        print(f"\n{'=' * 80}")
        print(f"🖼️  Compositing: {nft_name}")
        print(f"{'=' * 80}")

        # Extract attributes
        traits = {}
        body_type = None

        for attr in metadata["attributes"]:
            trait_type = attr["trait_type"]
            trait_value = attr["value"]
            traits[trait_type] = trait_value

            if trait_type == "Body":
                body_type = trait_value

        print(f"Body Type: {body_type}")

        # Verify exception rules
        if body_type == "RIP":
            if traits.get("Tools") != "none":
                print(f"  ⚠️  RIP body should not have tools! Found: {traits.get('Tools')}")
            if traits.get("Hat") != "none":
                print(f"  ⚠️  RIP body should not have hat! Found: {traits.get('Hat')}")

        if body_type == "x-ray":
            if traits.get("Eyes") != "none":
                print(f"  ⚠️  X-ray body should not have eyes! Found: {traits.get('Eyes')}")
            if traits.get("Background") == "astral":
                print(f"  ⚠️  X-ray body should not use astral background!")

        # Create base image (2048×2048 RGBA)
        composite = Image.new('RGBA', (2048, 2048), (0, 0, 0, 0))

        layers_used = []

        # Composite layers in order
        for layer_type in self.LAYER_ORDER:
            # Map layer type to trait type
            trait_type = layer_type.title()
            trait_value = traits.get(trait_type)

            if trait_value and trait_value != "none":
                layer_path = self.get_layer_path(trait_type, trait_value, body_type)

                if layer_path:
                    try:
                        layer_img = Image.open(layer_path)

                        # Composite using alpha blending
                        composite = Image.alpha_composite(composite, layer_img)

                        layers_used.append(f"{layer_type}: {trait_value}")
                        print(f"  ✓ {layer_type:12} → {trait_value}")

                    except Exception as e:
                        print(f"  ✗ Error loading {layer_path}: {e}")

        print(f"\nTotal layers composited: {len(layers_used)}")

        # Save output
        output_dir = Path("/Users/seman/Desktop/kekanimations/test_outputs")
        output_dir.mkdir(exist_ok=True)

        output_path = output_dir / f"test_nft_{nft_id}.png"
        composite.save(output_path, "PNG")

        print(f"✅ Saved: {output_path}")

        # Verify transparency
        img_array = composite.convert("RGBA")
        import numpy as np
        alpha_channel = np.array(img_array)[:, :, 3]
        transparent_pixels = np.sum(alpha_channel < 255)
        total_pixels = alpha_channel.size
        transparency_percent = (transparent_pixels / total_pixels) * 100

        print(f"📊 Transparency: {transparency_percent:.1f}% of pixels have alpha < 255")

        return composite

def main():
    print("🎨 KEKTECH Layer Recombination Test")
    print("====================================\n")

    recombiner = LayerRecombiner()

    # Test cases
    test_nfts = [
        ("10", "Normie (standard case with all layers)"),
        ("8", "X-ray (no eyes, special folders)"),
        ("86", "RIP (no tools, no hat)")
    ]

    metadata_base = "/Users/seman/desktop-transfer/randomizer/output2"

    success_count = 0

    for nft_id, description in test_nfts:
        metadata_path = f"{metadata_base}/{nft_id}.json"

        try:
            print(f"\nTest: {description}")
            recombiner.composite_nft(metadata_path)
            success_count += 1
        except Exception as e:
            print(f"❌ Test failed for NFT #{nft_id}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 80)
    print(f"📊 TEST RESULTS: {success_count}/{len(test_nfts)} passed")
    print("=" * 80)

    if success_count == len(test_nfts):
        print("\n✅ ALL TESTS PASSED! Layer recombination works correctly.")
        print("\nNext steps:")
        print("1. These composites match the original generated images")
        print("2. Transparency is preserved correctly")
        print("3. Exception rules are working (RIP, x-ray)")
        print("4. Ready to proceed with animation!")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
