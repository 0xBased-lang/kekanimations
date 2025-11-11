# ComfyUI Quick Reference - Animation Workflow

**Status**: ComfyUI launching...
**Workflow**: Layer animation for KEKTECH NFTs
**Target**: Generate 16-frame looping animation

---

## 🚀 Step 1: Access ComfyUI

**URL**: http://127.0.0.1:8188

```bash
# Open in browser
open http://127.0.0.1:8188
```

---

## 📥 Step 2: Load Workflow

### Option A: Load JSON File
1. Click **"Load"** in top menu
2. Navigate to: `/Users/seman/Desktop/kekanimations/workflows/layer_animation_workflow.json`
3. Click **"Open"**

### Option B: Manual Setup
If JSON doesn't load, create workflow manually (see PHASE1_COMFYUI_TESTING.md)

---

## ⚙️ Step 3: Configure Key Nodes

### 1. LoadImage Node
```
image: temp_normie_rgb.png
```
✅ Already in ComfyUI/input/ directory

### 2. CheckpointLoaderSimple
```
ckpt_name: v1-5-pruned-emaonly.safetensors
```

### 3. Positive Prompt (CLIPTextEncode)
```
character breathing, subtle idle animation, smooth motion, high quality
```

### 4. Negative Prompt (CLIPTextEncode)
```
distortion, morphing, color change, artifacts, blurry, low quality
```

### 5. AnimateDiff Loader
```
motion_model: mm_sd_v15_v2.ckpt
beta_schedule: sqrt_linear (AnimateDiff)
motion_scale: 1.0
context_length: 16
closed_loop: Enabled
```

### 6. ControlNet Loader
```
control_net_name: control_v11p_sd15_canny.pth
```

### 7. ControlNet Apply
```
strength: 0.85
```

### 8. KSampler
```
seed: randomize
steps: 18
cfg: 7.0
sampler_name: dpmpp_2m
scheduler: karras
denoise: 0.35
```

### 9. VideoCombine
```
frame_rate: 12
loop_count: 0
filename_prefix: normie_animation
format: image/png
save_output: true
```

---

## 🎬 Step 4: Generate Animation

1. Review all node configurations
2. Click **"Queue Prompt"** (right sidebar)
3. Watch progress in interface
4. Wait 3-5 minutes for completion

**Expected Output**:
```
~/Desktop/ComfyUI/output/normie_animation_00001_00000.png
~/Desktop/ComfyUI/output/normie_animation_00001_00001.png
...
~/Desktop/ComfyUI/output/normie_animation_00001_00015.png
```

---

## 🎨 Step 5: Restore Transparency

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
    frame = Image.open(frame_path)
    frame_rgba = frame.convert("RGBA")
    frame_rgba.putalpha(alpha)

    output_path = f"animated_frames/normie_{i:04d}.png"
    frame_rgba.save(output_path)
    print(f"✅ Frame {i}: {output_path}")

print(f"\n✅ All {len(frames)} frames with transparency restored")
EOF
```

---

## 🎬 Step 6: Create GIF

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

# View the result
open test_normie_animation.gif
```

---

## ✅ Step 7: Validate with Playwright

```bash
# Run validation on the GIF
npm run test -- layer-validation.spec.ts

# View results
npm run test:report
```

---

## 🔧 Troubleshooting

### ComfyUI Not Loading
```bash
# Check if running
curl http://127.0.0.1:8188

# View logs
cd ~/Desktop/ComfyUI
tail -f comfyui.log

# Restart
pkill -f "python main.py"
./launch_m1.sh
```

### Models Not Found
```bash
# Check models directory
ls ~/Desktop/ComfyUI/models/animatediff_models/
ls ~/Desktop/ComfyUI/models/controlnet/
ls ~/Desktop/ComfyUI/models/checkpoints/
```

### Out of Memory
- Close other applications
- Reduce context_length to 8
- Restart ComfyUI

### Black Frames
- Increase denoise to 0.45-0.50
- Check that models loaded correctly
- Verify MPS is enabled

---

## 📊 Expected Results

### Quality Checklist
- ✅ Animation is smooth (no jerky frames)
- ✅ Loops seamlessly (last frame → first frame smooth)
- ✅ Transparency working (background transparent)
- ✅ Character recognizable (normie pepe identity preserved)
- ✅ No morphing (character doesn't change shape)
- ✅ No color shifts (colors consistent)
- ✅ Motion is subtle (breathing/idle, not wild)
- ✅ No artifacts (no visual glitches)

### Performance Metrics
- Generation time: 3-5 minutes
- Output frames: 16 PNG files
- File sizes: ~500KB-1MB per frame
- Final GIF: 2-5MB

---

## 🎯 Next Steps After Success

1. **Document parameters** that worked
2. **Test with other body types** (ghastly, diablo, x-ray)
3. **Adjust parameters** per body type
4. **Create parameter reference** card
5. **Proceed to Phase 2** (generate all 43 templates)

---

## 📚 Full Guides

- **Complete workflow**: `PHASE1_COMFYUI_TESTING.md`
- **Technical details**: `research/LAYER_ANIMATION_GUIDE.md`
- **Project overview**: `PROJECT_OVERVIEW.md`

---

**You're ready to animate! Open http://127.0.0.1:8188 and follow the steps above.** 🚀
