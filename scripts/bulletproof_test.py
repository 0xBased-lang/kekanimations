#!/usr/bin/env python3
"""
Bulletproof Testing Suite - Comprehensive Validation
Tests edge cases, error handling, consistency, and performance
"""

import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import os
import sys
import time
import traceback
from pathlib import Path

class BulletproofTester:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def log(self, test_name, status, message, details=None):
        """Log test result."""
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details
        }
        self.results.append(result)

        # Console output
        status_icon = {
            'PASS': '✅',
            'FAIL': '❌',
            'WARN': '⚠️',
            'INFO': 'ℹ️'
        }.get(status, '•')

        print(f"{status_icon} {test_name}: {message}")
        if details:
            for key, value in details.items():
                print(f"    {key}: {value}")

        # Update counters
        if status == 'PASS':
            self.passed += 1
        elif status == 'FAIL':
            self.failed += 1
        elif status == 'WARN':
            self.warnings += 1

    def test_image_loading(self):
        """Test loading various image formats."""
        print("\n" + "=" * 60)
        print("TEST SUITE 1: Image Loading & Format Handling")
        print("=" * 60)

        test_images = [
            ('temp_normie_rgb_1024.png', 'RGB 1024x1024'),
            ('temp_normie_alpha_1024.png', 'RGBA 1024x1024'),
            ('temp_normie_rgb.png', 'RGB original size'),
            ('temp_normie_alpha.png', 'RGBA original size'),
        ]

        for img_path, description in test_images:
            try:
                if not os.path.exists(img_path):
                    self.log(
                        f"Load {description}",
                        'WARN',
                        f"File not found: {img_path}",
                        {'expected': img_path}
                    )
                    continue

                # Load image
                img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)

                if img is None:
                    self.log(
                        f"Load {description}",
                        'FAIL',
                        "cv2.imread returned None",
                        {'file': img_path}
                    )
                    continue

                # Check shape
                shape_str = f"{img.shape}"
                channels = img.shape[2] if len(img.shape) == 3 else 1

                self.log(
                    f"Load {description}",
                    'PASS',
                    f"Loaded successfully",
                    {
                        'shape': shape_str,
                        'channels': channels,
                        'dtype': str(img.dtype)
                    }
                )

            except Exception as e:
                self.log(
                    f"Load {description}",
                    'FAIL',
                    f"Exception: {str(e)}",
                    {'traceback': traceback.format_exc()}
                )

    def test_pixel_analysis_consistency(self):
        """Test if pixel analysis gives consistent results across runs."""
        print("\n" + "=" * 60)
        print("TEST SUITE 2: Pixel Analysis Consistency")
        print("=" * 60)

        test_image = 'temp_normie_rgb_1024.png'

        if not os.path.exists(test_image):
            self.log(
                "Consistency Test",
                'WARN',
                f"Test image not found: {test_image}"
            )
            return

        try:
            # Run analysis 3 times
            results = []

            for run in range(3):
                img = cv2.imread(test_image, cv2.IMREAD_UNCHANGED)

                # Add alpha if missing
                if len(img.shape) == 3 and img.shape[2] == 3:
                    alpha = np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255
                    img = np.dstack([img, alpha])

                rgb = img[:, :, :3]
                alpha = img[:, :, 3]

                visible_mask = alpha > 10
                visible_pixels = rgb[visible_mask].reshape(-1, 3).astype(float)

                # K-Means
                kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                labels = kmeans.fit_predict(visible_pixels)

                # Store color centers
                results.append(kmeans.cluster_centers_)

            # Compare results
            differences = []
            for i in range(len(results) - 1):
                diff = np.abs(results[i] - results[i+1])
                max_diff = np.max(diff)
                differences.append(max_diff)

            max_variance = max(differences) if differences else 0

            if max_variance < 0.01:  # Less than 0.01 RGB difference
                self.log(
                    "Consistency Test",
                    'PASS',
                    "Results are consistent across runs",
                    {
                        'runs': 3,
                        'max_variance': f"{max_variance:.6f}",
                        'tolerance': '0.01'
                    }
                )
            else:
                self.log(
                    "Consistency Test",
                    'WARN',
                    "Minor variance detected between runs",
                    {
                        'max_variance': f"{max_variance:.6f}",
                        'tolerance': '0.01'
                    }
                )

        except Exception as e:
            self.log(
                "Consistency Test",
                'FAIL',
                f"Exception: {str(e)}",
                {'traceback': traceback.format_exc()}
            )

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        print("\n" + "=" * 60)
        print("TEST SUITE 3: Edge Cases & Error Handling")
        print("=" * 60)

        # Test 1: Non-existent file
        try:
            img = cv2.imread('nonexistent_file.png', cv2.IMREAD_UNCHANGED)
            if img is None:
                self.log(
                    "Non-existent file",
                    'PASS',
                    "Correctly returns None for missing file"
                )
            else:
                self.log(
                    "Non-existent file",
                    'FAIL',
                    "Should return None for missing file"
                )
        except Exception as e:
            self.log(
                "Non-existent file",
                'FAIL',
                f"Should handle missing file gracefully: {str(e)}"
            )

        # Test 2: Empty clusters
        try:
            # Create mostly black image
            black_img = np.zeros((100, 100, 3), dtype=np.uint8)
            # Add just a few colored pixels
            black_img[50:52, 50:52] = [255, 0, 0]

            pixels = black_img.reshape(-1, 3).astype(float)
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            labels = kmeans.fit_predict(pixels)

            self.log(
                "Low variance clustering",
                'PASS',
                "Handles images with few colors",
                {'unique_clusters': len(np.unique(labels))}
            )

        except Exception as e:
            self.log(
                "Low variance clustering",
                'FAIL',
                f"Exception with low variance image: {str(e)}"
            )

        # Test 3: Single color image
        try:
            single_color = np.ones((100, 100, 3), dtype=np.uint8) * 128

            pixels = single_color.reshape(-1, 3).astype(float)
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            labels = kmeans.fit_predict(pixels)

            # All pixels should be in one cluster
            unique_labels = np.unique(labels)

            self.log(
                "Single color image",
                'PASS',
                "Handles single-color image",
                {'clusters_created': len(unique_labels)}
            )

        except Exception as e:
            self.log(
                "Single color image",
                'FAIL',
                f"Exception with single color: {str(e)}"
            )

    def test_animation_generation(self):
        """Test animation generation robustness."""
        print("\n" + "=" * 60)
        print("TEST SUITE 4: Animation Generation")
        print("=" * 60)

        test_image = 'temp_normie_rgb_1024.png'

        if not os.path.exists(test_image):
            self.log(
                "Animation Generation",
                'WARN',
                f"Test image not found: {test_image}"
            )
            return

        try:
            # Load image
            img = cv2.imread(test_image, cv2.IMREAD_UNCHANGED)

            # Generate animation
            frames = []
            h, w = img.shape[:2]

            for i in range(8):
                t = np.sin(i / 8 * 2 * np.pi)
                scale = 1.0 + (t * 0.015)

                new_w = int(w * scale)
                new_h = int(h * scale)

                resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

                canvas = np.zeros((h, w, img.shape[2] if len(img.shape) == 3 else 1), dtype=img.dtype)

                x_offset = (w - new_w) // 2
                y_offset = (h - new_h) // 2

                if new_w <= w and new_h <= h:
                    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
                else:
                    crop_x = (new_w - w) // 2
                    crop_y = (new_h - h) // 2
                    canvas = resized[crop_y:crop_y+h, crop_x:crop_x+w]

                frames.append(canvas)

            # Verify frames
            if len(frames) == 8:
                # Check all frames have same shape
                shapes = [f.shape for f in frames]
                if len(set(shapes)) == 1:
                    self.log(
                        "Animation Generation",
                        'PASS',
                        "All frames generated correctly",
                        {
                            'frames': len(frames),
                            'shape': str(frames[0].shape)
                        }
                    )
                else:
                    self.log(
                        "Animation Generation",
                        'FAIL',
                        "Frame shapes are inconsistent",
                        {'shapes': str(set(shapes))}
                    )
            else:
                self.log(
                    "Animation Generation",
                    'FAIL',
                    f"Wrong number of frames: {len(frames)}",
                    {'expected': 8, 'actual': len(frames)}
                )

        except Exception as e:
            self.log(
                "Animation Generation",
                'FAIL',
                f"Exception: {str(e)}",
                {'traceback': traceback.format_exc()}
            )

    def test_performance(self):
        """Test performance benchmarks."""
        print("\n" + "=" * 60)
        print("TEST SUITE 5: Performance Benchmarks")
        print("=" * 60)

        test_image = 'temp_normie_rgb_1024.png'

        if not os.path.exists(test_image):
            self.log(
                "Performance Benchmark",
                'WARN',
                f"Test image not found: {test_image}"
            )
            return

        # Benchmark 1: Image loading
        try:
            start = time.time()
            for _ in range(10):
                img = cv2.imread(test_image, cv2.IMREAD_UNCHANGED)
            end = time.time()

            avg_time = (end - start) / 10 * 1000  # milliseconds

            if avg_time < 100:  # Should be under 100ms
                self.log(
                    "Image Loading Speed",
                    'PASS',
                    f"Fast loading performance",
                    {'avg_time_ms': f"{avg_time:.2f}", 'runs': 10}
                )
            else:
                self.log(
                    "Image Loading Speed",
                    'WARN',
                    f"Slow loading performance",
                    {'avg_time_ms': f"{avg_time:.2f}", 'threshold': '100ms'}
                )

        except Exception as e:
            self.log(
                "Image Loading Speed",
                'FAIL',
                f"Exception: {str(e)}"
            )

        # Benchmark 2: Pixel analysis
        try:
            img = cv2.imread(test_image, cv2.IMREAD_UNCHANGED)

            if len(img.shape) == 3 and img.shape[2] == 3:
                alpha = np.ones((img.shape[0], img.shape[1]), dtype=np.uint8) * 255
                img = np.dstack([img, alpha])

            rgb = img[:, :, :3]
            alpha = img[:, :, 3]

            visible_mask = alpha > 10
            visible_pixels = rgb[visible_mask].reshape(-1, 3).astype(float)

            start = time.time()
            kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
            labels = kmeans.fit_predict(visible_pixels)
            end = time.time()

            elapsed_ms = (end - start) * 1000

            if elapsed_ms < 5000:  # Should be under 5 seconds
                self.log(
                    "K-Means Clustering Speed",
                    'PASS',
                    f"Fast clustering performance",
                    {
                        'time_ms': f"{elapsed_ms:.2f}",
                        'pixels': len(visible_pixels),
                        'threshold': '5000ms'
                    }
                )
            else:
                self.log(
                    "K-Means Clustering Speed",
                    'WARN',
                    f"Slow clustering performance",
                    {'time_ms': f"{elapsed_ms:.2f}", 'threshold': '5000ms'}
                )

        except Exception as e:
            self.log(
                "K-Means Clustering Speed",
                'FAIL',
                f"Exception: {str(e)}"
            )

        # Benchmark 3: Animation generation
        try:
            img = cv2.imread(test_image, cv2.IMREAD_UNCHANGED)

            start = time.time()

            frames = []
            h, w = img.shape[:2]

            for i in range(8):
                t = np.sin(i / 8 * 2 * np.pi)
                scale = 1.0 + (t * 0.015)

                new_w = int(w * scale)
                new_h = int(h * scale)

                resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

                canvas = np.zeros((h, w, img.shape[2] if len(img.shape) == 3 else 1), dtype=img.dtype)

                x_offset = (w - new_w) // 2
                y_offset = (h - new_h) // 2

                if new_w <= w and new_h <= h:
                    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
                else:
                    crop_x = (new_w - w) // 2
                    crop_y = (new_h - h) // 2
                    canvas = resized[crop_y:crop_y+h, crop_x:crop_x+w]

                frames.append(canvas)

            end = time.time()

            elapsed_ms = (end - start) * 1000

            if elapsed_ms < 3000:  # Should be under 3 seconds
                self.log(
                    "Animation Generation Speed",
                    'PASS',
                    f"Fast animation generation",
                    {
                        'time_ms': f"{elapsed_ms:.2f}",
                        'frames': len(frames),
                        'ms_per_frame': f"{elapsed_ms/len(frames):.2f}"
                    }
                )
            else:
                self.log(
                    "Animation Generation Speed",
                    'WARN',
                    f"Slow animation generation",
                    {'time_ms': f"{elapsed_ms:.2f}", 'threshold': '3000ms'}
                )

        except Exception as e:
            self.log(
                "Animation Generation Speed",
                'FAIL',
                f"Exception: {str(e)}"
            )

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("BULLETPROOF TEST SUMMARY")
        print("=" * 60)

        total = self.passed + self.failed + self.warnings

        print(f"\n📊 Results:")
        print(f"  Total tests: {total}")
        print(f"  ✅ Passed: {self.passed} ({self.passed/total*100:.1f}%)")
        print(f"  ❌ Failed: {self.failed} ({self.failed/total*100:.1f}%)")
        print(f"  ⚠️  Warnings: {self.warnings} ({self.warnings/total*100:.1f}%)")

        # Overall verdict
        print(f"\n🎯 Overall Verdict:")

        if self.failed == 0 and self.warnings == 0:
            print("  ✅ BULLETPROOF - System is production-ready!")
        elif self.failed == 0 and self.warnings <= 2:
            print("  ✅ ROBUST - System works with minor warnings")
        elif self.failed <= 2:
            print("  ⚠️  NEEDS FIXES - Some tests failed, requires attention")
        else:
            print("  ❌ NOT READY - Multiple failures, significant work needed")

        # Recommendations
        if self.failed > 0 or self.warnings > 0:
            print(f"\n📋 Issues Found:")
            for result in self.results:
                if result['status'] in ['FAIL', 'WARN']:
                    print(f"  {result['status']}: {result['test']} - {result['message']}")

def main():
    """Run all bulletproof tests."""

    print("\n" + "=" * 60)
    print("🔬 BULLETPROOF TESTING SUITE")
    print("=" * 60)
    print("\nValidating pixel-perfect animation system...")
    print("Testing edge cases, consistency, error handling, and performance")

    tester = BulletproofTester()

    # Run all test suites
    tester.test_image_loading()
    tester.test_pixel_analysis_consistency()
    tester.test_edge_cases()
    tester.test_animation_generation()
    tester.test_performance()

    # Print summary
    tester.print_summary()

    # Exit code
    sys.exit(0 if tester.failed == 0 else 1)

if __name__ == '__main__':
    main()
