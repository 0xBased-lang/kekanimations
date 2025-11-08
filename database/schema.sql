-- ============================================================================
-- KEKTECH NFT Collection Master Database Schema
-- Comprehensive analysis database for 4,200 NFTs
-- ============================================================================

-- ============================================================================
-- TABLE 1: NFTs Master Registry
-- ============================================================================
CREATE TABLE IF NOT EXISTS nfts (
    nft_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    image_path TEXT NOT NULL,
    metadata_path TEXT NOT NULL,

    -- Rarity Metrics
    rarity_score REAL NOT NULL DEFAULT 0,
    rarity_tier TEXT,  -- ultra_legendary, legendary, epic, rare, uncommon, common
    rarity_rank INTEGER,  -- 1-4200 ranking

    -- Visual Complexity (from image analysis)
    overall_complexity_score REAL,  -- 0-100
    color_complexity_score REAL,
    detail_complexity_score REAL,
    texture_complexity_score REAL,

    -- Animation Difficulty
    animation_difficulty_score REAL,  -- 0-100
    animation_difficulty_category TEXT,  -- very_hard, hard, medium, easy
    preservation_priority_score REAL,  -- How important to preserve exactly

    -- Trait Statistics
    total_traits INTEGER DEFAULT 11,
    legendary_trait_count INTEGER DEFAULT 0,
    epic_trait_count INTEGER DEFAULT 0,
    rare_trait_count INTEGER DEFAULT 0,
    common_trait_count INTEGER DEFAULT 0,

    -- Uniqueness
    unique_trait_combination_id TEXT,  -- Hash of all traits
    combination_uniqueness_score REAL,  -- How rare this exact combo is

    -- Processing Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    visual_analysis_completed BOOLEAN DEFAULT 0,
    profile_assigned BOOLEAN DEFAULT 0,

    -- Indexes for fast lookup
    UNIQUE(nft_id)
);

CREATE INDEX IF NOT EXISTS idx_nfts_rarity_score ON nfts(rarity_score DESC);
CREATE INDEX IF NOT EXISTS idx_nfts_rarity_tier ON nfts(rarity_tier);
CREATE INDEX IF NOT EXISTS idx_nfts_complexity ON nfts(overall_complexity_score);
CREATE INDEX IF NOT EXISTS idx_nfts_difficulty ON nfts(animation_difficulty_score);

-- ============================================================================
-- TABLE 2: Traits (11 categories × 4,200 NFTs = 46,200 records)
-- ============================================================================
CREATE TABLE IF NOT EXISTS traits (
    trait_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nft_id INTEGER NOT NULL,
    trait_type TEXT NOT NULL,  -- Background, Body, Tattoo, Style, etc.
    trait_value TEXT NOT NULL,

    -- Rarity Information
    trait_rarity TEXT,  -- legendary, epic, rare, common
    trait_rarity_score REAL,  -- Individual trait rarity
    trait_frequency REAL,  -- What % of collection has this trait
    trait_count INTEGER,  -- How many NFTs have this exact trait

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (nft_id) REFERENCES nfts(nft_id),
    UNIQUE(nft_id, trait_type)
);

CREATE INDEX IF NOT EXISTS idx_traits_nft_id ON traits(nft_id);
CREATE INDEX IF NOT EXISTS idx_traits_type ON traits(trait_type);
CREATE INDEX IF NOT EXISTS idx_traits_value ON traits(trait_value);
CREATE INDEX IF NOT EXISTS idx_traits_type_value ON traits(trait_type, trait_value);
CREATE INDEX IF NOT EXISTS idx_traits_rarity ON traits(trait_rarity);

-- ============================================================================
-- TABLE 3: Visual Features (20+ metrics per NFT)
-- ============================================================================
CREATE TABLE IF NOT EXISTS visual_features (
    feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nft_id INTEGER NOT NULL UNIQUE,

    -- Color Analysis
    color_palette_size INTEGER,  -- Unique colors count
    color_variance REAL,  -- Color distribution spread
    color_entropy REAL,  -- Shannon entropy of color histogram
    dominant_color_1_hex TEXT,
    dominant_color_2_hex TEXT,
    dominant_color_3_hex TEXT,
    dominant_color_4_hex TEXT,
    dominant_color_5_hex TEXT,
    color_complexity_score REAL,  -- 0-100

    -- Edge & Detail Analysis
    edge_density REAL,  -- Canny edge pixel ratio
    avg_gradient REAL,  -- Sobel gradient magnitude
    laplacian_variance REAL,  -- Focus/sharpness measure
    harris_corner_count INTEGER,  -- Distinctive feature points
    detail_complexity_score REAL,  -- 0-100

    -- Texture Analysis (GLCM)
    glcm_contrast REAL,  -- Local variation
    glcm_homogeneity REAL,  -- Uniformity
    glcm_energy REAL,  -- Orderliness
    glcm_correlation REAL,  -- Directional patterns
    texture_entropy REAL,  -- Information density
    texture_complexity_score REAL,  -- 0-100

    -- Spatial Frequency Analysis
    spatial_frequency REAL,  -- High-frequency content
    fractal_dimension REAL,  -- Pattern complexity

    -- Composite Scores
    overall_visual_complexity REAL,  -- 0-100 weighted composite
    animation_difficulty_score REAL,  -- 0-100 animation challenge
    recommended_denoise REAL,  -- Auto-calculated optimal denoise

    -- Metadata
    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (nft_id) REFERENCES nfts(nft_id)
);

CREATE INDEX IF NOT EXISTS idx_visual_nft_id ON visual_features(nft_id);
CREATE INDEX IF NOT EXISTS idx_visual_complexity ON visual_features(overall_visual_complexity);
CREATE INDEX IF NOT EXISTS idx_visual_difficulty ON visual_features(animation_difficulty_score);

-- ============================================================================
-- TABLE 4: Trait Statistics (Collection-wide analytics)
-- ============================================================================
CREATE TABLE IF NOT EXISTS trait_statistics (
    stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trait_type TEXT NOT NULL,
    trait_value TEXT NOT NULL,

    -- Distribution
    total_count INTEGER NOT NULL,
    percentage REAL NOT NULL,
    rarity_tier TEXT NOT NULL,

    -- Visual Correlation
    avg_visual_complexity REAL,  -- Average complexity for NFTs with this trait
    avg_color_complexity REAL,
    avg_detail_complexity REAL,

    -- Rarity Correlation
    avg_rarity_score REAL,  -- Average rarity of NFTs with this trait

    -- Animation Impact
    recommended_denoise_adjustment REAL,  -- +/- adjustment from base
    recommended_steps_adjustment INTEGER,
    recommended_motion_adjustment REAL,

    UNIQUE(trait_type, trait_value)
);

CREATE INDEX IF NOT EXISTS idx_trait_stats_type ON trait_statistics(trait_type);
CREATE INDEX IF NOT EXISTS idx_trait_stats_rarity ON trait_statistics(rarity_tier);

-- ============================================================================
-- TABLE 5: Trait Combinations (Pattern analysis)
-- ============================================================================
CREATE TABLE IF NOT EXISTS trait_combinations (
    combo_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Combination Definition
    trait_type_1 TEXT NOT NULL,
    trait_value_1 TEXT NOT NULL,
    trait_type_2 TEXT NOT NULL,
    trait_value_2 TEXT NOT NULL,

    -- Statistics
    co_occurrence_count INTEGER NOT NULL,  -- How many NFTs have both
    expected_count REAL,  -- Expected if independent
    correlation_strength REAL,  -- Actual/Expected ratio
    correlation_significance REAL,  -- Statistical significance

    -- Pattern Type
    pattern_type TEXT,  -- positive_correlation, negative_correlation, independent, impossible

    UNIQUE(trait_type_1, trait_value_1, trait_type_2, trait_value_2)
);

CREATE INDEX IF NOT EXISTS idx_combo_correlation ON trait_combinations(correlation_strength DESC);
CREATE INDEX IF NOT EXISTS idx_combo_pattern ON trait_combinations(pattern_type);

-- ============================================================================
-- TABLE 6: Animation Profiles (Parameter templates)
-- ============================================================================
CREATE TABLE IF NOT EXISTS animation_profiles (
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_name TEXT NOT NULL UNIQUE,
    description TEXT,

    -- Matching Criteria
    rarity_tier TEXT,  -- Which tier this applies to
    min_complexity_score REAL,
    max_complexity_score REAL,
    min_rarity_score REAL,
    max_rarity_score REAL,

    -- Base Parameters
    base_denoise REAL NOT NULL,
    base_steps INTEGER NOT NULL,
    base_motion_scale REAL DEFAULT 1.0,
    base_cfg_scale REAL DEFAULT 7.0,
    base_sampler TEXT DEFAULT 'dpmpp_2m',
    base_scheduler TEXT DEFAULT 'karras',

    -- Processing Strategy
    requires_manual_review BOOLEAN DEFAULT 0,
    processing_priority INTEGER DEFAULT 5,  -- 1-10, higher = process first
    estimated_processing_time_min REAL,
    estimated_success_rate REAL,

    -- Quality Targets
    target_character_preservation REAL DEFAULT 0.95,  -- SSIM threshold
    max_acceptable_file_size_mb REAL DEFAULT 5.0,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_profile_name ON animation_profiles(profile_name);
CREATE INDEX IF NOT EXISTS idx_profile_priority ON animation_profiles(processing_priority DESC);

-- ============================================================================
-- TABLE 7: NFT Profile Assignments (Each NFT → optimal profile)
-- ============================================================================
CREATE TABLE IF NOT EXISTS nft_profile_assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nft_id INTEGER NOT NULL UNIQUE,
    profile_id INTEGER NOT NULL,

    -- Final Calculated Parameters (after trait adjustments)
    final_denoise REAL NOT NULL,
    final_steps INTEGER NOT NULL,
    final_motion_scale REAL NOT NULL,
    final_cfg_scale REAL NOT NULL,
    final_sampler TEXT NOT NULL,
    final_scheduler TEXT NOT NULL,

    -- Confidence & Reasoning
    assignment_confidence REAL,  -- 0-100, how confident this is optimal
    reasoning TEXT,  -- Human-readable explanation
    trait_adjustments_applied TEXT,  -- JSON of adjustments

    -- Recommendations
    requires_manual_review BOOLEAN DEFAULT 0,
    processing_priority INTEGER DEFAULT 5,
    estimated_processing_time_min REAL,
    risk_factors TEXT,  -- Potential issues to watch for

    -- Metadata
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (nft_id) REFERENCES nfts(nft_id),
    FOREIGN KEY (profile_id) REFERENCES animation_profiles(profile_id)
);

CREATE INDEX IF NOT EXISTS idx_assignment_nft ON nft_profile_assignments(nft_id);
CREATE INDEX IF NOT EXISTS idx_assignment_profile ON nft_profile_assignments(profile_id);
CREATE INDEX IF NOT EXISTS idx_assignment_priority ON nft_profile_assignments(processing_priority DESC);
CREATE INDEX IF NOT EXISTS idx_assignment_manual_review ON nft_profile_assignments(requires_manual_review);

-- ============================================================================
-- TABLE 8: Collection Insights (Meta-analysis)
-- ============================================================================
CREATE TABLE IF NOT EXISTS collection_insights (
    insight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    insight_category TEXT NOT NULL,  -- rarity, complexity, traits, animation, etc.
    insight_type TEXT NOT NULL,  -- statistic, correlation, recommendation, warning

    -- Content
    insight_title TEXT NOT NULL,
    insight_description TEXT NOT NULL,
    insight_value REAL,  -- Numeric value if applicable
    insight_data TEXT,  -- JSON data for complex insights

    -- Priority
    importance_score REAL,  -- 0-100
    actionable BOOLEAN DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_insights_category ON collection_insights(insight_category);
CREATE INDEX IF NOT EXISTS idx_insights_importance ON collection_insights(importance_score DESC);
CREATE INDEX IF NOT EXISTS idx_insights_actionable ON collection_insights(actionable);

-- ============================================================================
-- VIEWS (Convenience queries)
-- ============================================================================

-- View: Legendary NFTs with full details
CREATE VIEW IF NOT EXISTS view_legendary_nfts AS
SELECT
    n.nft_id,
    n.name,
    n.rarity_score,
    n.rarity_tier,
    n.overall_complexity_score,
    n.animation_difficulty_score,
    a.final_denoise,
    a.final_steps,
    a.requires_manual_review,
    a.reasoning
FROM nfts n
LEFT JOIN nft_profile_assignments a ON n.nft_id = a.nft_id
WHERE n.rarity_tier IN ('ultra_legendary', 'legendary')
ORDER BY n.rarity_score DESC;

-- View: High complexity NFTs
CREATE VIEW IF NOT EXISTS view_high_complexity_nfts AS
SELECT
    n.nft_id,
    n.name,
    n.overall_complexity_score,
    v.color_complexity_score,
    v.detail_complexity_score,
    v.texture_complexity_score,
    a.final_denoise,
    a.requires_manual_review
FROM nfts n
JOIN visual_features v ON n.nft_id = v.nft_id
LEFT JOIN nft_profile_assignments a ON n.nft_id = a.nft_id
WHERE n.overall_complexity_score > 70
ORDER BY n.overall_complexity_score DESC;

-- View: Manual review queue
CREATE VIEW IF NOT EXISTS view_manual_review_queue AS
SELECT
    n.nft_id,
    n.name,
    n.rarity_score,
    n.overall_complexity_score,
    a.reasoning,
    a.risk_factors,
    a.processing_priority
FROM nfts n
JOIN nft_profile_assignments a ON n.nft_id = a.nft_id
WHERE a.requires_manual_review = 1
ORDER BY a.processing_priority DESC, n.rarity_score DESC;

-- View: Processing schedule
CREATE VIEW IF NOT EXISTS view_processing_schedule AS
SELECT
    n.rarity_tier,
    COUNT(*) as nft_count,
    AVG(a.estimated_processing_time_min) as avg_time_min,
    SUM(a.estimated_processing_time_min) as total_time_min,
    MIN(a.processing_priority) as min_priority,
    MAX(a.processing_priority) as max_priority
FROM nfts n
JOIN nft_profile_assignments a ON n.nft_id = a.nft_id
GROUP BY n.rarity_tier
ORDER BY max_priority DESC;

-- ============================================================================
-- INITIALIZATION COMPLETE
-- ============================================================================
