# Photo Sorter V2 - Setup Guide

## Prerequisites
- Python 3.12 or higher
- Ollama server running locally (for AI features)
  - Models required: `llava:7b` and `llama3.1:8b`

## Installation

### 1. Create Virtual Environment
```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

### Option 1: Using the run script (Linux/Mac)
```bash
./run.sh
```

### Option 2: Manual activation
```bash
source venv/bin/activate
python main_v2.py
```

## Dependencies
The application requires the following Python packages:
- **SpeechRecognition** (3.14.3) - For voice-to-text functionality
- **Pillow** (12.0.0) - For image processing and display
- **requests** (2.32.5) - For API communication with Ollama
- **piexif** (1.1.3) - For EXIF metadata manipulation
- **pytest** (9.0.1) - For running unit tests

## Running Tests
```bash
source venv/bin/activate
pytest
```

## Troubleshooting

### Speech Recognition Issues
Make sure you have a working microphone and the appropriate system audio libraries:
- **Linux**: `sudo apt-get install portaudio19-dev python3-pyaudio`
- **Mac**: `brew install portaudio`

### AI Features Not Working
1. Verify Ollama is running: `curl http://localhost:11434/api/tags`
2. Check models are installed: `ollama list`
3. Pull required models if needed:
   ```bash
   ollama pull llava:7b
   ollama pull llama3.1:8b
   ```

## Development

### Adding New Dependencies
```bash
source venv/bin/activate
pip install <package-name>
pip freeze > requirements.txt
```
