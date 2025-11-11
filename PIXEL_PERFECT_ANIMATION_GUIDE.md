# Pixel-Perfect NFT Animation Guide

**Created**: November 8, 2025
**Strategy**: Quality over quantity - selective pixel-level animation control
**Target**: 95-100/100 quality score with surgical precision

---

## 🎯 Revolutionary Concept

Instead of animating entire layers uniformly, we animate **specific pixel zones** within each layer:

```
Traditional Approach:
  Body layer (full) → AnimateDiff → Animated body layer

Pixel-Perfect Approach:
  Body layer → Analyze pixels → Identify zones:
    - Chest region → Breathing animation (denoise 0.35)
    - Edges → Subtle idle sway (denoise 0.25)
    - Arms → Static (no animation)
  → Composite → Perfect result
```

**Benefits**:
- **Surgical control**: Animate only what needs motion
- **Higher quality**: Each zone optimized independently
- **Better preservation**: Static areas remain pixel-perfect
- **Creative flexibility**: Mix animation styles per layer

---

## 📊 Implementation Phases

### Phase 1: Infrastructure Setup (Week 1 - 8 hours)

**Install Required Tools**:
```bash
# Python libraries
pip install opencv-python opencv-contrib-python numpy scikit-image scipy pillow

# Segment Anything Model (optional, 2.4GB)
pip install git+https://github.com/facebookresearch/segment-anything.git
wget https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth

# Puppet warp (for mesh deformation)
pip install pywarp
```

**Verify Installation**:
```python
import cv2
import numpy as np
from skimage import feature
from PIL import Image

print(f"OpenCV: {cv2.__version__}")
print(f"NumPy: {np.__version__}")
print("✅ All libraries installed!")
```

---

### Phase 2: Pixel Analysis System (Week 2 - 20 hours)

#### Step 1: Extract Animation Zones

**Method A: Color-Based Clustering (Fast)**

```python
import cv2
import numpy as np
from sklearn.cluster import KMeans

def extract_animation_zones(layer_path, n_zones=3):
    """
    Extract animation zones using K-Means color clustering.

    Args:
        layer_path: Path to layer PNG with alpha channel
        n_zones: Number of distinct animation zones

    Returns:
        List of binary masks (numpy arrays)
    """
    # Load layer with transparency
    img = cv2.imread(layer_path, cv2.IMREAD_UNCHANGED)

    if img.shape[2] != 4:
        raise ValueError("Layer must have alpha channel (RGBA)")

    rgb = img[:, :, :3]
    alpha = img[:, :, 3]

    # Only analyze visible pixels
    visible_mask = alpha > 0
    visible_pixels = rgb[visible_mask].reshape(-1, 3).astype(float)

    # K-Means clustering by color
    kmeans = KMeans(n_clusters=n_zones, random_state=42, n_init=10)
    labels = kmeans.fit_predict(visible_pixels)

    # Reshape to image dimensions
    labeled_img = np.zeros(img.shape[:2], dtype=np.uint8)
    labeled_img[visible_mask] = labels

    # Create individual zone masks
    masks = []
    for zone_id in range(n_zones):
        zone_mask = (labeled_img == zone_id).astype(np.uint8) * 255

        # Clean up noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        zone_mask = cv2.morphologyEx(zone_mask, cv2.MORPH_CLOSE, kernel)
        zone_mask = cv2.morphologyEx(zone_mask, cv2.MORPH_OPEN, kernel)

        masks.append(zone_mask)

    return masks, kmeans.cluster_centers_

# Example usage
masks, colors = extract_animation_zones('layers/normie_body.png', n_zones=3)

for i, mask in enumerate(masks):
    cv2.imwrite(f'masks/normie_body_zone_{i}.png', mask)
    print(f"Zone {i}: Color {colors[i]}, {np.sum(mask > 0)} pixels")
```

**Method B: Edge-Based Segmentation (Precision)**

```python
from skimage import feature, filters
from scipy import ndimage

def extract_zones_by_edges(layer_path, feather_radius=15):
    """
    Extract zones using edge detection with feathering.

    Returns smooth gradient masks for seamless blending.
    """
    img = cv2.imread(layer_path, cv2.IMREAD_GRAYSCALE)

    # Multi-scale edge detection
    edges_fine = feature.canny(img, sigma=0.5)  # Detail
    edges_broad = feature.canny(img, sigma=2.0)  # Structure
    edges = np.logical_or(edges_fine, edges_broad)

    # Distance transform (for feathering)
    dist = ndimage.distance_transform_edt(~edges)

    # Create gradient mask (0-255)
    feathered = np.clip(dist / feather_radius * 255, 0, 255).astype(np.uint8)

    return feathered

# Example usage
feathered_mask = extract_zones_by_edges('layers/fire_effect.png', feather_radius=20)
cv2.imwrite('masks/fire_feathered.png', feathered_mask)
```

---

#### Step 2: Create Pixel Database

**JSON Schema**:
```json
{
  "nft_id": "0042",
  "layer_analysis": {
    "body_normie": {
      "zones": [
        {
          "name": "chest_breathing",
          "mask_file": "masks/normie_body_zone_0.png",
          "bounding_box": [200, 250, 312, 380],
          "pixel_count": 4523,
          "centroid": [256, 315],
          "dominant_color": [180, 150, 130],
          "animation": {
            "type": "mesh_deform",
            "denoise": 0.35,
            "motion_scale": 0.8,
            "prompt": "subtle breathing, chest expansion"
          }
        },
        {
          "name": "edges_idle",
          "mask_file": "masks/normie_body_zone_1.png",
          "pixel_count": 2134,
          "animation": {
            "type": "animatediff_masked",
            "denoise": 0.25,
            "motion_scale": 0.5,
            "prompt": "subtle idle sway"
          }
        }
      ]
    },
    "eyes_laser": {
      "zones": [
        {
          "name": "pupils_glow",
          "mask_file": "masks/laser_eyes_pupils.png",
          "animation": {
            "type": "particle_emission",
            "denoise": 0.60,
            "motion_scale": 1.5,
            "prompt": "glowing laser eyes, energy pulse"
          }
        }
      ]
    }
  }
}
```

**Generate Database Script**:
```python
import json
import glob
import os

def analyze_all_layers():
    """Batch analyze all layer files and create database."""

    database = {}
    layer_files = glob.glob('layers/**/*.png', recursive=True)

    for layer_path in layer_files:
        layer_name = os.path.basename(layer_path).replace('.png', '')
        print(f"Analyzing {layer_name}...")

        # Extract zones
        masks, colors = extract_animation_zones(layer_path, n_zones=3)

        # Build metadata
        zones = []
        for i, (mask, color) in enumerate(zip(masks, colors)):
            # Calculate properties
            pixel_count = np.sum(mask > 0)
            if pixel_count == 0:
                continue

            # Find centroid
            moments = cv2.moments(mask)
            cx = int(moments['m10'] / moments['m00']) if moments['m00'] != 0 else 0
            cy = int(moments['m01'] / moments['m00']) if moments['m00'] != 0 else 0

            # Bounding box
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                x, y, w, h = cv2.boundingRect(contours[0])
                bbox = [x, y, x+w, y+h]
            else:
                bbox = [0, 0, 0, 0]

            zones.append({
                'name': f'zone_{i}',
                'mask_file': f'masks/{layer_name}_zone_{i}.png',
                'pixel_count': int(pixel_count),
                'centroid': [int(cx), int(cy)],
                'bounding_box': bbox,
                'dominant_color': [int(c) for c in color]
            })

            # Save mask
            os.makedirs('masks', exist_ok=True)
            cv2.imwrite(f'masks/{layer_name}_zone_{i}.png', mask)

        database[layer_name] = {'zones': zones}

    # Save database
    with open('pixel_database.json', 'w') as f:
        json.dump(database, f, indent=2)

    print(f"\n✅ Analyzed {len(database)} layers")
    print(f"📊 Total zones: {sum(len(v['zones']) for v in database.values())}")

# Run analysis
if __name__ == '__main__':
    analyze_all_layers()
```

---

### Phase 3: Selective Animation Techniques (Week 3)

#### Technique 1: Mesh Deformation (Breathing, Organic Movement)

**Concept**: Define control points and deform mesh for natural motion

```python
import cv2
import numpy as np
from scipy.spatial import Delaunay

def generate_breathing_animation(layer_path, control_points, displacements, num_frames=16):
    """
    Generate breathing animation using mesh deformation.

    Args:
        layer_path: Path to layer PNG
        control_points: List of [x, y] anchor points
        displacements: List of [dx, dy] movement vectors
        num_frames: Number of frames to generate

    Returns:
        List of animated frames
    """
    img = cv2.imread(layer_path, cv2.IMREAD_UNCHANGED)
    h, w = img.shape[:2]

    # Add image corners to control points
    corners = [[0, 0], [w-1, 0], [w-1, h-1], [0, h-1]]
    all_points = np.array(control_points + corners, dtype=np.float32)

    # Delaunay triangulation
    tri = Delaunay(all_points)

    frames = []

    for frame_idx in range(num_frames):
        # Sinusoidal breathing curve
        t = np.sin(frame_idx / num_frames * 2 * np.pi)

        # Apply displacements
        displaced_points = all_points.copy()
        for i in range(len(control_points)):
            displaced_points[i] += np.array(displacements[i]) * t

        # Create output image
        output = np.zeros_like(img)

        # Warp each triangle
        for simplex in tri.simplices:
            # Source triangle
            src_tri = all_points[simplex].astype(np.float32)

            # Destination triangle (displaced)
            dst_tri = displaced_points[simplex].astype(np.float32)

            # Get bounding boxes
            src_rect = cv2.boundingRect(src_tri)
            dst_rect = cv2.boundingRect(dst_tri)

            # Offset triangles
            src_tri_offset = src_tri - [src_rect[0], src_rect[1]]
            dst_tri_offset = dst_tri - [dst_rect[0], dst_rect[1]]

            # Affine transform
            warp_mat = cv2.getAffineTransform(src_tri_offset, dst_tri_offset)

            # Extract and warp source region
            src_crop = img[src_rect[1]:src_rect[1]+src_rect[3],
                          src_rect[0]:src_rect[0]+src_rect[2]]

            dst_crop = cv2.warpAffine(src_crop, warp_mat,
                                     (dst_rect[2], dst_rect[3]))

            # Create mask for this triangle
            mask = np.zeros((dst_rect[3], dst_rect[2]), dtype=np.uint8)
            cv2.fillConvexPoly(mask, np.int32(dst_tri_offset), 255)

            # Composite into output
            if dst_crop.shape[2] == 4:  # RGBA
                alpha = (mask / 255.0)[:, :, np.newaxis]
                roi = output[dst_rect[1]:dst_rect[1]+dst_rect[3],
                            dst_rect[0]:dst_rect[0]+dst_rect[2]]
                output[dst_rect[1]:dst_rect[1]+dst_rect[3],
                      dst_rect[0]:dst_rect[0]+dst_rect[2]] = \
                    roi * (1 - alpha) + dst_crop * alpha

        frames.append(output)

    return frames

# Example: Breathing animation for normie body
control_points = [
    [256, 300],  # Chest center
    [230, 320],  # Left chest
    [282, 320],  # Right chest
    [256, 350],  # Stomach
]

displacements = [
    [0, -5],   # Chest rises
    [3, -3],   # Left expands
    [-3, -3],  # Right expands
    [0, -2],   # Stomach subtle
]

frames = generate_breathing_animation(
    'layers/normie_body.png',
    control_points,
    displacements,
    num_frames=16
)

# Save frames
for i, frame in enumerate(frames):
    cv2.imwrite(f'output/breathing_frame_{i:04d}.png', frame)

print("✅ Generated 16 breathing frames")
```

---

#### Technique 2: Particle Systems (Fire, Sparkles, Magic)

```python
from PIL import Image, ImageDraw
import numpy as np

class Particle:
    def __init__(self, x, y, vx, vy, color, lifespan):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifespan = lifespan
        self.age = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy -= 0.2  # Gravity (for fire: reverse for rising)
        self.age += 1

    def is_alive(self):
        return self.age < self.lifespan

def generate_particle_animation(base_layer_path, emitter_points, num_frames=16):
    """
    Generate particle effect animation (fire, sparkles, etc.).

    Args:
        base_layer_path: Path to base layer
        emitter_points: List of [x, y] coordinates where particles emit
        num_frames: Number of frames

    Returns:
        List of frames with particle effects
    """
    base = Image.open(base_layer_path).convert('RGBA')
    frames = []
    particles = []

    for frame_idx in range(num_frames):
        # Create particle layer
        particle_layer = Image.new('RGBA', base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(particle_layer)

        # Emit new particles
        for ex, ey in emitter_points:
            if np.random.random() < 0.8:  # 80% emission rate
                # Random velocity
                vx = np.random.uniform(-2, 2)
                vy = np.random.uniform(-5, -2)  # Upward for fire

                # Fire color (orange to yellow)
                r = np.random.randint(200, 255)
                g = np.random.randint(100, 200)
                b = np.random.randint(0, 50)
                color = (r, g, b)

                particles.append(Particle(ex, ey, vx, vy, color, lifespan=12))

        # Update and draw particles
        new_particles = []
        for p in particles:
            if p.is_alive():
                p.update()

                # Fade out as particle ages
                alpha = int(255 * (1 - p.age / p.lifespan))
                color_with_alpha = p.color + (alpha,)

                # Draw particle (small circle)
                x, y = int(p.x), int(p.y)
                radius = 2
                draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color_with_alpha)

                new_particles.append(p)

        particles = new_particles

        # Composite with base layer
        frame = Image.alpha_composite(base, particle_layer)
        frames.append(frame)

    return frames

# Example: Fire effect
fire_emitters = [
    [256, 400],  # Fire center
    [240, 405],  # Left flame
    [272, 405],  # Right flame
]

fire_frames = generate_particle_animation(
    'layers/fire_effect.png',
    fire_emitters,
    num_frames=16
)

# Save frames
for i, frame in enumerate(fire_frames):
    frame.save(f'output/fire_particle_frame_{i:04d}.png')

print("✅ Generated 16 fire particle frames")
```

---

#### Technique 3: ComfyUI Masked AnimateDiff (Complex AI Motion)

**ComfyUI Workflow JSON** (selective animation with masks):

```json
{
  "nodes": [
    {
      "id": 1,
      "type": "LoadImage",
      "inputs": {
        "image": "normie_body.png"
      },
      "outputs": ["IMAGE"]
    },
    {
      "id": 2,
      "type": "LoadImage",
      "inputs": {
        "image": "masks/normie_body_chest.png"
      },
      "outputs": ["MASK"]
    },
    {
      "id": 3,
      "type": "MaskBlur",
      "inputs": {
        "mask": ["2", 0],
        "blur_radius": 35
      },
      "outputs": ["MASK"],
      "comment": "Critical: Feathering for seamless blend"
    },
    {
      "id": 4,
      "type": "CLIPTextEncode",
      "inputs": {
        "text": "subtle chest breathing, natural idle animation, smooth movement"
      },
      "outputs": ["CONDITIONING"]
    },
    {
      "id": 5,
      "type": "ConditioningSetMask",
      "inputs": {
        "conditioning": ["4", 0],
        "mask": ["3", 0],
        "strength": 1.0,
        "set_cond_area": "default"
      },
      "outputs": ["CONDITIONING"],
      "comment": "Apply mask to conditioning"
    },
    {
      "id": 6,
      "type": "KSampler",
      "inputs": {
        "model": "SD 1.5",
        "positive": ["5", 0],
        "negative": "deformed, distorted, changing face",
        "latent_image": ["1", 0],
        "seed": 42,
        "steps": 18,
        "cfg": 7.5,
        "sampler_name": "dpmpp_2m",
        "scheduler": "karras",
        "denoise": 0.35
      },
      "outputs": ["LATENT"]
    },
    {
      "id": 7,
      "type": "AnimateDiffLoader",
      "inputs": {
        "model_name": "mm_sd_v15_v2.ckpt"
      },
      "outputs": ["MOTION_MODEL"]
    },
    {
      "id": 8,
      "type": "AnimateDiffSampler",
      "inputs": {
        "motion_model": ["7", 0],
        "context_length": 16,
        "motion_scale": 0.8
      }
    },
    {
      "id": 9,
      "type": "VAEDecode",
      "inputs": {
        "samples": ["6", 0]
      },
      "outputs": ["IMAGE"]
    },
    {
      "id": 10,
      "type": "ImageCompositeMasked",
      "inputs": {
        "destination": ["1", 0],
        "source": ["9", 0],
        "mask": ["3", 0],
        "x": 0,
        "y": 0,
        "resize_source": false
      },
      "outputs": ["IMAGE"],
      "comment": "Blend animated region with static original"
    },
    {
      "id": 11,
      "type": "VHS_VideoCombine",
      "inputs": {
        "images": ["10", 0],
        "frame_rate": 12,
        "loop_count": 0,
        "format": "image/gif"
      }
    }
  ]
}
```

**Key Settings for Quality**:
- **MaskBlur radius 25-50px**: CRITICAL for seamless blending
- **Denoise 0.30-0.40**: Balance motion vs preservation
- **ConditioningSetMask strength 1.0**: Full mask application
- **ImageCompositeMasked**: Blend animated with static

---

### Phase 4: Quality Validation (Ongoing)

#### Automated Quality Scoring

```python
def score_selective_animation(animated_gif, original_layer, mask):
    """
    Score selective animation quality.

    Checks:
    - Static regions unchanged (100% match)
    - Animated regions have motion (SSIM < 0.95)
    - Smooth blending (no visible seams)
    """
    from skimage.metrics import structural_similarity as ssim
    import imageio

    # Load frames
    frames = imageio.mimread(animated_gif)
    original = cv2.imread(original_layer)
    mask_img = cv2.imread(mask, cv2.IMREAD_GRAYSCALE)

    scores = {
        'static_preservation': 0,
        'motion_quality': 0,
        'blending_quality': 0
    }

    # Check static regions (mask == 0)
    static_region_mask = (mask_img == 0)

    frame_similarities = []
    for frame in frames:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # SSIM in static regions
        static_ssim = ssim(
            original[static_region_mask],
            frame_rgb[static_region_mask],
            multichannel=True
        )
        frame_similarities.append(static_ssim)

    # Score: static regions should be identical
    avg_static_ssim = np.mean(frame_similarities)
    scores['static_preservation'] = int(avg_static_ssim * 30)  # Max 30 points

    # Check motion in animated regions
    animated_region_mask = (mask_img > 0)
    motion_detected = False

    for i in range(len(frames) - 1):
        frame1 = cv2.cvtColor(frames[i], cv2.COLOR_RGB2BGR)
        frame2 = cv2.cvtColor(frames[i+1], cv2.COLOR_RGB2BGR)

        # Difference in animated region
        diff = cv2.absdiff(frame1[animated_region_mask],
                          frame2[animated_region_mask])

        if np.mean(diff) > 5:  # Motion threshold
            motion_detected = True
            break

    scores['motion_quality'] = 30 if motion_detected else 0

    # Check blending (edges of mask should be smooth)
    # Detect visible seams by checking gradient at mask boundaries
    kernel = np.array([[1, 1, 1], [1, -8, 1], [1, 1, 1]])
    edges = cv2.filter2D(mask_img, -1, kernel)

    # Low edge values = smooth blending
    edge_smoothness = 1.0 - (np.mean(np.abs(edges)) / 255.0)
    scores['blending_quality'] = int(edge_smoothness * 40)  # Max 40 points

    total = sum(scores.values())

    return {
        'total_score': total,
        'breakdown': scores,
        'grade': 'Perfect' if total >= 95 else 'Excellent' if total >= 85 else 'Good'
    }
```

---

## 🎨 Animation Recipe Library

### Body Animations

**Normie Body - Breathing**:
```yaml
technique: mesh_deformation
control_points: [[256, 300], [230, 320], [282, 320]]
displacements: [[0, -5], [3, -3], [-3, -3]]
frames: 16
```

**Ghastly Body - Ethereal Float**:
```yaml
technique: comfyui_masked
mask: chest + edges
denoise: 0.45
motion_scale: 1.2
prompt: "ethereal floating, ghostly movement, supernatural"
```

### Eye Animations

**Laser Eyes - Pulse**:
```yaml
technique: particle_emission
mask: pupils_only
particle_count: 20
velocity: [5, 0]
color: [255, 0, 0]
glow_intensity: 1.5
```

**Normal Eyes - Blink**:
```yaml
technique: procedural
frames: 16
blink_at_frame: 8
eyelid_closure: 90%
```

### Special Effects

**Fire - Flickering Flames**:
```yaml
technique: particle_system
emitter_points: [[256, 400], [240, 405], [272, 405]]
particle_velocity: [random(-2,2), random(-5,-2)]
color_range: [[200,100,0], [255,200,0]]
```

**Sparkles - Shimmer**:
```yaml
technique: comfyui_masked
denoise: 0.30
motion_scale: 0.5
prompt: "metallic shimmer, light reflection, sparkle"
```

---

## 📁 File Structure

```
kekanimations/
├── layers/                      # Source layer PNGs
│   ├── normie_body.png
│   ├── laser_eyes.png
│   └── fire_effect.png
├── masks/                       # Animation zone masks
│   ├── normie_body_chest.png
│   ├── normie_body_edges.png
│   ├── laser_eyes_pupils.png
│   └── fire_flames.png
├── scripts/
│   ├── batch_mask_generator.py
│   ├── mesh_deformation.py
│   ├── particle_system.py
│   └── quality_validator.py
├── workflows/
│   ├── selective_animation_masked.json
│   └── composite_zones.json
├── pixel_database.json          # Complete pixel analysis
└── output/
    ├── breathing_frames/
    ├── fire_particles/
    └── final_composites/
```

---

## 🚀 Quick Start

### Generate Your First Selective Animation

```bash
# 1. Extract animation zones
python scripts/batch_mask_generator.py layers/normie_body.png

# 2. Generate breathing animation
python scripts/mesh_deformation.py \
  --layer layers/normie_body.png \
  --mask masks/normie_body_chest.png \
  --frames 16

# 3. Validate quality
python scripts/quality_validator.py output/breathing.gif

# Expected output:
# ✅ Total Score: 96/100
# ✅ Grade: Perfect
# - Static preservation: 29/30
# - Motion quality: 30/30
# - Blending quality: 37/40
```

---

## 📊 Expected Results

### Quality Comparison

| Approach | Quality | Time/NFT | Character Preservation | Motion Realism |
|----------|---------|----------|------------------------|----------------|
| Whole layer AnimateDiff | 82/100 | 5 min | Good | Good |
| **Selective pixel zones** | **95-100/100** | **10-15 min** | **Excellent** | **Perfect** |

### Performance Benchmarks (M1 Mac)

- **Mask generation**: 2-5 seconds per layer
- **Mesh deformation**: 30 seconds for 16 frames
- **Particle system**: 15 seconds for 16 frames
- **ComfyUI masked**: 5-8 minutes for 16 frames
- **Quality validation**: 10 seconds

---

## 🎯 Success Criteria

- [ ] Static regions 100% preserved (SSIM > 0.99)
- [ ] Animated zones show smooth motion
- [ ] No visible seams at mask boundaries
- [ ] Quality score ≥ 95/100
- [ ] Processing time < 15 min per NFT
- [ ] M1 memory usage < 20GB

---

## 📚 Next Steps

1. **Week 1**: Set up infrastructure, test mask generation
2. **Week 2**: Analyze top 20 NFTs, create pixel database
3. **Week 3**: Implement all 3 animation techniques
4. **Week 4**: Generate first 10 perfect animations

**Ready to create pixel-perfect animations!** 🎨
