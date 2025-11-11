#!/usr/bin/env python3
"""
KEKTECH NFT Collection - Master Database Builder
Comprehensive analysis and database population system

This script orchestrates the complete database build process:
1. Initialize SQLite database with schema
2. Load all 4,200 NFT metadata files
3. Run visual analysis on all images
4. Calculate trait correlations
5. Create animation profiles
6. Generate comprehensive reports

Usage:
    python3 build_database.py --metadata-dir /path/to/metadata --images-dir /path/to/images
"""

import sqlite3
import json
import argparse
from pathlib import Path
from datetime import datetime
import sys

# Add analysis modules to path
sys.path.append(str(Path(__file__).parent))


class NFTDatabaseBuilder:
    """Master orchestrator for building comprehensive NFT analysis database."""

    def __init__(self, db_path='database/nft_master_database.db'):
        """
        Initialize database builder.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.conn = None
        self.stats = {
            'nfts_loaded': 0,
            'traits_loaded': 0,
            'visual_analysis_completed': 0,
            'profiles_created': 0,
            'assignments_made': 0,
            'start_time': datetime.now()
        }

    def connect(self):
        """Connect to database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        print(f"✅ Connected to database: {self.db_path}")

    def initialize_schema(self):
        """Create database schema."""
        print("\n📊 Initializing database schema...")

        schema_path = Path('database/schema.sql')
        if not schema_path.exists():
            print(f"❌ Schema file not found: {schema_path}")
            return False

        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        # Execute schema
        self.conn.executescript(schema_sql)
        self.conn.commit()

        # Verify tables created
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]

        print(f"✅ Created {len(tables)} tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count} records")

        return True

    def load_metadata(self, metadata_dir, images_dir, rarity_report_path):
        """
        Load all NFT metadata and populate nfts + traits tables.

        Args:
            metadata_dir: Directory containing NFT metadata JSON files
            images_dir: Directory containing NFT images
            rarity_report_path: Path to rarity analysis JSON
        """
        print("\n📁 Loading NFT metadata...")

        metadata_dir = Path(metadata_dir)
        images_dir = Path(images_dir)

        # Load rarity report
        print(f"Loading rarity report: {rarity_report_path}")
        with open(rarity_report_path, 'r') as f:
            rarity_data = json.load(f)

        trait_stats = rarity_data.get('trait_statistics', {})

        # Find all metadata files
        metadata_files = sorted(metadata_dir.glob('*.json'))
        total_files = len(metadata_files)

        print(f"Found {total_files} metadata files")

        cursor = self.conn.cursor()
        nfts_loaded = 0
        traits_loaded = 0

        for i, metadata_file in enumerate(metadata_files):
            nft_id = int(metadata_file.stem)

            try:
                # Load metadata
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)

                # Find corresponding image
                image_path = images_dir / f"{nft_id}.png"
                if not image_path.exists():
                    print(f"⚠️  Image not found for NFT {nft_id}: {image_path}")
                    continue

                # Extract traits
                traits = {}
                for attr in metadata.get('attributes', []):
                    trait_type = attr['trait_type']
                    trait_value = attr['value']
                    traits[trait_type] = trait_value

                # Calculate trait combination ID (hash of all traits)
                trait_combo = '_'.join([f"{k}:{v}" for k, v in sorted(traits.items())])

                # Get rarity score (from simple rankings if available)
                # For now, use 0 as placeholder - will be updated from rankings
                rarity_score = 0.0

                # Insert NFT
                cursor.execute('''
                    INSERT OR IGNORE INTO nfts (
                        nft_id, name, description, image_path, metadata_path,
                        rarity_score, unique_trait_combination_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    nft_id,
                    metadata.get('name', f'KEKTECH#{nft_id}'),
                    metadata.get('description', ''),
                    str(image_path),
                    str(metadata_file),
                    rarity_score,
                    trait_combo
                ))

                nfts_loaded += 1

                # Insert traits
                for trait_type, trait_value in traits.items():
                    # Get trait rarity info from rarity report
                    trait_info = trait_stats.get(trait_type, {}).get(trait_value, {})

                    trait_rarity = trait_info.get('rarity', 'common')
                    trait_rarity_score = trait_info.get('rarity_score', 0)
                    trait_count = trait_info.get('count', 0)
                    trait_frequency = trait_info.get('percentage', 0) / 100

                    cursor.execute('''
                        INSERT OR IGNORE INTO traits (
                            nft_id, trait_type, trait_value,
                            trait_rarity, trait_rarity_score,
                            trait_frequency, trait_count
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        nft_id, trait_type, trait_value,
                        trait_rarity, trait_rarity_score,
                        trait_frequency, trait_count
                    ))

                    traits_loaded += 1

                # Commit every 100 NFTs
                if (i + 1) % 100 == 0:
                    self.conn.commit()
                    print(f"   Progress: {i+1}/{total_files} NFTs ({(i+1)/total_files*100:.1f}%)")

            except Exception as e:
                print(f"❌ Error loading NFT {nft_id}: {e}")
                continue

        self.conn.commit()

        self.stats['nfts_loaded'] = nfts_loaded
        self.stats['traits_loaded'] = traits_loaded

        print(f"\n✅ Metadata loading complete:")
        print(f"   NFTs loaded: {nfts_loaded}")
        print(f"   Traits loaded: {traits_loaded}")

        # Update trait counts per NFT
        self._update_trait_counts()

        return nfts_loaded > 0

    def _update_trait_counts(self):
        """Update trait rarity counts per NFT."""
        print("\n📊 Updating trait rarity counts...")

        cursor = self.conn.cursor()

        # Update counts for each rarity tier
        for rarity in ['legendary', 'epic', 'rare', 'common']:
            cursor.execute(f'''
                UPDATE nfts
                SET {rarity}_trait_count = (
                    SELECT COUNT(*)
                    FROM traits
                    WHERE traits.nft_id = nfts.nft_id
                    AND traits.trait_rarity = ?
                )
            ''', (rarity,))

        self.conn.commit()
        print("✅ Trait counts updated")

    def load_rarity_scores(self, rankings_path):
        """
        Load rarity scores from rankings JSON.

        Args:
            rankings_path: Path to simple_rankings.json
        """
        print(f"\n📊 Loading rarity scores from: {rankings_path}")

        with open(rankings_path, 'r') as f:
            rankings = json.load(f)

        cursor = self.conn.cursor()
        scores_loaded = 0

        for nft_data in rankings:
            nft_id = int(nft_data['id'])
            score = float(nft_data['score'])
            rank = int(nft_data['rank'])

            # Determine rarity tier based on score
            if score >= 80:
                tier = 'ultra_legendary'
            elif score >= 60:
                tier = 'legendary'
            elif score >= 40:
                tier = 'epic'
            elif score >= 25:
                tier = 'rare'
            elif score >= 15:
                tier = 'uncommon'
            else:
                tier = 'common'

            cursor.execute('''
                UPDATE nfts
                SET rarity_score = ?, rarity_tier = ?, rarity_rank = ?
                WHERE nft_id = ?
            ''', (score, tier, rank, nft_id))

            scores_loaded += 1

        self.conn.commit()

        print(f"✅ Updated rarity scores for {scores_loaded} NFTs")

        # Print tier distribution
        cursor.execute('''
            SELECT rarity_tier, COUNT(*) as count
            FROM nfts
            WHERE rarity_tier IS NOT NULL
            GROUP BY rarity_tier
            ORDER BY
                CASE rarity_tier
                    WHEN 'ultra_legendary' THEN 1
                    WHEN 'legendary' THEN 2
                    WHEN 'epic' THEN 3
                    WHEN 'rare' THEN 4
                    WHEN 'uncommon' THEN 5
                    WHEN 'common' THEN 6
                END
        ''')

        print("\n📊 Rarity Tier Distribution:")
        for row in cursor.fetchall():
            tier, count = row
            percentage = (count / scores_loaded) * 100
            print(f"   {tier:20s}: {count:4d} ({percentage:5.2f}%)")

    def create_initial_profiles(self):
        """Create initial animation profiles."""
        print("\n🎨 Creating animation profiles...")

        cursor = self.conn.cursor()

        profiles = [
            {
                'name': 'legendary_ultra_complex',
                'desc': 'Ultra-legendary NFTs with extreme visual complexity',
                'rarity_tier': 'ultra_legendary',
                'min_complexity': 70,
                'max_complexity': 100,
                'min_rarity': 80,
                'max_rarity': 100,
                'denoise': 0.30,
                'steps': 25,
                'motion': 0.8,
                'manual_review': 1,
                'priority': 10,
                'est_time': 10.0,
                'est_success': 0.92
            },
            {
                'name': 'legendary_complex',
                'desc': 'Legendary NFTs with high complexity',
                'rarity_tier': 'legendary',
                'min_complexity': 60,
                'max_complexity': 100,
                'min_rarity': 60,
                'max_rarity': 100,
                'denoise': 0.35,
                'steps': 25,
                'motion': 0.9,
                'manual_review': 0,
                'priority': 9,
                'est_time': 7.0,
                'est_success': 0.94
            },
            {
                'name': 'legendary_standard',
                'desc': 'Legendary NFTs with moderate complexity',
                'rarity_tier': 'legendary',
                'min_complexity': 0,
                'max_complexity': 60,
                'min_rarity': 60,
                'max_rarity': 100,
                'denoise': 0.40,
                'steps': 20,
                'motion': 1.0,
                'manual_review': 0,
                'priority': 8,
                'est_time': 5.0,
                'est_success': 0.96
            },
            {
                'name': 'epic_complex',
                'desc': 'Epic rarity with high visual complexity',
                'rarity_tier': 'epic',
                'min_complexity': 60,
                'max_complexity': 100,
                'min_rarity': 40,
                'max_rarity': 60,
                'denoise': 0.40,
                'steps': 20,
                'motion': 1.0,
                'manual_review': 0,
                'priority': 7,
                'est_time': 5.0,
                'est_success': 0.94
            },
            {
                'name': 'rare_standard',
                'desc': 'Rare tier standard processing',
                'rarity_tier': 'rare',
                'min_complexity': 0,
                'max_complexity': 100,
                'min_rarity': 25,
                'max_rarity': 60,
                'denoise': 0.45,
                'steps': 15,
                'motion': 1.0,
                'manual_review': 0,
                'priority': 6,
                'est_time': 4.0,
                'est_success': 0.95
            },
            {
                'name': 'uncommon_standard',
                'desc': 'Uncommon tier standard processing',
                'rarity_tier': 'uncommon',
                'min_complexity': 0,
                'max_complexity': 100,
                'min_rarity': 15,
                'max_rarity': 25,
                'denoise': 0.48,
                'steps': 12,
                'motion': 1.1,
                'manual_review': 0,
                'priority': 5,
                'est_time': 3.5,
                'est_success': 0.95
            },
            {
                'name': 'common_fast',
                'desc': 'Common tier optimized for speed',
                'rarity_tier': 'common',
                'min_complexity': 0,
                'max_complexity': 100,
                'min_rarity': 0,
                'max_rarity': 15,
                'denoise': 0.50,
                'steps': 12,
                'motion': 1.2,
                'manual_review': 0,
                'priority': 4,
                'est_time': 3.0,
                'est_success': 0.94
            }
        ]

        for profile in profiles:
            cursor.execute('''
                INSERT OR REPLACE INTO animation_profiles (
                    profile_name, description,
                    rarity_tier, min_complexity_score, max_complexity_score,
                    min_rarity_score, max_rarity_score,
                    base_denoise, base_steps, base_motion_scale,
                    requires_manual_review, processing_priority,
                    estimated_processing_time_min, estimated_success_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                profile['name'], profile['desc'],
                profile['rarity_tier'], profile['min_complexity'], profile['max_complexity'],
                profile['min_rarity'], profile['max_rarity'],
                profile['denoise'], profile['steps'], profile['motion'],
                profile['manual_review'], profile['priority'],
                profile['est_time'], profile['est_success']
            ))

        self.conn.commit()

        self.stats['profiles_created'] = len(profiles)

        print(f"✅ Created {len(profiles)} animation profiles")

    def print_summary(self):
        """Print final summary statistics."""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()

        print("\n" + "=" * 70)
        print("DATABASE BUILD COMPLETE")
        print("=" * 70)
        print(f"NFTs loaded:           {self.stats['nfts_loaded']:,}")
        print(f"Traits loaded:         {self.stats['traits_loaded']:,}")
        print(f"Visual analysis:       {self.stats['visual_analysis_completed']:,}")
        print(f"Profiles created:      {self.stats['profiles_created']:,}")
        print(f"Profile assignments:   {self.stats['assignments_made']:,}")
        print(f"Total time:            {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"Database location:     {self.db_path.absolute()}")
        print(f"Database size:         {self.db_path.stat().st_size / 1024 / 1024:.1f} MB")
        print("=" * 70)

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            print("\n✅ Database connection closed")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Build comprehensive NFT analysis database'
    )

    parser.add_argument(
        '--metadata-dir',
        type=str,
        required=True,
        help='Directory containing NFT metadata JSON files'
    )

    parser.add_argument(
        '--images-dir',
        type=str,
        required=True,
        help='Directory containing NFT images'
    )

    parser.add_argument(
        '--rarity-report',
        type=str,
        required=True,
        help='Path to rarity report JSON file'
    )

    parser.add_argument(
        '--rankings',
        type=str,
        required=True,
        help='Path to simple_rankings.json file'
    )

    parser.add_argument(
        '--db-path',
        type=str,
        default='database/nft_master_database.db',
        help='Path to SQLite database file'
    )

    parser.add_argument(
        '--skip-visual',
        action='store_true',
        help='Skip visual analysis (faster, for testing)'
    )

    args = parser.parse_args()

    # Initialize builder
    builder = NFTDatabaseBuilder(db_path=args.db_path)

    try:
        # Phase 1: Connect and initialize
        builder.connect()
        if not builder.initialize_schema():
            return 1

        # Phase 2: Load metadata
        if not builder.load_metadata(
            args.metadata_dir,
            args.images_dir,
            args.rarity_report
        ):
            return 1

        # Phase 2.5: Load rarity scores
        builder.load_rarity_scores(args.rankings)

        # Phase 3: Create profiles
        builder.create_initial_profiles()

        # Phase 4: Visual analysis (if not skipped)
        if not args.skip_visual:
            print("\n🔬 Visual analysis will be run separately")
            print("   Run: python3 analysis/visual_analyzer.py")

        # Print summary
        builder.print_summary()

        return 0

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 130

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        builder.close()


if __name__ == '__main__':
    exit(main())
