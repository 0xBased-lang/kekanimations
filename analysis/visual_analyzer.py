#!/usr/bin/env python3
"""
KEKTECH NFT Collection - Comprehensive Visual Analysis
Analyzes all 4,200 NFT images with 20+ visual metrics
"""

import sqlite3
import numpy as np
from pathlib import Path
import sys
from PIL import Image
import time

# Check for required libraries
HAS_ADVANCED = False
try:
    import cv2
    from scipy import stats
    from sklearn.cluster import KMeans
    from skimage.feature import graycomatrix, graycoprops
    HAS_ADVANCED = True
except ImportError as e:
    pass  # Will print warning in main()

class VisualAnalyzer:
    """Comprehensive visual analysis of NFT images"""

    def __init__(self, db_path: str, images_dir: str):
        self.db_path = db_path
        self.images_dir = Path(images_dir)
        self.conn = sqlite3.connect(db_path)

    def analyze_basic_image(self, image_path: Path) -> dict:
        """Basic image analysis using PIL only"""
        img = Image.open(image_path)

        # Convert to numpy array
        img_array = np.array(img)

        # Basic metrics
        channels = img_array.shape[2] if len(img_array.shape) > 2 else 1

        # Color analysis
        if channels >= 3:
            # Unique colors
            reshaped = img_array.reshape(-1, channels)
            unique_colors = len(np.unique(reshaped, axis=0))

            # Color variance
            r_var = np.var(img_array[:,:,0])
            g_var = np.var(img_array[:,:,1])
            b_var = np.var(img_array[:,:,2])
            color_variance = (r_var + g_var + b_var) / 3

        else:
            unique_colors = len(np.unique(img_array))
            color_variance = np.var(img_array)

        return {
            'color_palette_size': int(unique_colors),
            'color_variance': float(color_variance)
        }

    def analyze_advanced_image(self, image_path: Path) -> dict:
        """Advanced image analysis with CV2 and sklearn"""
        if not HAS_ADVANCED:
            return {}

        # Load image with OpenCV
        img = cv2.imread(str(image_path))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Edge detection (detail density)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.mean(edges) / 255.0

        # Laplacian variance (sharpness)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Sobel gradients
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.mean(np.sqrt(sobelx**2 + sobely**2))

        # Texture analysis (GLCM)
        # Downsample for speed
        small_gray = cv2.resize(gray, (256, 256))
        glcm = graycomatrix(small_gray, [1], [0], 256, symmetric=True, normed=True)

        contrast = graycoprops(glcm, 'contrast')[0, 0]
        homogeneity = graycoprops(glcm, 'homogeneity')[0, 0]
        energy = graycoprops(glcm, 'energy')[0, 0]
        correlation = graycoprops(glcm, 'correlation')[0, 0]

        # Entropy (information density)
        hist, _ = np.histogram(gray, bins=256, range=(0, 256))
        hist = hist / hist.sum()  # Normalize
        hist = hist[hist > 0]  # Remove zeros
        entropy = -np.sum(hist * np.log2(hist))

        # Dominant colors (K-means clustering)
        pixels = img.reshape(-1, 3)
        kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        kmeans.fit(pixels)
        dominant_colors = kmeans.cluster_centers_

        # Convert dominant colors to hex
        def rgb_to_hex(r, g, b):
            return '#{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))

        return {
            'edge_density': float(edge_density),  # 0-1 range
            'avg_gradient': float(sobel_magnitude),
            'laplacian_variance': float(laplacian_var),
            'glcm_contrast': float(contrast),
            'glcm_homogeneity': float(homogeneity),
            'glcm_energy': float(energy),
            'glcm_correlation': float(correlation),
            'texture_entropy': float(entropy),
            'dominant_color_1_hex': rgb_to_hex(dominant_colors[0][2], dominant_colors[0][1], dominant_colors[0][0]),
            'dominant_color_2_hex': rgb_to_hex(dominant_colors[1][2], dominant_colors[1][1], dominant_colors[1][0]) if len(dominant_colors) > 1 else None,
            'dominant_color_3_hex': rgb_to_hex(dominant_colors[2][2], dominant_colors[2][1], dominant_colors[2][0]) if len(dominant_colors) > 2 else None,
            'dominant_color_4_hex': rgb_to_hex(dominant_colors[3][2], dominant_colors[3][1], dominant_colors[3][0]) if len(dominant_colors) > 3 else None,
            'dominant_color_5_hex': rgb_to_hex(dominant_colors[4][2], dominant_colors[4][1], dominant_colors[4][0]) if len(dominant_colors) > 4 else None
        }

    def calculate_complexity_scores(self, basic: dict, advanced: dict) -> dict:
        """Calculate composite complexity scores"""

        # Color complexity (0-100)
        color_complexity = 0
        if basic.get('color_palette_size'):
            # Normalize unique colors (512x512 image has max ~262k pixels)
            color_norm = min(basic['color_palette_size'] / 50000, 1.0) * 100
            color_complexity = color_norm

        # Detail complexity (0-100) - based on edge density
        detail_complexity = 0
        if 'edge_density' in advanced:
            # Edge density is 0-1, convert to 0-100
            detail_complexity = advanced['edge_density'] * 100

        # Texture complexity (0-100) - based on entropy
        texture_complexity = 0
        if 'texture_entropy' in advanced:
            # Entropy typically 0-8, normalize to 0-100
            texture_complexity = min(advanced['texture_entropy'] / 8 * 100, 100)

        # Overall visual complexity (weighted average)
        if HAS_ADVANCED:
            overall_complexity = (
                color_complexity * 0.3 +
                detail_complexity * 0.4 +
                texture_complexity * 0.3
            )
        else:
            # Basic analysis only
            overall_complexity = color_complexity

        # Animation difficulty (0-100)
        # High complexity = harder to animate
        animation_difficulty = overall_complexity

        # Recommended denoise (inverse of complexity)
        # Higher complexity → lower denoise (more preservation)
        recommended_denoise = 0.60 - (overall_complexity / 100) * 0.30  # Range: 0.30-0.60

        return {
            'color_complexity_score': round(color_complexity, 2),
            'detail_complexity_score': round(detail_complexity, 2),
            'texture_complexity_score': round(texture_complexity, 2),
            'overall_visual_complexity': round(overall_complexity, 2),
            'animation_difficulty_score': round(animation_difficulty, 2),
            'recommended_denoise': round(recommended_denoise, 2)
        }

    def analyze_nft(self, nft_id: int, image_path: Path) -> dict:
        """Complete analysis of a single NFT"""

        if not image_path.exists():
            return None

        # Basic analysis (always runs)
        basic_metrics = self.analyze_basic_image(image_path)

        # Advanced analysis (if libraries available)
        advanced_metrics = {}
        if HAS_ADVANCED:
            try:
                advanced_metrics = self.analyze_advanced_image(image_path)
            except Exception as e:
                print(f"      ⚠️  Advanced analysis failed for NFT #{nft_id}: {e}")

        # Calculate complexity scores
        complexity_scores = self.calculate_complexity_scores(basic_metrics, advanced_metrics)

        # Combine all metrics
        return {
            **basic_metrics,
            **advanced_metrics,
            **complexity_scores,
            'nft_id': nft_id
        }

    def analyze_all(self, start_id: int = 0, limit: int = None):
        """Analyze all NFTs with progress tracking"""

        print("=" * 80)
        print("KEKTECH NFT Collection - Visual Analysis")
        print("=" * 80)
        print()

        if HAS_ADVANCED:
            print("✅ Advanced analysis enabled (CV2, sklearn, skimage)")
        else:
            print("⚠️  Basic analysis only (PIL)")
        print()

        # Get all NFT IDs
        cursor = self.conn.cursor()
        cursor.execute("SELECT nft_id, image_path FROM nfts WHERE image_path IS NOT NULL ORDER BY nft_id")
        nfts = cursor.fetchall()

        if start_id > 0:
            nfts = [(nft_id, path) for nft_id, path in nfts if nft_id >= start_id]

        if limit:
            nfts = nfts[:limit]

        total = len(nfts)
        print(f"📊 Analyzing {total} NFT images...")
        print()

        start_time = time.time()
        analyzed = 0
        failed = 0

        for i, (nft_id, image_path) in enumerate(nfts, 1):
            try:
                # Analyze image
                metrics = self.analyze_nft(nft_id, Path(image_path))

                if metrics is None:
                    failed += 1
                    continue

                # Store in database
                self._store_visual_features(metrics)

                # Update NFT complexity scores
                cursor.execute("""
                    UPDATE nfts
                    SET overall_complexity_score = ?,
                        color_complexity_score = ?,
                        detail_complexity_score = ?,
                        texture_complexity_score = ?,
                        animation_difficulty_score = ?,
                        visual_analysis_completed = 1
                    WHERE nft_id = ?
                """, (
                    metrics['overall_visual_complexity'],
                    metrics['color_complexity_score'],
                    metrics['detail_complexity_score'],
                    metrics['texture_complexity_score'],
                    metrics['animation_difficulty_score'],
                    nft_id
                ))

                analyzed += 1

                # Progress updates
                if i % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = i / elapsed
                    remaining = (total - i) / rate if rate > 0 else 0

                    print(f"   Progress: {i}/{total} ({i/total*100:.1f}%) | "
                          f"Rate: {rate:.1f} NFTs/sec | "
                          f"ETA: {remaining/60:.1f} min")

                    self.conn.commit()

            except Exception as e:
                print(f"   ❌ Failed to analyze NFT #{nft_id}: {e}")
                failed += 1

        self.conn.commit()

        elapsed = time.time() - start_time

        print()
        print("=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"✅ Successfully analyzed: {analyzed} NFTs")
        print(f"❌ Failed: {failed} NFTs")
        print(f"⏱️  Total time: {elapsed/60:.1f} minutes ({elapsed/3600:.2f} hours)")
        print(f"📊 Average rate: {analyzed/elapsed:.2f} NFTs/second")
        print("=" * 80)

    def _store_visual_features(self, metrics: dict):
        """Store visual features in database"""
        cursor = self.conn.cursor()

        # Build insert query dynamically based on available metrics
        columns = ['nft_id']
        values = [metrics['nft_id']]

        for key, value in metrics.items():
            if key != 'nft_id':
                columns.append(key)
                values.append(value)

        placeholders = ','.join(['?' for _ in values])
        cols = ','.join(columns)

        cursor.execute(f"""
            INSERT OR REPLACE INTO visual_features ({cols})
            VALUES ({placeholders})
        """, values)

def main():
    """Run visual analysis"""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze NFT images')
    parser.add_argument('--start-id', type=int, default=0, help='Start from this NFT ID')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of NFTs to analyze')
    parser.add_argument('--sample', action='store_true', help='Analyze only 10 NFTs as a test')

    args = parser.parse_args()

    DB_PATH = "database/nft_master_database.db"
    IMAGES_DIR = "/Users/seman/desktop-transfer/kek/images"

    analyzer = VisualAnalyzer(DB_PATH, IMAGES_DIR)

    if args.sample:
        print("🧪 Running sample analysis on 10 NFTs...")
        analyzer.analyze_all(limit=10)
    else:
        analyzer.analyze_all(start_id=args.start_id, limit=args.limit)

    print()
    print("✅ Visual analysis complete! Check database/nft_master_database.db")

if __name__ == '__main__':
    main()
