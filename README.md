# AI Generated Photo Tagging

A desktop application for rapidly sorting and tagging large photo collections with AI assistance.

## ⚡ Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd photo-sorter-v2
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Ollama (required for AI features)
ollama pull llava:7b
ollama pull llama3.1:8b

# 4. Run the application
./run.sh  # or: python main_v2.py
```

See [SETUP.md](SETUP.md) for detailed installation instructions and troubleshooting.

## ✨ Features

- **AI-Powered Vision Analysis**: Automatic tag suggestions from image content using LLaVA
- **Auto-Listening Speech Recognition**: Voice-to-text transcription starts automatically
- **Interactive Tag Pills**: AI-generated tags appear as editable pills with individual delete buttons
- **Smart Tag Processing**: AI cleans and standardizes your tags
- **EXIF Metadata Preservation**: Safely adds tags without modifying original camera data (GPS, date, etc.)
- **Fast Workflow**: Keep/Delete decisions with keyboard shortcuts
- **Session Logging**: Track all your sorting decisions

---

## 📖 Documentation

### 1. V1 Summary

Version 1.0 of the Rapid Photo Sorter was a resounding success. It delivered a stable, feature-complete desktop application capable of rapidly sorting and tagging large quantities of photos. The key achievement of V1 was the creation of a robust workflow combining manual decisions, voice-to-text transcription, and AI-powered tag cleaning, culminating in the permanent embedding of metadata into image files.

**V1 Core Features:**
*   A stable and responsive UI for image viewing, navigation, and rotation.
*   A simple "Keep/Delete" workflow for fast decision-making.
*   Voice-driven tagging with automatic transcription.
*   AI-powered tag cleaning and standardization using a local LLM.
*   Permanent EXIF metadata tagging for "kept" files.
*   Safe, non-destructive sorting into `sorted_kept` and `sorted_deleted` folders.

## 2. V2 Vision & Goals

The vision for V2 is to evolve the Rapid Photo Sorter from a powerful assistant into a semi-autonomous agent. While V1 required the user to provide all initial tags via voice or text, V2 will leverage advanced AI capabilities to **proactively suggest tags** based on the image content itself.

The primary goal is to further reduce the user's workload by automating the initial analysis of each photo, turning the user's role from a "tag creator" into a "tag curator."

**High-Level Goals for V2:**
1.  **Autonomous Image Analysis**: Implement a multi-modal AI model (like LLaVA) to "see" the image and generate a descriptive list of initial tags automatically.
2.  **Human-in-the-Loop Workflow**: The AI-generated tags will populate the tag box automatically. The user can then:
    *   Accept the tags as-is.
    *   Quickly edit the tags.
    *   Add more tags via voice or text.
3.  **Enhanced AI Reasoning**: Improve the AI's ability to recognize context, identify recurring subjects (e.g., "the family dog"), and suggest more nuanced or thematic tags.
4.  **Configuration and Settings**: Introduce a settings panel to allow users to configure AI parameters, such as the level of detail in auto-tagging or custom name lists.

V2 marks the transition from a "do what I say" tool to a "do what I mean" collaborative partner in the photo management process.

### 2.1 V2 Implementation Status ✅

**Version 2.0 is complete and delivers all core goals:**

✅ **Autonomous Image Analysis**: LLaVA vision model analyzes images automatically on load  
✅ **Human-in-the-Loop Workflow**: AI tags appear as interactive pills, user curates by deleting unwanted tags  
✅ **Auto-Listening**: Speech recognition activates automatically when images load  
✅ **Smart Tag Processing**: Llama 3.1 cleans and standardizes both voice and vision tags  
✅ **Visual Separation**: AI-generated tags appear in dedicated pill section, distinct from manual tags  

**See [agent_work_logs/](agent_work_logs/) for complete development history and technical documentation.**

## 🔧 Architecture

**Modular Structure:**
- `app/ai/` - Vision analysis and tag processing (LLaVA, Llama 3.1)
- `app/core/` - File operations and EXIF handling
- `app/ui/` - Tkinter GUI components and tag pill widgets
- `app/utils/` - Audio handling and logging
- `tests/` - Unit test suite (pytest)

**External Services:**
- Ollama server (localhost:11434) for AI models
- Google Speech Recognition API for voice transcription

## 📝 License

[Add your license here]

## 🤝 Contributing

Contributions welcome! Please see development guidelines in [docs/PROJECT_GUIDELINES.md](docs/PROJECT_GUIDELINES.md).
