#!/usr/bin/env python3
"""
Simplified KEKTECH NFT Database Builder
Works with actual file structure we have available
"""

import sqlite3
import json
from pathlib import Path
import sys

def build_database():
    """Build the NFT database from available data"""

    # File paths
    DB_PATH = "database/nft_master_database.db"
    METADATA_DIR = "/Users/seman/desktop-transfer/randomizer/output2"
    IMAGES_DIR = "/Users/seman/desktop-transfer/kek/images"
    RANKINGS_FILE = "/Users/seman/desktop-transfer/neu/rankings.json"

    print("=" * 80)
    print("KEKTECH NFT Collection - Simplified Database Builder")
    print("=" * 80)
    print()

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("✅ Connected to database")
    print()

    # Load schema
    print("📊 Loading database schema...")
    with open("database/schema.sql", 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
    conn.commit()
    print("   ✅ Schema loaded")
    print()

    # Load rankings
    print("📈 Loading rarity rankings...")
    with open(RANKINGS_FILE, 'r') as f:
        rankings_data = json.load(f)

    rankings_by_id = rankings_data['rankings_by_id']
    print(f"   ✅ Loaded {len(rankings_by_id)} rankings")
    print()

    # Load all metadata
    print("📦 Loading NFT metadata...")
    metadata_files = sorted(Path(METADATA_DIR).glob("*.json"))
    print(f"   Found {len(metadata_files)} metadata files")

    loaded_count = 0
    trait_count = 0

    for json_file in metadata_files:
        # Get NFT ID from filename
        nft_id = int(json_file.stem)

        # Load metadata
        with open(json_file, 'r') as f:
            metadata = json.load(f)

        # Get ranking info
        ranking_info = rankings_by_id.get(str(nft_id), {})
        rarity_score = ranking_info.get('rarity_score', 0)
        rank = ranking_info.get('rank', 9999)

        # Determine rarity tier
        if rarity_score >= 80:
            rarity_tier = 'ultra_legendary'
        elif rarity_score >= 60:
            rarity_tier = 'legendary'
        elif rarity_score >= 40:
            rarity_tier = 'epic'
        elif rarity_score >= 25:
            rarity_tier = 'rare'
        elif rarity_score >= 15:
            rarity_tier = 'uncommon'
        else:
            rarity_tier = 'common'

        # Check if image exists
        image_path = Path(IMAGES_DIR) / f"{nft_id}.png"
        has_image = 1 if image_path.exists() else 0

        # Insert NFT record
        cursor.execute("""
            INSERT OR REPLACE INTO nfts (
                nft_id, name, description, rarity_score, rarity_tier, rarity_rank,
                image_path, metadata_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nft_id,
            metadata['name'],
            metadata['description'],
            rarity_score,
            rarity_tier,
            rank,
            str(image_path) if has_image else None,
            str(json_file)
        ))

        # Insert traits
        for attr in metadata.get('attributes', []):
            trait_type = attr['trait_type']
            trait_value = attr['value']

            # Determine trait rarity tier (simplified - will be updated with full analysis)
            trait_rarity = 'common'  # Placeholder
            trait_rarity_score = 0  # Placeholder

            cursor.execute("""
                INSERT INTO traits (
                    nft_id, trait_type, trait_value, trait_rarity, trait_rarity_score
                ) VALUES (?, ?, ?, ?, ?)
            """, (nft_id, trait_type, trait_value, trait_rarity, trait_rarity_score))

            trait_count += 1

        loaded_count += 1

        if loaded_count % 500 == 0:
            print(f"   Progress: {loaded_count}/{len(metadata_files)} NFTs loaded...")
            conn.commit()

    conn.commit()

    print(f"   ✅ Loaded {loaded_count} NFTs")
    print(f"   ✅ Loaded {trait_count} trait records")
    print()

    # Calculate trait statistics
    print("📊 Calculating trait statistics...")

    # Get unique trait types
    cursor.execute("SELECT DISTINCT trait_type FROM traits")
    trait_types = [row[0] for row in cursor.fetchall()]

    for trait_type in trait_types:
        # Get all values for this trait
        cursor.execute("""
            SELECT trait_value, COUNT(*) as count
            FROM traits
            WHERE trait_type = ?
            GROUP BY trait_value
        """, (trait_type,))

        trait_values = cursor.fetchall()

        for trait_value, count in trait_values:
            percentage = (count / loaded_count) * 100

            # Determine rarity tier
            if percentage < 1:
                rarity_tier = 'legendary'
                rarity_score = 100 / percentage if percentage > 0 else 100
            elif percentage < 5:
                rarity_tier = 'epic'
                rarity_score = 50 / percentage if percentage > 0 else 50
            elif percentage < 15:
                rarity_tier = 'rare'
                rarity_score = 20 / percentage if percentage > 0 else 20
            elif percentage < 30:
                rarity_tier = 'uncommon'
                rarity_score = 10 / percentage if percentage > 0 else 10
            else:
                rarity_tier = 'common'
                rarity_score = 5 / percentage if percentage > 0 else 5

            # Update traits with calculated rarity
            cursor.execute("""
                UPDATE traits
                SET trait_rarity = ?, trait_rarity_score = ?
                WHERE trait_type = ? AND trait_value = ?
            """, (rarity_tier, round(rarity_score, 2), trait_type, trait_value))

    conn.commit()
    print("   ✅ Trait statistics calculated")
    print()

    # Database summary
    print("=" * 80)
    print("DATABASE SUMMARY")
    print("=" * 80)

    cursor.execute("SELECT COUNT(*) FROM nfts")
    nft_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM nfts WHERE image_path IS NOT NULL")
    with_images = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM traits")
    total_traits = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT trait_type) FROM traits")
    trait_types_count = cursor.fetchone()[0]

    print(f"✅ Total NFTs: {nft_count}")
    print(f"✅ NFTs with images: {with_images}")
    print(f"✅ Total trait records: {total_traits}")
    print(f"✅ Trait categories: {trait_types_count}")
    print()

    # Rarity distribution
    print("Rarity Distribution:")
    cursor.execute("""
        SELECT rarity_tier, COUNT(*) as count
        FROM nfts
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
    """)

    for tier, count in cursor.fetchall():
        percentage = (count / nft_count * 100) if nft_count > 0 else 0
        print(f"  {tier:15} {count:4} ({percentage:5.2f}%)")

    print()
    print("=" * 80)
    print("✅ Database build complete!")
    print("=" * 80)

    conn.close()

if __name__ == '__main__':
    try:
        build_database()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
