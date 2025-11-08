#!/usr/bin/env python3
"""
KEKTECH NFT Collection - Trait Correlation Analysis
Discovers patterns and relationships between traits across the collection
"""

import sqlite3
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from pathlib import Path
import json

class TraitCorrelationAnalyzer:
    """Analyzes trait correlations and patterns across the collection"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.trait_types = self._get_trait_types()

    def _get_trait_types(self) -> List[str]:
        """Get all trait type categories"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT trait_type FROM traits ORDER BY trait_type")
        return [row[0] for row in cursor.fetchall()]

    def calculate_correlation_matrix(self) -> pd.DataFrame:
        """
        Calculate correlation between all trait pairs
        Returns matrix showing how often traits co-occur relative to random chance
        """
        print("📊 Calculating trait correlation matrix...")

        # Build trait occurrence matrix
        trait_matrix = {}

        for trait_type in self.trait_types:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT nft_id, trait_value
                FROM traits
                WHERE trait_type = ?
            """, (trait_type,))

            trait_matrix[trait_type] = {
                row[0]: row[1] for row in cursor.fetchall()
            }

        # Calculate pairwise correlations
        correlations = []

        for i, trait_type1 in enumerate(self.trait_types):
            for trait_type2 in self.trait_types[i:]:
                if trait_type1 == trait_type2:
                    continue

                # Get all value combinations
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT t1.trait_value, t2.trait_value, COUNT(*) as count
                    FROM traits t1
                    JOIN traits t2 ON t1.nft_id = t2.nft_id
                    WHERE t1.trait_type = ? AND t2.trait_type = ?
                    GROUP BY t1.trait_value, t2.trait_value
                    ORDER BY count DESC
                """, (trait_type1, trait_type2))

                combinations = cursor.fetchall()

                # Find top correlations
                for val1, val2, count in combinations[:10]:  # Top 10 per pair
                    # Calculate expected frequency (random chance)
                    cursor.execute("""
                        SELECT COUNT(*) FROM traits
                        WHERE trait_type = ? AND trait_value = ?
                    """, (trait_type1, val1))
                    count1 = cursor.fetchone()[0]

                    cursor.execute("""
                        SELECT COUNT(*) FROM traits
                        WHERE trait_type = ? AND trait_value = ?
                    """, (trait_type2, val2))
                    count2 = cursor.fetchone()[0]

                    expected = (count1 / 4200) * (count2 / 4200) * 4200
                    lift = count / expected if expected > 0 else 0

                    if lift > 1.5 or lift < 0.5:  # Significant correlation
                        correlations.append({
                            'trait_type1': trait_type1,
                            'trait_value1': val1,
                            'trait_type2': trait_type2,
                            'trait_value2': val2,
                            'observed_count': count,
                            'expected_count': round(expected, 2),
                            'lift': round(lift, 2),
                            'significance': 'strong' if lift > 2 or lift < 0.3 else 'moderate'
                        })

        # Store in database
        print(f"   Found {len(correlations)} significant trait correlations")

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM trait_combinations")  # Clear existing

        for corr in correlations:
            cursor.execute("""
                INSERT INTO trait_combinations (
                    trait_type_1, trait_value_1, trait_type_2, trait_value_2,
                    co_occurrence_count, expected_count, correlation_strength, pattern_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                corr['trait_type1'], corr['trait_value1'],
                corr['trait_type2'], corr['trait_value2'],
                corr['observed_count'], corr['expected_count'],
                corr['lift'], corr['significance']
            ))

        self.conn.commit()
        print("   ✅ Trait correlations stored in database")

        return pd.DataFrame(correlations)

    def calculate_trait_statistics(self):
        """Calculate comprehensive statistics for each trait"""
        print("📈 Calculating trait statistics...")

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM trait_statistics")  # Clear existing

        for trait_type in self.trait_types:
            # Get all values for this trait type
            cursor.execute("""
                SELECT trait_value, COUNT(*) as count,
                       AVG(trait_rarity_score) as avg_rarity
                FROM traits
                WHERE trait_type = ?
                GROUP BY trait_value
            """, (trait_type,))

            trait_values = cursor.fetchall()

            for trait_value, count, avg_rarity in trait_values:
                percentage = (count / 4200) * 100

                # Classify rarity tier based on percentage
                if percentage < 1:
                    rarity_tier = 'legendary'
                elif percentage < 5:
                    rarity_tier = 'epic'
                elif percentage < 15:
                    rarity_tier = 'rare'
                elif percentage < 30:
                    rarity_tier = 'uncommon'
                else:
                    rarity_tier = 'common'

                # Calculate visual complexity correlation (skip if visual analysis not done)
                cursor.execute("""
                    SELECT COUNT(*) FROM visual_features LIMIT 1
                """)
                has_visual_data = cursor.fetchone()[0] > 0

                if has_visual_data:
                    cursor.execute("""
                        SELECT AVG(v.overall_visual_complexity)
                        FROM traits t
                        JOIN visual_features v ON t.nft_id = v.nft_id
                        WHERE t.trait_type = ? AND t.trait_value = ?
                    """, (trait_type, trait_value))
                    avg_complexity = cursor.fetchone()[0] or 0
                else:
                    avg_complexity = 0

                # Calculate rarity score correlation
                cursor.execute("""
                    SELECT AVG(n.rarity_score)
                    FROM traits t
                    JOIN nfts n ON t.nft_id = n.nft_id
                    WHERE t.trait_type = ? AND t.trait_value = ?
                """, (trait_type, trait_value))

                avg_nft_rarity = cursor.fetchone()[0] or 0

                # Insert statistics
                cursor.execute("""
                    INSERT INTO trait_statistics (
                        trait_type, trait_value, total_count, percentage,
                        rarity_tier, avg_rarity_score, avg_visual_complexity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    trait_type, trait_value, count, round(percentage, 2),
                    rarity_tier, round(avg_nft_rarity, 2),
                    round(avg_complexity, 2)
                ))

        self.conn.commit()
        print("   ✅ Trait statistics calculated and stored")

    def find_unique_combinations(self) -> List[Dict]:
        """Find NFTs with completely unique trait combinations"""
        print("🔍 Finding unique trait combinations...")

        cursor = self.conn.cursor()

        # Build combination signatures for each NFT
        cursor.execute("""
            SELECT nft_id,
                   GROUP_CONCAT(trait_value, '|') as combo_signature
            FROM (
                SELECT nft_id, trait_value
                FROM traits
                ORDER BY trait_type, trait_value
            )
            GROUP BY nft_id
        """)

        combo_counts = {}
        for nft_id, combo in cursor.fetchall():
            if combo not in combo_counts:
                combo_counts[combo] = []
            combo_counts[combo].append(nft_id)

        # Find unique combinations
        unique_combos = [
            {'nft_id': nft_ids[0], 'is_unique': True}
            for combo, nft_ids in combo_counts.items()
            if len(nft_ids) == 1
        ]

        # Find common combinations
        common_combos = [
            {
                'combo_signature': combo,
                'nft_count': len(nft_ids),
                'nft_ids': nft_ids
            }
            for combo, nft_ids in combo_counts.items()
            if len(nft_ids) > 1
        ]

        print(f"   Found {len(unique_combos)} NFTs with unique trait combinations ({len(unique_combos)/4200*100:.1f}%)")
        print(f"   Found {len(common_combos)} shared trait combinations")

        return {
            'unique_count': len(unique_combos),
            'shared_count': len(common_combos),
            'unique_nfts': unique_combos,
            'common_combos': common_combos[:20]  # Top 20 most common
        }

    def analyze_rarity_drivers(self) -> Dict:
        """Identify which traits contribute most to high rarity scores"""
        print("💎 Analyzing rarity drivers...")

        cursor = self.conn.cursor()

        drivers = []

        for trait_type in self.trait_types:
            cursor.execute("""
                SELECT t.trait_value,
                       AVG(n.rarity_score) as avg_rarity,
                       COUNT(*) as nft_count,
                       AVG(t.trait_rarity_score) as avg_trait_rarity
                FROM traits t
                JOIN nfts n ON t.nft_id = n.nft_id
                WHERE t.trait_type = ?
                GROUP BY t.trait_value
                HAVING nft_count >= 5
                ORDER BY avg_rarity DESC
                LIMIT 5
            """, (trait_type,))

            for trait_value, avg_rarity, count, avg_trait_rarity in cursor.fetchall():
                drivers.append({
                    'trait_type': trait_type,
                    'trait_value': trait_value,
                    'avg_nft_rarity': round(avg_rarity, 2),
                    'avg_trait_rarity': round(avg_trait_rarity or 0, 2),
                    'nft_count': count,
                    'rarity_contribution': round((avg_trait_rarity or 0) / avg_rarity * 100, 1) if avg_rarity > 0 else 0
                })

        # Sort by contribution
        drivers.sort(key=lambda x: x['avg_nft_rarity'], reverse=True)

        print(f"   Identified {len(drivers)} high-impact trait values")

        return {
            'top_drivers': drivers[:30],
            'total_analyzed': len(drivers)
        }

    def generate_correlation_report(self, output_path: str):
        """Generate comprehensive correlation analysis report"""
        print(f"📄 Generating correlation report: {output_path}")

        # Run all analyses
        correlations_df = self.calculate_correlation_matrix()
        unique_combos = self.find_unique_combinations()
        rarity_drivers = self.analyze_rarity_drivers()

        # Build markdown report
        report_lines = [
            "# KEKTECH NFT Collection - Trait Correlation Analysis",
            "",
            "## Overview",
            "",
            f"- **Total NFTs Analyzed**: 4,200",
            f"- **Trait Categories**: {len(self.trait_types)}",
            f"- **Unique Combinations**: {unique_combos['unique_count']} ({unique_combos['unique_count']/4200*100:.1f}%)",
            f"- **Shared Combinations**: {unique_combos['shared_count']}",
            f"- **Significant Correlations Found**: {len(correlations_df)}",
            "",
            "---",
            "",
            "## Strong Trait Correlations",
            "",
            "Trait pairs that co-occur significantly more (or less) often than random chance:",
            "",
            "| Trait 1 | Value 1 | Trait 2 | Value 2 | Observed | Expected | Lift | Significance |",
            "|---------|---------|---------|---------|----------|----------|------|--------------|"
        ]

        # Top correlations
        strong_corr = correlations_df[correlations_df['significance'] == 'strong'].head(30)
        for _, row in strong_corr.iterrows():
            report_lines.append(
                f"| {row['trait_type1']} | {row['trait_value1']} | "
                f"{row['trait_type2']} | {row['trait_value2']} | "
                f"{row['observed_count']} | {row['expected_count']} | "
                f"{row['lift']}× | {row['significance']} |"
            )

        report_lines.extend([
            "",
            "**Interpretation**:",
            "- **Lift > 1**: Traits co-occur MORE often than random",
            "- **Lift < 1**: Traits co-occur LESS often than random",
            "- **Lift ~1**: No correlation (random distribution)",
            "",
            "---",
            "",
            "## Rarity Drivers",
            "",
            "Trait values that contribute most to high rarity scores:",
            "",
            "| Rank | Trait Type | Trait Value | Avg NFT Rarity | Count | Contribution |",
            "|------|------------|-------------|----------------|-------|--------------|"
        ])

        for i, driver in enumerate(rarity_drivers['top_drivers'][:20], 1):
            report_lines.append(
                f"| {i} | {driver['trait_type']} | {driver['trait_value']} | "
                f"{driver['avg_nft_rarity']} | {driver['nft_count']} | "
                f"{driver['rarity_contribution']}% |"
            )

        report_lines.extend([
            "",
            "---",
            "",
            "## Most Common Trait Combinations",
            "",
            "Trait combinations shared by multiple NFTs:",
            "",
            "| Rank | NFT Count | Sample NFT IDs |",
            "|------|-----------|----------------|"
        ])

        for i, combo in enumerate(unique_combos['common_combos'][:15], 1):
            sample_ids = ', '.join(str(nft_id) for nft_id in combo['nft_ids'][:5])
            if len(combo['nft_ids']) > 5:
                sample_ids += f", ... (+{len(combo['nft_ids']) - 5} more)"

            report_lines.append(
                f"| {i} | {combo['nft_count']} | {sample_ids} |"
            )

        report_lines.extend([
            "",
            "---",
            "",
            "## Unique Trait Combinations",
            "",
            f"**{unique_combos['unique_count']} NFTs** have completely unique trait combinations (1-of-1 in the collection).",
            "",
            "These NFTs may command premium value due to their uniqueness.",
            "",
            "Sample unique NFT IDs:",
            ""
        ])

        unique_sample = unique_combos['unique_nfts'][:30]
        unique_ids = ', '.join(str(item['nft_id']) for item in unique_sample)
        report_lines.append(f"`{unique_ids}`")

        if len(unique_combos['unique_nfts']) > 30:
            report_lines.append(f"\n... and {len(unique_combos['unique_nfts']) - 30} more unique NFTs")

        report_lines.extend([
            "",
            "---",
            "",
            "## Database Queries",
            "",
            "Query all significant correlations:",
            "```sql",
            "SELECT * FROM trait_combinations",
            "WHERE significance = 'strong'",
            "ORDER BY lift DESC;",
            "```",
            "",
            "Query trait statistics:",
            "```sql",
            "SELECT trait_type, trait_value, total_count, percentage, rarity_tier",
            "FROM trait_statistics",
            "WHERE rarity_tier IN ('legendary', 'epic')",
            "ORDER BY percentage ASC;",
            "```",
            "",
            "Find unique NFTs:",
            "```sql",
            "SELECT nft_id, name, rarity_score",
            "FROM nfts",
            "WHERE unique_trait_combination = 1",
            "ORDER BY rarity_score DESC;",
            "```",
            ""
        ])

        # Write report
        with open(output_path, 'w') as f:
            f.write('\n'.join(report_lines))

        print(f"   ✅ Report saved: {output_path}")

def main():
    """Run trait correlation analysis"""
    analyzer = TraitCorrelationAnalyzer('database/nft_master_database.db')

    print("=" * 80)
    print("KEKTECH NFT Collection - Trait Correlation Analysis")
    print("=" * 80)
    print()

    # Calculate statistics
    analyzer.calculate_trait_statistics()

    # Generate report
    analyzer.generate_correlation_report('reports/trait_correlation_report.md')

    print()
    print("=" * 80)
    print("✅ Trait correlation analysis complete!")
    print("=" * 80)

if __name__ == '__main__':
    main()
