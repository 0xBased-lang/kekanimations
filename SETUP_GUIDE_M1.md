# ComfyUI Setup Guide for M1 Mac - Complete Walkthrough

**Target User**: First-time ComfyUI user on M1 Mac with 24GB memory
**Time Required**: 30-60 minutes
**Difficulty**: Beginner-friendly

---

## Prerequisites

Before starting, ensure you have:

- [ ] M1, M1 Pro, M1 Max, M2, M3, or M4 Mac
- [ ] macOS 12.3 (Monterey) or newer
- [ ] At least 20GB free disk space
- [ ] Internet connection (for downloading models)
- [ ] Administrator access (for installing software)
- [ ] Terminal access (Applications → Utilities → Terminal)

---

## Step 1: Install Homebrew (if not already installed)

Homebrew is a package manager for macOS that makes installing software easier.

### Check if Homebrew is already installed:

```bash
brew --version
```

If you see a version number, skip to Step 2.

### If not installed, install Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen instructions. This takes 5-10 minutes.

---

## Step 2: Install Python 3.11

ComfyUI works best with Python 3.10 or 3.11 on M1 Macs.

### Install Python via Homebrew:

```bash
brew install python@3.11
```

### Verify installation:

```bash
python3.11 --version
```

You should see: `Python 3.11.x`

---

## Step 3: Install Git (if not already installed)

Git is needed to clone the ComfyUI repository.

### Check if Git is installed:

```bash
git --version
```

### If not installed:

```bash
brew install git
```

---

## Step 4: Download ComfyUI

### Navigate to your preferred installation directory:

```bash
cd ~/Documents  # or wherever you prefer
```

### Clone ComfyUI repository:

```bash
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI
```

This downloads the latest ComfyUI code (~200MB).

---

## Step 5: Set Up Python Virtual Environment

Virtual environments keep ComfyUI's dependencies isolated from your system Python.

### Create virtual environment:

```bash
python3.11 -m venv venv
```

### Activate virtual environment:

```bash
source venv/bin/activate
```

Your terminal prompt should now show `(venv)` at the beginning.

**Important**: You need to activate this environment every time you run ComfyUI.

---

## Step 6: Install ComfyUI Dependencies

### Install PyTorch with MPS support:

```bash
pip install --upgrade pip
pip install torch torchvision torchaudio
```

This installs the latest PyTorch with Metal Performance Shaders (MPS) support for M1 acceleration.

### Install ComfyUI requirements:

```bash
pip install -r requirements.txt
```

This takes 5-10 minutes and installs all necessary packages.

---

## Step 7: Configure M1 Optimization Settings

### Create launch script with M1 optimizations:

Create a new file called `launch_m1.sh`:

```bash
nano launch_m1.sh
```

Paste the following content:

```bash
#!/bin/bash

# M1 optimization environment variables
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1

# Activate virtual environment
source venv/bin/activate

# Launch ComfyUI with M1-optimized flags
python main.py --force-fp16 --use-split-cross-attention --highvram --preview-method auto
```

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

### Make script executable:

```bash
chmod +x launch_m1.sh
```

---

## Step 8: Download Required Models

ComfyUI needs AI models to function. You'll download:
1. Stable Diffusion 1.5 checkpoint (~4GB)
2. AnimateDiff motion module (~1.8GB)
3. VAE model (~300MB)

### Create model directories:

```bash
mkdir -p models/checkpoints
mkdir -p models/animatediff_models
mkdir -p models/vae
```

### Download SD 1.5 Model:

```bash
cd models/checkpoints
curl -L -o v1-5-pruned-emaonly.safetensors "https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"
cd ../..
```

**Alternative**: Manual download:
1. Visit: https://huggingface.co/runwayml/stable-diffusion-v1-5/tree/main
2. Download `v1-5-pruned-emaonly.safetensors`
3. Place in `ComfyUI/models/checkpoints/`

### Download AnimateDiff Motion Module:

```bash
cd models/animatediff_models
curl -L -o mm_sd_v15_v2.ckpt "https://huggingface.co/guoyww/animatediff/resolve/main/mm_sd_v15_v2.ckpt"
cd ../..
```

**Alternative**: Manual download:
1. Visit: https://huggingface.co/guoyww/animatediff/tree/main
2. Download `mm_sd_v15_v2.ckpt`
3. Place in `ComfyUI/models/animatediff_models/`

### Download VAE Model (Optional but Recommended):

```bash
cd models/vae
curl -L -o vae-ft-mse-840000-ema-pruned.safetensors "https://huggingface.co/stabilityai/sd-vae-ft-mse-original/resolve/main/vae-ft-mse-840000-ema-pruned.safetensors"
cd ../..
```

**Total Download Size**: ~6-7GB
**Download Time**: 10-30 minutes (depending on internet speed)

---

## Step 9: Install AnimateDiff Custom Nodes

AnimateDiff requires custom nodes to work in ComfyUI.

### Navigate to custom_nodes directory:

```bash
cd custom_nodes
```

### Clone AnimateDiff Evolved:

```bash
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved
```

### Clone Video Helper Suite (for GIF export):

```bash
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite
```

### Install dependencies:

```bash
cd ComfyUI-AnimateDiff-Evolved
pip install -r requirements.txt
cd ..

cd ComfyUI-VideoHelperSuite
pip install -r requirements.txt
cd ../..
```

---

## Step 10: Test ComfyUI Installation

### Launch ComfyUI:

```bash
./launch_m1.sh
```

You should see output like:
```
Total VRAM 24576 MB, total RAM 24576 MB
Set vram state to: HIGH_VRAM
Device: mps
VAE dtype: torch.float16
Starting server

To see the GUI go to: http://127.0.0.1:8188
```

**Key things to verify**:
- Device shows `mps` (not `cpu`)
- No error messages
- Server starts successfully

### Open ComfyUI in browser:

Open your web browser and go to:
```
http://127.0.0.1:8188
```

You should see the ComfyUI interface with a node graph.

### Test basic generation:

1. The default workflow should be loaded
2. Click **"Queue Prompt"** (top right)
3. Watch as it generates a test image
4. If an image appears, congratulations! ComfyUI is working.

**Expected Generation Time**: 5-10 seconds for first image

### Stop ComfyUI:

Go back to Terminal and press `Ctrl+C` to stop the server.

---

## Step 11: Import KEKTECH Animation Workflow

### Copy workflow file:

1. Download `01_simple_nft_animation_m1.json` from this repository
2. Place it in a convenient location (e.g., `~/Documents/kekanimations/workflows/`)

### Launch ComfyUI:

```bash
cd ~/Documents/ComfyUI  # or wherever you installed it
./launch_m1.sh
```

### Import workflow:

1. Open browser to `http://127.0.0.1:8188`
2. Click **"Load"** button (top right)
3. Navigate to workflow file location
4. Select `01_simple_nft_animation_m1.json`
5. Click **Open**

The workflow will load as a node graph showing the animation pipeline.

---

## Step 12: Process Your First NFT Animation

### Prepare test NFT:

1. Select one NFT from your collection (PNG format, 512x512 recommended)
2. Copy it to an easily accessible location

### Load NFT into workflow:

1. Find the **LoadImage** node (should be at the top-left)
2. Click on the node
3. Click **"choose file to upload"**
4. Select your test NFT PNG
5. Click **Open**

### Configure settings (optional):

- In **CLIPTextEncode (positive)** node, update prompt to describe your NFT
- In **KSampler** node, you can change seed for different motion variations

### Generate animation:

1. Click **"Queue Prompt"** button (top right)
2. Watch the progress bar
3. Preview frames will appear as they generate
4. Wait 3-5 minutes for completion

### Find output:

1. Open Finder
2. Navigate to `ComfyUI/output/`
3. Look for the newest GIF file (named with timestamp)
4. Open and review your animated NFT!

---

## Step 13: Troubleshooting Common Issues

### Issue: ComfyUI shows "Device: cpu" instead of "Device: mps"

**Solution**:
```bash
# Verify PyTorch MPS support
python3 -c "import torch; print(torch.backends.mps.is_available())"
```

Should return `True`. If `False`:
```bash
pip uninstall torch torchvision torchaudio
pip install --upgrade torch torchvision torchaudio
```

### Issue: "Model not found" error

**Solution**:
- Verify model files are in correct directories
- Check file names match exactly (case-sensitive)
- Re-download if files are corrupted

### Issue: "Out of memory" error

**Solution**:
1. Close other applications
2. Restart ComfyUI
3. Ensure environment variable is set:
   ```bash
   echo $PYTORCH_MPS_HIGH_WATERMARK_RATIO
   ```
   Should return `0.0`

### Issue: Very slow generation (>10 min per frame)

**Solution**:
- Verify you're using `--force-fp16` flag
- Check you're not in CPU mode (see above)
- Close Chrome/Safari if many tabs open
- Restart Mac to clear memory

### Issue: Black or corrupted frames

**Solution**:
- In AnimateDiff node, reduce context to 8
- In KSampler node, reduce denoise to 0.35
- Try different motion model
- Update custom nodes:
  ```bash
  cd custom_nodes/ComfyUI-AnimateDiff-Evolved
  git pull
  cd ../ComfyUI-VideoHelperSuite
  git pull
  cd ../..
  ```

### Issue: Custom nodes not showing up

**Solution**:
- Restart ComfyUI (Ctrl+C, then relaunch)
- Check dependencies installed:
  ```bash
  cd custom_nodes/ComfyUI-AnimateDiff-Evolved
  pip install -r requirements.txt
  cd ../..
  ```
- Check for errors in terminal output

---

## Step 14: Ongoing Usage

### Daily Workflow:

1. **Open Terminal**
2. **Navigate to ComfyUI**:
   ```bash
   cd ~/Documents/ComfyUI
   ```
3. **Launch ComfyUI**:
   ```bash
   ./launch_m1.sh
   ```
4. **Open browser**: `http://127.0.0.1:8188`
5. **Load workflow and process NFTs**
6. **When done, stop server**: `Ctrl+C` in Terminal

### Updating ComfyUI:

```bash
cd ~/Documents/ComfyUI
git pull
pip install -r requirements.txt --upgrade
```

### Updating Custom Nodes:

```bash
cd custom_nodes/ComfyUI-AnimateDiff-Evolved
git pull
pip install -r requirements.txt --upgrade
cd ../ComfyUI-VideoHelperSuite
git pull
pip install -r requirements.txt --upgrade
cd ../..
```

---

## Quick Reference Commands

### Launch ComfyUI:
```bash
cd ~/Documents/ComfyUI && ./launch_m1.sh
```

### Stop ComfyUI:
```
Ctrl+C (in Terminal)
```

### Check if running:
```bash
curl http://127.0.0.1:8188
```

### Find output files:
```bash
open ~/Documents/ComfyUI/output/
```

### Check GPU usage (in another Terminal tab):
```bash
sudo powermetrics --samplers gpu_power -i 1000 -n 1
```

---

## Performance Expectations (M1 24GB)

| Task | Expected Time |
|------|---------------|
| ComfyUI startup | 5-10 seconds |
| Load workflow | Instant |
| Load NFT image | Instant |
| Generate 16-frame animation | 3-5 minutes |
| Process 10 NFTs | 30-50 minutes |
| Process 100 NFTs | 5-8 hours |
| Full collection (4,200 NFTs) | 210-350 hours (9-15 days) |

**Tips for speed**:
- Close all other applications
- Use `--highvram` flag (you have 24GB)
- Reduce steps from 15 to 12 (slight quality tradeoff)
- Process overnight in batches

---

## Next Steps

✅ ComfyUI installed and working
✅ Models downloaded
✅ First NFT animated

**Now you're ready to**:
1. Process your test batch (10-20 NFTs)
2. Review results and adjust settings
3. Get feedback from team
4. Scale to larger batches

See `TEST_BATCH_SETUP.md` for detailed test batch instructions.

---

## Getting Help

### Resources:
- ComfyUI Official Docs: https://docs.comfy.org/
- AnimateDiff Guide: https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved
- ComfyUI Reddit: r/comfyui
- ComfyUI Discord: https://discord.gg/comfyorg

### Common Questions:
- See `/research/M1_MAC_COMPATIBILITY.md` for M1-specific issues
- See `/workflows/README_WORKFLOWS.md` for workflow customization
- See `/research/COMFYUI_CAPABILITIES.md` for technical deep-dive

---

**Congratulations!** You're now set up to animate your KEKTECH NFT collection! 🐸🎬

