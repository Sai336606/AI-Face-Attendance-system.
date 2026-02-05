"""
Setup script for Face Attendance POC
Handles dependency installation and model download
"""
import subprocess
import sys
import os


def install_dependencies():
    """Install required packages"""
    print("=" * 60)
    print("Installing dependencies...")
    print("=" * 60)
    
    # Core dependencies that should install without issues
    packages = [
        "streamlit",
        "mediapipe",
        "onnxruntime",
        "opencv-python",
        "Pillow",
        "numpy",
        "scikit-learn",
        "pandas",
    ]
    
    for package in packages:
        print(f"\nInstalling {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {package}: {e}")
    
    print("\n" + "=" * 60)
    print("Dependency installation complete!")
    print("=" * 60)


def download_arcface_model():
    """Download ArcFace ONNX model"""
    print("\n" + "=" * 60)
    print("Downloading ArcFace model...")
    print("=" * 60)
    
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, "arcface_r100.onnx")
    
    if os.path.exists(model_path):
        print(f"✓ Model already exists at {model_path}")
        return
    
    print("\nModel download options:")
    print("1. Download from GitHub (recommended)")
    print("2. Manual download instructions")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        try:
            import urllib.request
            
            # Using a direct link to a pre-trained ArcFace ONNX model
            # This is a placeholder URL - replace with actual model URL
            url = "https://github.com/onnx/models/raw/main/vision/body_analysis/arcface/model/arcfaceresnet100-8.onnx"
            
            print(f"\nDownloading from {url}...")
            urllib.request.urlretrieve(url, model_path)
            print(f"✓ Model downloaded to {model_path}")
            
        except Exception as e:
            print(f"✗ Download failed: {e}")
            print("\nPlease download manually (see option 2)")
    
    else:
        print("\n" + "=" * 60)
        print("MANUAL DOWNLOAD INSTRUCTIONS")
        print("=" * 60)
        print("\n1. Download an ArcFace ONNX model from one of these sources:")
        print("   - https://github.com/onnx/models")
        print("   - https://github.com/deepinsight/insightface/tree/master/model_zoo")
        print("\n2. Save the model as:")
        print(f"   {model_path}")
        print("\n3. Recommended models:")
        print("   - arcfaceresnet100-8.onnx")
        print("   - w600k_r50.onnx")
        print("=" * 60)


def verify_installation():
    """Verify that all components are working"""
    print("\n" + "=" * 60)
    print("Verifying installation...")
    print("=" * 60)
    
    try:
        import streamlit
        print("✓ Streamlit")
    except ImportError:
        print("✗ Streamlit not installed")
    
    try:
        import mediapipe
        print("✓ MediaPipe")
    except ImportError:
        print("✗ MediaPipe not installed")
    
    try:
        import onnxruntime
        print("✓ ONNX Runtime")
    except ImportError:
        print("✗ ONNX Runtime not installed")
    
    try:
        import cv2
        print("✓ OpenCV")
    except ImportError:
        print("✗ OpenCV not installed")
    
    try:
        import numpy
        print("✓ NumPy")
    except ImportError:
        print("✗ NumPy not installed")
    
    try:
        import sklearn
        print("✓ scikit-learn")
    except ImportError:
        print("✗ scikit-learn not installed")
    
    try:
        import pandas
        print("✓ Pandas")
    except ImportError:
        print("✗ Pandas not installed")
    
    print("=" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FACE ATTENDANCE POC - SETUP")
    print("=" * 60)
    
    install_dependencies()
    download_arcface_model()
    verify_installation()
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("\nTo run the application:")
    print("  streamlit run app.py")
    print("=" * 60)
