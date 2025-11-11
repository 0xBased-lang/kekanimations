# Phase 1: ComfyUI Layer Animation Testing

**Goal**: Test single layer animation workflow to validate the approach before scaling to all 43 layer templates.

**Time**: ~1-2 hours
**Hardware**: M1 Mac with 24GB unified memory
**Status**: Ready to test

---

## Prerequisites

✅ ComfyUI installed at `~/Desktop/ComfyUI`
✅ PyTorch 2.9.0 with MPS support
✅ Models downloaded:
- ✅ Stable Diffusion 1.5 checkpoint
- ✅ AnimateDiff v2 motion model (mm_sd_v15_v2.ckpt)
- ✅ ControlNet Canny (control_v11p_sd15_canny.pth)
✅ Custom nodes:
- ✅ ComfyUI-AnimateDiff-Evolved
- ✅ ComfyUI-VideoHelperSuite

✅ Test layer prepared: `temp_normie_rgb.png` in ComfyUI input folder

---

## Step 1: Launch ComfyUI (5 minutes)

### Terminal Commands

```bash
cd ~/Desktop/ComfyUI
./launch_m1.sh
```

If `launch_m1.sh` doesn't exist, create it:

```bash
cat > launch_m1.sh << 'EOF'
#!/bin/bash
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
source venv/bin/activate
python main.py --force-fp16 --use-split-cross-attention --highvram --preview-method auto
EOF

chmod +x launch_m1.sh
./launch_m1.sh
```

### Expected Output

```
Starting server

To see the GUI go to: http://127.0.0.1:8188
```

### Open Browser

Navigate to: **http://127.0.0.1:8188**

---

## Step 2: Load Workflow (2 minutes)

### Import Workflow JSON

1. In ComfyUI web interface, click **"Load"** (top menu)
2. Navigate to: `/Users/seman/Desktop/kekanimations/workflows/layer_animation_workflow.json`
3. Click **"Open"**

**Alternative**: Click **"Load Default"** and manually recreate workflow using configuration below.

### Workflow Configuration

The workflow should have these nodes connected:

```
LoadImage → CannyEdgePreprocessor → ControlNetApply
         → VAEEncode

CheckpointLoader → AnimateDiffLoader → KSampler → VAEDecode → VideoCombine

CLIPTextEncode (positive) → ControlNetApply → KSampler
CLIPTextEncode (negative) → KSampler

VAELoader → VAEDecode
```

---

## Step 3: Configure Nodes (5 minutes)

### LoadImage Node

- **image**: `temp_normie_rgb.png`

### CheckpointLoaderSimple

- **ckpt_name**: `v1-5-pruned-emaonly.safetensors`

### CLIPTextEncode (Positive Prompt)

```
character breathing, subtle idle animation, smooth motion, high quality
```

**For different body types**:

- **normie**: `character breathing, subtle idle animation`
- **ghastly**: `ethereal ghost floating, supernatural glow, mysterious`
- **diablo**: `fire demon breathing, flames flickering, dark energy`
- **BasedAI**: `digital character, circuit glow, tech pulses`
- **RIP**: `ghost fading in and out, spectral, eerie`
- **x-ray**: `skeleton breathing, bones glowing, x-ray effect`

### CLIPTextEncode (Negative Prompt)

```
distortion, morphing, color change, artifacts, blurry, low quality
```

### ADE_AnimateDiffLoaderGen1

- **motion_model**: `mm_sd_v15_v2.ckpt`
- **beta_schedule**: `sqrt_linear (AnimateDiff)`
- **motion_scale**: `1.0`
- **context_length**: `16`
- **closed_loop**: `Enabled` (for seamless looping)

### ControlNetLoader

- **control_net_name**: `control_v11p_sd15_canny.pth`

### CannyEdgePreprocessor

- **low_threshold**: `100`
- **high_threshold**: `200`
- **resolution**: `2048`

### ControlNetApply

- **strength**: `0.85`

**Adjustment guide**:
- Higher (0.9-1.0): More character preservation, less animation
- Lower (0.6-0.7): More animation, risk of morphing

### VAEEncode

(No settings, just connects LoadImage → VAEEncode)

### KSampler

- **seed**: `randomize` (or fixed number for reproducibility)
- **steps**: `18`
- **cfg**: `7.0`
- **sampler_name**: `dpmpp_2m`
- **scheduler**: `karras`
- **denoise**: `0.35`

**Denoise adjustment guide**:
- Lower (0.25-0.30): Subtle animation, very close to original
- Medium (0.35-0.45): Balanced animation and preservation (recommended)
- Higher (0.50-0.60): More dramatic animation, risk of character changes

### VAELoader

- **vae_name**: `vae-ft-mse-840000-ema-pruned.safetensors`

(If not available, leave blank—ComfyUI will use default VAE from checkpoint)

### VAEDecode

(No settings, just connects KSampler → VAEDecode)

### VHS_VideoCombine

- **frame_rate**: `12`
- **loop_count**: `0` (infinite loop)
- **filename_prefix**: `normie_animation`
- **format**: `image/png`
- **save_output**: `true`

---

## Step 4: Generate Animation (3-5 minutes)

### Queue the Prompt

1. Click **"Queue Prompt"** (right sidebar)
2. Watch progress in web interface
3. Wait for completion (3-5 minutes on M1)

### Expected Progress

```
0% - Loading models
10% - Preprocessing with ControlNet
20-90% - Generating 16 frames with AnimateDiff
95% - Decoding frames
100% - Saving output
```

### Output Location

16 PNG frames saved in:
```
~/Desktop/ComfyUI/output/normie_animation_00001_00000.png
~/Desktop/ComfyUI/output/normie_animation_00001_00001.png
...
~/Desktop/ComfyUI/output/normie_animation_00001_00015.png
```

---

## Step 5: Restore Transparency (2 minutes)

### Python Script

```bash
cd /Users/seman/Desktop/kekanimations

python3 << 'EOF'
from PIL import Image
import glob
import os

# Load original alpha mask
alpha = Image.open("temp_normie_alpha.png")

# Find all generated frames
frame_pattern = os.path.expanduser("~/Desktop/ComfyUI/output/normie_animation_00001_*.png")
frames = sorted(glob.glob(frame_pattern))

print(f"Found {len(frames)} frames")

# Create output directory
os.makedirs("animated_frames", exist_ok=True)

# Restore alpha to each frame
for i, frame_path in enumerate(frames):
    # Load RGB frame
    frame = Image.open(frame_path)

    # Convert to RGBA
    frame_rgba = frame.convert("RGBA")

    # Restore original alpha
    frame_rgba.putalpha(alpha)

    # Save with transparency
    output_path = f"animated_frames/normie_{i:04d}.png"
    frame_rgba.save(output_path)

    print(f"✅ Frame {i}: {output_path}")

print(f"\n✅ All {len(frames)} frames with transparency restored")
print(f"Output: /Users/seman/Desktop/kekanimations/animated_frames/")
EOF
```

### Expected Output

```
Found 16 frames
✅ Frame 0: animated_frames/normie_0000.png
✅ Frame 1: animated_frames/normie_0001.png
...
✅ Frame 15: animated_frames/normie_0015.png

✅ All 16 frames with transparency restored
Output: /Users/seman/Desktop/kekanimations/animated_frames/
```

---

## Step 6: Create Test GIF (1 minute)

### Combine Frames into GIF

```bash
python3 << 'EOF'
from PIL import Image
import glob

# Load all frames
frames = [Image.open(f) for f in sorted(glob.glob("animated_frames/normie_*.png"))]

print(f"Creating GIF from {len(frames)} frames...")

# Resize to 512×512 for final output
frames_resized = [f.resize((512, 512), Image.Resampling.LANCZOS) for f in frames]

# Save as GIF
frames_resized[0].save(
    "test_normie_animation.gif",
    save_all=True,
    append_images=frames_resized[1:],
    duration=83,  # 12 fps (1000ms / 12 ≈ 83ms)
    loop=0,
    optimize=False
)

print("✅ GIF created: test_normie_animation.gif")
EOF
```

### View Result

```bash
open test_normie_animation.gif
```

---

## Step 7: Quality Validation (5 minutes)

### Visual Checklist

✅ **Animation is smooth**: No jerky frames or sudden jumps
✅ **Loops seamlessly**: Last frame transitions smoothly to first
✅ **Transparency working**: Background is transparent, not black/white
✅ **Character recognizable**: Normie pepe is still clearly a normie pepe
✅ **No morphing**: Character doesn't change shape dramatically
✅ **No color shifts**: Colors remain consistent with original
✅ **Motion is subtle**: Breathing/idle animation, not wild movement
✅ **No artifacts**: No visual glitches or distortions

### Success Criteria

**PASS** if:
- 7/8 checklist items are ✅
- Animation quality is acceptable for final collection
- Processing time is <10 minutes

**FAIL** if:
- Character is unrecognizable
- Major morphing or distortion
- Transparency lost or broken
- Processing crashes or errors

---

## Troubleshooting

### Problem: Out of Memory

**Symptoms**: ComfyUI crashes, "out of memory" error

**Solutions**:
1. Close other applications
2. Reduce context_length to `8`
3. Restart ComfyUI
4. Check Activity Monitor for memory pressure

### Problem: Black Frames in Output

**Symptoms**: Some/all frames are completely black

**Solutions**:
1. Increase denoise to `0.45-0.50`
2. Reduce context_length to `8`
3. Check that models are loaded correctly
4. Verify MPS is enabled (PyTorch check)

### Problem: Character Morphing

**Symptoms**: Character changes appearance between frames

**Solutions**:
1. Increase ControlNet strength to `0.90-0.95`
2. Decrease denoise to `0.25-0.30`
3. Increase CFG scale to `8.0-9.0`
4. Use more specific positive prompt

### Problem: Too Static (No Movement)

**Symptoms**: Animation looks like still image

**Solutions**:
1. Increase denoise to `0.45-0.55`
2. Increase motion_scale to `1.2-1.5`
3. Use more dynamic prompt (e.g., "breathing deeply, moving")
4. Reduce ControlNet strength to `0.70-0.75`

### Problem: Slow Generation

**Symptoms**: Takes >10 minutes per animation

**Solutions**:
1. Verify `--force-fp16` flag is set
2. Check MPS is enabled: `python3 -c "import torch; print(torch.backends.mps.is_available())"`
3. Reduce steps to `12-15`
4. Close background applications

---

## Next Steps After Successful Test

1. **Document successful settings**: Save exact parameters that worked
2. **Test with other body types**: Try ghastly, diablo, x-ray
3. **Adjust per body type**: Create parameter profiles
4. **Proceed to Phase 2**: Generate all 43 animation templates

---

## Parameter Reference Card

### Quick Settings for Different Layers

| Layer Type | Denoise | Motion Scale | ControlNet | Steps | Prompt Keywords |
|------------|---------|--------------|------------|-------|-----------------|
| **Body** (normie) | 0.35 | 1.0 | 0.85 | 18 | breathing, idle |
| **Body** (ghastly) | 0.45 | 1.2 | 0.80 | 18 | ethereal, floating |
| **Body** (diablo) | 0.50 | 1.3 | 0.80 | 18 | fire, flickering |
| **Body** (x-ray) | 0.45 | 1.4 | 0.85 | 18 | skeleton, glowing |
| **Eyes** | 0.30 | 0.8 | 0.90 | 15 | blinking, subtle |
| **Special** | 0.45 | 1.5 | 0.75 | 18 | particles, effects |
| **Background** | 0.30 | 0.5 | 0.85 | 15 | ambient, shifting |
| **Accessories** | 0.40 | 1.0 | 0.85 | 15 | shimmer, glow |

---

## Files Created

```
/Users/seman/Desktop/kekanimations/
├── temp_normie_rgb.png              (Input RGB layer)
├── temp_normie_alpha.png            (Saved alpha mask)
├── animated_frames/
│   ├── normie_0000.png              (16 frames with transparency)
│   └── ...normie_0015.png
└── test_normie_animation.gif        (Final test output)
```

---

**Status**: Ready to test! Launch ComfyUI and follow Step 1.
