# Photo Sorter V2 - Project Guidelines

This document outlines the strict operational protocols, naming conventions, and documentation standards that MUST be followed for the V2 project. It serves as the guiding prompt for the development agent.

## 1. Core Philosophy: Modularity and Maintainability

The primary failure of V1 was its monolithic structure. V2 will be built with a "modularity-first" approach. This means:
-   **Separation of Concerns**: Code will be strictly separated based on its function (AI, UI, Core Logic, Utilities).
-   **Clear Interfaces**: Modules will communicate through well-defined functions and classes, not by accessing each other's internal state.
-   **Reusability**: Components should be designed to be reusable and testable in isolation.

## 2. Directory Structure

All application code MUST reside within the `app/` directory.

*   `app/`: The main Python package for the application.
    *   `ai/`: For all AI-related processing. This includes API calls to Ollama, prompt engineering, and AI response handling.
    *   `core/`: For core application logic. This includes file handling (reading/moving images), EXIF data manipulation, and session management.
    *   `ui/`: For all GUI components. This includes Tkinter window creation, widgets, and layout management.
    *   `utils/`: For shared utility functions that don't belong to a specific domain (e.g., image encoding, logging setup).
*   `backups/`: Contains versioned backups of the `app/` directory, created after each major deliverable.
*   `docs/`: Project-level documentation, including these guidelines.
*   `agent_work_logs/`: Detailed, step-by-step development logs for every task.
*   `main.py`: The root-level entry point for the application. It should contain minimal code, primarily to instantiate and run the main application class.

## 3. Naming Conventions

Consistency is key. The following conventions are mandatory.

*   **Directories**: `snake_case` (e.g., `agent_work_logs`)
*   **Python Files**: `snake_case.py` (e.g., `visual_analyzer.py`)
*   **Classes**: `PascalCase` (e.g., `MainWindow`, `AiProcessor`)
*   **Functions & Methods**: `snake_case()` (e.g., `load_image`, `process_tags_with_ai`)
*   **Variables & Constants**: `snake_case` for variables, `UPPER_SNAKE_CASE` for constants (e.g., `image_path`, `DEFAULT_MODEL_NAME`).

## 4. Documentation Standards

Meticulous documentation is a primary requirement for V2.

*   **Work Logs**: Every development task, no matter how small, MUST begin with the creation of a new `DXX-DEV-XXX.md` file in the `agent_work_logs/` directory. This log must detail the plan, the steps taken, and the outcome.
*   **Docstrings**: All Python modules, classes, and functions MUST have clear, descriptive docstrings explaining their purpose, arguments (`Args:`), and return values (`Returns:`).
*   **Inline Comments**: Use inline comments (`#`) to explain complex, non-obvious, or "tricky" lines of code. Explain *why* the code is doing something, not just *what* it is doing.
*   **Commit-Style Messages**: All file edits will be accompanied by a clear message explaining the change, as if it were a git commit message.

## 5. Backup and Versioning Protocol

To prevent data loss and create clear restore points, the following backup protocol is in effect:

*   After the completion of each major deliverable (as defined by the project sponsor), a complete snapshot of the project MUST be copied into the `backups/` directory.
*   A complete snapshot includes:
    *   The entire `app/` directory.
    *   The entire `docs/` directory.
    *   The entire `agent_work_logs/` directory.
    *   The root `main_v2.py` entry point file.
*   The backup folder will be named according to the deliverable it concludes (e.g., `backup_D20_bugfix_complete/`).

## 6. Configuration Management

To ensure the application is flexible and easy to maintain, all configurable values MUST be centralized.

*   A dedicated configuration file (e.g., `app/config.py`) will be created.
*   This file will hold:
    *   AI model names (`VISION_MODEL = "llava:7b"`)
    *   API endpoints (`OLLAMA_API_URL = "http://localhost:11434/api/generate"`)
    *   Prompts
    *   UI style configurations (colors, fonts)
    *   Application settings (e.g., number of images to pre-load)
*   Code MUST import values from this configuration module, not contain hardcoded "magic strings" or numbers.
