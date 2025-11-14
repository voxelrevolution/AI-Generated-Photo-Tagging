import tkinter as tk
from tkinter import messagebox
import os
import threading
import logging

from app.ui.main_window import MainWindow
from app.core import file_operations
from app.ai.tag_processor import TagProcessor
from app.ai.vision_analyzer import VisionAnalyzer
from app.utils.audio_handler import AudioHandler
from app.config import AI_CONFIG, STYLE_CONFIG

class PhotoSorterApp:
    """
    Main application logic for the Photo Sorter.
    Connects the UI, file operations, and AI processing.
    """
    def __init__(self, root):
        """
        Initializes the main application.

        Args:
            root (tk.Tk): The root Tkinter window.
        """
        self.root = root
        self.logger = logging.getLogger(__name__)
        self.logger.info("PhotoSorterApp initializing.")
        
        # --- State Management ---
        self.folder_path = None
        self.image_files = []
        self.current_image_index = -1
        self.session_log = {}
        self.rotation_states = {}
        self.ai_processing_enabled = tk.BooleanVar(value=AI_CONFIG["ENABLED_BY_DEFAULT"])
        self.vision_processing_enabled = tk.BooleanVar(value=AI_CONFIG["ENABLED_BY_DEFAULT"])
        self.current_image_path = None
        self.current_ai_image_path = None

        # --- Concurrency Control ---
        self.ai_lock = threading.Lock()

        # --- Module Initialization ---
        self.tag_processor = TagProcessor(AI_CONFIG)
        self.vision_analyzer = VisionAnalyzer(AI_CONFIG)
        self.ui = MainWindow(root, self)
        self.audio_handler = AudioHandler(self)

        # Start with a clean slate
        self.ui.set_commit_button_state(tk.DISABLED)

    def select_folder(self):
        """
        Handles the 'Select Folder' action. Opens a dialog to choose a folder,
        then loads the images from it.
        """
        self.logger.info("Opening folder selection dialog.")
        folder_path = file_operations.select_folder_path()
        if not folder_path:
            self.logger.warning("Folder selection cancelled.")
            return

        self.logger.info(f"Folder selected: {folder_path}")
        self.folder_path = folder_path
        self.image_files = file_operations.get_image_files(folder_path)

        if self.image_files:
            self.logger.info(f"Found {len(self.image_files)} images.")
            self.current_image_index = 0
            self.session_log.clear()
            self.rotation_states.clear()
            self.ui.set_commit_button_state(tk.NORMAL)
            self._load_image(self.image_files[self.current_image_index])
        else:
            self.logger.warning(f"No valid images found in {folder_path}.")
            messagebox.showinfo("No Images", "No valid image files found in the selected folder.")
            self.ui.set_status("Select a folder with valid images.")

    def _load_image(self, image_path):
        """
        Loads, displays, and prepares the specified image for user interaction.
        This is the central method for changing the displayed image.

        Args:
            image_path (str): The absolute path to the image file.
        """
        self.logger.info(f"Loading image: {image_path}")
        self.current_image_path = image_path
        self.current_image_index = self.image_files.index(image_path)
        
        rotation_angle = self.rotation_states.get(image_path, 0)
        self.ui.update_image(image_path, rotation_angle)

        tags = self.session_log.get(image_path, {}).get('tags', '')
        self.ui.update_tags(tags)
        
        # Clear and restore AI tags from session if they exist
        self.ui.clear_ai_tags()
        ai_tags = self.session_log.get(image_path, {}).get('ai_tags', [])
        if ai_tags:
            self.ui.add_ai_tags(ai_tags)

        status_text = f"Image {self.current_image_index + 1} of {len(self.image_files)} | {os.path.basename(image_path)}"
        self.ui.set_status(status_text)
        
        self._trigger_vision_analysis()
        self.start_listening()

    def _trigger_vision_analysis(self):
        """
        Initiates the vision analysis process if the feature is enabled.
        It acquires the AI lock before starting the background thread.
        """
        if self.vision_processing_enabled.get() and self.current_image_path:
            self.logger.info("Attempting to acquire AI lock for vision analysis.")
            if self.ai_lock.acquire(blocking=False):
                self.current_ai_image_path = self.current_image_path
                self.logger.info(f"AI lock acquired. Starting vision analysis for {self.current_ai_image_path}")
                self.ui.set_status("Analyzing image with vision AI...")
                self.vision_analyzer.analyze_image_with_vision(
                    image_path=self.current_ai_image_path,
                    callback=self._vision_processing_callback
                )
            else:
                self.logger.warning("AI lock is busy. Vision analysis deferred.")
                self.ui.set_status("AI is busy. Please wait for the current analysis to finish.")

    def next_image(self):
        """Moves to the next image."""
        if self.image_files and self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self._load_image(self.image_files[self.current_image_index])

    def prev_image(self):
        """Moves to the previous image."""
        if self.image_files and self.current_image_index > 0:
            self.current_image_index -= 1
            self._load_image(self.image_files[self.current_image_index])

    def rotate_image(self):
        """Rotates the current image."""
        if self.current_image_path:
            current_angle = self.rotation_states.get(self.current_image_path, 0)
            new_angle = (current_angle + 90) % 360
            self.logger.info(f"Rotating image {self.current_image_path} from {current_angle} to {new_angle} degrees.")
            self.rotation_states[self.current_image_path] = new_angle
            self._load_image(self.current_image_path)

    def keep_image(self):
        """Records a 'keep' decision."""
        self._record_decision('keep')

    def delete_image(self):
        """Records a 'delete' decision."""
        self._record_decision('delete')

    def _record_decision(self, action):
        """Logs the decision and advances to the next image."""
        if self.current_image_index == -1:
            self.logger.warning("Attempted to record decision with no image loaded.")
            return

        image_path = self.image_files[self.current_image_index]
        manual_tags = self.ui.get_tags()
        ai_tags = self.ui.get_ai_tags()
        
        # Merge manual and AI tags for final storage
        all_tags = manual_tags
        if ai_tags:
            ai_tags_str = ', '.join(ai_tags)
            all_tags = f"{manual_tags}, {ai_tags_str}" if manual_tags else ai_tags_str
        
        self.logger.info(f"Recording decision for {image_path}: action='{action}', manual_tags='{manual_tags}', ai_tags={ai_tags}")
        self.session_log[image_path] = {
            'action': action, 
            'tags': all_tags,
            'ai_tags': ai_tags
        }
        
        self.audio_handler.is_listening.clear()
        self.ui.set_status(f"Marked for {action.upper()}.")
        
        self.next_image()

    def start_listening(self):
        """Starts the audio listener."""
        self.audio_handler.start_listening()

    def handle_transcription(self, transcribed_text):
        """
        Handles new transcribed text by cleaning it with AI and appending it
        to existing manual tags. It acquires the AI lock before processing.
        """
        self.logger.info(f"Handling transcription: '{transcribed_text}'")
        manual_tags = self.ui.get_tags()
        
        status_text = f"Image {self.current_image_index + 1} of {len(self.image_files)} | {os.path.basename(self.current_image_path)}"
        self.ui.set_status(status_text)

        if self.ai_processing_enabled.get() and transcribed_text:
            self.logger.info("Attempting to acquire AI lock for text processing.")
            if self.ai_lock.acquire(blocking=False):
                self.current_ai_image_path = self.current_image_path
                self.logger.info(f"AI lock acquired. Starting text processing for {self.current_ai_image_path}")
                self.ui.set_status("Processing transcribed tags with AI...")
                self.tag_processor.process_tags_with_ai(
                    image_path=self.current_ai_image_path,
                    manual_tags=manual_tags,
                    transcribed_text=transcribed_text,
                    callback=self._ai_processing_callback,
                    advance_on_complete=False
                )
            else:
                self.logger.warning("AI lock is busy. Text processing deferred.")
                self.ui.set_status("AI is busy. Please wait for the current analysis to finish.")
        elif transcribed_text:
            self.logger.info("AI processing is disabled. Appending raw transcription.")
            new_tags = f"{manual_tags}, {transcribed_text}" if manual_tags else transcribed_text
            self.ui.update_tags(new_tags)

    def _vision_processing_callback(self, image_path, generated_tags, error):
        """
        Callback for the vision analysis thread. This is the first step in the
        AI tagging chain. It validates context before proceeding.
        """
        self.logger.info(f"Vision callback received for {image_path}.")
        if image_path != self.current_ai_image_path:
            self.logger.warning(f"Discarding stale vision result. AI context is {self.current_ai_image_path}, result is for {image_path}.")
            self.ai_lock.release()
            return

        if error:
            self.logger.error(f"Vision analysis failed for {image_path}: {error}")
            self.ui.set_status(error)
            self.ai_lock.release()
            return

        if generated_tags:
            self.logger.info(f"Vision analysis successful for {image_path}. Passing to text processor.")
            self.ui.set_status("Cleaning vision tags with text AI...")
            self.tag_processor.process_tags_with_ai(
                image_path=image_path,
                manual_tags=self.ui.get_tags(),
                transcribed_text=generated_tags,
                callback=self._ai_processing_callback,
                advance_on_complete=False
            )
        else:
            self.logger.info(f"Vision analysis for {image_path} produced no tags. Releasing lock.")
            self.ai_lock.release()

    def _ai_processing_callback(self, image_path, manual_tags, cleaned_transcribed_text, error, advance_on_complete):
        """
        Callback for the text-based AI processing. This is the final step in
        any AI chain (voice or vision). It validates context and releases the lock.
        """
        self.logger.info(f"Text processing callback received for {image_path}.")
        try:
            if image_path != self.current_image_path:
                self.logger.warning(f"Discarding stale text result. UI is on {self.current_image_path}, result is for {image_path}.")
                self.ui.set_status(f"Discarding old AI results for {os.path.basename(image_path)}")
                return

            if error:
                self.logger.error(f"Text processing failed for {image_path}: {error}")
                self.ui.set_status(error)
                if advance_on_complete:
                    self.root.after(0, self.next_image)
                return

            if cleaned_transcribed_text:
                self.logger.info(f"Adding AI tags for {image_path} as pills.")
                
                # Add tags as pills in the AI tag section
                self.ui.add_ai_tags(cleaned_transcribed_text)
                
                # Store AI tags separately in session log
                if self.current_image_path not in self.session_log:
                    self.session_log[self.current_image_path] = {'action': None, 'tags': '', 'ai_tags': []}
                
                # Parse and store AI tags
                ai_tag_list = [tag.strip() for tag in cleaned_transcribed_text.split(',') if tag.strip()]
                self.session_log[self.current_image_path]['ai_tags'] = ai_tag_list

            self.ui.set_status("AI processing complete.")
            self.logger.info("AI processing complete.")

            if advance_on_complete:
                self.root.after(0, self.next_image)
        finally:
            if self.ai_lock.locked():
                self.logger.info(f"Releasing AI lock from text callback for {image_path}.")
                self.ai_lock.release()

    def commit_changes(self):
        """Commits all session changes to the filesystem."""
        self.logger.info("Commit changes initiated.")
        try:
            summary = file_operations.commit_session_changes(self.folder_path, self.session_log, self.rotation_states)
            self.logger.info(f"Commit summary: {summary}")
            messagebox.showinfo("Commit Summary", summary)
            self._reset_session()
        except RuntimeError as e:
            self.logger.error(f"Commit failed: {e}", exc_info=True)
            messagebox.showerror("Commit Failed", str(e))
        finally:
            self.ui.set_status("Commit complete. Select a folder to begin a new session.")

    def _reset_session(self):
        """Resets the application state for a new session."""
        self.logger.info("Resetting session state.")
        self.folder_path = None
        self.image_files = []
        self.current_image_index = -1
        self.session_log = {}
        self.rotation_states = {}
        self.current_image_path = None
        self.current_ai_image_path = None
        self.ui.set_commit_button_state(tk.DISABLED)
        self.ui.show_placeholder_image()
        self.ui.update_tags("")
