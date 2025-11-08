# KEKTECH NFT Collection - Trait Correlation Analysis

## Overview

- **Total NFTs Analyzed**: 4,200
- **Trait Categories**: 11
- **Unique Combinations**: 4200 (100.0%)
- **Shared Combinations**: 0
- **Significant Correlations Found**: 11

---

## Strong Trait Correlations

Trait pairs that co-occur significantly more (or less) often than random chance:

| Trait 1 | Value 1 | Trait 2 | Value 2 | Observed | Expected | Lift | Significance |
|---------|---------|---------|---------|----------|----------|------|--------------|
| Glasses | pixel | Style | pierced | 172 | 82.23 | 2.09× | strong |
| Glasses | pixel | Style | goth | 165 | 80.14 | 2.06× | strong |
| Glasses | AIagent | Style | demonic | 51 | 19.88 | 2.56× | strong |
| Glasses | pixel | Tattoo | 420 | 109 | 51.08 | 2.13× | strong |

**Interpretation**:
- **Lift > 1**: Traits co-occur MORE often than random
- **Lift < 1**: Traits co-occur LESS often than random
- **Lift ~1**: No correlation (random distribution)

---

## Rarity Drivers

Trait values that contribute most to high rarity scores:

| Rank | Trait Type | Trait Value | Avg NFT Rarity | Count | Contribution |
|------|------------|-------------|----------------|-------|--------------|
| 1 | Body | rare_diablo | 87.8 | 9 | 531.5% |
| 2 | Easter Eggs | free tattoo lifetime pass | 87.8 | 9 | 531.5% |
| 3 | Glasses | patched | 71.69 | 21 | 279.0% |
| 4 | Clothes | kekius | 43.86 | 30 | 319.2% |
| 5 | Hat | maximus | 35.92 | 22 | 531.5% |
| 6 | Glasses | rare_Aiagent | 26.19 | 7 | 2290.7% |
| 7 | Easter Eggs | golden ticket boost | 23.59 | 43 | 207.0% |
| 8 | Tools | golden_tickets | 23.59 | 43 | 207.0% |
| 9 | Tools | none | 22.97 | 65 | 140.7% |
| 10 | Special | rare_whitebeard | 20.6 | 59 | 172.7% |
| 11 | Eyes | diabolic | 17.44 | 79 | 152.4% |
| 12 | Hat | basedgod | 17.31 | 59 | 205.6% |
| 13 | Clothes | wizard | 17.16 | 67 | 182.6% |
| 14 | Tools | rare_flipper | 16.13 | 19 | 1370.5% |
| 15 | Tattoo | kekity_kek | 15.36 | 157 | 87.1% |
| 16 | Background | psychedelic | 14.65 | 61 | 235.0% |
| 17 | Hat | magic | 14.28 | 76 | 193.5% |
| 18 | Body | RIP | 12.55 | 56 | 298.8% |
| 19 | Glasses | rare_radioactive | 10.86 | 12 | 3222.1% |
| 20 | Tools | sorcerer | 10.08 | 143 | 145.7% |

---

## Most Common Trait Combinations

Trait combinations shared by multiple NFTs:

| Rank | NFT Count | Sample NFT IDs |
|------|-----------|----------------|

---

## Unique Trait Combinations

**4200 NFTs** have completely unique trait combinations (1-of-1 in the collection).

These NFTs may command premium value due to their uniqueness.

Sample unique NFT IDs:

`0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29`

... and 4170 more unique NFTs

---

## Database Queries

Query all significant correlations:
```sql
SELECT * FROM trait_combinations
WHERE significance = 'strong'
ORDER BY lift DESC;
```

Query trait statistics:
```sql
SELECT trait_type, trait_value, total_count, percentage, rarity_tier
FROM trait_statistics
WHERE rarity_tier IN ('legendary', 'epic')
ORDER BY percentage ASC;
```

Find unique NFTs:
```sql
SELECT nft_id, name, rarity_score
FROM nfts
WHERE unique_trait_combination = 1
ORDER BY rarity_score DESC;
```
