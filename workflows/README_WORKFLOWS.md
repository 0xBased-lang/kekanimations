# ComfyUI Workflows for KEKTECH NFT Animation

This directory contains ComfyUI workflow JSON files optimized for animating KEKTECH NFT collection.

---

## Available Workflows

### 01_simple_nft_animation_m1.json

**Description**: Beginner-friendly, M1-optimized workflow for creating subtle looping animations.

**Optimized For**:
- M1 Mac with 24GB memory
- First-time ComfyUI users
- Quick testing and iteration

**Features**:
- Simple img2img + AnimateDiff
- 16-frame looping GIF output
- Low denoise for character preservation
- Moderate motion scale (subtle movement)

**Settings**:
- Resolution: 512x512 (native NFT size)
- Frames: 16 (M1-safe)
- FPS: 12 (smooth loop)
- Denoise: 0.45 (preserves original character)
- Motion Scale: 1.0 (subtle motion)
- CFG Scale: 7.0 (balanced)
- Steps: 15 (fast generation)

**Processing Time (M1 24GB)**:
- Per NFT: ~3-5 minutes
- 10 NFTs: ~30-50 minutes
- 20 NFTs: ~60-100 minutes

**Output**:
- Format: GIF
- File size: ~2-5MB per NFT
- Duration: ~1.3 seconds (looping)

---

## How to Use These Workflows

### Step 1: Import Workflow into ComfyUI

1. Open ComfyUI in your browser (usually `http://127.0.0.1:8188`)
2. Click the **"Load"** button (top right)
3. Navigate to `kekanimations/workflows/`
4. Select `01_simple_nft_animation_m1.json`
5. Click **Open**

The workflow will appear as a node graph.

### Step 2: Configure for Your NFTs

#### Required Changes:

**Node 1: LoadImage**
- Click on the node
- Click **"choose file to upload"**
- Select your NFT PNG file
- OR drag-and-drop image onto node

**Node 2: CheckpointLoaderSimple**
- Select your installed SD 1.5 model
- Recommended: `v1-5-pruned-emaonly.safetensors`

**Node 6: AnimateDiff Loader**
- Motion Model: `mm_sd_v15_v2.ckpt` (default)
- Context Length: 16 (M1-safe, do not increase)

**Node 10: Video Combine**
- Frame rate: 12 FPS (smooth)
- Format: GIF
- Filename prefix: Will auto-name based on timestamp

#### Optional Adjustments:

**Node 3: Positive Prompt**
- Modify to describe your NFT:
  ```
  high quality, pepe frog character, detailed, colorful, meme art,
  (animated:1.2), subtle motion, breathing, [your custom traits]
  ```

**Node 4: Negative Prompt**
- Keep default or add:
  ```
  blurry, low quality, distorted, ugly, bad anatomy, watermark,
  text, signature, deformed
  ```

**Node 7: KSampler Settings**
- **Seed**: Change number for different motion variations
  - Use "fixed" for reproducible results
  - Use "randomize" for variety
- **Steps**: 15 (fast) → 20 (quality) → 25 (best)
  - More steps = better quality but slower
- **CFG Scale**: 7.0 (default)
  - Lower (5-6): More creative/loose
  - Higher (8-10): Stricter adherence to prompt
- **Denoise**: 0.45 (default)
  - Lower (0.3-0.4): More faithful to original
  - Higher (0.5-0.6): More motion but less accurate

### Step 3: Generate Animation

1. Click **"Queue Prompt"** button (top right)
2. Watch the progress bar
3. Preview frames appear as they generate
4. Final GIF saves to `ComfyUI/output/` directory

### Step 4: Review Output

1. Navigate to `ComfyUI/output/`
2. Find your GIF (named with timestamp)
3. Open and review animation
4. If satisfied, proceed to next NFT
5. If not, adjust settings and regenerate

---

## Batch Processing Multiple NFTs

### Manual Batch Method (Beginner-Friendly)

1. Load workflow
2. Generate NFT #1
3. Wait for completion
4. Load NFT #2 (replace image in LoadImage node)
5. Click "Queue Prompt" again
6. Repeat for all test NFTs

**Pros**: Simple, no scripting
**Cons**: Manual labor, can't run unattended

### Automated Batch Method (Advanced)

Coming soon: Python script for automated batch processing.

---

## Workflow Customization Tips

### For Rare/Legendary NFTs (More Dramatic)

In **Node 7 (KSampler)**:
- Increase denoise: `0.50-0.60` (more motion)
- Increase steps: `20-25` (better quality)

In **Node 6 (AnimateDiff)**:
- Keep context at 16 (M1 limitation)

### For Common NFTs (Subtle, Faster)

In **Node 7 (KSampler)**:
- Decrease denoise: `0.30-0.40` (minimal motion)
- Decrease steps: `12-15` (faster generation)

### For Different Art Styles

In **Node 3 (Positive Prompt)**:
- Laser eyes: Add `glowing red eyes, laser beams`
- Sparkles: Add `magical particles, sparkles, shimmer`
- Dramatic: Add `cinematic, epic, dramatic lighting`
- Psychedelic: Add `trippy, colorful patterns, wavy`

---

## Troubleshooting Workflow Issues

### Problem: "Model not found"

**Solution**: Download required models (see setup guide)

### Problem: Black or corrupted frames

**Solution**:
- Reduce context length to 8 in AnimateDiff node
- Lower denoise to 0.35-0.40
- Check that MPS is enabled (not CPU mode)

### Problem: Very slow generation (>10 min per NFT)

**Solution**:
- Verify you launched with `--force-fp16` flag
- Check you're not in CPU mode
- Close other applications
- Reduce steps to 12-15

### Problem: "Out of memory" error

**Solution**:
- Restart ComfyUI
- Set `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0` (see setup guide)
- Ensure only one generation running at a time

### Problem: Character looks too different from original

**Solution**:
- Lower denoise: try 0.35 or 0.40
- Increase CFG scale: try 8.0 or 9.0
- Use more descriptive positive prompt
- Consider adding ControlNet (advanced)

---

## Next Steps

1. ✅ Import `01_simple_nft_animation_m1.json`
2. ✅ Test on 1-2 sample NFTs
3. ✅ Adjust settings based on results
4. ✅ Process test batch (10-20 NFTs)
5. ⏳ Get feedback from team
6. ⏳ Refine workflow
7. ⏳ Scale to larger batches

---

## Advanced Workflows (Coming Soon)

- `02_controlnet_preservation.json` - Maximum character fidelity
- `03_trait_based_animation.json` - Different motion per trait
- `04_rarity_tiered_effects.json` - Intensity based on rarity
- `05_batch_processing.json` - Automated folder processing

---

**Questions?** See `/research/` directory for detailed documentation or ask for help!
