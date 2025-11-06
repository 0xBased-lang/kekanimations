# ComfyUI on M1 Mac - Compatibility & Optimization Guide

**Updated**: November 6, 2025
**Hardware**: M1 Mac with 24GB Unified Memory
**Status**: ✅ ComfyUI works | ⚠️ AnimateDiff has limitations

---

## TL;DR - What Works on M1

✅ **WORKS WELL:**
- ComfyUI core functionality (fully supported)
- Basic image generation (SD 1.5 models)
- img2img workflows
- Batch processing (with patience)
- Simple AnimateDiff (8-16 frames)
- ControlNet (with optimized settings)

⚠️ **WORKS WITH LIMITATIONS:**
- AnimateDiff (max 8-16 frames, avoid upscaling)
- SDXL models (very slow, 45-60 min per image)
- Long animations (memory crashes possible)

❌ **PROBLEMATIC:**
- AnimateDiff with >16 frames (black output or crashes)
- AnimateDiff + Latent Upscale (instant crash)
- High-resolution generations without optimization

---

## M1 Mac Setup Requirements

### System Specifications
- **Your Hardware**: M1 with 24GB unified memory ✅ Good!
- **Minimum**: 8GB RAM (works but limited)
- **Recommended**: 16GB+ (you exceed this)
- **Optimal**: 32GB+ (future-proof)

### Software Requirements
- **macOS**: 12.3+ (Monterey or newer)
- **Python**: 3.10 or 3.11 (recommended)
- **PyTorch**: 2.0+ with MPS support
- **ComfyUI**: Latest version (January 2025+)

---

## Critical M1 Optimization Settings

### 1. Environment Variables (MUST SET)

Add these to your shell profile (`~/.zshrc` or `~/.bash_profile`):

```bash
# Critical for M1 memory management
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0

# Enable MPS fallback for unsupported operations
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

Apply changes:
```bash
source ~/.zshrc  # or source ~/.bash_profile
```

### 2. ComfyUI Launch Flags

**Recommended startup command**:
```bash
python main.py --force-fp16 --use-split-cross-attention
```

**Flag explanations**:
- `--force-fp16`: Forces 16-bit floating point (faster, less memory)
- `--use-split-cross-attention`: Optimized attention mechanism for Mac

**Optional flags**:
- `--preview-method auto`: Enable live previews
- `--highvram`: If you have 24GB+ (you do!)

**DO NOT USE**:
- `--cpu`: Forces CPU-only mode (20+ min per image)
- `--lowvram`: Not needed with 24GB

### 3. ComfyUI Settings (In UI)

Once ComfyUI is running, set these in Settings:

- **Device**: `mps` (Metal Performance Shaders)
- **VAE Precision**: `fp16` (faster)
- **Cross Attention Method**: `split` (M1 optimized)

---

## AnimateDiff on M1 - Known Issues & Solutions

### Issue 1: Black Frames Above 10-16 Frames

**Problem**: Generated frames come out black when batch size > 10-16.

**Solution**:
- Limit animations to **8-16 frames maximum**
- Use "context" setting at 8 or 16 (not higher)
- For longer animations, render in chunks and stitch later

**Workflow Setting**:
```
AnimateDiff Loader:
- Context: 16 (max)
- Frame count: 16 (safe)
```

### Issue 2: Memory Crashes with Upscaling

**Problem**: AnimateDiff + Latent Upscale = instant crash.

**Solution**:
- **DO NOT use Latent Upscale node with AnimateDiff**
- Generate at target resolution directly (512x512)
- If upscaling needed, do AFTER animation completes:
  1. Generate 512x512 animation
  2. Export frames
  3. Upscale frames separately with RealESRGAN
  4. Reassemble into GIF

### Issue 3: Slow Generation Times

**Problem**: Each frame takes 20-60 seconds.

**Solution**:
- Use **SD 1.5 models** (not SDXL)
- Enable `--force-fp16` flag
- Reduce resolution (512x512 is sweet spot)
- Consider cloud GPU for bulk processing (see below)

**Expected Performance (M1 24GB)**:
- 512x512 single frame: ~5-10 seconds
- 512x512 with AnimateDiff (16 frames): ~2-5 minutes
- Per NFT animation: ~3-6 minutes

**For 10 test NFTs**: ~30-60 minutes total
**For 100 NFTs**: ~5-10 hours
**For 4,200 NFTs**: ~210-420 hours (9-18 days)

---

## Recommended Workflow Strategy for M1

### Phase 1: Test on M1 (10-20 NFTs)
- Perfect for learning and proof-of-concept
- Manageable timeframes (30-120 minutes)
- Iterate and refine workflow
- Get feedback before scaling

### Phase 2: Small Batch on M1 (50-100 NFTs)
- Overnight processing (8-10 hours)
- Still manageable on your hardware
- Good for top-tier rarities

### Phase 3: Full Scale on Cloud GPU (4,200 NFTs)
- **Recommendation**: Switch to cloud for bulk processing
- Cost: ~$0.30-0.50/hour on RunPod/Vast.ai
- A100 40GB: Process full collection in 24-48 hours
- Total cost: ~$12-24 for entire collection

---

## Cloud GPU Options (For Final Batch)

If M1 becomes too slow for full collection:

### Option 1: RunPod (Recommended)
- **Website**: https://www.runpod.io/
- **GPU**: RTX 4090 (24GB) or A100 (40GB)
- **Cost**: $0.34-0.64/hour
- **Setup**: Pre-configured ComfyUI templates
- **Speed**: 5-10x faster than M1

### Option 2: Vast.ai (Budget Option)
- **Website**: https://vast.ai/
- **GPU**: RTX 3090 (24GB)
- **Cost**: $0.20-0.40/hour
- **Setup**: Manual ComfyUI installation
- **Speed**: 3-5x faster than M1

### Option 3: Google Colab (Free Tier Available)
- **Website**: https://colab.research.google.com/
- **GPU**: T4 (16GB) free, V100 paid
- **Cost**: Free tier or ~$10/month
- **Limitations**: Session timeouts, slower than dedicated

**Workflow**:
1. Develop and test workflow on M1 (local)
2. Export workflow JSON
3. Upload to cloud GPU
4. Process full collection in 1-2 days
5. Download results

---

## M1-Optimized Workflow Recommendations

### For Your Test Batch (10-20 NFTs)

**Recommended Approach**:
- Simple img2img + AnimateDiff
- 16 frames max
- 512x512 resolution
- SD 1.5 model (not SDXL)
- Low denoise (0.3-0.5)
- Motion scale (0.4-0.7)
- Output: GIF or MP4

**Avoid on M1**:
- ControlNet (adds 50-100% processing time)
- Latent Upscale (crashes)
- Frame counts >16 (black outputs)
- Multiple ControlNet stacks
- SDXL models (too slow)

**Timeline**:
- 10 NFTs: ~30-60 minutes
- 20 NFTs: ~60-120 minutes

### For Production (After Testing)

**Two Paths**:

**Path A: Continue on M1**
- Process overnight in batches of 50-100
- ~10 days for full collection (4,200 NFTs)
- Free (no cloud costs)
- Requires patience

**Path B: Move to Cloud GPU**
- Port tested workflow to RunPod/Vast.ai
- Process in 24-48 hours
- Cost: ~$12-24 total
- Faster turnaround

---

## Troubleshooting M1 Issues

### Issue: "MPS backend out of memory"
**Solution**:
- Restart ComfyUI
- Set `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0`
- Use `--force-fp16` flag
- Reduce batch size

### Issue: "Operation not supported on MPS"
**Solution**:
- Set `PYTORCH_ENABLE_MPS_FALLBACK=1`
- Update PyTorch to latest version
- Check custom node compatibility

### Issue: Black or corrupted outputs
**Solution**:
- Reduce AnimateDiff frame count to 8-16
- Lower motion scale (0.3-0.5)
- Remove Latent Upscale nodes
- Try different motion models

### Issue: Very slow generation (>5 min per frame)
**Solution**:
- Verify you're NOT using `--cpu` flag
- Confirm MPS is active (check ComfyUI logs)
- Use SD 1.5 instead of SDXL
- Close other applications

---

## Testing Your M1 Setup

Before processing NFTs, run this test:

1. **Basic Generation Test** (30 seconds):
   - Load SD 1.5 model
   - Generate 512x512 image
   - Expected time: 5-10 seconds

2. **AnimateDiff Test** (5 minutes):
   - Load AnimateDiff workflow
   - Generate 16-frame animation
   - Expected time: 2-5 minutes

3. **Batch Test** (30 minutes):
   - Load 10 test images
   - Apply same workflow
   - Expected time: 20-50 minutes

If these work smoothly, you're ready for NFT processing!

---

## Final Recommendations for Your Setup

**Your Hardware**: M1 24GB - **Good for testing, consider cloud for scale**

### Recommended Path:

**Week 1: Test & Iterate (M1 local)**
- Process 10-20 test NFTs (2-3 hours total)
- Refine workflow based on results
- Get team/community feedback
- Perfect the animation style

**Week 2: Priority Batch (M1 local)**
- Process top 50-100 rarest NFTs (overnight, ~8-12 hours)
- Use for marketing launch
- Validate workflow stability

**Week 3-4: Full Collection (Cloud GPU)**
- Export tested workflow
- Rent RTX 4090 on RunPod ($0.34/hour)
- Process all 4,200 NFTs (48 hours = ~$16-20)
- Download and deploy

**Total Timeline**: 3-4 weeks
**Total Cost**: ~$20 (cloud GPU only)
**M1 Usage**: Perfect for development, minimal cloud costs

---

## Next Steps

1. ✅ Install ComfyUI with M1 optimizations
2. ✅ Download required models (SD 1.5 + AnimateDiff)
3. ✅ Test basic workflow on 1-2 images
4. ✅ Process test batch (10-20 NFTs)
5. ⏳ Review results and iterate
6. ⏳ Scale to production (M1 or cloud)

---

**Bottom Line**: Your M1 with 24GB is GREAT for testing and small batches. For the full 4,200 NFT collection, consider cloud GPU to save days of processing time for ~$20.

