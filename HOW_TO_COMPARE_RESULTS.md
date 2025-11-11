# 🔍 How to Compare Animation Results

**Created**: November 8, 2025
**Tool**: `scripts/compare_animations.py`
**Status**: ✅ Ready to use

---

## 🎯 Quick Start - Compare Different Results

### Step 1: Generate Comparison Set

```bash
source venv-pixel/bin/activate
python scripts/compare_animations.py <your_image.png>
```

**Example**:
```bash
python scripts/compare_animations.py temp_normie_rgb_1024.png
```

**What this does**:
- Generates **8 different animation variations**
- Creates **interactive HTML comparison viewer**
- Shows **side-by-side comparisons** in your browser

---

## 📊 What Gets Generated

### 8 Variations Automatically Created

**Breathing Intensity Variations** (16 frames, 12 FPS):
1. **Subtle** (±1.5%) - Very gentle breathing
2. **Normal** (±2.0%) - Standard breathing (default)
3. **Dramatic** (±3.0%) - More noticeable breathing
4. **Extreme** (±5.0%) - Very pronounced breathing

**Frame Count Variations** (±2.0%, 12 FPS):
5. **8 frames** - Faster, smaller file size
6. **24 frames** - Smoother, larger file size

**FPS Variations** (16 frames, ±2.0%):
7. **10 FPS** - Slower playback
8. **15 FPS** - Faster playback

---

## 🌐 Interactive HTML Viewer

### Automatic Features

**The HTML viewer shows**:
- ✅ All 8 animations side-by-side
- ✅ Live playback for each variation
- ✅ Stats for each (frames, FPS, file size)
- ✅ Clear descriptions
- ✅ Recommendations

**How to use**:
```bash
# Auto-opens in your default browser
open output/comparisons/<name>_comparison.html
```

**In the browser you can**:
- See all animations playing simultaneously
- Compare breathing intensities visually
- Check file sizes
- Read recommendations

---

## 📁 Output Files

**Location**: `output/comparisons/`

**Files created**:
```
temp_normie_rgb_1024_subtle.gif       (1.7 MB)
temp_normie_rgb_1024_normal.gif       (1.7 MB)
temp_normie_rgb_1024_dramatic.gif     (1.7 MB)
temp_normie_rgb_1024_extreme.gif      (1.8 MB)
temp_normie_rgb_1024_8frames.gif      (0.9 MB)
temp_normie_rgb_1024_24frames.gif     (2.5 MB)
temp_normie_rgb_1024_10fps.gif        (1.7 MB)
temp_normie_rgb_1024_15fps.gif        (1.7 MB)
temp_normie_rgb_1024_comparison.html  (12 KB)
```

---

## 🎨 How to Pick the Best One

### Visual Comparison Checklist

**Watch each animation and check**:
- [ ] Is the breathing motion natural?
- [ ] Does it enhance the NFT or distract?
- [ ] Is the character preserved perfectly?
- [ ] Does the loop feel seamless?
- [ ] Is the file size acceptable?

### Recommended Settings by Use Case

**For Most NFTs** (Best balance):
- Intensity: **Normal** (±2.0%)
- Frames: **16**
- FPS: **12**
- Why: Good motion, reasonable file size

**For Rare/Legendary NFTs** (Maximum impact):
- Intensity: **Dramatic** (±3.0%)
- Frames: **24**
- FPS: **15**
- Why: Smoother, more noticeable, premium feel

**For Web Optimization** (Smallest files):
- Intensity: **Subtle** (±1.5%)
- Frames: **8**
- FPS: **10**
- Why: Small file size, fast loading

**For Maximum Drama** (Hero NFTs):
- Intensity: **Extreme** (±5.0%)
- Frames: **24**
- FPS: **15**
- Why: Very noticeable, commanding presence

---

## 🔍 Detailed Comparison Methods

### Method 1: Side-by-Side in Browser (Easiest)

**Open the HTML file**:
```bash
open output/comparisons/temp_normie_rgb_1024_comparison.html
```

**Benefits**:
- ✅ All 8 variations visible at once
- ✅ Easy to compare breathing intensity
- ✅ Stats shown for each
- ✅ No extra tools needed

---

### Method 2: Individual File Review

**View each GIF separately**:
```bash
# Open all in Preview (Mac)
open output/comparisons/*.gif

# Or open one at a time
open output/comparisons/temp_normie_rgb_1024_subtle.gif
open output/comparisons/temp_normie_rgb_1024_dramatic.gif
```

**Benefits**:
- ✅ Full-screen viewing
- ✅ Can pause/play individually
- ✅ Easy to share specific versions

---

### Method 3: Quick File Size Check

**See all file sizes**:
```bash
ls -lh output/comparisons/*.gif
```

**Compare sizes**:
```
898K  - 8 frames (smallest)
1.7M  - 16 frames (standard)
2.5M  - 24 frames (largest)
```

**Why this matters**:
- Smaller = faster web loading
- Larger = smoother animation
- Balance quality vs performance

---

## 💡 Tips for Choosing

### Breathing Intensity Guide

**Subtle (±1.5%)**:
- ✅ Professional, understated
- ✅ Good for collections with many NFTs
- ✅ Won't distract from details
- ❌ Might be too subtle to notice

**Normal (±2.0%)** ⭐ RECOMMENDED:
- ✅ Noticeable but not distracting
- ✅ Works for most NFTs
- ✅ Good balance
- ✅ Industry standard

**Dramatic (±3.0%)**:
- ✅ Eye-catching
- ✅ Good for rare NFTs
- ✅ Clear motion
- ⚠️ Might be too much for some styles

**Extreme (±5.0%)**:
- ✅ Maximum impact
- ⚠️ Can look exaggerated
- ⚠️ Use sparingly (legendary only)
- ❌ Might distort character

---

### Frame Count Guide

**8 frames**:
- File size: 50% smaller
- Smoothness: Good for web
- Use for: Common NFTs, web galleries

**16 frames** ⭐ RECOMMENDED:
- File size: Standard (~1.7 MB)
- Smoothness: Very good
- Use for: Most NFTs

**24 frames**:
- File size: 50% larger
- Smoothness: Excellent
- Use for: Premium/rare NFTs

---

### FPS Guide

**10 FPS**:
- Playback: Slower, more dramatic
- Use for: Contemplative feel

**12 FPS** ⭐ RECOMMENDED:
- Playback: Standard, balanced
- Use for: Most NFTs

**15 FPS**:
- Playback: Faster, more energetic
- Use for: Dynamic NFTs

---

## 🎬 Custom Comparisons

### Generate Your Own Variations

**Test specific settings**:
```bash
source venv-pixel/bin/activate

# Test different intensities
python scripts/animate_nft.py nft.png --intensity 0.01 --name very_subtle
python scripts/animate_nft.py nft.png --intensity 0.025 --name medium
python scripts/animate_nft.py nft.png --intensity 0.04 --name very_dramatic

# Test different frame counts
python scripts/animate_nft.py nft.png --frames 12 --name quick
python scripts/animate_nft.py nft.png --frames 20 --name smooth
python scripts/animate_nft.py nft.png --frames 32 --name ultra_smooth

# Test different FPS
python scripts/animate_nft.py nft.png --fps 8 --name slow
python scripts/animate_nft.py nft.png --fps 20 --name fast
```

**Then compare manually** in Preview or browser.

---

## 📊 Decision Matrix

### Choose Based On Your Goals

**Goal**: Maximum quality, don't care about file size
→ **Dramatic** intensity, **24 frames**, **15 FPS**

**Goal**: Best balance of quality and size
→ **Normal** intensity, **16 frames**, **12 FPS** ⭐

**Goal**: Smallest file size for web
→ **Subtle** intensity, **8 frames**, **10 FPS**

**Goal**: Showcase rare NFTs
→ **Dramatic** intensity, **24 frames**, **12 FPS**

**Goal**: Fast batch processing
→ **Normal** intensity, **8 frames**, **12 FPS**

---

## 🎯 Quick Decision Guide

**Answer these 3 questions**:

1. **How rare is this NFT?**
   - Common → Normal intensity
   - Rare → Dramatic intensity
   - Legendary → Dramatic or Extreme

2. **Where will it be shown?**
   - Website → Smaller (8-16 frames)
   - Social media → Standard (16 frames)
   - Showcase → Larger (24 frames)

3. **What's your file size budget?**
   - <1 MB → 8 frames
   - <2 MB → 16 frames
   - Don't care → 24 frames

---

## 📈 Performance Comparison

**Generation time** (from testing):

| Variation | Frames | Time | Size |
|-----------|--------|------|------|
| 8 frames | 8 | 0.72s | 898 KB |
| 16 frames | 16 | 1.36s | 1.7 MB |
| 24 frames | 24 | 2.07s | 2.5 MB |

**Intensity doesn't affect**:
- Generation time (same)
- File size (minimal difference)
- Only affects visual motion

---

## ✅ Final Recommendations

### For Your KEKTECH Collection

**Tier 1 - Common NFTs** (70% of collection):
- Intensity: **Normal** (±2.0%)
- Frames: **16**
- FPS: **12**
- Why: Consistent quality, reasonable size

**Tier 2 - Rare NFTs** (25% of collection):
- Intensity: **Dramatic** (±3.0%)
- Frames: **24**
- FPS: **12**
- Why: Premium feel, worth the extra size

**Tier 3 - Legendary NFTs** (5% of collection):
- Intensity: **Dramatic** (±3.0%)
- Frames: **24**
- FPS: **15**
- Why: Maximum smoothness and impact

---

## 🚀 Quick Commands Reference

```bash
# Generate full comparison set
python scripts/compare_animations.py temp_normie_rgb_1024.png

# Open comparison viewer
open output/comparisons/temp_normie_rgb_1024_comparison.html

# View all generated files
ls -lh output/comparisons/

# Generate custom test
python scripts/animate_nft.py nft.png --intensity 0.025 --frames 20 --name custom_test
```

---

## 💬 Still Not Sure?

**Try this experiment**:

1. Generate the comparison set (8 variations)
2. Ask 2-3 friends which one they prefer
3. Note which gets the most positive reactions
4. Use that setting for your collection

**Remember**: There's no "wrong" choice - it's about what fits your artistic vision!

---

**The comparison tool makes it easy to see all options and pick what works best for your collection!** 🎨
