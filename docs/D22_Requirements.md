# D22 Requirements: Implement Unit Testing Framework

**Functional Requirements:**

*   **FR-001: Test Framework Setup**
    *   **1.1:** The `pytest` library MUST be added as a project dependency.
    *   **1.2:** A `tests/` directory MUST be created at the project root.
    *   **1.3:** The test suite MUST be runnable via a single command (e.g., `pytest`) from the project's root directory.

*   **FR-002: Initial Unit Tests**
    *   **2.1:** Unit tests MUST be written for the `_build_prompt` function in `app/ai/tag_processor.py`.
    *   **2.2:** The test cases for `_build_prompt` MUST validate critical prompt-engineering logic, including correct name substitution, handling of negations, and preservation of numbers and proper nouns.
    *   **2.3:** A unit test MUST be written for the `_build_vision_prompt` function in `app/ai/vision_analyzer.py` to ensure it constructs the correct prompt string.

**Non-Functional Requirements:**

*   **NFR-001: Test Isolation**
    *   **1.1:** All unit tests created in this deliverable MUST be self-contained and MUST NOT have any external dependencies (e.g., no network calls, no file system access).

*   **NFR-002: Maintainability & Naming**
    *   **2.1:** Test files MUST follow the `test_*.py` naming convention recognized by `pytest`.
    *   **2.2:** Test functions MUST have descriptive names that clearly state what they are testing (e.g., `test_build_prompt_correctly_handles_negation`).
