-- ============================================================================
-- Schema Migration v2: Critical Style Classification & Character Anatomy
-- Based on research findings showing 92% correlation with animation success
-- ============================================================================

-- Add critical style classification fields to visual_features table
ALTER TABLE visual_features ADD COLUMN artistic_style TEXT;
-- Values: 'pixel_art', 'smooth_digital', 'hand_drawn', '3d_rendered', 'mixed'

ALTER TABLE visual_features ADD COLUMN style_confidence REAL DEFAULT 0.0;
-- Confidence score 0-1 for the style classification

ALTER TABLE visual_features ADD COLUMN is_pixel_art BOOLEAN DEFAULT 0;
-- Quick boolean flag for pixel art (most critical distinction)

ALTER TABLE visual_features ADD COLUMN estimated_pixel_grid_size INTEGER;
-- For pixel art: detected grid size (e.g., 16x16, 32x32)

-- Character anatomy features (Tier 1 - Critical)
ALTER TABLE visual_features ADD COLUMN character_prominence REAL DEFAULT 0.0;
-- Percentage of image occupied by main character (0-1)

ALTER TABLE visual_features ADD COLUMN character_bbox_x INTEGER;
ALTER TABLE visual_features ADD COLUMN character_bbox_y INTEGER;
ALTER TABLE visual_features ADD COLUMN character_bbox_width INTEGER;
ALTER TABLE visual_features ADD COLUMN character_bbox_height INTEGER;
-- Bounding box for main character (from SAM 2 or simple detection)

ALTER TABLE visual_features ADD COLUMN face_detected BOOLEAN DEFAULT 0;
-- Whether a face/facial features are present

ALTER TABLE visual_features ADD COLUMN face_bbox_x INTEGER;
ALTER TABLE visual_features ADD COLUMN face_bbox_y INTEGER;
ALTER TABLE visual_features ADD COLUMN face_bbox_width INTEGER;
ALTER TABLE visual_features ADD COLUMN face_bbox_height INTEGER;
-- Face bounding box if detected

ALTER TABLE visual_features ADD COLUMN facial_preservation_priority TEXT;
-- 'critical', 'high', 'medium', 'low', 'none'

ALTER TABLE visual_features ADD COLUMN face_size_ratio REAL DEFAULT 0.0;
-- Face size as % of total image (>0.15 = large face, needs critical preservation)

-- Pose and motion prediction features
ALTER TABLE visual_features ADD COLUMN pose_type TEXT;
-- 'standing', 'sitting', 'action', 'floating', 'unknown'

ALTER TABLE visual_features ADD COLUMN energy_level TEXT;
-- 'calm', 'moderate', 'energetic', 'dynamic'

ALTER TABLE visual_features ADD COLUMN motion_compatibility_score REAL DEFAULT 0.5;
-- How well the image will support motion (0-1)

-- Background complexity (critical for segmented workflow decision)
ALTER TABLE visual_features ADD COLUMN background_complexity_score REAL DEFAULT 0.0;
-- 0-100, >70 suggests segmented workflow needed

ALTER TABLE visual_features ADD COLUMN character_background_separation_quality REAL DEFAULT 0.0;
-- 0-1, <0.6 suggests segmented workflow needed

-- Research-based optimal parameters (calculated from style + anatomy)
ALTER TABLE visual_features ADD COLUMN optimal_denoise_research REAL;
-- Calculated optimal denoise based on style classification (0.28 for pixel, 0.45 for smooth)

ALTER TABLE visual_features ADD COLUMN optimal_motion_scale_research REAL;
-- Calculated optimal motion scale based on pose + style (0.4 for pixel, 0.9 for smooth)

ALTER TABLE visual_features ADD COLUMN optimal_controlnet_strength REAL;
-- Calculated ControlNet strength (0.95 for pixel art, 0.7-0.8 for smooth)

ALTER TABLE visual_features ADD COLUMN recommended_workflow TEXT;
-- 'A_pixel_art', 'B_smooth_standard', 'C_dynamic', 'D_segmented', 'E_high_quality'

ALTER TABLE visual_features ADD COLUMN style_classification_method TEXT;
-- How style was determined: 'palette_analysis', 'edge_analysis', 'ml_classifier', 'manual'

-- Create indexes for fast querying by style
CREATE INDEX IF NOT EXISTS idx_visual_artistic_style ON visual_features(artistic_style);
CREATE INDEX IF NOT EXISTS idx_visual_pixel_art ON visual_features(is_pixel_art);
CREATE INDEX IF NOT EXISTS idx_visual_face_detected ON visual_features(face_detected);
CREATE INDEX IF NOT EXISTS idx_visual_workflow ON visual_features(recommended_workflow);

-- ============================================================================
-- Update animation_profiles table with research-based profiles
-- ============================================================================

-- Add style-specific fields to profiles
ALTER TABLE animation_profiles ADD COLUMN target_artistic_style TEXT;
-- Which style this profile is optimized for

ALTER TABLE animation_profiles ADD COLUMN use_controlnet BOOLEAN DEFAULT 0;
ALTER TABLE animation_profiles ADD COLUMN controlnet_type TEXT;
-- 'canny', 'depth', 'openpose', 'multi'

ALTER TABLE animation_profiles ADD COLUMN controlnet_strength REAL DEFAULT 0.0;

ALTER TABLE animation_profiles ADD COLUMN requires_segmentation BOOLEAN DEFAULT 0;
-- Whether this profile uses segmented character + background workflow

-- ============================================================================
-- Views for quick analysis
-- ============================================================================

-- View: NFTs by artistic style
CREATE VIEW IF NOT EXISTS nfts_by_style AS
SELECT
    n.nft_id,
    n.name,
    n.rarity_tier,
    vf.artistic_style,
    vf.style_confidence,
    vf.is_pixel_art,
    vf.optimal_denoise_research,
    vf.optimal_motion_scale_research,
    vf.recommended_workflow
FROM nfts n
LEFT JOIN visual_features vf ON n.nft_id = vf.nft_id
WHERE vf.artistic_style IS NOT NULL;

-- View: Pixel art NFTs requiring special handling
CREATE VIEW IF NOT EXISTS pixel_art_nfts AS
SELECT
    n.nft_id,
    n.name,
    n.rarity_tier,
    vf.color_palette_size,
    vf.edge_density,
    vf.estimated_pixel_grid_size,
    vf.optimal_denoise_research,
    vf.optimal_controlnet_strength
FROM nfts n
JOIN visual_features vf ON n.nft_id = vf.nft_id
WHERE vf.is_pixel_art = 1;

-- View: NFTs with faces requiring preservation
CREATE VIEW IF NOT EXISTS face_preservation_nfts AS
SELECT
    n.nft_id,
    n.name,
    n.rarity_tier,
    vf.face_detected,
    vf.face_size_ratio,
    vf.facial_preservation_priority,
    vf.optimal_denoise_research
FROM nfts n
JOIN visual_features vf ON n.nft_id = vf.nft_id
WHERE vf.face_detected = 1
ORDER BY vf.face_size_ratio DESC;

-- View: Complex backgrounds needing segmented workflow
CREATE VIEW IF NOT EXISTS segmented_workflow_candidates AS
SELECT
    n.nft_id,
    n.name,
    vf.background_complexity_score,
    vf.character_background_separation_quality,
    vf.recommended_workflow
FROM nfts n
JOIN visual_features vf ON n.nft_id = vf.nft_id
WHERE vf.character_background_separation_quality < 0.6
   OR vf.background_complexity_score > 70;

-- ============================================================================
-- Migration Notes
-- ============================================================================

-- This migration adds 30+ critical fields based on November 2025 research showing:
-- 1. Artistic style classification has 92% correlation with optimal denoise
-- 2. Character anatomy features have 85-95% correlation with quality
-- 3. Traditional complexity metrics have only 30-40% correlation
--
-- Key Research Findings:
-- - pixel_art → denoise 0.28, motion 0.4, ControlNet Canny 0.95
-- - smooth_digital → denoise 0.45, motion 0.9, ControlNet optional
-- - face_size_ratio > 0.15 → denoise max 0.32, ControlNet 0.90+
-- - background_complexity > 70 → use segmented workflow D
--
-- References:
-- - docs/FEATURE_EXTRACTION_EXECUTIVE_SUMMARY.md
-- - research/SOTA_VIDEO_GENERATION_2024_2025.md
-- - docs/NFT_FEATURE_EXTRACTION_FRAMEWORK.md
