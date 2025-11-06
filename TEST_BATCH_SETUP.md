# Test Batch Setup Guide

**Purpose**: Process 10-20 NFTs as proof-of-concept before scaling to full collection

---

## Test Batch Selection Strategy

### Recommended Approach: Mixed Rarity Sample

Select **10-20 NFTs** representing different rarity tiers:

**Breakdown** (for 15 NFT test):
- 3x Common (baseline, most abundant)
- 3x Uncommon (mid-tier)
- 3x Rare (higher tier)
- 3x Epic (very rare)
- 3x Legendary (ultra rare, showcase pieces)

**Why mixed rarities?**
- Test workflow on different art styles
- Identify if certain traits cause issues
- Preview how different tiers will look
- Get diverse feedback from community

---

## Test Batch Folder Structure

### Step 1: Create Test Batch Directory

```bash
cd /path/to/your/nft-collection/
mkdir test_batch
cd test_batch
```

### Step 2: Copy Selected NFTs

Manually select and copy 10-20 representative NFTs:

```bash
# Example structure:
test_batch/
├── common/
│   ├── kek_0042.png
│   ├── kek_0157.png
│   └── kek_0883.png
├── uncommon/
│   ├── kek_0234.png
│   ├── kek_0789.png
│   └── kek_1456.png
├── rare/
│   ├── kek_0089.png
│   ├── kek_1234.png
│   └── kek_2567.png
├── epic/
│   ├── kek_0003.png
│   ├── kek_0666.png
│   └── kek_3333.png
└── legendary/
    ├── kek_0001.png
    ├── kek_0420.png
    └── kek_4200.png
```

**OR** (simpler flat structure):

```bash
test_batch/
├── test_01_common.png
├── test_02_common.png
├── test_03_common.png
├── test_04_uncommon.png
├── test_05_uncommon.png
├── test_06_uncommon.png
├── test_07_rare.png
├── test_08_rare.png
├── test_09_rare.png
├── test_10_epic.png
├── test_11_epic.png
├── test_12_epic.png
├── test_13_legendary.png
├── test_14_legendary.png
└── test_15_legendary.png
```

### Step 3: Document Selections

Create a `test_batch_manifest.txt` to track which NFTs you selected:

```
# KEKTECH Test Batch Manifest
# Date: 2025-11-06

COMMON TIER:
- kek_0042.png | Traits: [list traits]
- kek_0157.png | Traits: [list traits]
- kek_0883.png | Traits: [list traits]

UNCOMMON TIER:
- kek_0234.png | Traits: [list traits]
- kek_0789.png | Traits: [list traits]
- kek_1456.png | Traits: [list traits]

RARE TIER:
- kek_0089.png | Traits: [list traits]
- kek_1234.png | Traits: [list traits]
- kek_2567.png | Traits: [list traits]

EPIC TIER:
- kek_0003.png | Traits: [list traits]
- kek_0666.png | Traits: [list traits]
- kek_3333.png | Traits: [list traits]

LEGENDARY TIER:
- kek_0001.png | Traits: [list traits]
- kek_0420.png | Traits: [list traits]
- kek_4200.png | Traits: [list traits]
```

---

## Processing Test Batch

### Method 1: Manual Processing (Recommended for First Time)

**Estimated Time**: 30-90 minutes for 15 NFTs

1. Open ComfyUI
2. Load `01_simple_nft_animation_m1.json` workflow
3. For each NFT:
   - Load image into LoadImage node
   - Click "Queue Prompt"
   - Wait for generation (~3-5 min)
   - Review output in `ComfyUI/output/`
   - Document any issues

4. After all NFTs processed:
   - Collect all GIFs
   - Review as a set
   - Identify best/worst results
   - Note any patterns

### Method 2: Queue Multiple (Intermediate)

**Estimated Time**: 30-60 minutes (mostly unattended)

1. Open ComfyUI
2. For each NFT:
   - Load workflow
   - Load image
   - Click "Queue Prompt" (doesn't wait)
   - Repeat for next NFT
3. ComfyUI will process queue sequentially
4. Come back in 30-60 minutes
5. Review all outputs at once

---

## Test Batch Evaluation Checklist

After processing your test batch, evaluate each animation:

### Technical Quality
- [ ] All frames generated (no black frames)
- [ ] No artifacts or corruption
- [ ] Smooth loop (no jarring transition)
- [ ] Acceptable file size (< 5MB)
- [ ] Character recognizable from original

### Animation Quality
- [ ] Motion looks natural
- [ ] Not too subtle (visible movement)
- [ ] Not too dramatic (character still identifiable)
- [ ] Appropriate for NFT style
- [ ] Appealing and entertaining

### Consistency Across Tiers
- [ ] Common tier: Subtle, professional
- [ ] Rare tier: Noticeable, attractive
- [ ] Legendary tier: Eye-catching, premium

### Issues to Note
- [ ] Any NFTs that failed to generate
- [ ] Character traits that caused problems
- [ ] Backgrounds that didn't animate well
- [ ] File sizes that are too large
- [ ] Generation times that were too slow

---

## Test Results Documentation

### Create Test Results Directory

```bash
cd kekanimations/
mkdir test_results
cd test_results
```

### Document Findings

Create `test_batch_results.md`:

```markdown
# Test Batch Results - KEKTECH NFT Animation

**Date**: [Date]
**Batch Size**: [Number] NFTs
**Hardware**: M1 Mac 24GB
**Workflow**: 01_simple_nft_animation_m1.json

---

## Processing Stats

- **Total NFTs Processed**: __/15
- **Successful Animations**: __/15
- **Failed Generations**: __/15
- **Average Time per NFT**: __ minutes
- **Total Processing Time**: __ minutes
- **Average File Size**: __ MB

---

## Quality Assessment

### Best Results
1. [NFT name/number] - [Why it's great]
2. [NFT name/number] - [Why it's great]
3. [NFT name/number] - [Why it's great]

### Worst Results
1. [NFT name/number] - [What went wrong]
2. [NFT name/number] - [What went wrong]
3. [NFT name/number] - [What went wrong]

---

## Findings by Rarity Tier

### Common Tier
- Motion intensity: [Too subtle / Just right / Too much]
- Character preservation: [Excellent / Good / Fair / Poor]
- Notes: [Observations]

### Uncommon Tier
- Motion intensity: [Too subtle / Just right / Too much]
- Character preservation: [Excellent / Good / Fair / Poor]
- Notes: [Observations]

### Rare Tier
- Motion intensity: [Too subtle / Just right / Too much]
- Character preservation: [Excellent / Good / Fair / Poor]
- Notes: [Observations]

### Epic Tier
- Motion intensity: [Too subtle / Just right / Too much]
- Character preservation: [Excellent / Good / Fair / Poor]
- Notes: [Observations]

### Legendary Tier
- Motion intensity: [Too subtle / Just right / Too much]
- Character preservation: [Excellent / Good / Fair / Poor]
- Notes: [Observations]

---

## Technical Issues Encountered

- [ ] Black frames
- [ ] Memory errors
- [ ] Slow generation (>10 min per NFT)
- [ ] Character drift/mutation
- [ ] Corrupted outputs
- [ ] Other: [Describe]

**Details**: [Describe any technical problems]

---

## Workflow Adjustments Needed

Based on test results, what should be changed?

### Settings to Adjust:
- [ ] Denoise strength: [Current: 0.45] → [Recommended: ___]
- [ ] Steps: [Current: 15] → [Recommended: ___]
- [ ] CFG Scale: [Current: 7.0] → [Recommended: ___]
- [ ] Motion scale: [Current: 1.0] → [Recommended: ___]
- [ ] Frame count: [Current: 16] → [Recommended: ___]

### Prompts to Refine:
- Positive prompt additions: [List]
- Negative prompt additions: [List]

---

## Community Feedback

### Internal Team Reactions:
- [Team member 1]: [Feedback]
- [Team member 2]: [Feedback]
- [Team member 3]: [Feedback]

### Community Reactions (if shared):
- [Feedback summary]
- [Most common suggestions]

---

## Next Steps

Based on test batch results:

1. [ ] Workflow is ready for production (no changes needed)
2. [ ] Needs minor adjustments (list above)
3. [ ] Needs major rework (describe needed changes)

**Recommended Path Forward**:
- [Action item 1]
- [Action item 2]
- [Action item 3]

---

## Approved for Production?

- [ ] YES - Proceed to next batch (50-100 NFTs)
- [ ] NO - Iterate on test batch with adjustments
- [ ] PARTIAL - Use different settings for different tiers
```

---

## Sharing Test Results

### For Team Review

Create a folder with sample outputs:

```bash
examples/
└── test_batch_samples/
    ├── 01_common_kek0042.gif
    ├── 02_uncommon_kek0234.gif
    ├── 03_rare_kek0089.gif
    ├── 04_epic_kek0003.gif
    ├── 05_legendary_kek0001.gif
    └── comparison.md
```

### For Community Sneak Peek

Select 2-3 best animations to share on social media:
- 1x Common/Uncommon (show baseline quality)
- 1x Rare/Epic (show mid-tier quality)
- 1x Legendary (show flagship quality)

**Suggested Post**:
```
🐸 KEKTECH Animation Preview 🐸

We're bringing the collection to life! Check out these animated versions.

Which rarity tier looks best? 👇

#KEKTECH #NFT #Animation #Pepe
```

---

## Test Batch Timeline

### Phase 1: Preparation (30 minutes)
- Select 10-20 representative NFTs
- Copy to test_batch folder
- Document selections

### Phase 2: Processing (30-90 minutes)
- Load workflow in ComfyUI
- Process all test NFTs
- Monitor for issues

### Phase 3: Review (30-60 minutes)
- Watch all animations
- Fill out evaluation checklist
- Document findings

### Phase 4: Feedback (24-48 hours)
- Share with team
- Get community input (optional)
- Make decisions on adjustments

### Phase 5: Iteration (if needed)
- Adjust workflow settings
- Reprocess failed/poor-quality NFTs
- Validate improvements

**Total Timeline**: 2-4 hours active work + 1-2 days feedback

---

## Success Criteria

Your test batch is successful if:

✅ **80%+ success rate** (12+ out of 15 NFTs look good)
✅ **Processing time acceptable** (< 10 min per NFT)
✅ **Character preservation** (recognizable from original)
✅ **Team approval** (majority positive feedback)
✅ **Technical stability** (no crashes, consistent results)

If you meet these criteria, you're ready to scale up! 🚀

---

## Next Steps After Test Batch

### If Successful:
1. Process next batch: Top 50-100 rarest NFTs
2. Use for marketing launch
3. Plan full collection processing

### If Needs Iteration:
1. Document specific issues
2. Adjust workflow settings
3. Reprocess test batch
4. Re-evaluate

### If Major Problems:
1. Review M1 compatibility guide
2. Check installation/setup
3. Try simplified workflow
4. Consider cloud GPU testing

---

**Remember**: This test batch is about learning and iteration. Don't expect perfection on first try! 🎯
