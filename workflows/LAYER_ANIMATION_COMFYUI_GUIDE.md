# ComfyUI Workflow Guide: Layer-Based NFT Animation

**Purpose**: Animate individual layer PNG files while preserving transparency for later recombination

**Critical Requirement**: Transparency MUST be preserved through the animation process

---

## Workflow Overview

```
Input: Single layer PNG (2048×2048 RGBA with transparency)
    ↓
AnimateDiff + ControlNet (preserve structure)
    ↓
Output: 16-frame animated sequence (PNG sequence or video)
    ↓
Recombine: Stack animated layers per NFT metadata
    ↓
Final: Animated NFT GIF (512×512 or 1024×1024)
```

---

## ComfyUI Setup Requirements

### Required Models

1. **Stable Diffusion 1.5** checkpoint
   - `runwayml/stable-diffusion-v1-5` or similar
   - Trained on illustrations (not photorealistic)

2. **AnimateDiff Motion Module**
   - `mm_sd_v15_v3.ckpt` (1.67 GB) - RECOMMENDED
   - Download: https://huggingface.co/guoyww/animatediff/

3. **ControlNet Models**
   - `control_v11p_sd15_canny.pth` (1.45 GB) - For edge preservation
   - Alternative: `control_v11f1p_sd15_depth.pth` - For depth-based control

4. **VAE**
   - `vae-ft-mse-840000-ema-pruned.safetensors` (optional, improves quality)

### Required Custom Nodes

1. **ComfyUI-AnimateDiff-Evolved** (Kosinkadink)
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved
   cd ComfyUI-AnimateDiff-Evolved && pip install -r requirements.txt
   ```

2. **ComfyUI-VideoHelperSuite** (Kosinkadink)
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite
   cd ComfyUI-VideoHelperSuite && pip install -r requirements.txt
   ```

3. **ComfyUI-Advanced-ControlNet**
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet
   ```

---

## Critical: Preserving Transparency

### Challenge

AnimateDiff and Stable Diffusion **do not natively support transparency**. The VAE encoder expects RGB images and will fill transparent areas with black or artifacts.

### Solutions

#### **Option A: Mask-Based Approach (RECOMMENDED)**

1. **Before Animation**:
   - Extract alpha channel from layer PNG → save as mask
   - Create RGB version of layer (alpha → white or black background)

2. **Animate RGB version** through AnimateDiff

3. **After Animation**:
   - Apply original alpha mask to each frame
   - Result: Animated layer with transparency restored

#### **Option B: Segmentation Approach**

1. Load layer with transparency
2. Use SAM 2 or similar to detect foreground
3. Animate foreground only
4. Composite back with transparent background

#### **Option C: Inpainting Approach**

1. Identify transparent regions
2. Use inpainting to generate background fill
3. Animate full image
4. Remove background using original alpha mask

**VERDICT**: **Option A is fastest and most reliable** for our use case.

---

## Workflow Node Configuration

### Basic Layer Animation Workflow

```
┌─────────────┐
│  Load Image │ (Single layer PNG)
└──────┬──────┘
       │
   ┌───▼────────────┐
   │ Split RGBA     │ (Separate alpha channel)
   │ - RGB → Animate│
   │ - A → Save mask│
   └───┬────────────┘
       │
   ┌───▼───────────────┐
   │ Encode RGB to     │
   │ Latent (VAE)      │
   └───┬───────────────┘
       │
   ┌───▼──────────────────┐
   │ AnimateDiff Module   │
   │ - Motion model       │
   │ - Context: 16 frames │
   │ - Closed loop: True  │
   └───┬──────────────────┘
       │
   ┌───▼──────────────────┐
   │ KSampler             │
   │ - Denoise: 0.30-0.45 │
   │ - Steps: 15-20       │
   │ - CFG: 7.0           │
   └───┬──────────────────┘
       │
   ┌───▼──────────────────┐
   │ ControlNet (Canny)   │
   │ - Strength: 0.85-0.95│
   │ - Preserve edges     │
   └───┬──────────────────┘
       │
   ┌───▼──────────────────┐
   │ VAE Decode           │
   │ (Latent → RGB)       │
   └───┬──────────────────┘
       │
   ┌───▼──────────────────┐
   │ Apply Alpha Mask     │
   │ (Restore transparency)│
   └───┬──────────────────┘
       │
   ┌───▼──────────────────┐
   │ Save PNG Sequence    │
   │ (16 frames)          │
   └──────────────────────┘
```

### Layer-Specific Parameters

#### **Body Animation**

```python
{
    "denoise": 0.35,
    "steps": 18,
    "cfg_scale": 7.0,
    "motion_scale": 0.4,  # Subtle breathing
    "controlnet_strength": 0.85,
    "positive_prompt": "character breathing, subtle idle animation, smooth motion",
    "negative_prompt": "distortion, morphing, color change, artifacts, dissolving"
}
```

#### **Eyes Animation**

```python
{
    "denoise": 0.30,
    "steps": 15,
    "cfg_scale": 7.5,
    "motion_scale": 0.6,  # More pronounced
    "controlnet_strength": 0.90,
    "positive_prompt": "blinking eyes, natural eye movement, smooth eyelids",
    "negative_prompt": "distortion, face morphing, color shift, extra eyes"
}
```

#### **Hat/Accessory Animation**

```python
{
    "denoise": 0.40,
    "steps": 15,
    "cfg_scale": 7.0,
    "motion_scale": 0.8,  # Bouncy physics
    "controlnet_strength": 0.80,
    "positive_prompt": "gentle bouncing motion, physics-based movement",
    "negative_prompt": "distortion, morphing, dissolving, artifacts"
}
```

#### **Background Animation** (Selective)

```python
{
    "denoise": 0.45,
    "steps": 15,
    "cfg_scale": 6.5,
    "motion_scale": 0.3,  # Minimal
    "controlnet_strength": 0.70,
    "positive_prompt": "subtle atmospheric movement, gentle parallax, {style_specific}",
    "negative_prompt": "distortion, major changes, character appearance"
}
```

---

## Step-by-Step: Animating a Single Layer

### 1. Prepare Layer

```python
from PIL import Image
import numpy as np

# Load layer
layer = Image.open("body/normie.png")

# Split RGBA
rgb = layer.convert("RGB")
alpha = layer.split()[3]  # Alpha channel

# Save RGB for ComfyUI
rgb.save("temp/normie_rgb.png")

# Save alpha mask for later
alpha.save("temp/normie_alpha.png")
```

### 2. Load in ComfyUI

- Use **Load Image** node
- Input: `temp/normie_rgb.png`

### 3. Set Up ControlNet

- **ControlNet Preprocessor**: Canny Edge Detection
  - `low_threshold`: 100
  - `high_threshold`: 200
  - `resolution`: 2048

- **ControlNet Apply**:
  - `strength`: 0.85
  - `start_percent`: 0.0
  - `end_percent`: 1.0

### 4. Configure AnimateDiff

- **Context Options**:
  - `context_length`: 16
  - `context_overlap`: 4
  - `closed_loop`: True

- **Motion Model**:
  - Model: `mm_sd_v15_v3.ckpt`
  - `motion_scale`: 0.4 (breathing), 0.6 (eyes), 0.8 (accessories)

### 5. KSampler Settings

```
seed: Random (or fixed for consistency)
steps: 18
cfg: 7.0
sampler_name: dpmpp_2m
scheduler: karras
denoise: 0.35 (body), 0.30 (eyes), 0.40 (accessories)
```

### 6. Generate Frames

- Output: 16 PNG frames (numbered 0-15)
- Resolution: 2048×2048 RGB

### 7. Restore Transparency (Python)

```python
from PIL import Image
import glob

# Load alpha mask
alpha_mask = Image.open("temp/normie_alpha.png")

# Process each frame
for frame_path in sorted(glob.glob("output/normie_frame_*.png")):
    frame = Image.open(frame_path)

    # Combine RGB frame with original alpha
    frame_rgba = frame.convert("RGBA")
    frame_rgba.putalpha(alpha_mask)

    # Save with transparency
    frame_rgba.save(frame_path.replace(".png", "_alpha.png"))
```

---

## Batch Processing Script

```python
#!/usr/bin/env python3
"""
Batch animate all unique layers
"""

import os
from pathlib import Path
from PIL import Image

LAYER_FOLDERS = [
    "body", "eyes", "hat", "glasses", "tools", "special",
    "background", "clothes", "tattoo", "style"
]

ANIMATION_PARAMS = {
    "body": {"denoise": 0.35, "motion": 0.4, "steps": 18},
    "eyes": {"denoise": 0.30, "motion": 0.6, "steps": 15},
    "hat": {"denoise": 0.40, "motion": 0.8, "steps": 15},
    # ... etc
}

def prepare_layer_for_comfyui(layer_path):
    """Extract RGB and alpha for ComfyUI processing"""
    layer = Image.open(layer_path)

    rgb = layer.convert("RGB")
    alpha = layer.split()[3] if layer.mode == "RGBA" else None

    layer_name = layer_path.stem
    rgb.save(f"temp/{layer_name}_rgb.png")

    if alpha:
        alpha.save(f"temp/{layer_name}_alpha.png")

    return rgb, alpha

def process_all_layers():
    """Prepare all 104 layers for ComfyUI batch processing"""
    base_path = Path("/Users/seman/desktop-transfer/randomizer")

    for folder in LAYER_FOLDERS:
        folder_path = base_path / folder

        if not folder_path.exists():
            continue

        for layer_file in folder_path.glob("*.png"):
            print(f"Preparing: {folder}/{layer_file.name}")
            prepare_layer_for_comfyui(layer_file)

if __name__ == "__main__":
    process_all_layers()
```

---

## Quality Validation

### Checklist Per Animated Layer

- [ ] Transparency preserved (alpha mask intact)
- [ ] No color bleeding or artifacts
- [ ] Motion is smooth and natural
- [ ] Edges remain sharp (ControlNet working)
- [ ] Animation loops seamlessly (frame 0 = frame 16)
- [ ] Character identity preserved
- [ ] File size reasonable (~100-200 MB per animation)

---

## Troubleshooting

### Issue: Black/White Background Instead of Transparency

**Cause**: Alpha channel not properly restored

**Solution**:
1. Verify alpha mask was saved correctly
2. Check `Image.putalpha()` is being called
3. Ensure output format is PNG (not JPG)

### Issue: Character Morphing/Distortion

**Cause**: Denoise too high or ControlNet too weak

**Solution**:
1. Reduce denoise (try 0.25-0.30)
2. Increase ControlNet strength (0.90-0.95)
3. Increase CFG scale (8.0-9.0)

### Issue: Animation Too Subtle/Static

**Cause**: Motion scale too low or denoise too low

**Solution**:
1. Increase motion_scale (0.6-1.0)
2. Increase denoise slightly (0.40-0.45)
3. Adjust positive prompt (add "dynamic", "energetic")

### Issue: Animation Not Looping Smoothly

**Cause**: `closed_loop` not enabled

**Solution**:
1. Enable `closed_loop: True` in AnimateDiff Context Options
2. Verify frame count is multiple of context_length

---

## Next Steps

1. **Test single layer animation**:
   - Animate `body/normie.png`
   - Verify transparency preservation
   - Validate motion quality

2. **Create template workflows**:
   - Body animation template
   - Eyes animation template
   - Accessory animation template

3. **Batch process all layers**:
   - 6 body animations
   - 8 eye animations
   - 35+ total animation templates

4. **Build recombination pipeline**:
   - Load animated layers
   - Composite per NFT metadata
   - Export final GIFs

---

**Document Status**: Implementation ready
**Next Action**: Test single layer animation in ComfyUI
**Expected Time**: 30-60 minutes per animation template