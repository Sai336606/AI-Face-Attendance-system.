# Face Attendance

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
```
python download_model.py  #to download the model
```

## Usage

### Run the application:
```bash
streamlit run app.py
```

