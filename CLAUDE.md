# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Type**: ComfyUI Workflow Research & Development Repository
**Goal**: Automate animation of 4,200 KEKTECH Pepe NFTs using AI-generated motion
**Stage**: Research Phase (proven concept, scaling preparation)
**Hardware**: M1 Mac with 24GB unified memory
**Delivery**: JSON workflow files, comprehensive documentation, setup guides

## Core Architecture

This is a **workflow configuration and documentation project**, not traditional software. The deliverables are:

1. **Reusable ComfyUI Workflows** (`workflows/`): JSON files importable into ComfyUI for consistent, reproducible animation generation
2. **Setup & Operations Documentation**: Multi-level guides from quick-start to deep technical reference
3. **Technical Research**: Capabilities analysis and M1-specific optimization documentation

### Main Deliverable: The Animation Workflow

**File**: `workflows/01_simple_nft_animation_m1.json`

**Processing Flow**:
```
NFT PNG (512×512)
    ↓
Stable Diffusion 1.5 (image-to-image with denoise 0.45)
    ↓
AnimateDiff (16 frames, motion scale 1.0)
    ↓
VAE Decode + Frame Combine
    ↓
GIF Output (512×512, 12 FPS, ~2-5MB)
```

**Performance**: 3-5 minutes per NFT on M1 with --force-fp16

**Key Design Decisions**:
- **16-frame context**: M1 memory sweet spot (24GB unified memory)
- **Denoise 0.45**: Preserve character identity while enabling animation
- **Steps 15**: Speed optimization without sacrificing quality
- **512×512 native**: Matches original NFT resolution

### Technology Stack

- **ComfyUI**: Node-based Stable Diffusion UI (installed locally, user manages ComfyUI directory)
- **AnimateDiff**: Motion generation via custom node (ComfyUI-AnimateDiff-Evolved)
- **Stable Diffusion 1.5**: Foundation model for image generation
- **Python 3.11**: M1-optimized runtime (via Homebrew)
- **PyTorch with MPS**: GPU acceleration leveraging Apple Silicon
- **Custom Nodes**: VideoHelperSuite for frame combining and GIF output

## Development Setup

### First-Time Installation (30-60 minutes)

Follow **SETUP_GUIDE_M1.md** in the repo for step-by-step instructions. Key steps:

1. Install Homebrew, Python 3.11, Git
2. Clone ComfyUI to user's local directory (e.g., `~/Documents/ComfyUI`)
3. Create Python 3.11 venv inside ComfyUI
4. Download models (~6GB total):
   - Stable Diffusion 1.5 checkpoint
   - AnimateDiff motion model (mm_sd_v15_v2.ckpt)
   - VAE model (optional, improves quality)
5. Install custom nodes:
   - ComfyUI-AnimateDiff-Evolved
   - ComfyUI-VideoHelperSuite
6. Create M1 launch script with optimization flags

### M1 Launch Requirements

ComfyUI must launch with these flags to utilize MPS (Metal Performance Shaders):

```bash
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
python main.py --force-fp16 --use-split-cross-attention --highvram --preview-method auto
```

**What these do**:
- `--force-fp16`: Half-precision float, ~2× speed on M1
- `--use-split-cross-attention`: Reduce memory usage
- `--highvram`: Use all available unified memory
- `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0`: Prevent MPS memory fragmentation

### Running Workflows

1. Launch ComfyUI: `cd ~/Documents/ComfyUI && ./launch_m1.sh`
2. Open browser: `http://127.0.0.1:8188`
3. Load workflow JSON from `kekanimations/workflows/`
4. Replace "LoadImage" node with target NFT file
5. Click "Queue Prompt" (3-5 min per NFT)
6. GIF saves to `ComfyUI/output/`

**No build, test, or CI/CD needed**: This is visual/creative work with manual quality evaluation.

## Documentation Organization

All documentation follows a **user-journey approach** for maximum accessibility:

| Document | Audience | Purpose | Time |
|----------|----------|---------|------|
| **QUICKSTART.md** | New users | Start here—path selection (M1 vs cloud) | 5 min |
| **SETUP_GUIDE_M1.md** | Installers | Complete installation walkthrough | 30-60 min |
| **TEST_BATCH_SETUP.md** | Operators | Running first 10-20 NFT batch | 2-4 hours |
| **workflows/README_WORKFLOWS.md** | Configurers | Customizing prompts and parameters | 20 min |
| **research/COMFYUI_CAPABILITIES.md** | Architects | Deep tech reference—4 workflow variants | Reference |
| **research/M1_MAC_COMPATIBILITY.md** | Troubleshooters | M1-specific solutions and workarounds | Reference |
| **research/BRAINSTORMING_QUESTIONS.md** | Planners | Strategic decisions and scaling options | Reference |

## Workflow Development Workflow

### Phase 1: Setup & Test (Week 1)
- Install ComfyUI with M1 optimizations
- Download ~6GB models
- Test batch: 10-20 NFTs with mixed rarities
- Visual quality evaluation
- Confirm processing time acceptable (~3-5 min/NFT)

### Phase 2: Priority Batch (Week 2)
- Process 50-100 rarest/most valuable NFTs
- Use for marketing launch and community preview
- Overnight processing (~8-12 hours continuous)
- Gather feedback

### Phase 3: Full Collection (Week 3-4)
- **Option A**: Continue M1 processing (9-15 days continuous)
- **Option B**: Scale to cloud GPU (RunPod/Vast.ai, 24-48 hours, ~$20 cost)
- **Option C**: Hybrid (rare on M1, common on cloud for speed)

## Workflow Customization

### Current Workflow Parameters (01_simple_nft_animation_m1.json)

**Stable Diffusion Settings**:
- **Denoise**: 0.45 (balance between character preservation and motion generation)
- **Steps**: 15 (fast, quality is good at this level)
- **CFG Scale**: 7.0 (guidance strength—how much to follow prompt)
- **Sampler**: DPM++ 2M Karras (good quality/speed tradeoff)

**AnimateDiff Settings**:
- **Context length**: 16 (M1 hard limit due to 24GB unified memory)
- **Motion model**: mm_sd_v15_v2.ckpt (best for SD 1.5)
- **Motion scale**: 1.0 (subtle movement—higher = more dramatic)
- **Video combine FPS**: 12 (smooth looping, 16 frames = 1.3 sec duration)

### Customization Options

**For Rare/Legendary NFTs** (More dramatic animation):
- Increase denoise: 0.50-0.60 (more deviation from original)
- Increase steps: 20-25 (better quality, +1-2 min processing)
- Adjust positive prompt: Add emotive words (`ethereal`, `magical`, `epic`)

**For Common NFTs** (Subtle, fast):
- Decrease denoise: 0.30-0.40 (minimal change)
- Decrease steps: 12-15 (3-5x speed boost)
- Use generic/calm prompt to reduce processing variation

**Style Modifications** (via positive prompt):
- Laser eyes: `with glowing red eyes, laser beams`
- Sparkles: `magical particles, shimmer, sparkles`
- Dramatic: `cinematic lighting, epic, dynamic`
- Psychedelic: `trippy, colorful patterns, rainbow`

## M1 Performance & Limits

### Processing Time

| Scope | Time | Steps | Denoise |
|-------|------|-------|---------|
| Single NFT | 3-5 min | 15 | 0.45 |
| 10 NFTs | 30-50 min | 15 | 0.45 |
| 100 NFTs | 5-8 hours | 15 | 0.45 |
| 1,000 NFTs | 50-80 hours | 15 | 0.45 |
| Full collection (4,200) | 210-420 hours (9-18 days) | 15 | 0.45 |

**Actual time depends on**: System load, exact model configuration, seed complexity, prompt length

### Memory Management

**M1 24GB Unified Memory**:
- AnimateDiff context limited to 16 frames (higher = OOM)
- Use `--highvram` flag and `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0`
- Close other applications during processing
- Monitor Activity Monitor for memory pressure

### Known M1 Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Black frames in GIF | Context too high or denoise too low | Reduce context to 8, raise denoise to 0.50 |
| Out of memory crash | Insufficient unified memory | Close background apps, reduce context, restart ComfyUI |
| CPU fallback (slow) | PyTorch MPS not initialized | Verify: `python3 -c "import torch; print(torch.backends.mps.is_available())"` |
| Slow generation | Not using fp16 | Confirm `--force-fp16` flag set in launch script |
| Character distorted | Denoise too high | Lower to 0.35-0.40, increase CFG scale |
| Seed not working | GPU randomization | Set seed before queuing each prompt |

## File Management

### Repository Structure

```
kekanimations/
├── CLAUDE.md                        ← You are here
├── QUICKSTART.md                    ← Entry point for new users
├── SETUP_GUIDE_M1.md               ← Installation walkthrough
├── TEST_BATCH_SETUP.md             ← First batch workflow
│
├── workflows/                       ← JSON workflow files
│   ├── 01_simple_nft_animation_m1.json   (CURRENT—M1 optimized)
│   └── README_WORKFLOWS.md
│
├── research/                        ← Technical reference
│   ├── COMFYUI_CAPABILITIES.md      (4 workflow strategies)
│   ├── M1_MAC_COMPATIBILITY.md      (M1-specific deep dive)
│   └── BRAINSTORMING_QUESTIONS.md   (Planning & strategy)
│
├── examples/                        ← Sample outputs (placeholder)
├── scripts/                         ← Automation scripts (placeholder)
└── docs/                           ← Additional docs (placeholder)
```

### ComfyUI Directory Structure (User's Local Install)

```
~/Documents/ComfyUI/                 ← User creates this
├── models/
│   ├── checkpoints/                ← SD 1.5 checkpoint (~4GB)
│   ├── animatediff_models/         ← AnimateDiff models (~400MB)
│   ├── vae/                        ← VAE models (optional)
│   └── clip/
├── custom_nodes/
│   ├── ComfyUI-AnimateDiff-Evolved
│   └── ComfyUI-VideoHelperSuite
├── output/                         ← Generated GIFs appear here
├── venv/                           ← Python environment
├── launch_m1.sh                    ← User creates with env vars
└── [Workflow JSONs imported here]
```

**Important**: The `kekanimations/workflows/` directory contains the JSON files. Users import these into ComfyUI manually via the web interface.

## Key M1 Considerations for Development

### Environment Variables (Required)

Always set before launching ComfyUI:
```bash
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0  # Prevent memory fragmentation
export PYTORCH_ENABLE_MPS_FALLBACK=1         # Fallback to CPU if needed
```

### PyTorch MPS Verification

Before claiming M1 optimization works:
```python
import torch
print(f"MPS Available: {torch.backends.mps.is_available()}")
print(f"MPS Built: {torch.backends.mps.is_built()}")
print(f"Device: {torch.device('mps')}")
```

### GPU Acceleration

M1 uses **unified memory** (single pool for CPU & GPU):
- No separate VRAM like NVIDIA
- All memory is accessible to GPU
- `--highvram` flag tells PyTorch to use all available
- MPS (Metal Performance Shaders) provides hardware acceleration

## Development Commands & Workflows

### One-Time Setup

```bash
# Clone ComfyUI (user's choice of location)
git clone https://github.com/comfyanonymous/ComfyUI ~/Documents/ComfyUI
cd ~/Documents/ComfyUI

# Python environment
python3.11 -m venv venv
source venv/bin/activate

# Install PyTorch with MPS
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu

# ComfyUI dependencies
pip install -r requirements.txt

# Custom nodes
cd custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite

cd ComfyUI-AnimateDiff-Evolved && pip install -r requirements.txt && cd ..
cd ComfyUI-VideoHelperSuite && pip install -r requirements.txt && cd ../..

# Create launch script
cat > launch_m1.sh << 'EOF'
#!/bin/bash
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
source venv/bin/activate
python main.py --force-fp16 --use-split-cross-attention --highvram --preview-method auto
EOF

chmod +x launch_m1.sh
```

### Regular Workflow

```bash
cd ~/Documents/ComfyUI
./launch_m1.sh
# Open http://127.0.0.1:8188 in browser
```

### Update ComfyUI & Custom Nodes

```bash
cd ~/Documents/ComfyUI
git pull
pip install -r requirements.txt --upgrade

cd custom_nodes/ComfyUI-AnimateDiff-Evolved
git pull && pip install -r requirements.txt --upgrade

cd ../ComfyUI-VideoHelperSuite
git pull && pip install -r requirements.txt --upgrade
```

## Quality Assurance

### No Automated Testing
This is a visual/creative project. Quality is evaluated manually:

**Success Criteria for Test Batch**:
- ✅ 80%+ of outputs look good (12+ of 15 NFTs)
- ✅ Processing time acceptable (<10 min per NFT)
- ✅ Characters remain recognizable
- ✅ No crashes or technical errors
- ✅ Community/stakeholder approval

**Visual Quality Checklist**:
- Character is recognizable from original
- Motion is smooth and natural
- No artifacts, distortions, or color shifts
- GIF loops smoothly without jumps
- Style consistent with original NFT

## Future Development

### Planned Workflows (Not Yet Implemented)

**02_controlnet_preservation.json**: ControlNet for exact character preservation
**03_trait_based_animation.json**: Different animation intensity per NFT trait
**04_rarity_tiered_effects.json**: Animation style based on rarity score
**05_batch_processing.json**: Automated batch folder processing

### Future Automation Scripts

Planned in `/scripts/` directory:
- Python batch processor (folder input → folder output)
- Trait-based workflow selector (automatically pick workflow variant)
- Output validator (check for artifacts, quality issues)
- Platform uploader integration

## When Adding Features

### Workflow Changes
1. Test on actual M1 hardware (not in theory)
2. Include performance impact assessment
3. Document new parameters and rationale
4. Create sample outputs demonstrating change
5. Update relevant workflow docs

### Documentation Updates
1. Follow existing MD structure and style
2. Include time estimates and hardware requirements
3. Provide step-by-step instructions with screenshots
4. Add troubleshooting sections for common issues
5. Link to related documentation

### Research Documentation
1. Document decisions and trade-offs
2. Include test results and performance data
3. Note M1-specific considerations
4. Link to external resources/papers
5. Date entries for context

## External Resources

- **ComfyUI Official**: https://docs.comfy.org/
- **ComfyUI Discord**: https://discord.gg/comfyorg
- **AnimateDiff Repo**: https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved
- **VideoHelperSuite**: https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite
- **Stable Diffusion Docs**: https://huggingface.co/docs/diffusers
- **KEKTECH NFTs**: https://www.kektech.xyz/

## Git Workflow

**Current Branch**: `claude/nft-animation-comfyui-research-011CUs9E4sbw4LDpoJU7RYNL`

**Commit Strategy**:
- Document research findings and decisions
- Include workflow JSON files in commits
- Update relevant MD files with each phase
- Reference specific test results in commit messages

**Recent Commits**:
- Add comprehensive quick start guide
- Add M1-optimized workflows and complete setup documentation
- Initial research: ComfyUI capabilities for KEKTECH NFT animation

## Notes for Claude Code

### When Making Changes
- **Test on M1 hardware**: Theory is not proof; verify on actual device
- **Document M1 implications**: Always note if something is M1-specific
- **Include performance data**: Processing time, memory usage, etc.
- **Update documentation**: Guides are living documents

### When Troubleshooting
1. Check M1 optimization flags (PYTORCH_MPS_HIGH_WATERMARK_RATIO, --force-fp16)
2. Verify all models exist and are accessible
3. Check ComfyUI logs for specific errors
4. Consult M1_MAC_COMPATIBILITY.md for known issues
5. Verify PyTorch MPS is available with test script above

### When Documenting
- Follow user-journey approach (new users → operators → architects)
- Include time estimates and resource requirements
- Provide step-by-step instructions
- Add troubleshooting sections for edge cases
- Link to relevant technical deep-dives

## Immediate Next Steps

**Phase 1 Completion**:
- ✅ Research complete (all questions answered)
- ✅ Workflow created and M1-optimized
- ✅ Setup documentation comprehensive
- ⏳ **Run test batch** (10-20 NFTs—2-4 hours)
- ⏳ Evaluate results and gather feedback
- ⏳ Create batch automation scripts
- ⏳ Plan Phase 2 (priority batch of 50-100 rarest NFTs)
