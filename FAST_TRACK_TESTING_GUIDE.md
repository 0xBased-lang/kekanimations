# Fast-Track Quality Optimization Testing Guide

**Goal**: Achieve 85/100 quality score (currently at 82/100)
**Strategy**: Test 2 optimized variants based on Quality Scorer recommendations
**Time Estimate**: 1-2 hours total

---

## 🎯 Quick Summary

**Current Baseline**:
- Score: 82/100 (Excellent category)
- Parameters: denoise=0.25, sampler=euler
- Issues: Visual fidelity (10/15), Identity preservation (16/20)

**Optimization Strategy**:
- **Variant A**: denoise=0.30, sampler=dpmpp_2m (moderate improvement)
- **Variant B**: denoise=0.35, sampler=dpmpp_2m (higher improvement)

**Target**: ≥85/100 score

---

## 📝 Step-by-Step Testing Protocol

### Step 1: Generate Variant A (10 minutes)

**File**: `workflows/05_optimized_variant_A.json`

**Changes from Baseline**:
- ✅ Denoise: 0.25 → **0.30** (+20% more animation)
- ✅ Sampler: euler → **dpmpp_2m** (better character preservation)
- ⚡ All other parameters unchanged

**In ComfyUI**:
1. Open ComfyUI (http://127.0.0.1:8188)
2. Load workflow: Drag `05_optimized_variant_A.json` into browser
3. Verify input image is `temp_normie_rgb.png`
4. Click "Queue Prompt"
5. Wait 3-5 minutes for generation
6. Output will be: `ComfyUI/output/AnimatedNFT_VariantA_00001.gif`

**What to Watch For**:
- Processing time should be similar to baseline (~3-5 min)
- No memory errors (if error occurs, close other apps and retry)
- GIF should be ~2-5MB in size

---

### Step 2: Score Variant A (2 minutes)

**Copy output to project**:
```bash
cp ~/Desktop/ComfyUI/output/AnimatedNFT_VariantA_00001.gif ~/Desktop/kekanimations/final_output/variant_A.gif
```

**Run Quality Scorer**:
```bash
cd ~/Desktop/kekanimations
npx playwright test quality-validation --grep "normie_8frames"
```

**Manually update test** to score variant_A.gif:
- Edit `tests/quality-validation.spec.ts`
- Change animation path temporarily to `final_output/variant_A.gif`
- Run test again

**Record Results**:
- Total Score: __/100
- Visual Fidelity: __/15 (baseline: 10/15)
- Identity Preservation: __/20 (baseline: 16/20)
- Visual Assessment (1-5): __/5

---

### Step 3: Generate Variant B (10 minutes)

**File**: `workflows/06_optimized_variant_B.json`

**Changes from Baseline**:
- ✅ Denoise: 0.25 → **0.35** (+40% more animation)
- ✅ Sampler: euler → **dpmpp_2m** (better character preservation)
- ⚡ All other parameters unchanged

**In ComfyUI**:
1. Load workflow: Drag `06_optimized_variant_B.json` into browser
2. Verify input image is `temp_normie_rgb.png`
3. Click "Queue Prompt"
4. Wait 3-5 minutes for generation
5. Output will be: `ComfyUI/output/AnimatedNFT_VariantB_00001.gif`

---

### Step 4: Score Variant B (2 minutes)

**Copy output to project**:
```bash
cp ~/Desktop/ComfyUI/output/AnimatedNFT_VariantB_00001.gif ~/Desktop/kekanimations/final_output/variant_B.gif
```

**Run Quality Scorer** (same process as Variant A):
```bash
cd ~/Desktop/kekanimations
# Update test to point to variant_B.gif
npx playwright test quality-validation
```

**Record Results**:
- Total Score: __/100
- Visual Fidelity: __/15 (baseline: 10/15)
- Identity Preservation: __/20 (baseline: 16/20)
- Visual Assessment (1-5): __/5

---

### Step 5: Compare Results & Select Winner (5 minutes)

**Comparison Matrix**:

| Metric | Baseline | Variant A | Variant B | Winner |
|--------|----------|-----------|-----------|--------|
| **Total Score** | 82/100 | __/100 | __/100 | __ |
| Visual Fidelity | 10/15 | __/15 | __/15 | __ |
| Identity Preservation | 16/20 | __/20 | __/20 | __ |
| Technical Quality | 33/40 | __/40 | __/40 | __ |
| Character Preservation | 24/30 | __/30 | __/30 | __ |
| Motion Quality | 15/20 | __/20 | __/20 | __ |
| **Visual Assessment** | 4/5 | __/5 | __/5 | __ |

**Decision Criteria**:
1. **If either variant ≥85/100**: That variant WINS → Move to validation
2. **If both <85/100 but improved**: Pick higher scorer → Move to validation anyway
3. **If both worse than baseline**: Investigate issues, may need different approach

**Visual Review**:
- Open all 3 GIFs side-by-side in browser
- Does character look like original?
- Is motion smooth and natural?
- Which looks best to your eye?

---

### Step 6: Validate Winner on Diverse NFTs (30-60 minutes)

**If winner achieved ≥85/100 OR significantly improved visual quality**:

**Select 2-3 Diverse Test NFTs**:
1. **Simple NFT**: Solid background, basic traits
   - Example: Common tier, minimal accessories
2. **Complex NFT**: Busy background, multiple traits
   - Example: Uncommon/rare tier with accessories
3. **Rare NFT**: Unique traits, special effects (optional)
   - Example: Legendary tier with special background

**Testing Protocol**:
For each test NFT:
1. Copy NFT image to ComfyUI input folder as `temp_test_nft.png`
2. Load winner workflow (Variant A or B)
3. Update LoadImage node to use `temp_test_nft.png`
4. Generate animation
5. Score with Quality Scorer
6. Visual assessment

**Success Criteria**:
- ✅ 2/3 NFTs score ≥80/100 (or all ≥75/100)
- ✅ Visual quality acceptable across all types
- ✅ Character preservation good on all
- ✅ No major artifacts or distortions

**If Success**: WORKFLOW IS READY FOR PRODUCTION! 🎉

---

## 📊 Results Documentation Template

### Final Results

**Winning Variant**: [ ] Variant A  [ ] Variant B  [ ] Baseline (if no improvement)

**Parameters**:
- Denoise: __
- Sampler: __
- ControlNet Strength: 0.85
- CFG Scale: 7.0
- Motion Scale: 1.0
- Steps: 15
- Frames: 8

**Quality Scores**:
- **Normie NFT** (baseline test): __/100
- **Simple NFT**: __/100
- **Complex NFT**: __/100
- **Rare NFT** (if tested): __/100
- **Average**: __/100

**Visual Quality** (human assessment):
- Normie: __/5
- Simple: __/5
- Complex: __/5
- Rare: __/5
- **Average**: __/5

**Success**: [ ] YES - Ready for production  [ ] NO - Need more testing

---

## 🚨 Troubleshooting

### Issue: Out of Memory Error

**Symptoms**: ComfyUI crashes or shows "Not enough memory" error

**Solutions**:
1. Close all other applications
2. Restart ComfyUI
3. Try reducing frame count from 8 to 4 frames temporarily
4. Verify M1 has ~20GB free memory (Activity Monitor)

### Issue: Generation is Very Slow (>10 minutes)

**Symptoms**: Generation taking significantly longer than baseline

**Solutions**:
1. Verify `--force-fp16` flag is set in ComfyUI launch script
2. Check Activity Monitor - ensure MPS (GPU) is being used
3. dpmpp_2m sampler is slightly slower than euler (expected)
4. If consistently >10 min, may need to adjust parameters

### Issue: Black Frames or Corrupted Output

**Symptoms**: GIF has black frames or visual corruption

**Solutions**:
1. Denoise may be too high - try 0.30 instead of 0.35
2. Verify all models are loaded (check ComfyUI console)
3. Clear ComfyUI cache and restart
4. Re-generate with different seed

### Issue: Score Went DOWN Instead of UP

**Symptoms**: Variant scores lower than baseline 82/100

**Analysis**:
- **If Visual Fidelity decreased**: Denoise may be too high, try lowering
- **If Identity Preservation decreased**: Character drifting, increase ControlNet strength
- **If Motion Quality decreased**: Animation may be too subtle or too exaggerated

**Solutions**:
1. Review Quality Scorer recommendations in output
2. Try intermediate denoise value (e.g., 0.27 or 0.28)
3. Test with different sampler (ddim or euler_ancestral)
4. May need systematic parameter sweep instead of fast-track

### Issue: Can't Score with Quality Scorer

**Symptoms**: Playwright test fails or doesn't find file

**Solutions**:
1. Verify GIF was copied to `final_output/` folder
2. Check file name matches what test is looking for
3. Ensure Playwright is running (npm test should work)
4. Temporarily modify test file to point to correct path

---

## ✅ Next Steps After Testing

### If Successful (≥85/100 on diverse NFTs):

1. **Document Final Workflow**:
   - Save winning workflow as `workflows/FINAL_OPTIMIZED.json`
   - Update `OPTIMIZATION_LOG.md` with results
   - Create troubleshooting guide for operators

2. **Update Framework**:
   - Update `OPTIMIZATION_FRAMEWORK.md` with final parameters
   - Record lessons learned
   - Document edge cases discovered

3. **Prepare for Production**:
   - Test batch processing (5-10 NFTs)
   - Create operator instructions
   - Plan full collection processing (4,200 NFTs)

### If Not Successful (<85/100):

1. **Analyze Results**:
   - Review Quality Scorer breakdown
   - Identify which metrics are still low
   - Compare visual quality vs scores

2. **Decide Next Steps**:
   - **Option A**: Try intermediate values (denoise 0.27, 0.28, 0.32)
   - **Option B**: Test different sampler (ddim, heun, euler_ancestral)
   - **Option C**: Adjust ControlNet strength (0.80, 0.90, 0.95)
   - **Option D**: Continue with full systematic testing (original 6-day plan)

3. **Document Findings**:
   - Record what didn't work and why
   - Update hypotheses for next tests
   - Plan next optimization iteration

---

## 📌 Quick Reference

**Baseline Score**: 82/100
**Target Score**: 85/100
**Gap**: +3 points

**Test Variants**:
- Variant A: denoise=0.30, dpmpp_2m
- Variant B: denoise=0.35, dpmpp_2m

**Time Budget**:
- Generation: 20 minutes (2 variants × 10 min)
- Scoring: 10 minutes (2 variants × 5 min)
- Comparison: 5 minutes
- Validation: 30-60 minutes (2-3 diverse NFTs)
- **Total**: 1-2 hours

**Success Criteria**:
- ✅ Score ≥85/100
- ✅ Visual quality ≥4/5
- ✅ Works on diverse NFTs (2/3 success rate)
- ✅ Character preservation maintained

---

**Ready to start? Load Variant A in ComfyUI and queue the first prompt!** 🚀