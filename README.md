# Face Attendance POC

High-speed face attendance system using MediaPipe, InsightFace, and passive liveness detection.

## Features

- **Face Detection**: MediaPipe (single face validation)
- **Face Embeddings**: InsightFace ArcFace (512-D vectors)
- **Matching**: Cosine similarity (1:N matching)
- **Anti-Spoofing**: Passive liveness detection
- **Database**: SQLite for embeddings and logs
- **UI**: Streamlit web interface

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Download InsightFace models** (automatic on first run):
The system will automatically download the required models on first use.

## Usage

### Run the application:
```bash
streamlit run app.py
```

### Workflow:

1. **Register Face**:
   - Navigate to "Register Face" page
   - Enter student ID and name
   - Capture face photo
   - System generates and stores 512-D embedding

2. **Mark Attendance**:
   - Navigate to "Mark Attendance" page
   - Capture face photo
   - System performs:
     - Face detection (single face only)
     - Liveness check (anti-spoofing)
     - Embedding generation
     - 1:N matching against database
   - Results displayed with similarity score

3. **View Logs**:
   - Navigate to "View Logs" page
   - View attendance history
   - Filter by status
   - Download logs as CSV
   - View performance statistics

## Performance Targets

- End-to-end verification: < 1.5 seconds
- Vector search: < 10ms for 5,000 users
- Matching accuracy: > 99.5%

## Project Structure

```
face_attendance_poc/
├── app.py                    # Main Streamlit app
├── requirements.txt          # Dependencies
├── pages/
│   ├── register.py          # Face registration
│   ├── attendance.py        # Attendance marking
│   └── logs.py              # Logs viewer
├── face_engine/
│   ├── detector.py          # MediaPipe face detection
│   ├── embedder.py          # ArcFace embeddings
│   ├── liveness.py          # Passive liveness check
│   └── matcher.py           # Cosine similarity matching
├── db/
│   ├── database.py          # Database operations
│   └── models.py            # SQLite schemas
└── utils/
    └── config.py            # Configuration settings
```

## Configuration

Edit `utils/config.py` to adjust:
- Similarity threshold (default: 0.65)
- Liveness detection parameters
- Performance targets
- Database path

## Scale Testing

To test with 5,000 dummy embeddings:

```python
from db.database import get_database

db = get_database()
db.generate_dummy_embeddings(5000)
```

To clear dummy data:

```python
db.clear_dummy_data()
```

## Security Features

- Single face detection (rejects multiple faces)
- Passive liveness check (detects static photos)
- Conservative similarity threshold (minimizes false positives)
- Identity-locked attendance (1:N matching)

## Limitations (POC)

- Liveness detection is POC-level (passive only)
- Single frame capture (production would use video stream)
- No active liveness prompts (blink on command, head turn, etc.)
- Local SQLite database (production would use distributed DB)

## License

POC for demonstration purposes.
