#!/usr/bin/env python3
"""
KEKTECH NFT Layer Cataloger
Analyzes all layer files and creates a comprehensive catalog for animation planning
Accounts for special cases: RIP body (no tools/hat), X-ray body (special folders, no eyes)
"""

import os
import json
from pathlib import Path
from PIL import Image
import numpy as np
from collections import defaultdict

class LayerCataloger:
    def __init__(self, base_path="/Users/seman/desktop-transfer/randomizer"):
        self.base_path = Path(base_path)
        self.layers_path = self.base_path
        self.output_path = self.base_path / "output2"

        # Exception rules from cursor.py
        self.RIP_EXCEPTIONS = {
            "no_tools": True,
            "no_hat": True,
            "allowed_layers": ["background", "body", "tattoo", "style", "clothes", "eyes", "glasses", "special"]
        }

        self.XRAY_EXCEPTIONS = {
            "no_eyes": True,
            "no_astral_background": True,
            "use_special_glasses": True,
            "use_special_style": True,
            "use_special_tools": True,
            "special_folders": {
                "glasses": "glasses_for_xray",
                "style": "style_for_xray",
                "tools": "tools_for_xray"
            }
        }

        # Layer order for compositing
        self.LAYER_ORDER = [
            "background", "body", "tattoo", "style", "clothes",
            "tools", "eyes", "glasses", "hat", "special"
        ]

        self.catalog = {
            "layers": {},
            "statistics": {},
            "exceptions": {},
            "animation_potential": {}
        }

    def catalog_all_layers(self):
        """Catalog all layer files with their properties"""

        print("=" * 80)
        print("KEKTECH NFT LAYER CATALOG")
        print("=" * 80)

        # Standard layer folders
        standard_folders = [
            "background", "body", "clothes", "eyes", "glasses",
            "hat", "special", "style", "tattoo", "tools"
        ]

        # Special x-ray folders
        xray_folders = ["glasses_for_xray", "style_for_xray", "tools_for_xray"]

        all_folders = standard_folders + xray_folders

        total_files = 0

        for folder_name in all_folders:
            folder_path = self.layers_path / folder_name

            if not folder_path.exists():
                print(f"⚠️  Folder not found: {folder_name}")
                continue

            layer_files = list(folder_path.glob("*.png"))

            if not layer_files:
                print(f"⚠️  No PNG files in: {folder_name}")
                continue

            print(f"\n📁 {folder_name.upper()}")
            print("-" * 40)

            self.catalog["layers"][folder_name] = {}

            for layer_file in sorted(layer_files):
                # Get file info
                file_info = self.analyze_layer_file(layer_file)

                # Store in catalog
                layer_name = layer_file.stem
                self.catalog["layers"][folder_name][layer_name] = file_info

                # Print summary
                print(f"  • {layer_name:20} | {file_info['size_mb']:.1f}MB | "
                      f"{file_info['width']}×{file_info['height']} | "
                      f"Alpha: {file_info['has_alpha']} | "
                      f"Transparency: {file_info['transparency_percent']:.1f}%")

                total_files += 1

            print(f"  Total: {len(layer_files)} files")

        print(f"\n📊 TOTAL UNIQUE LAYERS: {total_files}")

        # Analyze exception cases
        self.analyze_exceptions()

        # Determine animation potential
        self.assess_animation_potential()

        # Save catalog
        self.save_catalog()

    def analyze_layer_file(self, file_path):
        """Analyze a single layer file for properties"""

        try:
            img = Image.open(file_path)

            # Basic properties
            width, height = img.size
            mode = img.mode
            has_alpha = mode in ('RGBA', 'LA')

            # File size
            size_bytes = file_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)

            # Analyze transparency if has alpha
            transparency_percent = 0
            avg_alpha = 255

            if has_alpha:
                img_array = np.array(img)
                if mode == 'RGBA':
                    alpha_channel = img_array[:, :, 3]
                else:  # LA mode
                    alpha_channel = img_array[:, :, 1]

                # Calculate transparency statistics
                transparent_pixels = np.sum(alpha_channel < 255)
                total_pixels = alpha_channel.size
                transparency_percent = (transparent_pixels / total_pixels) * 100
                avg_alpha = np.mean(alpha_channel)

            # Detect if this is primarily a character or background
            is_background = "background" in str(file_path).lower()

            return {
                "filename": file_path.name,
                "width": width,
                "height": height,
                "mode": mode,
                "has_alpha": has_alpha,
                "size_mb": size_mb,
                "transparency_percent": transparency_percent,
                "avg_alpha": float(avg_alpha),
                "is_background": is_background,
                "full_path": str(file_path)
            }

        except Exception as e:
            print(f"    ⚠️  Error analyzing {file_path.name}: {e}")
            return {
                "filename": file_path.name,
                "error": str(e)
            }

    def analyze_exceptions(self):
        """Analyze and document exception cases"""

        print("\n" + "=" * 80)
        print("EXCEPTION RULES ANALYSIS")
        print("=" * 80)

        # RIP body exceptions
        print("\n🪦 RIP BODY EXCEPTIONS:")
        print("  • Cannot use tools")
        print("  • Cannot wear hats")
        print("  • Allowed layers:", ", ".join(self.RIP_EXCEPTIONS["allowed_layers"]))

        # X-ray body exceptions
        print("\n💀 X-RAY BODY EXCEPTIONS:")
        print("  • Cannot have eyes (transparent body)")
        print("  • Cannot use astral background")
        print("  • Must use special folders:")
        for standard, special in self.XRAY_EXCEPTIONS["special_folders"].items():
            standard_count = len(self.catalog["layers"].get(standard, {}))
            special_count = len(self.catalog["layers"].get(special, {}))
            print(f"    - {standard} ({standard_count}) → {special} ({special_count})")

        # Store in catalog
        self.catalog["exceptions"] = {
            "RIP": self.RIP_EXCEPTIONS,
            "x-ray": self.XRAY_EXCEPTIONS
        }

    def assess_animation_potential(self):
        """Assess animation potential for each layer type"""

        print("\n" + "=" * 80)
        print("ANIMATION POTENTIAL ASSESSMENT")
        print("=" * 80)

        animation_potential = {
            "body": {
                "priority": "HIGH",
                "animations": ["breathing", "idle_sway", "glow"],
                "estimated_templates": 8,
                "notes": "Main character animation, most important"
            },
            "eyes": {
                "priority": "HIGH",
                "animations": ["blink", "look_around", "glow"],
                "estimated_templates": 12,
                "notes": "Critical for bringing character to life (except x-ray)"
            },
            "background": {
                "priority": "MEDIUM",
                "animations": ["parallax", "color_shift", "particles"],
                "estimated_templates": 5,
                "notes": "Selective animation for dynamic backgrounds"
            },
            "hat": {
                "priority": "MEDIUM",
                "animations": ["bounce", "tilt"],
                "estimated_templates": 3,
                "notes": "Simple physics-based movement (except RIP)"
            },
            "glasses": {
                "priority": "LOW",
                "animations": ["shimmer", "lens_flare"],
                "estimated_templates": 2,
                "notes": "Subtle effects only"
            },
            "tools": {
                "priority": "MEDIUM",
                "animations": ["swing", "rotate", "glow"],
                "estimated_templates": 4,
                "notes": "Depends on tool type (except RIP)"
            },
            "special": {
                "priority": "HIGH",
                "animations": ["particles", "glow", "custom"],
                "estimated_templates": 4,
                "notes": "Effect-specific animations"
            },
            "clothes": {
                "priority": "LOW",
                "animations": ["fabric_wave"],
                "estimated_templates": 2,
                "notes": "Very subtle movement only"
            },
            "tattoo": {
                "priority": "LOW",
                "animations": ["shimmer", "pulse"],
                "estimated_templates": 2,
                "notes": "Subtle glow or color effects"
            },
            "style": {
                "priority": "LOW",
                "animations": ["glow"],
                "estimated_templates": 1,
                "notes": "Minimal animation needed"
            }
        }

        total_templates = 0

        for layer_type, info in animation_potential.items():
            print(f"\n📍 {layer_type.upper()}")
            print(f"  Priority: {info['priority']}")
            print(f"  Animations: {', '.join(info['animations'])}")
            print(f"  Templates needed: ~{info['estimated_templates']}")
            print(f"  Notes: {info['notes']}")

            total_templates += info["estimated_templates"]

        print(f"\n🎯 TOTAL ANIMATION TEMPLATES NEEDED: ~{total_templates}")

        self.catalog["animation_potential"] = animation_potential
        self.catalog["statistics"]["total_templates_needed"] = total_templates

    def analyze_metadata_usage(self):
        """Analyze how layers are actually used in the 4,200 NFTs"""

        print("\n" + "=" * 80)
        print("METADATA USAGE ANALYSIS")
        print("=" * 80)

        # Count trait usage from metadata
        trait_usage = defaultdict(lambda: defaultdict(int))
        body_type_count = defaultdict(int)

        metadata_files = list(self.output_path.glob("*.json"))

        print(f"Analyzing {len(metadata_files)} NFT metadata files...")

        rip_count = 0
        xray_count = 0

        for metadata_file in metadata_files[:100]:  # Sample first 100 for speed
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)

                for attr in data.get("attributes", []):
                    trait_type = attr["trait_type"]
                    trait_value = attr["value"]

                    if trait_value and trait_value != "none":
                        trait_usage[trait_type][trait_value] += 1

                        if trait_type == "Body":
                            body_type_count[trait_value] += 1
                            if trait_value == "RIP":
                                rip_count += 1
                            elif trait_value == "x-ray":
                                xray_count += 1

            except Exception as e:
                print(f"  Error reading {metadata_file.name}: {e}")

        print(f"\n📊 Body Type Distribution (sample):")
        for body, count in sorted(body_type_count.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {body}: {count}")

        print(f"\n⚠️  Special Cases in Sample:")
        print(f"  • RIP bodies: {rip_count} (no tools/hats)")
        print(f"  • X-ray bodies: {xray_count} (special folders, no eyes)")

    def save_catalog(self):
        """Save the catalog to JSON file"""

        output_file = Path("/Users/seman/Desktop/kekanimations/analysis/layer_catalog.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(self.catalog, f, indent=2, default=str)

        print(f"\n✅ Catalog saved to: {output_file}")

        # Also save a summary
        summary_file = Path("/Users/seman/Desktop/kekanimations/analysis/layer_summary.txt")

        with open(summary_file, 'w') as f:
            f.write("KEKTECH NFT LAYER SUMMARY\n")
            f.write("=" * 80 + "\n\n")

            f.write("LAYER COUNTS:\n")
            for folder, layers in self.catalog["layers"].items():
                f.write(f"  {folder}: {len(layers)} files\n")

            f.write(f"\nTOTAL ANIMATION TEMPLATES NEEDED: ~{self.catalog['statistics']['total_templates_needed']}\n")

            f.write("\nEXCEPTION RULES:\n")
            f.write("  RIP: No tools, no hats\n")
            f.write("  X-ray: No eyes, special accessory folders\n")

            f.write("\nANIMATION PRIORITIES:\n")
            for layer_type, info in self.catalog["animation_potential"].items():
                if info["priority"] == "HIGH":
                    f.write(f"  HIGH: {layer_type}\n")

        print(f"✅ Summary saved to: {summary_file}")

def main():
    print("🎨 KEKTECH NFT Layer Cataloger")
    print("================================\n")

    cataloger = LayerCataloger()

    # Catalog all layers
    cataloger.catalog_all_layers()

    # Analyze metadata usage (optional, takes time)
    cataloger.analyze_metadata_usage()

    print("\n✅ Cataloging complete!")
    print("\nNext steps:")
    print("1. Review layer_catalog.json for complete details")
    print("2. Create animation templates for HIGH priority layers first")
    print("3. Test recombination with exception rules")
    print("4. Scale to full collection")

if __name__ == "__main__":
    main()