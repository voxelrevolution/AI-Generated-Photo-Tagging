# Project Documentation: D20 - Concurrency Model Overhaul

**Date:** 2025-11-13
**Author:** GitHub Copilot
**Related Work Log:** `agent_work_logs/D20-DEV-001.md`

## 1. Overview

This document details the significant architectural changes implemented during the D20 development cycle. The primary focus of this update was to resolve a critical race condition, nicknamed "tag bleeding," that was discovered during the initial user acceptance testing (UAT) of the D19 vision analysis feature.

This change represents a fundamental improvement in the application's stability and reliability when handling asynchronous AI operations.

## 2. The "Tag Bleeding" Race Condition

### 2.1. Problem Description

When a user navigated away from an image (e.g., by clicking "Next" or "Delete") while an AI analysis process (either vision or voice-to-text) was still running in the background for that image, the following would occur:

1.  The UI would load the **new image**.
2.  The background AI thread for the **previous image** would complete its work.
3.  The AI thread's callback function would fire, containing the tags for the **previous image**.
4.  The callback would update the UI's tag box with these old tags, incorrectly applying them to the **new image** currently on screen.

This was a critical data corruption bug that undermined the core purpose of the application.

### 2.2. Root Cause

The root cause was a lack of context and control in the asynchronous callback system. The AI callbacks were "fire-and-forget"; they knew *what* tags to apply, but they had no awareness of *which image* those tags belonged to. They simply updated whatever image was currently visible in the UI, leading to the race condition.

## 3. The New Concurrency Model: Lock and Context

To solve this, a more robust concurrency model was implemented in `app/app.py`. The solution has two key components:

### 3.1. AI Processing Lock (`self.ai_lock`)

-   A `threading.Lock` instance, `self.ai_lock`, was added to the `PhotoSorterApp` class.
-   **Purpose**: To ensure that **only one AI processing job can be active at any given time**.
-   **Mechanism**: Before an AI background thread is started (for either vision or text processing), the main thread attempts to acquire this lock using a **non-blocking** call (`self.ai_lock.acquire(blocking=False)`).
    -   If the lock is acquired, the AI job proceeds.
    -   If it's not acquired (meaning another AI job is already running), the new job is aborted, and a "busy" message is displayed to the user. This prevents multiple threads from competing and provides clear feedback.

### 3.2. Image Context Verification

This is the most critical part of the fix.

-   **State Tracking**: A new state variable, `self.current_ai_image_path`, was introduced. Before an AI job is dispatched, this variable is set to the path of the image being analyzed.
-   **Context Propagation**: The `image_path` is now passed as an argument through the entire asynchronous chain: from the initial call (`analyze_image_with_vision`, `process_tags_with_ai`) to the final callback (`_ai_processing_callback`).
-   **The Check**: Inside the callback functions, a crucial comparison is now made:
    ```python
    if image_path != self.current_image_path:
        # The user has moved on. Discard the results.
        return
    ```
-   **Outcome**: This check ensures that the UI is only ever updated if the results from the AI job match the image currently on the user's screen. Results from old, irrelevant jobs are now safely and silently discarded.

### 3.3. Guaranteed Lock Release

The `ai_lock` is always released within a `finally` block in the final callback (`_ai_processing_callback`). This guarantees that the lock is freed even if an error occurs during processing, preventing application deadlocks.

## 4. Architectural Impact

This change moves the application from a simple, but fragile, "fire-and-forget" concurrency model to a managed, context-aware system. It makes the AI features significantly more robust and reliable, preventing a whole class of potential race condition bugs. This is a foundational improvement for any future asynchronous features.
