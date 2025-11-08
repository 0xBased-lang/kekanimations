# Automated ComfyUI Testing Framework - Complete Usage Guide

This guide walks you through running automated overnight testing to optimize your NFT animation workflows.

---

## 🎯 What This Does

The automated testing framework runs **hundreds of parameter combinations** while you sleep, testing different settings for:

- **Denoise** (0.30-0.60): Character preservation vs. motion intensity
- **Steps** (12-25): Quality vs. processing speed
- **Motion Scale** (0.8-1.5): Animation intensity
- **Samplers & Schedulers**: Quality and temporal consistency
- **CFG Scale** (6.0-8.0): Prompt adherence

**Output**: Data-driven recommendations for optimal settings to process 4,200 NFTs.

---

## 📋 Prerequisites

### 1. System Requirements

- ComfyUI running locally on `http://127.0.0.1:8188`
- Python 3.11+ (you already have this)
- 5-10GB free disk space for test outputs
- 4GB+ free RAM (M1 Mac has plenty)

### 2. Install Dependencies

```bash
cd /Users/seman/Desktop/kekanimations

# Required
pip install websocket-client

# Highly recommended
pip install tqdm psutil

# Optional (for Phase 1 true Latin Hypercube)
pip install scipy
```

### 3. Verify ComfyUI Connection

```bash
# Test API connection
python3 scripts/comfyui_api.py
```

Expected output:
```
✅ ComfyUI connection successful!
System stats: {...}
```

If this fails:
```bash
# Start ComfyUI first
cd ~/Desktop/ComfyUI
./launch_m1.sh
```

---

## 🚀 Quick Start: Run Phase 1 Tonight

**Goal**: Test 50 diverse parameter combinations with 1 NFT (~3-4 hours)

### Step 1: Prepare Test NFTs

Copy 10 representative NFTs to the test directory:

```bash
cd /Users/seman/Desktop/kekanimations

# Copy a common NFT
cp /Users/seman/desktop-transfer/randomizer/output2/nft_images/0.png input_test_nfts/nft_0001.png

# Copy the legendary #420
cp /Users/seman/desktop-transfer/randomizer/output2/nft_images/420.png input_test_nfts/nft_0420.png

# Copy a rare one (#1337)
cp /Users/seman/desktop-transfer/randomizer/output2/nft_images/1337.png input_test_nfts/nft_1337.png

# Copy 7 more diverse NFTs (mix of common/uncommon/rare)
# ... (see selection guide below)
```

### Step 2: Launch Phase 1

```bash
# Make sure ComfyUI is running first!
python3 scripts/automated_testing.py --config config_testing.json --phase 1 --nfts nft_0001
```

This will:
- Generate 50 test parameter combinations (Latin Hypercube)
- Test all 50 with `nft_0001.png`
- Run for **3-4 hours**
- Save results to `experiments/` and `experiments.db`

### Step 3: Check Progress

```bash
# In another terminal, monitor progress
tail -f automated_testing.log

# Or check database
sqlite3 experiments.db "SELECT COUNT(*) as completed FROM experiments WHERE success=1"
```

### Step 4: Morning After - Analyze Results

```bash
# Generate analysis reports
python3 scripts/analyze_results.py --db experiments.db --output experiments

# View summary
cat experiments/summary.txt

# Open visual gallery
open experiments/gallery.html
```

---

## 📊 Three-Phase Testing Strategy

### Phase 1: Broad Exploration (50 tests, ~4 hours)

**Purpose**: Identify promising parameter regions

**Parameters**:
- Denoise: 0.30-0.60 (full range)
- Steps: 12, 15, 20, 25
- Motion Scale: 0.8-1.5 (full range)
- Samplers: euler, dpmpp_2m, dpmpp_sde
- Schedulers: normal, karras, exponential

**NFTs**: 1 representative NFT (use common tier)

**Command**:
```bash
python3 scripts/automated_testing.py --phase 1 --nfts nft_0001
```

**Expected Results**:
- Best denoise range identified (e.g., 0.40-0.50 works best)
- Optimal steps value (e.g., 15 is good enough, 25 is overkill)
- Best sampler/scheduler combo

---

### Phase 2: Focused Factorial (120 tests, ~8-10 hours)

**Purpose**: Refine best parameters across multiple NFTs

**Parameters** (narrowed from Phase 1):
- Denoise: 0.40, 0.45, 0.50 (best range)
- Steps: 15, 20 (optimal)
- Motion Scale: 1.0, 1.2 (best motion)
- Samplers: dpmpp_2m, dpmpp_sde (top 2)
- Scheduler: karras (best)
- CFG Scale: 7.0 (fixed)

**NFTs**: 5 diverse NFTs (1 legendary, 1 rare, 3 common/uncommon)

**Command**:
```bash
python3 scripts/automated_testing.py --phase 2 --nfts nft_0420,nft_1337,nft_0001,nft_0500,nft_2000
```

**Expected Results**:
- Confirmation that settings work across NFT types
- Fine-tuned optimal configuration
- Trade-off analysis (speed vs quality)

---

### Phase 3: Validation (60 tests, ~5-6 hours)

**Purpose**: Validate top 3 configurations across collection

**Configurations**:
1. **Safe & Fast**: denoise 0.40, steps 15, motion 1.0
2. **Balanced**: denoise 0.45, steps 20, motion 1.0
3. **High Motion**: denoise 0.50, steps 20, motion 1.2

**NFTs**: 20 diverse NFTs (spanning all rarity tiers)

**Command**:
```bash
python3 scripts/automated_testing.py --phase 3 --nfts nft_0001,nft_0042,...(list 20 NFTs)
```

**Expected Results**:
- Best configuration for bulk processing
- Alternative configs for different tiers
- Expected failure rate (e.g., 8% will need re-runs)

---

## 🛠️ Advanced Usage

### Custom Test Matrix

Create your own parameter combinations:

```bash
# Generate custom matrix
python3 scripts/generate_test_matrix.py --phase 1 --output my_test_matrix.json

# Edit my_test_matrix.json as needed

# Run with custom matrix
python3 scripts/automated_testing.py --matrix my_test_matrix.json --nfts nft_0001
```

### Resume Interrupted Tests

Tests automatically save checkpoints. If interrupted:

```bash
# Just run the same command again - it will resume!
python3 scripts/automated_testing.py --phase 1 --nfts nft_0001
```

### Test Specific NFTs

```bash
# Test multiple specific NFTs
python3 scripts/automated_testing.py --phase 2 --nfts nft_0420,nft_1337,nft_3000

# Test all NFTs in input directory
python3 scripts/automated_testing.py --phase 2
# (automatically uses all .png files in input_test_nfts/)
```

---

## 📈 Analyzing Results

### 1. Text Summary

```bash
cat experiments/summary.txt
```

Shows:
- Overall success/failure rates
- Success rates by denoise value
- Success rates by steps
- Average processing times
- **Top 5 recommended configurations**
- Warnings about problematic settings

### 2. HTML Gallery

```bash
open experiments/gallery.html
```

Visual grid of all generated animations with parameters displayed.

### 3. CSV Export

```bash
# Opens in Excel/Numbers
open experiments/results.csv
```

Full data table for custom analysis, pivot tables, charts.

### 4. Database Queries

```bash
# Most successful denoise values
sqlite3 experiments.db "
  SELECT denoise,
         COUNT(*) as total,
         SUM(success) as successful,
         ROUND(SUM(success) * 100.0 / COUNT(*), 1) as success_rate
  FROM experiments
  GROUP BY ROUND(denoise, 2)
  ORDER BY success_rate DESC
"

# Average processing time by steps
sqlite3 experiments.db "
  SELECT steps,
         ROUND(AVG(duration_seconds), 1) as avg_duration,
         COUNT(*) as total_tests
  FROM experiments
  WHERE success = 1
  GROUP BY steps
  ORDER BY steps
"
```

---

## 🎯 Selecting Test NFTs

### Recommended 10-NFT Test Set

Copy these to `input_test_nfts/`:

**Legendary Tier** (3 NFTs):
- **#420** - Top NFT, score 94.11
- **#4199** - Score 94.0
- **#3000** - Score 93.7

**Rare Tier** (2 NFTs):
- **#1337** - Score 83.49
- **#2222** - Score 85.92

**Uncommon Tier** (3 NFTs):
- **#500** - Mid-range common
- **#1000** - Different trait combo
- **#2500** - Another variation

**Common Tier** (2 NFTs):
- **#0** - Very first NFT
- **#3500** - Standard common

**Bash Script to Copy**:
```bash
cd /Users/seman/Desktop/kekanimations

# Legendary
cp /Users/seman/desktop-transfer/randomizer/output2/nft_images/420.png input_test_nfts/nft_0420.png
cp /Users/seman/desktop-transfer/randomizer/output2/nft_images/4199.png input_test_nfts/nft_4199.png
cp /Users/seman/desktop-transfer/randomizer/output2/nft_images/3000.png input_test_nfts/nft_3000.png

# Rare
cp /Users/seman/desktop-transfer/randomizer/output2/nft_images/1337.png input_test_nfts/nft_1337.png
cp /Users/seman/desktop-transfer/randomizer/output2/nft_images/2222.png input_test_nfts/nft_2222.png

# Uncommon
cp /Users/seman/desktop-transfer/randomizer/output2/nft_images/500.png input_test_nfts/nft_0500.png
cp /Users/seman/desktop-transfer/randomizer/output2/nft_images/1000.png input_test_nfts/nft_1000.png
cp /Users/seman/desktop-transfer/randomizer/output2/nft_images/2500.png input_test_nfts/nft_2500.png

# Common
cp /Users/seman/desktop-transfer/randomizer/output2/nft_images/0.png input_test_nfts/nft_0001.png
cp /Users/seman/desktop-transfer/randomizer/output2/nft_images/3500.png input_test_nfts/nft_3500.png

# Verify
ls -la input_test_nfts/
```

---

## 🔧 Troubleshooting

### "Connection refused" Error

ComfyUI is not running. Start it:
```bash
cd ~/Desktop/ComfyUI
./launch_m1.sh
```

### "No module named 'websocket'"

Install dependencies:
```bash
pip install websocket-client
```

### "Low memory" Warning

Close other applications or reduce `min_free_memory_gb` in `config_testing.json`.

### Tests Running Very Slowly

Check ComfyUI is using M1 optimization:
```bash
ps aux | grep python | grep "force-fp16"
# Should see --force-fp16 flag
```

### Results Look Bad / High Failure Rate

This is expected! That's why we're testing. The analysis will identify which parameters work.

---

## ⏱️ Realistic Timeline

**Total Testing Time**: 16-20 hours (spread across 2-3 nights)

| Phase | Tests | Time | When to Run |
|-------|-------|------|-------------|
| Phase 1 | 50 | 3-4 hours | Tonight |
| Review | - | 30 min | Tomorrow morning |
| Phase 2 | 120 | 8-10 hours | Tomorrow night |
| Review | - | 30 min | Next morning |
| Phase 3 | 60 | 5-6 hours | Next night |
| Final Analysis | - | 1 hour | Final morning |

**Calendar Time**: 3 days (mostly unattended)

---

## 📝 What You'll Learn

After completing all phases, you'll have:

✅ **Optimal denoise value** with quantified success rate
✅ **Best steps setting** balancing quality and speed
✅ **Ideal motion scale** for your NFT style
✅ **Best sampler/scheduler combo** for smooth animations
✅ **Expected re-run rate** (e.g., "~8% will need re-processing")
✅ **Accurate timeline** for processing 4,200 NFTs
✅ **Tier-specific strategies** (legendary vs common settings)
✅ **Visual gallery** of 230+ test outputs for comparison
✅ **Statistical confidence** in your production workflow

---

## 🚀 Next Steps After Testing

1. **Choose winning configuration** from Top 5 recommendations
2. **Update base workflow** with optimal parameters
3. **Run test batch** of 20-50 NFTs with winning config
4. **Community preview** with generated animations
5. **Full production** processing of 4,200 NFTs

---

## 💡 Pro Tips

- **Run Phase 1 first, always**. Don't skip to Phase 2.
- **Review results between phases**. Adjust Phase 2 ranges based on Phase 1.
- **Use `screen` or `tmux`** for truly unattended operation.
- **Check progress remotely** via SSH if needed.
- **Keep ComfyUI terminal open** to monitor for errors.
- **Backup experiments.db** periodically (contains all data).

---

## 🆘 Need Help?

1. Check `automated_testing.log` for detailed execution logs
2. Review `experiments.db` with sqlite3 for data debugging
3. Test single workflow manually in ComfyUI to isolate issues
4. Verify Python dependencies are installed correctly

---

**You're all set!** Start with Phase 1 tonight and let the automation gather insights while you sleep. 🌙
