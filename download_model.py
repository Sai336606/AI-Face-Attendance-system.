"""
Model Download Helper
Downloads a working ArcFace ONNX model for face embeddings
"""
import os
import urllib.request
import sys


def download_model():
    """Download ArcFace ONNX model"""
    
    # Model directory
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = os.path.join(model_dir, "arcface_r100.onnx")
    
    print("=" * 60)
    print("ArcFace ONNX Model Downloader")
    print("=" * 60)
    
    # Check if model already exists
    if os.path.exists(model_path):
        file_size = os.path.getsize(model_path)
        print(f"\n✓ Model already exists at: {model_path}")
        print(f"  File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
        
        response = input("\nDo you want to re-download? (y/n): ").strip().lower()
        if response != 'y':
            print("Keeping existing model.")
            return
        
        print("Removing existing model...")
        os.remove(model_path)
    
    print("\n" + "=" * 60)
    print("Downloading ArcFace ONNX Model")
    print("=" * 60)
    
    # Direct download URL for ArcFace model from ONNX Model Zoo
    # This is arcfaceresnet100-8 from the ONNX Model Zoo
    url = "https://github.com/onnx/models/raw/main/validated/vision/body_analysis/arcface/model/arcfaceresnet100-8.onnx"
    
    print(f"\nSource: {url}")
    print(f"Destination: {model_path}")
    print("\nDownloading... (this may take a few minutes)")
    
    try:
        # Download with progress
        def reporthook(blocknum, blocksize, totalsize):
            readsofar = blocknum * blocksize
            if totalsize > 0:
                percent = readsofar * 100 / totalsize
                s = f"\r{percent:5.1f}% {readsofar:,} / {totalsize:,} bytes"
                sys.stderr.write(s)
                if readsofar >= totalsize:
                    sys.stderr.write("\n")
            else:
                sys.stderr.write(f"\rRead {readsofar:,} bytes")
        
        urllib.request.urlretrieve(url, model_path, reporthook)
        
        # Verify download
        file_size = os.path.getsize(model_path)
        
        print("\n" + "=" * 60)
        print("✓ Download Complete!")
        print("=" * 60)
        print(f"\nModel saved to: {model_path}")
        print(f"File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
        
        # Verify it's a valid ONNX file
        if file_size < 1000:
            print("\n⚠ WARNING: File size is very small, may be corrupted!")
            return
        
        print("\n✓ Model appears valid!")
        print("\nYou can now run the application:")
        print("  streamlit run app.py")
        
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        print("\nPlease try one of these alternatives:")
        print("\n1. Download manually from:")
        print("   https://github.com/onnx/models/tree/main/validated/vision/body_analysis/arcface")
        print(f"\n2. Save the model as: {model_path}")
        print("\n3. Or try a different model from:")
        print("   https://github.com/deepinsight/insightface/tree/master/model_zoo")


if __name__ == "__main__":
    download_model()
