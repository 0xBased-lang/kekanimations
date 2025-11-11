#!/bin/bash
# Pixel-Perfect Animation System Setup Script
# M1 Mac optimized installation

set -e

echo "🎨 Setting up Pixel-Perfect NFT Animation System"
echo "================================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version"
echo ""

# Create virtual environment
if [ ! -d "venv-pixel" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv-pixel
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv-pixel/bin/activate

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip upgraded"

# Install core dependencies
echo ""
echo "📦 Installing core dependencies..."
pip install opencv-python opencv-contrib-python > /dev/null 2>&1
echo "  ✅ OpenCV installed"

pip install numpy scikit-image scipy > /dev/null 2>&1
echo "  ✅ NumPy, scikit-image, SciPy installed"

pip install pillow > /dev/null 2>&1
echo "  ✅ Pillow installed"

pip install scikit-learn > /dev/null 2>&1
echo "  ✅ scikit-learn installed (for K-Means)"

# Optional: SAM (large download - 2.4GB)
echo ""
echo "🤖 Segment Anything Model (SAM) installation..."
read -p "Install SAM? (2.4GB download, optional) [y/N]: " install_sam

if [[ $install_sam =~ ^[Yy]$ ]]; then
    echo "Installing SAM (this may take several minutes)..."
    pip install git+https://github.com/facebookresearch/segment-anything.git > /dev/null 2>&1

    # Download SAM model
    if [ ! -f "sam_vit_h_4b8939.pth" ]; then
        echo "Downloading SAM model (2.4GB)..."
        wget -q --show-progress https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
    fi

    echo "✅ SAM installed"
else
    echo "⏭️  SAM installation skipped"
fi

# Create directory structure
echo ""
echo "📁 Creating directory structure..."
mkdir -p masks
mkdir -p scripts
mkdir -p output/breathing_frames
mkdir -p output/fire_particles
mkdir -p output/final_composites
echo "✅ Directories created"

# Verify installations
echo ""
echo "✅ Verifying installations..."
python3 << 'EOF'
import cv2
import numpy as np
from skimage import feature
from PIL import Image
from sklearn.cluster import KMeans

print(f"  ✅ OpenCV: {cv2.__version__}")
print(f"  ✅ NumPy: {np.__version__}")
print(f"  ✅ Pillow: {Image.__version__}")
print(f"  ✅ scikit-learn: KMeans available")

try:
    from segment_anything import SamPredictor
    print(f"  ✅ SAM: Installed")
except ImportError:
    print(f"  ⏭️  SAM: Not installed (optional)")
EOF

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate environment: source venv-pixel/bin/activate"
echo "2. Run analysis: python scripts/batch_mask_generator.py"
echo "3. Generate animations: python scripts/mesh_deformation.py"
echo ""
echo "Documentation: PIXEL_PERFECT_ANIMATION_GUIDE.md"
