# KEKTECH NFT Layer-Based Animation Framework

**Document Version**: 1.0
**Date**: November 2025
**Status**: Implementation Ready
**Approach**: Layer-based modular animation (10x more efficient than image-based)

---

## Executive Summary

Instead of processing 4,200 composite images through ComfyUI (210-420 hours), we will animate ~104 original layer files and recombine them programmatically (20-40 hours total). This approach guarantees perfect quality, consistency, and allows for modular adjustments.

---

## 1. Complete Layer Inventory & Exception Rules

### 1.1 Layer File Structure

```
Total Unique Layers: 104 files
Resolution: 2048×2048 PNG RGBA
Perfect alignment: All use same canvas
Transparency: Full alpha channel support
```

### 1.2 Layer Categories & Animation Potential

| Layer Type | Count | Animation Priority | Motion Type |
|------------|-------|-------------------|-------------|
| **Body** | 6 | HIGH | Breathing, idle sway, glow effects |
| **Background** | 11 | MEDIUM | Parallax, color shift (psychedelic) |
| **Clothes** | 17 | LOW | Subtle fabric movement |
| **Eyes** | 8 | HIGH | Blinking, looking, glow |
| **Glasses** | 4+4* | LOW | Shimmer, lens flare |
| **Hat** | 14 | MEDIUM | Bounce, tilt |
| **Special** | 6 | HIGH | Particle effects, glow |
| **Style** | 3+3* | LOW | Subtle effects |
| **Tattoo** | 5 | LOW | Shimmer, pulse |
| **Tools** | 11+12* | MEDIUM | Rotation, swing |

*Additional variants for x-ray body type

### 1.3 Body Type Exception Rules

#### **RIP Body (Suicide/Dead Character)**
```python
RIP_EXCEPTIONS = {
    "no_tools": True,      # Dead character doesn't hold tools
    "no_hat": True,        # No hat on RIP body
    "allowed_layers": ["background", "body", "tattoo", "style", "clothes", "eyes", "glasses", "special"]
}
```

#### **X-Ray Body (Transparent/Skeleton)**
```python
XRAY_EXCEPTIONS = {
    "no_eyes": True,                    # Transparent body shows skeleton, not eyes
    "no_astral_background": True,       # Cannot use astral background
    "use_special_glasses": True,        # Must use glasses_for_xray folder
    "use_special_style": True,          # Must use style_for_xray folder
    "use_special_tools": True,          # Must use tools_for_xray folder
    "special_folders": {
        "glasses": "glasses_for_xray",  # 4 variants
        "style": "style_for_xray",      # 3 variants
        "tools": "tools_for_xray"       # 12 variants
    }
}
```

#### **Special Attribute Constraints**
```python
SPECIAL_CONSTRAINTS = {
    "hairy_special_bodies": ["normie", "ghastly"],  # Only these can have hairy
    "rare_whitebeard_special_bodies": ["diablo", "BasedAI", "x-ray"],
    "rare_hairy_special_bodies": ["diablo", "BasedAI", "x-ray"]
}
```

---

## 2. Layer Compositing Order

### Standard Stacking (Bottom to Top)
```
1. background     (base layer, opaque)
2. body           (main character)
3. tattoo         (on body)
4. style          (facial/body modifications)
5. clothes        (worn items)
6. tools          (held items - except for RIP)
7. eyes           (facial feature - except for x-ray)
8. glasses        (facial overlay)
9. hat            (head accessory - except for RIP)
10. special       (top effects layer)
```

---

## 3. Animation Template Strategy

### 3.1 Required Animation Templates (~35 total)

#### Body Animations (8 templates)
```python
BODY_ANIMATIONS = {
    "normie": {
        "breathing": {"denoise": 0.35, "motion": 0.4, "frames": 16},
        "idle_sway": {"denoise": 0.40, "motion": 0.5, "frames": 24}
    },
    "ghastly": {
        "ethereal_float": {"denoise": 0.45, "motion": 0.6, "frames": 20}
    },
    "diablo": {
        "fire_glow": {"denoise": 0.50, "motion": 0.7, "frames": 16}
    },
    "BasedAI": {
        "digital_pulse": {"denoise": 0.40, "motion": 0.5, "frames": 12}
    },
    "RIP": {
        "subtle_fade": {"denoise": 0.30, "motion": 0.3, "frames": 24}
    },
    "x-ray": {
        "skeleton_glow": {"denoise": 0.45, "motion": 0.8, "frames": 16},
        "bone_pulse": {"denoise": 0.40, "motion": 0.6, "frames": 20}
    }
}
```

#### Eye Animations (12 templates)
```python
EYE_ANIMATIONS = {
    "standard": ["blink", "look_around", "wink"],
    "special": {
        "baked": "half_lid_float",
        "diabolic": "red_glow_pulse",
        "wrecked": "erratic_movement"
    }
    # Note: x-ray body has no eyes
}
```

#### Background Animations (5 selective)
```python
BACKGROUND_ANIMATIONS = {
    "psychedelic": "color_shift",
    "creature_cloud": "cloud_movement",
    "astral": "star_twinkle",  # Not for x-ray
    "UV": "neon_pulse",
    "void": "subtle_particles"
}
```

#### Accessory Animations (8 templates)
```python
ACCESSORY_ANIMATIONS = {
    "hat": "gentle_bounce",           # Not for RIP
    "glasses": "lens_shimmer",
    "tools": "swing_rotation",        # Not for RIP
    "special_honk": "horn_particles",
    "special_spyware": "scan_effect",
    "tattoo": "subtle_glow"
}
```

---

## 4. Implementation Workflow

### Phase 1: Template Creation (Week 1)

#### Step 1: Create Animation Test Set
```python
# Select one NFT from each body type for testing
test_nfts = {
    "normie": "KEKTECH#1234",  # Standard case
    "ghastly": "KEKTECH#2345",  # Ethereal animation
    "diablo": "KEKTECH#3456",   # Fire effects
    "BasedAI": "KEKTECH#4567",  # Digital effects
    "RIP": "KEKTECH#5678",      # No tools/hat
    "x-ray": "KEKTECH#6789"     # Special folders, no eyes
}
```

#### Step 2: ComfyUI Workflow per Layer Type
```python
def create_layer_animation(layer_path, animation_type):
    """
    1. Load PNG with transparency
    2. Apply AnimateDiff with specific parameters
    3. Use ControlNet Canny for edge preservation
    4. Export as transparent video/image sequence
    """
    params = ANIMATION_PARAMS[animation_type]

    workflow = {
        "denoise": params["denoise"],
        "motion_scale": params["motion"],
        "frames": params["frames"],
        "controlnet": "canny",
        "controlnet_strength": 0.85,
        "preserve_alpha": True
    }

    return animated_layer
```

### Phase 2: Layer Processing (Week 2)

#### Step 3: Batch Process All Unique Layers
```python
layers_to_animate = [
    ("body/normie.png", "breathing"),
    ("body/ghastly.png", "ethereal_float"),
    ("body/diablo.png", "fire_glow"),
    ("body/BasedAI.png", "digital_pulse"),
    ("body/RIP.png", "subtle_fade"),
    ("body/x-ray.png", "skeleton_glow"),

    ("eyes/blue.png", "blink"),
    ("eyes/baked.png", "half_lid_float"),
    # ... (35 total animations)
]
```

### Phase 3: Recombination System (Week 3)

#### Step 4: Build Recombination Engine
```python
def generate_nft_animation(nft_id, metadata):
    """
    Read metadata → Load animated layers → Composite → Export
    """

    # Parse metadata
    traits = metadata["attributes"]
    body_type = get_trait(traits, "Body")

    # Apply exception rules
    if body_type == "RIP":
        traits = remove_traits(traits, ["Tools", "Hat"])
    elif body_type == "x-ray":
        traits = remove_trait(traits, "Eyes")
        traits = use_xray_folders(traits)

    # Load animated layers
    animated_layers = []
    for layer_type in LAYER_ORDER:
        trait_value = get_trait(traits, layer_type)
        if trait_value and trait_value != "none":
            layer_path = get_animated_layer_path(layer_type, trait_value, body_type)
            animated_layers.append(load_animated_layer(layer_path))

    # Composite frames
    frames = []
    for frame_idx in range(16):  # 16 frame animation
        frame = Image.new('RGBA', (2048, 2048), (0, 0, 0, 0))
        for layer in animated_layers:
            frame = Image.alpha_composite(frame, layer.get_frame(frame_idx))
        frames.append(frame)

    # Export as GIF
    save_as_gif(frames, f"output/{nft_id}.gif", fps=12)
```

### Phase 4: Batch Generation (Week 4)

#### Step 5: Process All 4,200 NFTs
```python
def batch_generate_all():
    """
    Process all NFTs using animated layer templates
    """

    # Load all metadata
    metadata_files = glob.glob("output2/*.json")

    # Process in batches for memory efficiency
    batch_size = 100
    for batch in chunks(metadata_files, batch_size):
        for metadata_file in batch:
            nft_id = extract_id(metadata_file)
            metadata = load_json(metadata_file)

            try:
                generate_nft_animation(nft_id, metadata)
                print(f"✓ Generated {nft_id}")
            except Exception as e:
                print(f"✗ Failed {nft_id}: {e}")
                log_error(nft_id, e)

    print(f"Completed: {success_count}/4200")
```

---

## 5. Quality Assurance

### Validation Checklist

#### Layer Animation Quality
- [ ] Each body type breathing looks natural
- [ ] Eyes blink without distortion
- [ ] Transparency preserved in all frames
- [ ] No color bleeding between layers
- [ ] Motion is smooth and looping

#### Exception Rules Validation
- [ ] RIP bodies have no tools or hats
- [ ] X-ray bodies have no eyes
- [ ] X-ray uses special accessory folders
- [ ] Special attributes only on correct bodies

#### Technical Validation
- [ ] All 4,200 GIFs generated
- [ ] File sizes reasonable (2-5MB)
- [ ] Perfect loops (no jump at end)
- [ ] Consistent frame rate (12 fps)

---

## 6. Advantages of Layer-Based Approach

### Quality
- **Perfect preservation**: No degradation from reprocessing
- **Perfect alignment**: All layers pixel-perfect
- **Perfect transparency**: Alpha channels maintained
- **Consistent quality**: Same animation for all NFTs

### Efficiency
- **Time**: 20-40 hours vs 200-400 hours (10x faster)
- **Compute**: Process 35 templates vs 4,200 images
- **Storage**: Reuse animated templates
- **Scalability**: Easy to adjust and regenerate

### Flexibility
- **Modular**: Can update individual layer animations
- **Versioning**: Create different animation styles
- **Customization**: Special animations for rare NFTs
- **Future-proof**: Add new animation types easily

---

## 7. ComfyUI Workflow Configuration

### Base Workflow for Layer Animation
```json
{
  "model": "SD 1.5 (optimized for illustrations)",
  "vae": "standard",
  "positive_prompt": "perfect quality, smooth animation, {layer_specific_prompt}",
  "negative_prompt": "distortion, morphing, color change, artifacts",
  "animatediff": {
    "model": "mm_sd_v15_v3.ckpt",
    "context_length": 16,
    "frames": 16,
    "closed_loop": true
  },
  "controlnet": {
    "type": "canny",
    "strength": 0.85,
    "preprocessor": "canny_edge"
  },
  "output": {
    "format": "png_sequence",
    "preserve_alpha": true,
    "fps": 12
  }
}
```

### Layer-Specific Parameters
```python
LAYER_PARAMS = {
    "body": {
        "denoise": 0.35,
        "motion_scale": 0.4,
        "prompt_addon": "character breathing, subtle movement"
    },
    "eyes": {
        "denoise": 0.30,
        "motion_scale": 0.6,
        "prompt_addon": "blinking eyes, natural eye movement"
    },
    "background": {
        "denoise": 0.45,
        "motion_scale": 0.3,
        "prompt_addon": "atmospheric movement, parallax"
    }
}
```

---

## 8. Next Steps

### Immediate Actions (This Week)
1. Set up ComfyUI with AnimateDiff and ControlNet
2. Test single layer animation with transparency
3. Verify recombination preserves quality
4. Create first complete NFT animation

### Week 1 Deliverables
- [ ] 6 body type animations
- [ ] 8 eye animations
- [ ] Test recombination script
- [ ] Quality validation

### Week 2 Deliverables
- [ ] All 35 animation templates
- [ ] Exception rules implemented
- [ ] Batch processing script

### Week 3-4 Deliverables
- [ ] 100 NFT validation batch
- [ ] Full 4,200 collection
- [ ] Quality report
- [ ] Final delivery

---

**Document Status**: Ready for implementation
**Estimated Timeline**: 4 weeks
**Expected Quality**: 95%+ excellent animations
**Risk Level**: Low (proven approach)