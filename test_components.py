"""
Simple test script to verify face engine components
"""
import numpy as np
from face_engine.detector import FaceDetector
from face_engine.matcher import FaceMatcher
from db.database import get_database


def test_detector():
    """Test MediaPipe face detector"""
    print("Testing Face Detector...")
    try:
        detector = FaceDetector()
        print("✓ Face detector initialized successfully")
        detector.close()
        return True
    except Exception as e:
        print(f"✗ Face detector failed: {e}")
        return False


def test_embedder():
    """Test face embedder"""
    print("\nTesting Face Embedder...")
    try:
        from face_engine.embedder import FaceEmbedder
        embedder = FaceEmbedder()
        
        if embedder.is_ready():
            print("✓ Face embedder initialized successfully")
            return True
        else:
            print("⚠ Face embedder initialized but model not loaded")
            print("  Please download the ArcFace ONNX model")
            return False
    except Exception as e:
        print(f"✗ Face embedder failed: {e}")
        return False


def test_matcher():
    """Test cosine similarity matcher"""
    print("\nTesting Face Matcher...")
    try:
        matcher = FaceMatcher()
        
        # Create dummy embeddings
        emb1 = np.random.randn(512).astype(np.float32)
        emb1 = emb1 / np.linalg.norm(emb1)
        
        emb2 = np.random.randn(512).astype(np.float32)
        emb2 = emb2 / np.linalg.norm(emb2)
        
        similarity = matcher.calculate_similarity(emb1, emb2)
        
        print(f"✓ Face matcher working (test similarity: {similarity:.4f})")
        return True
    except Exception as e:
        print(f"✗ Face matcher failed: {e}")
        return False


def test_database():
    """Test database operations"""
    print("\nTesting Database...")
    try:
        db = get_database()
        
        # Test insert
        test_embedding = np.random.randn(512).astype(np.float32)
        test_embedding = test_embedding / np.linalg.norm(test_embedding)
        
        success = db.insert_student("TEST_001", "Test Student", test_embedding)
        
        if success:
            print("✓ Database insert successful")
            
            # Test retrieve
            embeddings = db.get_all_embeddings()
            print(f"✓ Database retrieve successful ({len(embeddings)} students)")
            
            # Clean up test data
            db.get_connection().execute("DELETE FROM students WHERE student_id = 'TEST_001'")
            db.get_connection().commit()
            
            return True
        else:
            print("✗ Database insert failed")
            return False
            
    except Exception as e:
        print(f"✗ Database failed: {e}")
        return False


def test_liveness():
    """Test liveness detector"""
    print("\nTesting Liveness Detector...")
    try:
        from face_engine.liveness import LivenessDetector
        liveness = LivenessDetector()
        print("✓ Liveness detector initialized successfully")
        liveness.close()
        return True
    except Exception as e:
        print(f"✗ Liveness detector failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("FACE ATTENDANCE POC - COMPONENT TESTS")
    print("=" * 60)
    
    results = []
    
    results.append(("Face Detector", test_detector()))
    results.append(("Face Embedder", test_embedder()))
    results.append(("Face Matcher", test_matcher()))
    results.append(("Database", test_database()))
    results.append(("Liveness Detector", test_liveness()))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20} {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("\n🎉 All tests passed! System is ready.")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
    
    print("=" * 60)
