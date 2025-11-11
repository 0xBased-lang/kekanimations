#!/usr/bin/env python3
"""
Artisanal NFT Animation Playground - Backend API
FastAPI server for real-time effect processing and ComfyUI integration
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Initialize FastAPI app
app = FastAPI(
    title="NFT Animation Playground API",
    description="Interactive animation studio for hand-crafted premium NFT animations",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
UPLOAD_DIR = Path(__file__).parent / "uploads"
OUTPUT_DIR = Path(__file__).parent / "outputs"
PREVIEW_DIR = Path(__file__).parent / "previews"

# Create directories
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
PREVIEW_DIR.mkdir(exist_ok=True)


# Pydantic models for request/response
class EffectConfig(BaseModel):
    """Configuration for an animation effect"""
    type: str  # breathing, fire, sparkles, glow, rotation, etc.
    intensity: float = 1.0
    parameters: Dict[str, Any] = {}


class AnimationRequest(BaseModel):
    """Request for generating animation with effects"""
    image_filename: str
    effects: List[EffectConfig]
    num_frames: int = 24
    fps: int = 12
    quality_target: int = 85


class PresetConfig(BaseModel):
    """Preset animation configuration"""
    name: str
    description: str
    effects: List[EffectConfig]
    num_frames: int = 24
    fps: int = 12


# Built-in presets
PRESETS = {
    "dramatic": PresetConfig(
        name="Dramatic",
        description="Fire particles + rotation + glow for legendary NFTs",
        effects=[
            EffectConfig(type="breathing", intensity=0.02),
            EffectConfig(type="fire", intensity=1.5, parameters={"particle_count": 50}),
            EffectConfig(type="rotation", intensity=5.0, parameters={"degrees": 10}),
            EffectConfig(type="glow", intensity=2.0, parameters={"color": [255, 0, 0]})
        ]
    ),
    "subtle": PresetConfig(
        name="Subtle",
        description="Gentle breathing + sparkles for elegant NFTs",
        effects=[
            EffectConfig(type="breathing", intensity=0.015),
            EffectConfig(type="sparkles", intensity=0.5, parameters={"particle_count": 20})
        ]
    ),
    "psychedelic": PresetConfig(
        name="Psychedelic",
        description="Color shift + warp + kaleidoscope effects",
        effects=[
            EffectConfig(type="breathing", intensity=0.02),
            EffectConfig(type="color_shift", intensity=1.0, parameters={"hue_shift": 180}),
            EffectConfig(type="warp", intensity=0.5, parameters={"frequency": 2})
        ]
    ),
    "3d": PresetConfig(
        name="3D",
        description="Holographic rotation + depth mapping",
        effects=[
            EffectConfig(type="rotation_3d", intensity=1.0, parameters={"axis": "y", "degrees": 360}),
            EffectConfig(type="holographic", intensity=0.8)
        ]
    ),
    "minimal": PresetConfig(
        name="Minimal",
        description="Breathing only - elegant and clean",
        effects=[
            EffectConfig(type="breathing", intensity=0.02)
        ]
    )
}


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "NFT Animation Playground API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "upload": "/api/upload",
            "breathing": "/api/effects/breathing",
            "preview": "/api/effects/preview",
            "export": "/api/export/gif",
            "presets": "/api/presets"
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "upload_dir": str(UPLOAD_DIR),
        "output_dir": str(OUTPUT_DIR),
        "presets_available": list(PRESETS.keys())
    }


@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload NFT image for animation"""
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

        return {
            "success": True,
            "filename": file.filename,
            "path": str(file_path),
            "size": len(content)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/presets")
async def get_presets():
    """Get all available animation presets"""
    return {
        "presets": {
            name: preset.dict()
            for name, preset in PRESETS.items()
        }
    }


@app.get("/api/presets/{preset_name}")
async def get_preset(preset_name: str):
    """Get specific preset configuration"""
    if preset_name not in PRESETS:
        raise HTTPException(status_code=404, detail=f"Preset '{preset_name}' not found")

    return PRESETS[preset_name].dict()


@app.post("/api/effects/breathing")
async def apply_breathing_effect(request: AnimationRequest):
    """
    Apply breathing effect to uploaded image
    Uses validated code from scripts/test_mesh_deformation.py
    """
    try:
        # Import breathing effect processor
        from effects.breathing_effect import apply_breathing

        # Get uploaded image path
        image_path = UPLOAD_DIR / request.image_filename
        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"Image '{request.image_filename}' not found")

        # Extract breathing config
        breathing_config = next(
            (effect for effect in request.effects if effect.type == "breathing"),
            EffectConfig(type="breathing", intensity=0.02)
        )

        # Apply breathing effect
        output_frames = await apply_breathing(
            image_path=str(image_path),
            intensity=breathing_config.intensity,
            num_frames=request.num_frames,
            fps=request.fps
        )

        return {
            "success": True,
            "frames_generated": len(output_frames),
            "output_dir": str(OUTPUT_DIR),
            "preview_available": True
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Breathing effect failed: {str(e)}")


@app.post("/api/effects/preview")
async def generate_preview(request: AnimationRequest):
    """
    Generate low-res preview for real-time feedback
    Optimized for speed (<1 second response)
    """
    try:
        # Import preview generator
        from effects.preview_generator import generate_preview

        # Get uploaded image
        image_path = UPLOAD_DIR / request.image_filename
        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"Image '{request.image_filename}' not found")

        # Generate low-res preview (256x256 for speed)
        preview_path = await generate_preview(
            image_path=str(image_path),
            effects=request.effects,
            num_frames=8,  # Fewer frames for preview
            size=(256, 256)  # Low res for speed
        )

        return FileResponse(
            preview_path,
            media_type="image/gif",
            headers={"Cache-Control": "no-cache"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preview generation failed: {str(e)}")


@app.post("/api/export/gif")
async def export_final_gif(request: AnimationRequest):
    """
    Export final high-quality GIF with all effects applied
    Includes Playwright quality validation
    """
    try:
        # Import export generator
        from export_generator import generate_final_animation

        # Get uploaded image
        image_path = UPLOAD_DIR / request.image_filename
        if not image_path.exists():
            raise HTTPException(status_code=404, detail=f"Image '{request.image_filename}' not found")

        # Generate final animation
        result = await generate_final_animation(
            image_path=str(image_path),
            effects=request.effects,
            num_frames=request.num_frames,
            fps=request.fps,
            quality_target=request.quality_target,
            output_dir=str(OUTPUT_DIR)
        )

        return {
            "success": True,
            "output_path": result["output_path"],
            "quality_score": result["quality_score"],
            "file_size": result["file_size"],
            "validation_passed": result["quality_score"] >= request.quality_target,
            "download_url": f"/api/download/{Path(result['output_path']).name}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download generated animation file"""
    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found")

    return FileResponse(
        file_path,
        media_type="image/gif",
        filename=filename
    )


if __name__ == "__main__":
    print("🚀 Starting NFT Animation Playground API...")
    print(f"📁 Upload directory: {UPLOAD_DIR}")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"🎨 Presets available: {', '.join(PRESETS.keys())}")
    print("\n🌐 API will be available at: http://localhost:8000")
    print("📖 API docs: http://localhost:8000/docs")
    print("\nPress CTRL+C to stop\n")

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )
