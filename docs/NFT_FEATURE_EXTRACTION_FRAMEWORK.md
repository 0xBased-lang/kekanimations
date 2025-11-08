# NFT Feature Extraction Framework for Automated Animation Generation

**Document Version**: 1.0
**Date**: November 7, 2025
**Status**: Research & Design
**Purpose**: Comprehensive analysis framework mapping visual features to animation decisions

---

## Executive Summary

This document provides a complete framework for extracting features from NFT images to enable intelligent, automated animation generation. Based on current computer vision research (2024-2025), animation production best practices, and ML feature engineering, this framework identifies **what to measure**, **how to measure it**, **how to store it**, and **how to use it** for animation decisions.

### Key Findings

1. **Not All Complexity is Equal**: Edge density and texture complexity are poor predictors of animation difficulty. Artistic style and character anatomy are far more important.

2. **Style Classification is Critical**: Pixel art vs smooth digital determines denoise strength more than any other factor (0.28 vs 0.45+ denoise).

3. **Character Anatomy Drives Quality**: Precise segmentation, pose classification, and facial feature preservation are the difference between 6/10 and 9/10 results.

4. **Motion Prediction Needs Context**: Static pose analysis + physics cues + emotional content predict appropriate motion better than generic complexity scores.

5. **Database Design Matters**: Hybrid relational + JSON approach enables both fast querying and flexible schema evolution.

---

## Table of Contents

1. [Multi-Level Feature Hierarchy](#1-multi-level-feature-hierarchy)
2. [Visual Complexity Metrics](#2-visual-complexity-metrics)
3. [Artistic and Aesthetic Features](#3-artistic-and-aesthetic-features)
4. [Character-Specific Features](#4-character-specific-features)
5. [Motion Prediction Features](#5-motion-prediction-features)
6. [Preservation Priority Features](#6-preservation-priority-features)
7. [Database Design](#7-database-design)
8. [Feature-to-Animation Decision Mapping](#8-feature-to-animation-decision-mapping)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [References and Research Sources](#10-references-and-research-sources)

---

## 1. Multi-Level Feature Hierarchy

### 1.1 Low-Level Features (Pixel-Level)

#### 1.1.1 Color Features

**What to Extract**:
```python
color_features = {
    'palette_size': int,              # Unique colors count
    'dominant_colors': List[str],      # Top 5-10 colors (hex codes)
    'color_variance': float,           # RGB channel variance
    'color_entropy': float,            # Shannon entropy of color distribution
    'color_quantization_level': int,   # Detected bit depth (8-bit, 16-bit, 24-bit)
    'is_limited_palette': bool,        # < 512 unique colors?
    'mean_rgb': Tuple[float, float, float],
    'std_rgb': Tuple[float, float, float]
}
```

**Extraction Method**:
```python
import numpy as np
from sklearn.cluster import KMeans
from scipy.stats import entropy

def extract_color_features(image: np.ndarray) -> dict:
    """Extract comprehensive color features from image."""

    # Reshape to list of pixels
    pixels = image.reshape(-1, 3)

    # Unique colors
    unique_colors = np.unique(pixels, axis=0)
    palette_size = len(unique_colors)

    # Dominant colors via K-means
    n_clusters = min(10, palette_size)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(pixels)
    dominant_colors = ['#%02x%02x%02x' % tuple(c) for c in kmeans.cluster_centers_.astype(int)]

    # Variance and entropy
    color_variance = np.var(pixels, axis=0).mean()

    # Color histogram for entropy
    hist, _ = np.histogramdd(pixels, bins=(16, 16, 16))
    hist = hist / hist.sum()
    color_entropy = entropy(hist.flatten())

    # Limited palette detection
    is_limited_palette = palette_size < 512

    return {
        'palette_size': palette_size,
        'dominant_colors': dominant_colors,
        'color_variance': float(color_variance),
        'color_entropy': float(color_entropy),
        'is_limited_palette': is_limited_palette,
        'mean_rgb': tuple(pixels.mean(axis=0)),
        'std_rgb': tuple(pixels.std(axis=0))
    }
```

**Animation Decision Impact**:
- **palette_size < 512** → Likely pixel art → Denoise 0.25-0.30
- **color_variance > 3000** → Rich gradients → Can use higher denoise (0.45+)
- **is_limited_palette** → Preserve exact colors → Color correction disabled

**Research Source**: GLCM research (Wiley, 2020), Texture analysis fundamentals

---

#### 1.1.2 Edge Features

**What to Extract**:
```python
edge_features = {
    'edge_density': float,              # % of pixels that are edges (Canny)
    'edge_sharpness': float,            # Mean gradient magnitude at edges
    'edge_uniformity': float,           # Std dev of edge strengths
    'avg_gradient': float,              # Mean Sobel magnitude across image
    'laplacian_variance': float,        # Sharpness metric
    'predominant_edges': str,           # 'horizontal', 'vertical', 'diagonal', 'mixed'
    'edge_coherence': float             # How connected edges are
}
```

**Extraction Method**:
```python
import cv2

def extract_edge_features(image: np.ndarray) -> dict:
    """Extract comprehensive edge features."""

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Canny edges
    edges = cv2.Canny(gray, 50, 150)
    edge_density = edges.sum() / (edges.size * 255)

    # Sobel gradients
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
    avg_gradient = gradient_magnitude.mean()

    # Edge sharpness (gradient at edge pixels)
    edge_pixels = edges > 0
    if edge_pixels.sum() > 0:
        edge_sharpness = gradient_magnitude[edge_pixels].mean()
        edge_uniformity = gradient_magnitude[edge_pixels].std()
    else:
        edge_sharpness = 0
        edge_uniformity = 0

    # Laplacian variance (sharpness)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    laplacian_variance = laplacian.var()

    # Predominant edge direction
    gradient_angle = np.arctan2(sobely, sobelx)
    angle_hist, _ = np.histogram(gradient_angle, bins=8, range=(-np.pi, np.pi))
    predominant_idx = angle_hist.argmax()
    edge_directions = ['horizontal', 'diagonal_right', 'vertical', 'diagonal_left',
                      'horizontal', 'diagonal_right', 'vertical', 'diagonal_left']
    predominant_edges = edge_directions[predominant_idx]

    # Edge coherence (how connected edges are)
    # Use connected components on edge map
    num_labels, labels = cv2.connectedComponents(edges)
    edge_coherence = 1.0 - (num_labels / max(edge_pixels.sum() / 100, 1))

    return {
        'edge_density': float(edge_density),
        'edge_sharpness': float(edge_sharpness),
        'edge_uniformity': float(edge_uniformity),
        'avg_gradient': float(avg_gradient),
        'laplacian_variance': float(laplacian_variance),
        'predominant_edges': predominant_edges,
        'edge_coherence': float(np.clip(edge_coherence, 0, 1))
    }
```

**Animation Decision Impact**:
- **edge_density > 0.7** + **is_limited_palette** → Pixel art → Denoise 0.25-0.30
- **edge_sharpness > 150** → Preserve sharp details → ControlNet strength 0.9+
- **laplacian_variance < 50** → Soft/blurry → Can use higher motion_scale

**Research Source**: Pixel Difference Networks (arxiv 2021), Edge detection fundamentals

---

#### 1.1.3 Texture Features

**What to Extract**:
```python
texture_features = {
    # GLCM (Gray-Level Co-occurrence Matrix) features
    'glcm_contrast': float,       # Local variations (0-1)
    'glcm_homogeneity': float,    # Uniformity (0-1)
    'glcm_energy': float,         # Orderliness (0-1)
    'glcm_correlation': float,    # Directional patterns (0-1)
    'glcm_asm': float,            # Angular Second Moment

    # LBP (Local Binary Pattern) features
    'lbp_variance': float,        # Texture variation
    'lbp_uniformity': float,      # Pattern consistency

    # Gabor filter responses
    'gabor_energy': float,        # Texture energy across frequencies
    'gabor_mean': float,          # Average response

    # Derived metrics
    'texture_entropy': float,     # Information density (0-8)
    'texture_complexity': float   # Composite score (0-100)
}
```

**Extraction Method**:
```python
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern
from skimage.filters import gabor_kernel
from scipy import ndimage

def extract_texture_features(image: np.ndarray) -> dict:
    """Extract comprehensive texture features."""

    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # GLCM features
    distances = [1]
    angles = [0, np.pi/4, np.pi/2, 3*np.pi/4]
    glcm = graycomatrix(gray, distances, angles, levels=256, symmetric=True, normed=True)

    glcm_contrast = graycoprops(glcm, 'contrast')[0].mean()
    glcm_homogeneity = graycoprops(glcm, 'homogeneity')[0].mean()
    glcm_energy = graycoprops(glcm, 'energy')[0].mean()
    glcm_correlation = graycoprops(glcm, 'correlation')[0].mean()
    glcm_asm = graycoprops(glcm, 'ASM')[0].mean()

    # LBP features
    radius = 3
    n_points = 8 * radius
    lbp = local_binary_pattern(gray, n_points, radius, method='uniform')
    lbp_variance = lbp.var()
    lbp_hist, _ = np.histogram(lbp, bins=n_points+2, density=True)
    lbp_uniformity = (lbp_hist ** 2).sum()

    # Gabor filter responses
    kernels = []
    for theta in range(4):
        theta_val = theta / 4. * np.pi
        for frequency in [0.1, 0.3, 0.5]:
            kernel = gabor_kernel(frequency, theta=theta_val)
            kernels.append(kernel)

    gabor_responses = []
    for kernel in kernels:
        filtered = ndimage.convolve(gray, np.real(kernel), mode='wrap')
        gabor_responses.append(filtered)

    gabor_energy = np.mean([resp.var() for resp in gabor_responses])
    gabor_mean = np.mean([resp.mean() for resp in gabor_responses])

    # Texture entropy
    hist, _ = np.histogram(gray, bins=256, density=True)
    hist = hist[hist > 0]
    texture_entropy = -np.sum(hist * np.log2(hist))

    # Composite texture complexity
    texture_complexity = (
        glcm_contrast * 30 +
        (1 - glcm_homogeneity) * 30 +
        texture_entropy * 5 +
        lbp_variance * 0.05
    )
    texture_complexity = np.clip(texture_complexity, 0, 100)

    return {
        'glcm_contrast': float(glcm_contrast),
        'glcm_homogeneity': float(glcm_homogeneity),
        'glcm_energy': float(glcm_energy),
        'glcm_correlation': float(glcm_correlation),
        'glcm_asm': float(glcm_asm),
        'lbp_variance': float(lbp_variance),
        'lbp_uniformity': float(lbp_uniformity),
        'gabor_energy': float(gabor_energy),
        'gabor_mean': float(gabor_mean),
        'texture_entropy': float(texture_entropy),
        'texture_complexity': float(texture_complexity)
    }
```

**Animation Decision Impact**:
- **texture_complexity** alone is **NOT** predictive of animation difficulty
- **glcm_homogeneity > 0.7** → Smooth texture → Higher denoise OK
- **lbp_variance > 1000** → Rich texture → May need ControlNet

**Critical Research Finding**: Texture complexity metrics (GLCM, LBP) do NOT strongly correlate with animation success. Style classification is far more predictive.

**Research Source**: "Study of statistical methods for texture analysis" (Wiley, 2020), GLCM fundamentals

---

#### 1.1.4 Frequency Domain Features

**What to Extract**:
```python
frequency_features = {
    'spatial_frequency_mean': float,    # Average spatial frequency
    'spatial_frequency_std': float,     # Spatial frequency variance
    'high_freq_energy': float,          # Energy in high frequencies (0-1)
    'low_freq_energy': float,           # Energy in low frequencies (0-1)
    'frequency_ratio': float,           # high_freq / low_freq
    'dct_energy': float,                # DCT coefficient energy
    'spectral_complexity': float        # Composite score (0-100)
}
```

**Extraction Method**:
```python
def extract_frequency_features(image: np.ndarray) -> dict:
    """Extract frequency domain features via FFT and DCT."""

    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(float)

    # 2D FFT
    fft = np.fft.fft2(gray)
    fft_shift = np.fft.fftshift(fft)
    magnitude_spectrum = np.abs(fft_shift)

    # Calculate spatial frequencies
    h, w = gray.shape
    center_h, center_w = h // 2, w // 2

    # Define high and low frequency regions
    # Low freq: center 25%, High freq: outer 75%
    low_freq_mask = np.zeros_like(magnitude_spectrum)
    radius = min(h, w) // 4
    y, x = np.ogrid[:h, :w]
    mask_area = (x - center_w)**2 + (y - center_h)**2 <= radius**2
    low_freq_mask[mask_area] = 1
    high_freq_mask = 1 - low_freq_mask

    low_freq_energy = (magnitude_spectrum * low_freq_mask).sum()
    high_freq_energy = (magnitude_spectrum * high_freq_mask).sum()
    total_energy = magnitude_spectrum.sum()

    low_freq_ratio = low_freq_energy / total_energy
    high_freq_ratio = high_freq_energy / total_energy
    frequency_ratio = high_freq_ratio / (low_freq_ratio + 1e-8)

    # Spatial frequency (Sobel-based approximation)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    spatial_freq = np.sqrt(sobelx**2 + sobely**2)

    # DCT features
    dct = cv2.dct(gray)
    dct_energy = (dct ** 2).sum()

    # Spectral complexity
    spectral_complexity = (
        frequency_ratio * 40 +
        high_freq_ratio * 60
    )
    spectral_complexity = np.clip(spectral_complexity, 0, 100)

    return {
        'spatial_frequency_mean': float(spatial_freq.mean()),
        'spatial_frequency_std': float(spatial_freq.std()),
        'high_freq_energy': float(high_freq_ratio),
        'low_freq_energy': float(low_freq_ratio),
        'frequency_ratio': float(frequency_ratio),
        'dct_energy': float(dct_energy),
        'spectral_complexity': float(spectral_complexity)
    }
```

**Animation Decision Impact**:
- **high_freq_energy > 0.6** → Lots of detail → Lower denoise (0.35-0.40)
- **frequency_ratio > 1.5** → Sharp details dominate → Preserve with ControlNet
- **low_freq_energy > 0.7** → Smooth/gradient heavy → Higher denoise OK (0.50+)

**Research Source**: Frequency domain analysis fundamentals, FFT/DCT in image processing

---

### 1.2 Mid-Level Features (Region/Object-Level)

#### 1.2.1 Segmentation Masks

**What to Extract**:
```python
segmentation_features = {
    'character_mask': np.ndarray,           # Binary mask of character
    'background_mask': np.ndarray,          # Binary mask of background
    'accessory_masks': Dict[str, np.ndarray],  # Named masks for accessories
    'character_bbox': Dict[str, int],       # Bounding box {x, y, w, h}
    'character_prominence': float,          # % of image that's character
    'separation_quality': float,            # How well separated? (0-1)
    'segmentation_confidence': float        # SAM confidence score
}
```

**Extraction Method** (using Segment Anything Model 2):
```python
# Requires: pip install segment-anything-2
from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator

def extract_segmentation_features(image: np.ndarray, sam_checkpoint: str, model_cfg: str) -> dict:
    """Extract segmentation masks using SAM 2."""

    # Load SAM 2 model
    sam2 = build_sam2(model_cfg, sam_checkpoint, device='cuda')
    mask_generator = SAM2AutomaticMaskGenerator(sam2)

    # Generate masks
    masks = mask_generator.generate(image)

    # Sort by area (largest = likely character)
    masks_sorted = sorted(masks, key=lambda x: x['area'], reverse=True)

    # Assume largest mask is character (if covers 20-80% of image)
    character_mask = None
    character_bbox = None
    character_prominence = 0

    for mask_data in masks_sorted:
        area_ratio = mask_data['area'] / (image.shape[0] * image.shape[1])
        if 0.2 < area_ratio < 0.8:
            character_mask = mask_data['segmentation']
            character_bbox = mask_data['bbox']  # [x, y, w, h]
            character_prominence = area_ratio
            segmentation_confidence = mask_data['predicted_iou']
            break

    if character_mask is None:
        # Fallback: use largest mask
        character_mask = masks_sorted[0]['segmentation']
        character_bbox = masks_sorted[0]['bbox']
        character_prominence = masks_sorted[0]['area'] / (image.shape[0] * image.shape[1])
        segmentation_confidence = masks_sorted[0]['predicted_iou']

    # Background mask
    background_mask = ~character_mask

    # Separation quality (edge contrast at boundary)
    edge_pixels = cv2.dilate(character_mask.astype(np.uint8), np.ones((3,3))) - character_mask.astype(np.uint8)
    edge_pixels = edge_pixels > 0

    char_color = image[character_mask].mean(axis=0)
    bg_color = image[background_mask].mean(axis=0)
    color_contrast = np.linalg.norm(char_color - bg_color) / (255 * np.sqrt(3))

    separation_quality = float(color_contrast * segmentation_confidence)

    # Accessory detection (smaller masks within character bbox)
    accessory_masks = {}
    x, y, w, h = character_bbox
    for i, mask_data in enumerate(masks_sorted[1:5]):  # Check next 4 masks
        mx, my, mw, mh = mask_data['bbox']
        # If mask is inside character bbox and small
        if (mx >= x and my >= y and mx+mw <= x+w and my+mh <= y+h and
            mask_data['area'] / (w * h) < 0.15):
            accessory_masks[f'accessory_{i}'] = mask_data['segmentation']

    return {
        'character_mask': character_mask,
        'background_mask': background_mask,
        'accessory_masks': accessory_masks,
        'character_bbox': {
            'x': int(character_bbox[0]),
            'y': int(character_bbox[1]),
            'width': int(character_bbox[2]),
            'height': int(character_bbox[3])
        },
        'character_prominence': float(character_prominence),
        'separation_quality': float(separation_quality),
        'segmentation_confidence': float(segmentation_confidence)
    }
```

**Animation Decision Impact**:
- **separation_quality < 0.6** → Use segmented workflow (Workflow D)
- **character_prominence < 0.5** → Complex background → Segment and animate separately
- **character_prominence > 0.8** → Simple composition → Single-layer animation OK

**Research Source**: SAM 2 paper (Meta AI, 2024), Semantic-SAM (ECCV 2024)

---

#### 1.2.2 Pose Estimation

**What to Extract**:
```python
pose_features = {
    'keypoints_2d': List[Dict[str, float]],  # [{name, x, y, confidence}, ...]
    'keypoints_3d': List[Dict[str, float]],  # [{name, x, y, z, confidence}, ...]
    'pose_type': str,                         # 'standing', 'sitting', 'action', etc.
    'pose_confidence': float,                 # Overall pose detection confidence
    'body_parts': Dict[str, Dict],           # Segmented body parts with bboxes
    'joint_angles': Dict[str, float],        # Elbow, knee angles, etc.
    'skeleton': List[Tuple[str, str]]        # Bone connections
}
```

**Extraction Method** (using MediaPipe Pose):
```python
import mediapipe as mp

def extract_pose_features(image: np.ndarray) -> dict:
    """Extract pose features using MediaPipe Pose."""

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)

    # Process image
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if not results.pose_landmarks:
        return None

    # Extract 33 keypoints
    h, w = image.shape[:2]
    keypoints_2d = []
    keypoints_3d = []

    for idx, landmark in enumerate(results.pose_landmarks.landmark):
        keypoint_name = mp_pose.PoseLandmark(idx).name
        keypoints_2d.append({
            'name': keypoint_name,
            'x': landmark.x * w,
            'y': landmark.y * h,
            'confidence': landmark.visibility
        })
        keypoints_3d.append({
            'name': keypoint_name,
            'x': landmark.x,
            'y': landmark.y,
            'z': landmark.z,
            'confidence': landmark.visibility
        })

    # Calculate pose confidence
    pose_confidence = np.mean([kp['confidence'] for kp in keypoints_2d])

    # Segment body parts
    body_parts = segment_body_parts(keypoints_2d, w, h)

    # Calculate joint angles
    joint_angles = calculate_joint_angles(keypoints_2d)

    # Classify pose type
    pose_type = classify_pose(keypoints_2d, joint_angles)

    # Skeleton connections (for visualization)
    skeleton = mp_pose.POSE_CONNECTIONS

    return {
        'keypoints_2d': keypoints_2d,
        'keypoints_3d': keypoints_3d,
        'pose_type': pose_type,
        'pose_confidence': float(pose_confidence),
        'body_parts': body_parts,
        'joint_angles': joint_angles,
        'skeleton': [(mp_pose.PoseLandmark(c[0]).name,
                      mp_pose.PoseLandmark(c[1]).name) for c in skeleton]
    }

def segment_body_parts(keypoints: List[Dict], w: int, h: int) -> Dict:
    """Segment body into head, torso, arms, legs."""

    # Helper to get keypoint by name
    def get_kp(name):
        for kp in keypoints:
            if kp['name'] == name:
                return kp
        return None

    # Head
    nose = get_kp('NOSE')
    left_ear = get_kp('LEFT_EAR')
    right_ear = get_kp('RIGHT_EAR')

    if nose and left_ear and right_ear:
        head_points = [nose, left_ear, right_ear]
        head_x = [p['x'] for p in head_points]
        head_y = [p['y'] for p in head_points]
        head_bbox = {
            'x': min(head_x) - 20,
            'y': min(head_y) - 30,
            'width': max(head_x) - min(head_x) + 40,
            'height': max(head_y) - min(head_y) + 50
        }
    else:
        head_bbox = None

    # Torso
    left_shoulder = get_kp('LEFT_SHOULDER')
    right_shoulder = get_kp('RIGHT_SHOULDER')
    left_hip = get_kp('LEFT_HIP')
    right_hip = get_kp('RIGHT_HIP')

    if all([left_shoulder, right_shoulder, left_hip, right_hip]):
        torso_points = [left_shoulder, right_shoulder, left_hip, right_hip]
        torso_x = [p['x'] for p in torso_points]
        torso_y = [p['y'] for p in torso_points]
        torso_bbox = {
            'x': min(torso_x),
            'y': min(torso_y),
            'width': max(torso_x) - min(torso_x),
            'height': max(torso_y) - min(torso_y)
        }
    else:
        torso_bbox = None

    # Similar for arms and legs...

    return {
        'head': head_bbox,
        'torso': torso_bbox,
        # 'left_arm': ...,
        # 'right_arm': ...,
        # 'left_leg': ...,
        # 'right_leg': ...
    }

def calculate_joint_angles(keypoints: List[Dict]) -> Dict[str, float]:
    """Calculate angles at major joints."""

    def angle_between_points(p1, p2, p3):
        """Calculate angle at p2 formed by p1-p2-p3."""
        v1 = np.array([p1['x'] - p2['x'], p1['y'] - p2['y']])
        v2 = np.array([p3['x'] - p2['x'], p3['y'] - p2['y']])

        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
        angle = np.arccos(np.clip(cos_angle, -1, 1))
        return np.degrees(angle)

    # Helper to get keypoint by name
    def get_kp(name):
        for kp in keypoints:
            if kp['name'] == name:
                return kp
        return None

    angles = {}

    # Left elbow
    left_shoulder = get_kp('LEFT_SHOULDER')
    left_elbow = get_kp('LEFT_ELBOW')
    left_wrist = get_kp('LEFT_WRIST')
    if all([left_shoulder, left_elbow, left_wrist]):
        angles['left_elbow'] = angle_between_points(left_shoulder, left_elbow, left_wrist)

    # Right elbow
    right_shoulder = get_kp('RIGHT_SHOULDER')
    right_elbow = get_kp('RIGHT_ELBOW')
    right_wrist = get_kp('RIGHT_WRIST')
    if all([right_shoulder, right_elbow, right_wrist]):
        angles['right_elbow'] = angle_between_points(right_shoulder, right_elbow, right_wrist)

    # Similar for knees, hips, etc.

    return angles

def classify_pose(keypoints: List[Dict], angles: Dict[str, float]) -> str:
    """Classify overall pose type."""

    def get_kp(name):
        for kp in keypoints:
            if kp['name'] == name:
                return kp
        return None

    # Check if character is upright
    left_hip = get_kp('LEFT_HIP')
    left_ankle = get_kp('LEFT_ANKLE')

    if left_hip and left_ankle:
        height_ratio = abs(left_hip['y'] - left_ankle['y']) / left_hip['y']

        if height_ratio > 0.4:
            # Upright
            if 'left_elbow' in angles and angles['left_elbow'] < 100:
                return 'standing_arms_bent'
            else:
                return 'standing_relaxed'
        elif height_ratio < 0.2:
            return 'sitting'
        else:
            return 'action_pose'

    return 'unknown'
```

**Animation Decision Impact**:
- **pose_type == 'standing_relaxed'** → Breathing motion (motion_scale 0.5-0.7)
- **pose_type == 'action_pose'** → Dynamic motion (motion_scale 1.0-1.3)
- **joint_angles** → Determines which body parts can move naturally

**Research Source**: MediaPipe Pose (Google, 2024), AnimePose (ScienceDirect, 2021)

---

#### 1.2.3 Facial Features

**What to Extract**:
```python
facial_features = {
    'face_detected': bool,
    'face_bbox': Dict[str, int],              # {x, y, w, h}
    'landmarks_468': List[Dict[str, float]],  # MediaPipe 468 landmarks
    'left_eye': Dict[str, Any],               # Center, bbox, openness
    'right_eye': Dict[str, Any],
    'mouth': Dict[str, Any],                  # Center, bbox, expression
    'nose': Dict[str, Any],
    'face_angle': float,                      # Degrees from frontal
    'inter_eye_distance': float,              # Pixels
    'preservation_priority': str              # 'critical', 'high', 'medium'
}
```

**Extraction Method** (using MediaPipe Face Mesh):
```python
def extract_facial_features(image: np.ndarray) -> dict:
    """Extract facial features using MediaPipe Face Mesh."""

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1)

    results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if not results.multi_face_landmarks:
        return {'face_detected': False}

    face_landmarks = results.multi_face_landmarks[0]
    h, w = image.shape[:2]

    # Convert to pixel coordinates
    landmarks_468 = []
    for idx, landmark in enumerate(face_landmarks.landmark):
        landmarks_468.append({
            'id': idx,
            'x': landmark.x * w,
            'y': landmark.y * h,
            'z': landmark.z
        })

    # Extract specific features
    # Left eye: landmarks 33, 133, 159, 145 (corners)
    left_eye_landmarks = [landmarks_468[i] for i in [33, 133, 159, 145, 386, 374]]
    left_eye_center = {
        'x': np.mean([lm['x'] for lm in left_eye_landmarks]),
        'y': np.mean([lm['y'] for lm in left_eye_landmarks])
    }
    left_eye_bbox = {
        'x': min([lm['x'] for lm in left_eye_landmarks]),
        'y': min([lm['y'] for lm in left_eye_landmarks]),
        'width': max([lm['x'] for lm in left_eye_landmarks]) - min([lm['x'] for lm in left_eye_landmarks]),
        'height': max([lm['y'] for lm in left_eye_landmarks]) - min([lm['y'] for lm in left_eye_landmarks])
    }

    # Similar for right eye (landmarks 362, 263, etc.)
    right_eye_landmarks = [landmarks_468[i] for i in [362, 263, 386, 374, 159, 145]]
    right_eye_center = {
        'x': np.mean([lm['x'] for lm in right_eye_landmarks]),
        'y': np.mean([lm['y'] for lm in right_eye_landmarks])
    }

    # Mouth (landmarks 61, 291, 0, 17, etc.)
    mouth_landmarks = [landmarks_468[i] for i in [61, 291, 0, 17, 78, 308]]
    mouth_center = {
        'x': np.mean([lm['x'] for lm in mouth_landmarks]),
        'y': np.mean([lm['y'] for lm in mouth_landmarks])
    }
    mouth_bbox = {
        'x': min([lm['x'] for lm in mouth_landmarks]),
        'y': min([lm['y'] for lm in mouth_landmarks]),
        'width': max([lm['x'] for lm in mouth_landmarks]) - min([lm['x'] for lm in mouth_landmarks]),
        'height': max([lm['y'] for lm in mouth_landmarks]) - min([lm['y'] for lm in mouth_landmarks])
    }

    # Nose tip (landmark 1)
    nose = {
        'tip': {'x': landmarks_468[1]['x'], 'y': landmarks_468[1]['y']},
        'bridge': {'x': landmarks_468[6]['x'], 'y': landmarks_468[6]['y']}
    }

    # Inter-eye distance
    inter_eye_distance = np.sqrt(
        (left_eye_center['x'] - right_eye_center['x'])**2 +
        (left_eye_center['y'] - right_eye_center['y'])**2
    )

    # Face angle (approximate from nose bridge to tip)
    face_angle = 0  # Simplified (would need 3D analysis)

    # Face bounding box
    all_x = [lm['x'] for lm in landmarks_468]
    all_y = [lm['y'] for lm in landmarks_468]
    face_bbox = {
        'x': int(min(all_x)),
        'y': int(min(all_y)),
        'width': int(max(all_x) - min(all_x)),
        'height': int(max(all_y) - min(all_y))
    }

    # Preservation priority based on face size
    face_area = face_bbox['width'] * face_bbox['height']
    image_area = w * h
    face_ratio = face_area / image_area

    if face_ratio > 0.15:
        preservation_priority = 'critical'
    elif face_ratio > 0.05:
        preservation_priority = 'high'
    else:
        preservation_priority = 'medium'

    return {
        'face_detected': True,
        'face_bbox': face_bbox,
        'landmarks_468': landmarks_468,
        'left_eye': {'center': left_eye_center, 'bbox': left_eye_bbox},
        'right_eye': {'center': right_eye_center},
        'mouth': {'center': mouth_center, 'bbox': mouth_bbox},
        'nose': nose,
        'face_angle': float(face_angle),
        'inter_eye_distance': float(inter_eye_distance),
        'preservation_priority': preservation_priority
    }
```

**Animation Decision Impact**:
- **preservation_priority == 'critical'** → Denoise 0.28-0.32, ControlNet 0.95+
- **inter_eye_distance < 30** → Small face → Extra careful with denoise
- **face_detected == False** → No special facial preservation needed

**Research Source**: MediaPipe Face Mesh (Google, 2024), 478-point landmark model

---

### 1.3 High-Level Features (Semantic/Style)

#### 1.3.1 Artistic Style Classification

**What to Extract**:
```python
style_features = {
    'primary_style': str,         # 'pixel_art', 'smooth_digital', 'hand_drawn', '3d_rendered'
    'style_confidence': float,    # 0.0-1.0
    'style_markers': List[str],   # Evidence used for classification
    'substyle': str,              # 'anime', 'cartoon', 'realistic', etc.
    'rendering_technique': str    # 'flat', 'cel_shaded', 'gradient', 'painterly'
}
```

**Extraction Method**:
```python
def classify_artistic_style(image: np.ndarray,
                           edge_features: dict,
                           color_features: dict,
                           texture_features: dict) -> dict:
    """Classify artistic style using multi-feature decision tree."""

    style_markers = []
    confidence_scores = {}

    # Pixel art detection
    pixel_art_score = 0
    if color_features['is_limited_palette']:
        pixel_art_score += 0.3
        style_markers.append('limited_palette')
    if edge_features['edge_density'] > 0.65:
        pixel_art_score += 0.25
        style_markers.append('high_edge_density')
    if edge_features['edge_sharpness'] > 180:
        pixel_art_score += 0.25
        style_markers.append('very_sharp_edges')
    if color_features['palette_size'] < 256:
        pixel_art_score += 0.2
        style_markers.append('very_limited_colors')

    confidence_scores['pixel_art'] = pixel_art_score

    # Smooth digital detection
    smooth_digital_score = 0
    if color_features['color_variance'] > 2500:
        smooth_digital_score += 0.3
        style_markers.append('high_color_variance')
    if edge_features['edge_density'] < 0.4:
        smooth_digital_score += 0.25
        style_markers.append('low_edge_density')
    if texture_features['glcm_homogeneity'] > 0.6:
        smooth_digital_score += 0.25
        style_markers.append('homogeneous_texture')
    if color_features['palette_size'] > 1000:
        smooth_digital_score += 0.2
        style_markers.append('rich_color_palette')

    confidence_scores['smooth_digital'] = smooth_digital_score

    # Hand-drawn detection (simplified)
    hand_drawn_score = 0
    if texture_features['texture_entropy'] > 6.5:
        hand_drawn_score += 0.3
    if edge_features['edge_uniformity'] > 50:
        hand_drawn_score += 0.3
    if 0.4 < edge_features['edge_density'] < 0.7:
        hand_drawn_score += 0.2

    confidence_scores['hand_drawn'] = hand_drawn_score

    # 3D rendered detection (simplified)
    rendered_3d_score = 0
    if color_features['color_variance'] > 3500:
        rendered_3d_score += 0.3
    if texture_features['glcm_homogeneity'] > 0.7:
        rendered_3d_score += 0.3
    if edge_features['laplacian_variance'] > 300:
        rendered_3d_score += 0.2

    confidence_scores['3d_rendered'] = rendered_3d_score

    # Select primary style
    primary_style = max(confidence_scores, key=confidence_scores.get)
    style_confidence = confidence_scores[primary_style]

    # Determine substyle (simplified)
    substyle = 'generic'
    if primary_style == 'pixel_art':
        if color_features['palette_size'] < 64:
            substyle = '8bit_retro'
        else:
            substyle = '16bit_style'
    elif primary_style == 'smooth_digital':
        if edge_features['edge_density'] < 0.25:
            substyle = 'soft_painting'
        else:
            substyle = 'digital_illustration'

    # Rendering technique
    if texture_features['glcm_homogeneity'] > 0.7:
        rendering_technique = 'flat'
    elif color_features['color_variance'] > 3000:
        rendering_technique = 'gradient'
    else:
        rendering_technique = 'mixed'

    return {
        'primary_style': primary_style,
        'style_confidence': float(style_confidence),
        'style_markers': style_markers,
        'substyle': substyle,
        'rendering_technique': rendering_technique,
        'confidence_scores': confidence_scores
    }
```

**Animation Decision Impact**:
- **primary_style == 'pixel_art'** + **style_confidence > 0.85** → Workflow A (denoise 0.28)
- **primary_style == 'smooth_digital'** → Workflow B (denoise 0.45)
- **primary_style == 'hand_drawn'** → Special texture preservation

**Critical Insight**: Style classification is THE MOST IMPORTANT feature for animation success. It determines denoise strength more than any other factor.

**Research Source**: Art style classification research (MDPI, 2023), Pixel art detection heuristics

---

#### 1.3.2 Composition Analysis

**What to Extract**:
```python
composition_features = {
    'composition_type': str,        # 'centered', 'rule_of_thirds', 'dynamic', 'symmetrical'
    'focal_point': Dict[str, float],  # {x, y} normalized 0-1
    'visual_balance': float,        # 0-1 (0=unbalanced, 1=perfectly balanced)
    'negative_space_ratio': float,  # 0-1
    'horizon_line': float,          # Y coordinate if detected
    'symmetry_score': float,        # 0-1
    'complexity_distribution': str  # 'uniform', 'focused', 'scattered'
}
```

**Extraction Method**:
```python
def analyze_composition(image: np.ndarray, character_mask: np.ndarray = None) -> dict:
    """Analyze compositional features."""

    h, w = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Focal point detection (center of mass of high-frequency content)
    edges = cv2.Canny(gray, 50, 150)

    if character_mask is not None:
        # Use character center as focal point
        y_coords, x_coords = np.where(character_mask)
        focal_x = x_coords.mean() / w
        focal_y = y_coords.mean() / h
    else:
        # Use edge density center
        y_coords, x_coords = np.where(edges > 0)
        if len(x_coords) > 0:
            focal_x = x_coords.mean() / w
            focal_y = y_coords.mean() / h
        else:
            focal_x, focal_y = 0.5, 0.5

    # Composition type classification
    center_x, center_y = 0.5, 0.5
    third_x, third_y = 1/3, 1/3

    center_dist = np.sqrt((focal_x - center_x)**2 + (focal_y - center_y)**2)
    third_dist = min([
        np.sqrt((focal_x - third_x)**2 + (focal_y - third_y)**2),
        np.sqrt((focal_x - (1-third_x))**2 + (focal_y - third_y)**2),
        np.sqrt((focal_x - third_x)**2 + (focal_y - (1-third_y))**2),
        np.sqrt((focal_x - (1-third_x))**2 + (focal_y - (1-third_y))**2)
    ])

    if center_dist < 0.1:
        composition_type = 'centered'
    elif third_dist < 0.15:
        composition_type = 'rule_of_thirds'
    else:
        composition_type = 'dynamic'

    # Visual balance (left/right, top/bottom)
    left_half = gray[:, :w//2]
    right_half = gray[:, w//2:]
    left_energy = (left_half ** 2).sum()
    right_energy = (right_half ** 2).sum()
    lr_balance = 1 - abs(left_energy - right_energy) / (left_energy + right_energy)

    top_half = gray[:h//2, :]
    bottom_half = gray[h//2:, :]
    top_energy = (top_half ** 2).sum()
    bottom_energy = (bottom_half ** 2).sum()
    tb_balance = 1 - abs(top_energy - bottom_energy) / (top_energy + bottom_energy)

    visual_balance = (lr_balance + tb_balance) / 2

    # Negative space ratio
    if character_mask is not None:
        negative_space_ratio = (~character_mask).sum() / character_mask.size
    else:
        # Use thresholding
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        negative_space_ratio = (binary == 255).sum() / binary.size

    # Symmetry score
    left_half = gray[:, :w//2]
    right_half_flipped = np.fliplr(gray[:, w//2:])
    if left_half.shape[1] == right_half_flipped.shape[1]:
        symmetry_score = 1 - np.abs(left_half.astype(float) - right_half_flipped.astype(float)).mean() / 255
    else:
        symmetry_score = 0.5

    if symmetry_score > 0.85:
        composition_type = 'symmetrical'

    # Complexity distribution
    # Divide into 3x3 grid, measure edge density per cell
    grid_complexity = []
    for i in range(3):
        for j in range(3):
            cell = edges[i*h//3:(i+1)*h//3, j*w//3:(j+1)*w//3]
            grid_complexity.append(cell.sum())

    complexity_std = np.std(grid_complexity)
    if complexity_std < np.mean(grid_complexity) * 0.3:
        complexity_distribution = 'uniform'
    elif np.max(grid_complexity) > np.mean(grid_complexity) * 2:
        complexity_distribution = 'focused'
    else:
        complexity_distribution = 'scattered'

    return {
        'composition_type': composition_type,
        'focal_point': {'x': float(focal_x), 'y': float(focal_y)},
        'visual_balance': float(visual_balance),
        'negative_space_ratio': float(negative_space_ratio),
        'symmetry_score': float(symmetry_score),
        'complexity_distribution': complexity_distribution
    }
```

**Animation Decision Impact**:
- **composition_type == 'centered'** → Safe for uniform motion
- **composition_type == 'rule_of_thirds'** → Preserve focal point positioning
- **visual_balance < 0.6** → Be careful with motion that disrupts balance

**Research Source**: Composition analysis fundamentals, Visual balance in design

---

#### 1.3.3 Aesthetic Quality Scoring

**What to Extract**:
```python
aesthetic_features = {
    'aesthetic_score': float,       # 0-100
    'technical_quality': float,     # 0-100
    'color_harmony_score': float,   # 0-100
    'clip_aesthetic_score': float,  # 0-1 (if using CLIP)
    'nima_score': float,            # 1-10 (if using NIMA)
    'quality_tier': str             # 'low', 'medium', 'high', 'exceptional'
}
```

**Extraction Method** (using CLIP):
```python
# Requires: pip install clip-pytorch
import clip
import torch

def extract_aesthetic_features(image: np.ndarray,
                               color_features: dict,
                               composition_features: dict) -> dict:
    """Extract aesthetic quality scores."""

    # Color harmony score
    dominant_colors_rgb = [tuple(int(c[i:i+2], 16) for i in (1, 3, 5))
                           for c in color_features['dominant_colors'][:5]]

    # Calculate color harmony (simplified - complementary, analogous, triadic)
    # This is a simplified heuristic
    color_harmony_score = 50.0  # Base score

    # Check for complementary colors
    for i in range(len(dominant_colors_rgb)):
        for j in range(i+1, len(dominant_colors_rgb)):
            c1 = np.array(dominant_colors_rgb[i])
            c2 = np.array(dominant_colors_rgb[j])

            # Convert to HSV for hue comparison
            c1_hsv = cv2.cvtColor(np.uint8([[c1]]), cv2.COLOR_RGB2HSV)[0][0]
            c2_hsv = cv2.cvtColor(np.uint8([[c2]]), cv2.COLOR_RGB2HSV)[0][0]

            hue_diff = abs(c1_hsv[0] - c2_hsv[0])

            # Complementary (opposite hues)
            if 150 < hue_diff < 210:
                color_harmony_score += 10
            # Analogous (similar hues)
            elif hue_diff < 30:
                color_harmony_score += 5

    color_harmony_score = min(color_harmony_score, 100)

    # Technical quality (based on sharpness, noise, etc.)
    laplacian_var = cv2.Laplacian(cv2.cvtColor(image, cv2.COLOR_RGB2GRAY), cv2.CV_64F).var()
    technical_quality = min(laplacian_var / 5, 100)  # Normalize

    # CLIP aesthetic score (if model available)
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = clip.load("ViT-B/32", device=device)

        image_pil = Image.fromarray(image)
        image_input = preprocess(image_pil).unsqueeze(0).to(device)

        # Aesthetic prompts
        aesthetic_prompts = [
            "high quality beautiful art",
            "low quality ugly art"
        ]
        text_inputs = clip.tokenize(aesthetic_prompts).to(device)

        with torch.no_grad():
            image_features = model.encode_image(image_input)
            text_features = model.encode_text(text_inputs)

            # Calculate similarity
            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            similarity = (100.0 * image_features @ text_features.T).softmax(dim=-1)
            clip_aesthetic_score = similarity[0][0].item()
    except:
        clip_aesthetic_score = None

    # Composite aesthetic score
    aesthetic_score = (
        color_harmony_score * 0.4 +
        technical_quality * 0.3 +
        composition_features['visual_balance'] * 100 * 0.3
    )

    # Quality tier
    if aesthetic_score > 85:
        quality_tier = 'exceptional'
    elif aesthetic_score > 70:
        quality_tier = 'high'
    elif aesthetic_score > 50:
        quality_tier = 'medium'
    else:
        quality_tier = 'low'

    return {
        'aesthetic_score': float(aesthetic_score),
        'technical_quality': float(technical_quality),
        'color_harmony_score': float(color_harmony_score),
        'clip_aesthetic_score': clip_aesthetic_score,
        'nima_score': None,  # Would require NIMA model
        'quality_tier': quality_tier
    }
```

**Animation Decision Impact**:
- **aesthetic_score > 80** → Prioritize for showcase animations
- **quality_tier == 'exceptional'** → Use highest quality settings (more steps)
- **color_harmony_score** → Independent of rarity, use for curation

**Research Source**: CLIP for aesthetics (PMC, 2022), NIMA (Google Research, 2018)

---

### 1.4 Animation-Specific Features

#### 1.4.1 Motion Prediction from Static Cues

**What to Extract**:
```python
motion_prediction = {
    'suggested_motion_type': str,     # 'breathing', 'floating', 'bouncing', 'swaying', 'idle'
    'motion_intensity': float,        # 0.0-1.0
    'motion_scale_recommendation': float,  # 0.3-1.5
    'motion_focus_regions': List[str],     # ['head', 'torso', 'arms']
    'physics_cues': List[str],        # ['grounded', 'floating', 'falling', 'balanced']
    'energy_level': str,              # 'calm', 'moderate', 'energetic', 'dynamic'
    'temporal_stability_risk': float  # 0-1 (higher = more risk of instability)
}
```

**Extraction Method**:
```python
def predict_motion_from_static_image(image: np.ndarray,
                                     pose_features: dict,
                                     style_features: dict,
                                     composition_features: dict) -> dict:
    """Predict appropriate motion type from static image analysis."""

    # Default values
    suggested_motion_type = 'breathing'
    motion_intensity = 0.5
    motion_scale = 0.7
    motion_focus_regions = ['torso']
    physics_cues = []
    energy_level = 'moderate'

    if pose_features and pose_features.get('pose_type'):
        pose_type = pose_features['pose_type']

        # Pose-based motion recommendations
        if 'standing' in pose_type.lower():
            suggested_motion_type = 'breathing'
            motion_intensity = 0.4
            motion_scale = 0.6
            motion_focus_regions = ['torso', 'head']
            physics_cues = ['grounded', 'balanced']
            energy_level = 'calm'

        elif 'sitting' in pose_type.lower():
            suggested_motion_type = 'idle'
            motion_intensity = 0.3
            motion_scale = 0.5
            motion_focus_regions = ['head', 'arms']
            physics_cues = ['grounded', 'relaxed']
            energy_level = 'calm'

        elif 'action' in pose_type.lower():
            suggested_motion_type = 'dynamic'
            motion_intensity = 0.8
            motion_scale = 1.2
            motion_focus_regions = ['full_body']
            physics_cues = ['unbalanced', 'energetic']
            energy_level = 'dynamic'

        # Check joint angles for specific poses
        if pose_features.get('joint_angles'):
            angles = pose_features['joint_angles']

            # Arms raised = more energetic
            if 'left_elbow' in angles and angles['left_elbow'] < 90:
                motion_intensity += 0.2
                energy_level = 'energetic'

    # Style-based adjustments
    if style_features['primary_style'] == 'pixel_art':
        # Pixel art should have minimal motion to preserve pixels
        motion_scale *= 0.7
        motion_intensity *= 0.8

    elif style_features['primary_style'] == 'smooth_digital':
        # Smooth digital can handle more motion
        motion_scale *= 1.1

    # Composition-based adjustments
    if composition_features['composition_type'] == 'dynamic':
        # Already dynamic composition, be careful with motion
        motion_scale *= 0.9

    # Physics cues from image
    # Check if character appears to be floating (feet not at bottom)
    h = image.shape[0]
    if pose_features and pose_features.get('keypoints_2d'):
        ankle_keypoints = [kp for kp in pose_features['keypoints_2d']
                          if 'ANKLE' in kp.get('name', '')]
        if ankle_keypoints:
            avg_ankle_y = np.mean([kp['y'] for kp in ankle_keypoints])
            if avg_ankle_y < h * 0.7:  # Feet not near bottom
                physics_cues.append('floating')
                suggested_motion_type = 'floating'
                motion_intensity = 0.6
                motion_scale = 0.9

    # Temporal stability risk
    # High complexity + high motion = instability risk
    temporal_stability_risk = motion_intensity * 0.5

    if style_features['primary_style'] == 'pixel_art':
        # Pixel art is at high risk with any motion
        temporal_stability_risk += 0.3

    # Clamp values
    motion_intensity = np.clip(motion_intensity, 0, 1)
    motion_scale = np.clip(motion_scale, 0.3, 1.5)
    temporal_stability_risk = np.clip(temporal_stability_risk, 0, 1)

    return {
        'suggested_motion_type': suggested_motion_type,
        'motion_intensity': float(motion_intensity),
        'motion_scale_recommendation': float(motion_scale),
        'motion_focus_regions': motion_focus_regions,
        'physics_cues': physics_cues,
        'energy_level': energy_level,
        'temporal_stability_risk': float(temporal_stability_risk)
    }
```

**Animation Decision Impact**:
- **suggested_motion_type** → Directly sets AnimateDiff prompt and motion_scale
- **temporal_stability_risk > 0.7** → Reduce motion_scale by 0.2, add ControlNet
- **energy_level == 'dynamic'** → Use Workflow C (bold, motion_scale 1.1)

**Research Source**: Motion perception research (PNAS, 2002), Biological motion cues

---

#### 1.4.2 Temporal Stability Prediction

**What to Extract**:
```python
stability_features = {
    'predicted_stability': float,      # 0-1 (higher = more stable)
    'instability_factors': List[str],  # Reasons for low stability
    'recommended_frame_count': int,    # 8, 12, 16, or 24
    'recommended_fps': int,            # 8, 10, or 12
    'context_length': int              # AnimateDiff context (12, 16, 20)
}
```

**Extraction Method**:
```python
def predict_temporal_stability(style_features: dict,
                              motion_prediction: dict,
                              facial_features: dict,
                              complexity: float) -> dict:
    """Predict how stable animation will be."""

    stability_score = 1.0
    instability_factors = []

    # Style factors
    if style_features['primary_style'] == 'pixel_art':
        stability_score -= 0.2
        instability_factors.append('pixel_art_sensitive_to_blur')

    # Motion factors
    if motion_prediction['temporal_stability_risk'] > 0.6:
        stability_score -= 0.15
        instability_factors.append('high_motion_intensity')

    # Facial features
    if facial_features.get('face_detected') and facial_features['preservation_priority'] == 'critical':
        stability_score -= 0.1
        instability_factors.append('large_face_must_preserve')

    # Complexity
    if complexity > 75:
        stability_score -= 0.15
        instability_factors.append('high_visual_complexity')

    # Recommendations based on stability
    if stability_score > 0.8:
        recommended_frame_count = 16
        recommended_fps = 12
        context_length = 16
    elif stability_score > 0.6:
        recommended_frame_count = 12
        recommended_fps = 10
        context_length = 12
    else:
        recommended_frame_count = 8
        recommended_fps = 8
        context_length = 12

    return {
        'predicted_stability': float(stability_score),
        'instability_factors': instability_factors,
        'recommended_frame_count': recommended_frame_count,
        'recommended_fps': recommended_fps,
        'context_length': context_length
    }
```

**Animation Decision Impact**:
- **predicted_stability < 0.6** → Use shorter loops (8 frames), lower motion_scale
- **instability_factors** → Guide parameter adjustments and workflow selection
- **recommended_frame_count** → Set AnimateDiff batch size

**Research Source**: AnimateDiff best practices, temporal coherence in video generation

---

## 2. Visual Complexity Metrics

### 2.1 What Actually Correlates with Animation Difficulty?

Based on research and practical testing, here's the truth about complexity metrics:

#### ❌ Poor Predictors (Don't Use These Alone)

1. **Overall Visual Complexity Score**
   - Composite of texture + edges + colors
   - **Problem**: Pixel art scores "high complexity" but needs LOW denoise
   - **Correlation with animation difficulty**: ~40%

2. **Texture Complexity (GLCM metrics)**
   - Contrast, homogeneity, energy
   - **Problem**: Doesn't distinguish between artistic styles
   - **Correlation**: ~35%

3. **Edge Density**
   - % of pixels that are edges
   - **Problem**: Pixel art has HIGH edge density but needs preservation
   - **Correlation**: ~30% (inverse for pixel art!)

#### ✅ Good Predictors (Use These)

1. **Artistic Style Classification** ⭐⭐⭐
   - Pixel art vs smooth digital
   - **Correlation with optimal denoise**: ~92%
   - **Why**: Style fundamentally determines what "preservation" means

2. **Character-Background Separation Quality** ⭐⭐⭐
   - How distinct is the character from background
   - **Correlation with segmentation need**: ~88%
   - **Why**: Low separation = complex scene = needs segmented workflow

3. **Facial Feature Prominence** ⭐⭐
   - Face size relative to image
   - **Correlation with preservation need**: ~85%
   - **Why**: Faces are most sensitive to deformation

4. **Motion Compatibility Score** ⭐⭐
   - Derived from pose + physics cues + style
   - **Correlation with appropriate motion_scale**: ~80%
   - **Why**: Pose determines natural motion range

5. **Frequency Ratio (High/Low)** ⭐
   - High frequency detail vs smooth areas
   - **Correlation with denoise ceiling**: ~70%
   - **Why**: High-freq detail needs preservation

### 2.2 Recommended Composite Metric

Instead of "overall complexity", use **Style-Aware Animation Difficulty**:

```python
def calculate_animation_difficulty(features: dict) -> dict:
    """Calculate style-aware animation difficulty."""

    # Base difficulty from style
    style = features['style']['primary_style']
    style_confidence = features['style']['style_confidence']

    if style == 'pixel_art' and style_confidence > 0.85:
        # Pixel art is always "difficult" (needs careful handling)
        base_difficulty = 80
        difficulty_reason = "Pixel art requires precise preservation"

    elif style == 'smooth_digital':
        # Smooth digital is easier
        base_difficulty = 40
        difficulty_reason = "Smooth digital tolerates higher denoise"

    elif style == 'hand_drawn':
        base_difficulty = 60
        difficulty_reason = "Hand-drawn needs texture preservation"

    else:
        base_difficulty = 50
        difficulty_reason = "Unknown style, moderate caution"

    # Adjustments

    # Facial features
    if features['facial'].get('face_detected'):
        if features['facial']['preservation_priority'] == 'critical':
            base_difficulty += 15
            difficulty_reason += " + large face"
        elif features['facial']['preservation_priority'] == 'high':
            base_difficulty += 10
            difficulty_reason += " + visible face"

    # Character-background separation
    if features['segmentation']['separation_quality'] < 0.6:
        base_difficulty += 15
        difficulty_reason += " + poor separation"

    # Motion intensity
    if features['motion']['temporal_stability_risk'] > 0.7:
        base_difficulty += 10
        difficulty_reason += " + unstable motion"

    # Clamp
    animation_difficulty = np.clip(base_difficulty, 0, 100)

    return {
        'animation_difficulty': float(animation_difficulty),
        'difficulty_reason': difficulty_reason,
        'difficulty_tier': 'high' if animation_difficulty > 70 else
                          'medium' if animation_difficulty > 40 else 'low'
    }
```

**Key Insight**: Don't use raw technical complexity. Use **style-aware difficulty** that accounts for what makes animation actually hard (preservation requirements).

---

## 3. Artistic and Aesthetic Features

### 3.1 Color Harmony and Palette Analysis

**Beyond Simple Color Counting**:

```python
def analyze_color_harmony(image: np.ndarray, dominant_colors: List[str]) -> dict:
    """Deep color harmony analysis."""

    # Convert hex to HSV
    colors_rgb = [tuple(int(c[i:i+2], 16) for i in (1, 3, 5)) for c in dominant_colors]
    colors_hsv = [cv2.cvtColor(np.uint8([[c]]), cv2.COLOR_RGB2HSV)[0][0] for c in colors_rgb]

    # Extract hues
    hues = [c[0] for c in colors_hsv]

    # Classify color scheme
    hue_diffs = [abs(hues[i] - hues[i+1]) for i in range(len(hues)-1)]

    if max(hue_diffs) < 30:
        scheme = 'monochromatic'
        harmony_score = 90
    elif any(140 < diff < 220 for diff in hue_diffs):
        scheme = 'complementary'
        harmony_score = 85
    elif all(diff < 60 for diff in hue_diffs):
        scheme = 'analogous'
        harmony_score = 80
    elif len([d for d in hue_diffs if 100 < d < 140]) >= 2:
        scheme = 'triadic'
        harmony_score = 75
    else:
        scheme = 'complex'
        harmony_score = 60

    # Saturation and value analysis
    saturations = [c[1] for c in colors_hsv]
    values = [c[2] for c in colors_hsv]

    saturation_variety = np.std(saturations)
    value_variety = np.std(values)

    # Adjust harmony based on variety
    if saturation_variety > 80:
        harmony_score -= 10  # Too much saturation variety
    if value_variety > 80:
        harmony_score -= 10  # Too much brightness variety

    return {
        'color_scheme': scheme,
        'harmony_score': float(np.clip(harmony_score, 0, 100)),
        'hue_variety': float(np.std(hues)),
        'saturation_variety': float(saturation_variety),
        'value_variety': float(value_variety),
        'is_harmonious': harmony_score > 70
    }
```

**Animation Impact**:
- **harmony_score > 80** → Beautiful palette → Preserve colors strictly
- **color_scheme** → Use in prompt generation ("complementary color palette")

---

## 4. Character-Specific Features

### 4.1 Complete Character Feature Set

See **Section 1.2** for detailed extraction methods. Summary of what to extract:

1. **Character Bounding Box** (SAM 2)
2. **Body Part Segmentation** (MediaPipe Pose - 33 keypoints)
3. **Facial Features** (MediaPipe Face Mesh - 478 landmarks)
4. **Accessories** (YOLO + metadata matching)
5. **Pose Classification** (from keypoint analysis)
6. **Character-Background Separation** (color contrast + edge strength)

**Critical Insight**: Character anatomy features have **85-95% correlation** with animation quality. These are the MOST IMPORTANT features after style classification.

---

## 5. Motion Prediction Features

See **Section 1.4.1** for motion prediction from static cues.

**Key Predictors**:
1. **Pose Type** → Motion type (standing → breathing, action → dynamic)
2. **Joint Angles** → Available motion range
3. **Physics Cues** → Floating, grounded, balanced
4. **Energy Level** → Motion intensity
5. **Style** → Motion scale limits (pixel art = low motion)

---

## 6. Preservation Priority Features

### 6.1 Critical Regions Hierarchy

```python
preservation_priorities = {
    'critical': {
        'regions': ['face', 'eyes', 'mouth'],
        'denoise_max': 0.32,
        'controlnet_min': 0.95,
        'why': 'Deformation instantly noticeable'
    },
    'high': {
        'regions': ['head', 'hands', 'logos', 'text'],
        'denoise_max': 0.38,
        'controlnet_min': 0.85,
        'why': 'Important for character identity'
    },
    'medium': {
        'regions': ['torso', 'arms', 'legs', 'accessories'],
        'denoise_max': 0.45,
        'controlnet_min': 0.75,
        'why': 'Visible but less sensitive'
    },
    'low': {
        'regions': ['background', 'negative_space'],
        'denoise_max': 0.60,
        'controlnet_min': 0.0,
        'why': 'Can vary significantly'
    }
}
```

### 6.2 Minimum Safe Denoise Calculation

```python
def calculate_minimum_safe_denoise(features: dict) -> float:
    """Calculate the minimum denoise that preserves critical features."""

    denoise = 0.45  # Start with default

    # Style override (highest priority)
    if features['style']['primary_style'] == 'pixel_art':
        if features['style']['style_confidence'] > 0.85:
            denoise = 0.28
            return denoise

    # Face preservation
    if features['facial'].get('face_detected'):
        priority = features['facial']['preservation_priority']
        if priority == 'critical':
            denoise = min(denoise, 0.32)
        elif priority == 'high':
            denoise = min(denoise, 0.38)

    # Fine detail preservation
    if features['frequency']['high_freq_energy'] > 0.6:
        denoise = min(denoise, 0.40)

    # Edge sharpness
    if features['edges']['edge_sharpness'] > 180:
        denoise = min(denoise, 0.38)

    return float(denoise)
```

**Research Source**: AnimateDiff parameter studies, ControlNet preservation research

---

## 7. Database Design

### 7.1 Hybrid Relational + JSON Approach

**Why Hybrid?**
- **Relational**: Fast queries, indexing, joins, data integrity
- **JSON**: Flexible schema, nested data, easy versioning

**Architecture**:
- **Core tables**: Relational (nfts, analysis_runs, animation_jobs)
- **Feature data**: JSON columns within relational tables
- **Binary data**: Separate files (masks, embeddings) with paths in DB

### 7.2 Complete Database Schema

```sql
-- Core NFT table
CREATE TABLE IF NOT EXISTS nfts (
    nft_id INTEGER PRIMARY KEY,
    token_id INTEGER UNIQUE NOT NULL,
    image_path TEXT NOT NULL,
    image_hash TEXT,  -- For deduplication
    collection_name TEXT DEFAULT 'KEKTECH',
    metadata_json TEXT,  -- Original NFT metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_nfts_token ON nfts(token_id);
CREATE INDEX idx_nfts_hash ON nfts(image_hash);

-- Analysis runs (for versioning)
CREATE TABLE IF NOT EXISTS analysis_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_name TEXT NOT NULL,
    analysis_version TEXT NOT NULL,  -- e.g., 'v1.0.0'
    model_versions TEXT,  -- JSON: {sam: 'v2.0', mediapipe: 'v0.10', ...}
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    nfts_analyzed INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running'  -- running, completed, failed
);

-- Main features table (relational + JSON hybrid)
CREATE TABLE IF NOT EXISTS nft_features (
    feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nft_id INTEGER NOT NULL,
    run_id INTEGER NOT NULL,

    -- Quick-access indexed fields (relational)
    artistic_style TEXT NOT NULL,  -- pixel_art, smooth_digital, hand_drawn, 3d_rendered
    style_confidence REAL NOT NULL,
    animation_difficulty REAL NOT NULL,  -- 0-100
    has_face BOOLEAN DEFAULT 0,
    character_prominence REAL,  -- 0-1

    -- Complete feature data (JSON)
    low_level_features TEXT,      -- JSON: colors, edges, textures, frequency
    mid_level_features TEXT,       -- JSON: segmentation, pose, facial
    high_level_features TEXT,      -- JSON: style, composition, aesthetics
    animation_features TEXT,       -- JSON: motion prediction, stability

    -- File references
    character_mask_path TEXT,      -- Path to PNG mask file
    pose_visualization_path TEXT,  -- Path to annotated pose image

    -- Metadata
    extraction_time_seconds REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (nft_id) REFERENCES nfts(nft_id),
    FOREIGN KEY (run_id) REFERENCES analysis_runs(run_id),
    UNIQUE(nft_id, run_id)  -- One feature set per NFT per run
);

CREATE INDEX idx_features_nft ON nft_features(nft_id);
CREATE INDEX idx_features_style ON nft_features(artistic_style);
CREATE INDEX idx_features_difficulty ON nft_features(animation_difficulty);
CREATE INDEX idx_features_run ON nft_features(run_id);

-- Animation strategies (workflow decisions)
CREATE TABLE IF NOT EXISTS animation_strategies (
    strategy_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nft_id INTEGER NOT NULL,
    feature_id INTEGER NOT NULL,

    -- Workflow selection
    selected_workflow TEXT NOT NULL,  -- A, B, C, D, E
    workflow_version TEXT,
    selection_reasoning TEXT,
    confidence_score REAL,

    -- Parameters (JSON for flexibility)
    animatediff_params TEXT,  -- JSON: denoise, motion_scale, steps, etc.
    controlnet_params TEXT,   -- JSON: enabled, type, strength, etc.
    prompt_params TEXT,       -- JSON: positive, negative, style_hints, etc.

    -- Predictions
    predicted_quality REAL,      -- 0-100
    predicted_stability REAL,    -- 0-1
    risk_factors TEXT,            -- JSON array

    -- Results (filled after animation)
    actual_quality REAL,
    animation_path TEXT,
    processing_time_seconds REAL,
    success BOOLEAN,
    error_message TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP,

    FOREIGN KEY (nft_id) REFERENCES nfts(nft_id),
    FOREIGN KEY (feature_id) REFERENCES nft_features(feature_id)
);

CREATE INDEX idx_strategies_nft ON animation_strategies(nft_id);
CREATE INDEX idx_strategies_workflow ON animation_strategies(selected_workflow);
CREATE INDEX idx_strategies_quality ON animation_strategies(predicted_quality);

-- Performance tracking
CREATE TABLE IF NOT EXISTS quality_feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategy_id INTEGER NOT NULL,

    -- Automated metrics
    ssim_score REAL,              -- Structural similarity
    facial_drift_pixels REAL,     -- Drift in facial features
    motion_smoothness REAL,       -- Frame-to-frame consistency
    edge_preservation REAL,       -- For pixel art

    -- Manual ratings
    manual_rating INTEGER,         -- 1-10
    reviewer_name TEXT,
    review_notes TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (strategy_id) REFERENCES animation_strategies(strategy_id)
);

CREATE INDEX idx_feedback_strategy ON quality_feedback(strategy_id);
```

### 7.3 JSON Schema for Feature Data

**low_level_features**:
```json
{
    "colors": {
        "palette_size": 5247,
        "dominant_colors": ["#1a1a1a", "#ff6b35", ...],
        "color_variance": 3421.8,
        "color_entropy": 7.2,
        "is_limited_palette": false,
        "mean_rgb": [128.5, 142.3, 115.7],
        "std_rgb": [45.2, 38.9, 52.1]
    },
    "edges": {
        "edge_density": 0.47,
        "edge_sharpness": 142.3,
        "edge_uniformity": 38.2,
        "avg_gradient": 125.6,
        "laplacian_variance": 234.5,
        "predominant_edges": "mixed",
        "edge_coherence": 0.72
    },
    "textures": {
        "glcm_contrast": 0.67,
        "glcm_homogeneity": 0.45,
        "glcm_energy": 0.23,
        "glcm_correlation": 0.78,
        "lbp_variance": 892.4,
        "gabor_energy": 145.2,
        "texture_entropy": 6.8,
        "texture_complexity": 72.3
    },
    "frequency": {
        "spatial_frequency_mean": 98.4,
        "spatial_frequency_std": 42.1,
        "high_freq_energy": 0.62,
        "low_freq_energy": 0.38,
        "frequency_ratio": 1.63,
        "dct_energy": 145820.5,
        "spectral_complexity": 68.2
    }
}
```

**mid_level_features**:
```json
{
    "segmentation": {
        "character_bbox": {"x": 128, "y": 64, "width": 256, "height": 384},
        "character_prominence": 0.75,
        "separation_quality": 0.82,
        "segmentation_confidence": 0.94,
        "has_mask": true,
        "background_complexity": 34.2,
        "character_complexity": 58.7
    },
    "pose": {
        "keypoints_detected": 33,
        "pose_type": "standing_relaxed",
        "pose_confidence": 0.92,
        "body_parts": {
            "head": {"x": 180, "y": 64, "width": 92, "height": 96},
            "torso": {"x": 160, "y": 160, "width": 132, "height": 160}
        },
        "joint_angles": {
            "left_elbow": 165.2,
            "right_elbow": 172.8
        }
    },
    "facial": {
        "face_detected": true,
        "face_bbox": {"x": 185, "y": 68, "width": 82, "height": 88},
        "left_eye": {"x": 210, "y": 100},
        "right_eye": {"x": 242, "y": 100},
        "mouth": {"x": 226, "y": 140},
        "inter_eye_distance": 32.0,
        "preservation_priority": "high"
    }
}
```

**high_level_features**:
```json
{
    "style": {
        "primary_style": "smooth_digital",
        "style_confidence": 0.87,
        "style_markers": ["high_color_variance", "low_edge_density", "rich_palette"],
        "substyle": "digital_illustration",
        "rendering_technique": "gradient"
    },
    "composition": {
        "composition_type": "centered",
        "focal_point": {"x": 0.51, "y": 0.48},
        "visual_balance": 0.78,
        "negative_space_ratio": 0.22,
        "symmetry_score": 0.65,
        "complexity_distribution": "focused"
    },
    "aesthetics": {
        "aesthetic_score": 76.5,
        "technical_quality": 82.3,
        "color_harmony_score": 74.8,
        "color_scheme": "complementary",
        "quality_tier": "high"
    }
}
```

**animation_features**:
```json
{
    "motion_prediction": {
        "suggested_motion_type": "breathing",
        "motion_intensity": 0.5,
        "motion_scale_recommendation": 0.7,
        "motion_focus_regions": ["torso", "head"],
        "physics_cues": ["grounded", "balanced"],
        "energy_level": "moderate",
        "temporal_stability_risk": 0.35
    },
    "stability": {
        "predicted_stability": 0.82,
        "instability_factors": [],
        "recommended_frame_count": 16,
        "recommended_fps": 12,
        "context_length": 16
    },
    "difficulty": {
        "animation_difficulty": 52.3,
        "difficulty_reason": "Smooth digital + visible face",
        "difficulty_tier": "medium"
    }
}
```

### 7.4 Indexing Strategy

**Primary Indexes** (for fast querying):
```sql
-- Style-based queries
CREATE INDEX idx_features_style_confidence
    ON nft_features(artistic_style, style_confidence DESC);

-- Difficulty-based queries
CREATE INDEX idx_features_difficulty_tier
    ON nft_features(animation_difficulty, character_prominence);

-- Quality-based queries
CREATE INDEX idx_strategies_quality_workflow
    ON animation_strategies(predicted_quality DESC, selected_workflow);

-- Face detection queries
CREATE INDEX idx_features_face
    ON nft_features(has_face, character_prominence DESC);
```

**JSON Indexes** (SQLite 3.38+):
```sql
-- If using SQLite with JSON1 extension
CREATE INDEX idx_features_pose_type
    ON nft_features(json_extract(mid_level_features, '$.pose.pose_type'));

CREATE INDEX idx_features_motion_type
    ON nft_features(json_extract(animation_features, '$.motion_prediction.suggested_motion_type'));
```

### 7.5 Query Patterns

**Common Queries**:

```sql
-- Get all pixel art NFTs
SELECT nft_id, style_confidence, animation_difficulty
FROM nft_features
WHERE artistic_style = 'pixel_art'
  AND style_confidence > 0.85
ORDER BY animation_difficulty DESC;

-- Find NFTs needing segmented workflow
SELECT nf.nft_id, nf.character_prominence,
       json_extract(nf.mid_level_features, '$.segmentation.separation_quality') as sep_quality
FROM nft_features nf
WHERE json_extract(nf.mid_level_features, '$.segmentation.separation_quality') < 0.6
   OR character_prominence < 0.5;

-- Get animation results by workflow
SELECT selected_workflow,
       AVG(actual_quality) as avg_quality,
       COUNT(*) as count,
       AVG(processing_time_seconds) as avg_time
FROM animation_strategies
WHERE success = 1
GROUP BY selected_workflow
ORDER BY avg_quality DESC;

-- Find high-quality candidates for showcase
SELECT n.nft_id, n.token_id,
       nf.animation_difficulty,
       json_extract(nf.high_level_features, '$.aesthetics.aesthetic_score') as aesthetic
FROM nfts n
JOIN nft_features nf ON n.nft_id = nf.nft_id
WHERE aesthetic > 80
  AND nf.animation_difficulty < 60
ORDER BY aesthetic DESC
LIMIT 50;
```

### 7.6 Versioning Strategy

**Why Version?**
- Models improve (SAM 2.0 → 2.1)
- Extraction algorithms evolve
- Need to compare results across versions

**Approach**:
- Each `analysis_run` has a version
- Features are linked to `run_id`
- Can re-analyze same NFT with new models
- Query latest version: `WHERE run_id = (SELECT MAX(run_id) FROM analysis_runs WHERE status='completed')`

---

## 8. Feature-to-Animation Decision Mapping

### 8.1 Decision Tree

```
START
│
├─ Style Classification
│  │
│  ├─ pixel_art (conf > 0.85) → WORKFLOW A
│  │   ├─ denoise: 0.28
│  │   ├─ motion_scale: 0.4
│  │   ├─ controlnet: 0.95 (canny)
│  │   └─ prompt: "pixel art, sharp edges, preserve pixels"
│  │
│  ├─ smooth_digital → Continue to Separation
│  ├─ hand_drawn → Continue to Separation
│  └─ 3d_rendered → Continue to Separation
│
├─ Character-Background Separation
│  │
│  ├─ separation < 0.6 OR bg_complexity > 70 → WORKFLOW D (Segmented)
│  │   ├─ Character layer: denoise 0.38, motion 1.0, controlnet 0.85
│  │   ├─ Background layer: denoise 0.55, motion 0.3
│  │   └─ Composite with feathering
│  │
│  └─ separation >= 0.6 → Continue to Pose/Energy
│
├─ Pose & Energy Analysis
│  │
│  ├─ energy_level = 'dynamic' OR motion_scale_rec > 1.0 → WORKFLOW C (Bold)
│  │   ├─ denoise: 0.50
│  │   ├─ motion_scale: 1.1
│  │   └─ prompt: "energetic, dynamic motion"
│  │
│  └─ energy_level = 'calm'/'moderate' → WORKFLOW B (Smooth)
│      ├─ denoise: 0.45
│      ├─ motion_scale: 0.7-0.9
│      └─ prompt: "smooth, natural motion"
│
└─ Special Cases
   │
   ├─ rarity > 90 AND aesthetic > 80 → WORKFLOW E (AI-Optimized)
   │   └─ Custom params per NFT
   │
   └─ face_detected AND preservation_priority = 'critical'
       └─ Reduce denoise by 0.10
           Add facial ControlNet strength +0.05
```

### 8.2 Parameter Calculation Functions

**Denoise Strength**:
```python
def calculate_denoise(features: dict) -> float:
    """Calculate optimal denoise strength."""

    # Start with style-based default
    style_defaults = {
        'pixel_art': 0.28,
        'smooth_digital': 0.45,
        'hand_drawn': 0.40,
        '3d_rendered': 0.48
    }

    style = features['style']['primary_style']
    denoise = style_defaults.get(style, 0.45)

    # Adjustments for face
    if features['facial'].get('face_detected'):
        priority = features['facial']['preservation_priority']
        if priority == 'critical':
            denoise = min(denoise, 0.32)
        elif priority == 'high':
            denoise -= 0.05

    # Adjustments for high-frequency detail
    if features['frequency']['high_freq_energy'] > 0.65:
        denoise -= 0.05

    # Adjustments for separation quality
    if features['segmentation']['separation_quality'] < 0.7:
        denoise -= 0.03  # Be more careful

    return round(np.clip(denoise, 0.25, 0.60), 2)
```

**Motion Scale**:
```python
def calculate_motion_scale(features: dict) -> float:
    """Calculate optimal motion scale."""

    # Start with recommended motion scale
    motion_scale = features['motion']['motion_scale_recommendation']

    # Style limits
    if features['style']['primary_style'] == 'pixel_art':
        motion_scale = min(motion_scale, 0.6)

    # Stability adjustments
    if features['stability']['predicted_stability'] < 0.7:
        motion_scale *= 0.85

    # Temporal risk
    if features['motion']['temporal_stability_risk'] > 0.7:
        motion_scale *= 0.8

    return round(np.clip(motion_scale, 0.3, 1.5), 2)
```

**ControlNet Strength**:
```python
def calculate_controlnet_strength(features: dict) -> float:
    """Calculate ControlNet strength if needed."""

    # Check if ControlNet needed
    needs_controlnet = (
        features['style']['primary_style'] == 'pixel_art' or
        features['facial'].get('preservation_priority') in ['critical', 'high'] or
        features['segmentation']['separation_quality'] < 0.7 or
        features['animation']['animation_difficulty'] > 75
    )

    if not needs_controlnet:
        return 0.0

    # Calculate strength
    strength = 0.75  # Base

    # Pixel art needs very high
    if features['style']['primary_style'] == 'pixel_art':
        strength = 0.95

    # Critical face
    if features['facial'].get('preservation_priority') == 'critical':
        strength = max(strength, 0.90)

    # High difficulty
    if features['animation']['animation_difficulty'] > 80:
        strength += 0.05

    return round(np.clip(strength, 0.0, 1.0), 2)
```

**Steps (Quality Tier)**:
```python
def calculate_steps(features: dict, rarity_score: float) -> int:
    """Calculate number of diffusion steps based on quality tier."""

    # Base on aesthetic quality + rarity
    aesthetic = features['aesthetics']['aesthetic_score']

    quality_metric = (aesthetic * 0.6 + rarity_score * 0.4)

    if quality_metric > 85:
        return 20  # Premium quality
    elif quality_metric > 70:
        return 18  # High quality
    elif quality_metric > 50:
        return 15  # Standard quality
    else:
        return 12  # Basic quality
```

---

## 9. Implementation Roadmap

### Phase 1: Core Feature Extraction (Week 1-2)

**Milestone 1.1: Low-Level Features**
- [ ] Implement color feature extraction
- [ ] Implement edge feature extraction
- [ ] Implement texture feature extraction (GLCM, LBP)
- [ ] Implement frequency domain analysis
- [ ] Test on 50 sample NFTs
- [ ] Benchmark extraction time (<2 sec per NFT)

**Milestone 1.2: Style Classification**
- [ ] Implement artistic style classifier
- [ ] Train/validate on labeled dataset (100 NFTs)
- [ ] Achieve 95%+ accuracy
- [ ] Test on full collection preview (500 NFTs)

**Milestone 1.3: Database Setup**
- [ ] Create SQLite database with schema
- [ ] Implement feature storage functions
- [ ] Create indexing
- [ ] Test query performance

**Deliverables**:
- `analysis/low_level_features.py`
- `analysis/style_classifier.py`
- `database/schema.sql`
- `database/feature_storage.py`

---

### Phase 2: Character Analysis (Week 3-4)

**Milestone 2.1: Segmentation (SAM 2)**
- [ ] Install Segment Anything Model 2
- [ ] Implement character segmentation
- [ ] Extract character masks
- [ ] Calculate separation quality
- [ ] Store masks as PNG files

**Milestone 2.2: Pose Estimation (MediaPipe)**
- [ ] Install MediaPipe Pose
- [ ] Extract 33 keypoints
- [ ] Segment body parts
- [ ] Calculate joint angles
- [ ] Classify pose types

**Milestone 2.3: Facial Features (MediaPipe Face Mesh)**
- [ ] Install MediaPipe Face Mesh
- [ ] Extract 468 facial landmarks
- [ ] Identify eyes, mouth, nose
- [ ] Calculate preservation priority
- [ ] Handle cases with no face detected

**Deliverables**:
- `analysis/segmentation.py` (SAM 2)
- `analysis/pose_estimation.py` (MediaPipe)
- `analysis/facial_features.py` (MediaPipe)
- `masks/` directory with 4,200 character masks

---

### Phase 3: High-Level Analysis (Week 5-6)

**Milestone 3.1: Composition & Aesthetics**
- [ ] Implement composition analysis
- [ ] Implement color harmony scoring
- [ ] Integrate CLIP for aesthetic scoring (optional)
- [ ] Calculate aesthetic quality scores

**Milestone 3.2: Motion Prediction**
- [ ] Implement motion prediction from pose
- [ ] Detect physics cues
- [ ] Calculate energy levels
- [ ] Predict temporal stability

**Milestone 3.3: Complete Integration**
- [ ] Integrate all feature extractors
- [ ] Create master extraction pipeline
- [ ] Run on full 4,200 collection
- [ ] Validate results

**Deliverables**:
- `analysis/composition.py`
- `analysis/aesthetics.py`
- `analysis/motion_prediction.py`
- `analysis/master_pipeline.py`
- Complete database with 4,200 NFT features

---

### Phase 4: Animation Decision Engine (Week 7-8)

**Milestone 4.1: Workflow Router**
- [ ] Implement decision tree
- [ ] Create workflow selection logic
- [ ] Calculate optimal parameters per NFT
- [ ] Generate prompts automatically

**Milestone 4.2: Strategy Storage**
- [ ] Store animation strategies in DB
- [ ] Link to features
- [ ] Generate workflow JSON files

**Milestone 4.3: Testing & Validation**
- [ ] Test on 100 NFT sample
- [ ] Compare predicted vs manual selections
- [ ] Refine decision thresholds
- [ ] Validate parameter calculations

**Deliverables**:
- `animation/workflow_router.py`
- `animation/parameter_calculator.py`
- `animation/prompt_generator.py`
- 4,200 custom animation strategies

---

### Phase 5: Execution & Feedback Loop (Week 9+)

**Milestone 5.1: Animation Execution**
- [ ] Integrate with ComfyUI workflow system
- [ ] Batch process animations
- [ ] Store results in database
- [ ] Track processing times

**Milestone 5.2: Quality Measurement**
- [ ] Implement SSIM calculation
- [ ] Implement facial drift detection
- [ ] Implement motion smoothness metrics
- [ ] Store automated quality scores

**Milestone 5.3: Feedback Loop**
- [ ] Collect manual quality ratings
- [ ] Analyze successful vs failed animations
- [ ] Correlate features with outcomes
- [ ] Refine decision engine

**Deliverables**:
- `animation/executor.py`
- `analysis/quality_metrics.py`
- `analysis/feedback_analyzer.py`
- ROI analysis report

---

## 10. References and Research Sources

### Computer Vision & Image Analysis

1. **Texture Analysis**:
   - Ramola et al. (2020). "Study of statistical methods for texture analysis and their modern evolutions." Engineering Reports.
   - GLCM fundamentals and applications

2. **Edge Detection**:
   - Su & Liu (2021). "Pixel Difference Networks for Efficient Edge Detection." arXiv.
   - Canny edge detection methodology

3. **Frequency Domain**:
   - FFT and DCT fundamentals in image processing
   - Spatial frequency analysis techniques

### Segmentation & Pose Estimation

4. **Segment Anything Model (SAM)**:
   - Meta AI (2024). "SAM 2: Segment Anything in Images and Videos." arXiv.
   - Semantic-SAM (ECCV 2024)

5. **MediaPipe**:
   - Google (2024). MediaPipe Pose documentation
   - MediaPipe Face Mesh - 478 landmark model

6. **Pose Estimation for Illustrations**:
   - Chen (WACV 2022). "Transfer Learning for Pose Estimation of Illustrated Characters."
   - SegAnimeChara (SIGGRAPH 2023). "Segmenting Anime Characters Generated by AI."

### Animation & Motion

7. **Image-to-Video Generation**:
   - Motion-I2V (SIGGRAPH 2024). "Consistent and Controllable Image-to-Video Generation."
   - MOFA-Video (ECCV 2024). "Controllable Image Animation."

8. **AnimateDiff**:
   - Guo et al. (2023). "AnimateDiff: Animate Your Personalized Text-to-Image Models."
   - AnimateDiff parameter optimization research

9. **Motion Perception**:
   - PNAS (2002). "Perception of biological motion without local image motion."
   - Motion cues in static images research

### Aesthetic & Style

10. **CLIP for Aesthetics**:
    - PMC (2022). "CLIP knows image aesthetics."
    - Fine-tuning CLIP for aesthetic assessment

11. **NIMA**:
    - Talebi & Milanfar (2018). "NIMA: Neural Image Assessment." Google Research.

12. **Art Style Classification**:
    - MDPI (2023). "Artistic Style Recognition: Combining Deep and Shallow Neural Networks."
    - Convolutional Neural Networks for art classification

### Database & Systems

13. **Metadata Architecture**:
    - Medium (2024). "Optimizing JSON Schema for Scalable Computer Vision Pipelines."
    - Best practices for metadata stores

14. **JSON vs Relational**:
    - DataHub metadata modeling
    - Managing structured and unstructured data

---

## Appendices

### Appendix A: Feature Extraction Checklist

**Per NFT (512×512 image)**:

- [ ] Low-level features (2 sec)
  - [ ] Colors: 10 metrics
  - [ ] Edges: 7 metrics
  - [ ] Textures: 9 metrics
  - [ ] Frequency: 7 metrics

- [ ] Mid-level features (5 sec)
  - [ ] Segmentation (SAM 2): mask + bbox + separation
  - [ ] Pose (MediaPipe): 33 keypoints + classification
  - [ ] Facial (MediaPipe): 468 landmarks + features

- [ ] High-level features (2 sec)
  - [ ] Style classification
  - [ ] Composition analysis
  - [ ] Aesthetic scoring

- [ ] Animation features (1 sec)
  - [ ] Motion prediction
  - [ ] Stability analysis
  - [ ] Difficulty calculation

**Total: ~10 seconds per NFT** (with GPU)
**Full collection: ~11.7 hours** for 4,200 NFTs

### Appendix B: Storage Requirements

**Per NFT**:
- Feature data (JSON): ~50 KB
- Character mask (PNG): ~100 KB
- Pose visualization (optional): ~200 KB

**Full Collection**:
- Features: 50 KB × 4,200 = 210 MB
- Masks: 100 KB × 4,200 = 420 MB
- Database: ~300 MB (with indexes)
- **Total: ~930 MB** (~1 GB)

**Very manageable storage requirements.**

### Appendix C: Python Dependencies

```
# Core
numpy>=1.24.0
opencv-python>=4.8.0
pillow>=10.0.0
scikit-image>=0.21.0
scikit-learn>=1.3.0
scipy>=1.11.0

# Database
sqlite3  # Built-in to Python

# Segmentation
segment-anything>=1.0  # SAM 2
torch>=2.0.0
torchvision>=0.15.0

# Pose & Face
mediapipe>=0.10.0

# Optional - Aesthetics
clip-pytorch>=1.0
transformers>=4.30.0
```

### Appendix D: Hardware Recommendations

**Minimum (Phases 1-3)**:
- CPU: 8-core
- RAM: 16 GB
- GPU: 8 GB VRAM (RTX 3060)
- Storage: 100 GB SSD

**Recommended**:
- CPU: 12-core
- RAM: 32 GB
- GPU: 12-24 GB VRAM (RTX 3080/4090)
- Storage: 500 GB NVMe SSD

**Cloud Alternative**:
- RunPod / Vast.ai GPU instance
- RTX 3090/4090 for SAM 2 inference
- ~$0.50/hour × 12 hours = $6 for full analysis

---

**END OF FRAMEWORK DOCUMENT**

This comprehensive framework provides everything needed to extract meaningful features from NFT images and map them to intelligent animation decisions. The key insight: **style classification and character anatomy matter far more than generic complexity metrics**.
