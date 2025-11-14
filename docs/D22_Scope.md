# D22 Scope: Implement Unit Testing Framework

**Goal:** To establish a foundational unit testing framework using `pytest`. This will improve code quality, prevent regressions, and enable safer, more confident refactoring in the future. The initial focus will be on testing business logic that is isolated from the UI and external services.

**In Scope:**
*   **Framework Setup:** Install and configure the `pytest` library.
*   **Directory Structure:** Create a dedicated `tests/` directory to house all automated tests, keeping them separate from the application source code.
*   **Initial Unit Tests:** Write the first set of unit tests targeting "pure functions"—those without external dependencies like file I/O or network calls. Good initial candidates are the prompt-building functions within the AI modules, as their logic is critical and can be tested deterministically.
*   **Test Execution:** Ensure the test suite can be easily executed from the command line.

**Out of Scope for D22:**
*   **UI Testing:** End-to-end testing of the Tkinter GUI will not be included.
*   **Integration Testing:** Tests that require a live Ollama server or interact with the file system are excluded for now.
*   **Mocking:** Advanced techniques like mocking external dependencies will be deferred to a future deliverable.
*   **Code Coverage:** Measuring and reporting on test coverage is not part of this initial setup.
