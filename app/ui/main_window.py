import tkinter as tk
from tkinter import filedialog, messagebox, Label, Button, Frame, Text
from PIL import Image, ImageTk
import os

from app.config import STYLE_CONFIG, APP_CONFIG
from app.ui.tag_pill import AITagContainer

class MainWindow:
    """
    The main window of the Rapid Photo Sorter application.
    Handles the creation and layout of all UI widgets.
    """
    def __init__(self, root, app_logic):
        """
        Initializes the main UI window.

        Args:
            root (tk.Tk): The root Tkinter window.
            app_logic (PhotoSorterApp): A reference to the main application logic class.
        """
        self.root = root
        self.app = app_logic # Reference to the main application logic

        self.root.title(APP_CONFIG["title"])
        self.root.geometry(APP_CONFIG["geometry"])
        self.root.configure(bg=STYLE_CONFIG["bg_color"])

        self._create_widgets()
        self._create_text_widget_context_menu()
        self.show_placeholder_image()

    def _create_widgets(self):
        """
        Creates and lays out all UI widgets using a grid-based architecture.
        This method orchestrates the creation of the main UI frames.
        """
        # --- Configure Root Window Grid ---
        self.root.grid_rowconfigure(0, weight=0)    # Top bar (fixed height)
        self.root.grid_rowconfigure(1, weight=1)    # Main image area (expandable)
        self.root.grid_rowconfigure(2, weight=0)    # Bottom controls/status (fixed height)
        self.root.grid_columnconfigure(0, weight=1) # Main column (expandable)

        # --- Create Main Layout Frames ---
        top_frame = Frame(self.root, bg=STYLE_CONFIG["bg_color"], padx=10, pady=5)
        top_frame.grid(row=0, column=0, sticky="ew")

        self.image_frame = Frame(self.root, bg=STYLE_CONFIG["image_bg_color"], relief=tk.SUNKEN, bd=2, padx=10, pady=5)
        self.image_frame.grid(row=1, column=0, sticky="nsew")

        bottom_frame = Frame(self.root, bg=STYLE_CONFIG["bg_color"], padx=10, pady=5)
        bottom_frame.grid(row=2, column=0, sticky="ew")

        # --- Populate Frames with Widgets ---
        self._create_top_bar_widgets(top_frame)
        self._create_image_display_widgets(self.image_frame)
        self._create_bottom_bar_widgets(bottom_frame)

    def _create_top_bar_widgets(self, parent_frame):
        """
        Creates the top-level control buttons (Select Folder, AI Toggles, Commit).

        Args:
            parent_frame (tk.Frame): The frame to contain these widgets.
        """
        # Configure column weights for proper spacing.
        # The spacer column (3) has a weight of 1, so it expands to fill available
        # space, pushing the "Commit Changes" button to the far right.
        parent_frame.grid_columnconfigure(0, weight=0) # Select Folder
        parent_frame.grid_columnconfigure(1, weight=0) # AI Tag Processing
        parent_frame.grid_columnconfigure(2, weight=0) # Vision Analysis
        parent_frame.grid_columnconfigure(3, weight=1) # Spacer
        parent_frame.grid_columnconfigure(4, weight=0) # Commit Changes

        self.btn_select_folder = Button(parent_frame, text="Select Folder", command=self.app.select_folder,
                                        bg=STYLE_CONFIG["widget_bg_color"], fg=STYLE_CONFIG["text_color"],
                                        relief=STYLE_CONFIG["button_relief"])
        self.btn_select_folder.grid(row=0, column=0, sticky="w")

        self.ai_toggle_button = tk.Checkbutton(parent_frame, text="AI Tag Processing", var=self.app.ai_processing_enabled,
                                               bg=STYLE_CONFIG["bg_color"], fg=STYLE_CONFIG["text_color"],
                                               selectcolor=STYLE_CONFIG["widget_bg_color"], activebackground=STYLE_CONFIG["bg_color"],
                                               activeforeground=STYLE_CONFIG["text_color"], relief=tk.FLAT, anchor='w')
        self.ai_toggle_button.grid(row=0, column=1, sticky="w", padx=(20, 0))

        self.vision_toggle_button = tk.Checkbutton(parent_frame, text="Vision Analysis", var=self.app.vision_processing_enabled,
                                               bg=STYLE_CONFIG["bg_color"], fg=STYLE_CONFIG["text_color"],
                                               selectcolor=STYLE_CONFIG["widget_bg_color"], activebackground=STYLE_CONFIG["bg_color"],
                                               activeforeground=STYLE_CONFIG["text_color"], relief=tk.FLAT, anchor='w')
        self.vision_toggle_button.grid(row=0, column=2, sticky="w", padx=(20, 0))


        self.btn_commit = Button(parent_frame, text="Commit Changes", command=self.app.commit_changes,
                                 bg=STYLE_CONFIG["widget_bg_color"], fg=STYLE_CONFIG["text_color"],
                                 relief=STYLE_CONFIG["button_relief"], state=tk.DISABLED)
        self.btn_commit.grid(row=0, column=4, sticky="e")

    def _create_image_display_widgets(self, parent_frame):
        """
        Creates the main image label and navigation/rotation buttons.

        Args:
            parent_frame (tk.Frame): The frame to contain these widgets.
        """
        self.image_label = Label(parent_frame, bg=STYLE_CONFIG["image_bg_color"])
        self.image_label.pack(expand=True, fill=tk.BOTH)

        self.btn_back = Button(parent_frame, text="◀", command=self.app.prev_image,
                               bg=STYLE_CONFIG["widget_bg_color"], fg=STYLE_CONFIG["text_color"],
                               relief=STYLE_CONFIG["button_relief"], font=STYLE_CONFIG["font_nav"])
        self.btn_back.place(relx=0.02, rely=0.5, anchor="w")

        self.btn_next = Button(parent_frame, text="▶", command=self.app.next_image,
                               bg=STYLE_CONFIG["widget_bg_color"], fg=STYLE_CONFIG["text_color"],
                               relief=STYLE_CONFIG["button_relief"], font=STYLE_CONFIG["font_nav"])
        self.btn_next.place(relx=0.98, rely=0.5, anchor="e")

        self.btn_rotate = Button(parent_frame, text="↻", command=self.app.rotate_image,
                                 bg=STYLE_CONFIG["widget_bg_color"], fg=STYLE_CONFIG["text_color"],
                                 relief=STYLE_CONFIG["button_relief"], font=STYLE_CONFIG["font_nav"])
        self.btn_rotate.place(relx=0.5, rely=0.95, anchor="s")

    def _create_bottom_bar_widgets(self, parent_frame):
        """
        Creates the tag box, decision buttons, and status bar in the bottom frame.

        Args:
            parent_frame (tk.Frame): The frame to contain these widgets.
        """
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(0, weight=0) # Manual Tags
        parent_frame.grid_rowconfigure(1, weight=0) # AI Generated Tags
        parent_frame.grid_rowconfigure(2, weight=0) # Decision Buttons
        parent_frame.grid_rowconfigure(3, weight=0) # Status Bar

        # --- Manual Tags Section ---
        tag_frame = Frame(parent_frame, bg=STYLE_CONFIG["bg_color"])
        tag_frame.grid(row=0, column=0, sticky="ew", pady=(5,0))
        tag_frame.grid_columnconfigure(1, weight=1)

        tag_label = Label(tag_frame, text="Tags:", bg=STYLE_CONFIG["bg_color"], fg=STYLE_CONFIG["text_color"])
        tag_label.grid(row=0, column=0, sticky="w", padx=(0, 5))

        self.tag_text = Text(tag_frame, height=2, bg="#3c3c3c", fg=STYLE_CONFIG["text_color"],
                             relief=STYLE_CONFIG["button_relief"], state=tk.NORMAL)
        self.tag_text.grid(row=0, column=1, sticky="ew")
        self.tag_text.bind("<Button-3>", self._show_text_context_menu)

        self.btn_record = Button(tag_frame, text="🎤", command=self.app.start_listening,
                                 bg=STYLE_CONFIG["widget_bg_color"], fg=STYLE_CONFIG["text_color"],
                                 relief=STYLE_CONFIG["button_relief"])
        self.btn_record.grid(row=0, column=2, sticky="e", padx=(5, 0))

        # --- AI Generated Tags Section ---
        ai_tag_section = Frame(parent_frame, bg=STYLE_CONFIG["bg_color"])
        ai_tag_section.grid(row=1, column=0, sticky="ew", pady=(10, 5))
        ai_tag_section.grid_columnconfigure(0, weight=1)
        ai_tag_section.grid_rowconfigure(0, weight=0)
        ai_tag_section.grid_rowconfigure(1, weight=0)
        
        ai_tag_label = Label(ai_tag_section, text="AI Generated Tags:", 
                            bg=STYLE_CONFIG["bg_color"], fg=STYLE_CONFIG["text_color"],
                            font=("Arial", 9, "italic"))
        ai_tag_label.grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        self.ai_tag_container = AITagContainer(ai_tag_section)
        self.ai_tag_container.grid(row=1, column=0, sticky="ew")

        # --- Decision Buttons ---
        decision_frame = Frame(parent_frame, bg=STYLE_CONFIG["bg_color"])
        decision_frame.grid(row=2, column=0, sticky="ew", pady=5)
        decision_frame.grid_columnconfigure(0, weight=1)
        decision_frame.grid_columnconfigure(1, weight=1)

        self.btn_delete = Button(decision_frame, text="Delete", command=self.app.delete_image,
                                 bg=STYLE_CONFIG["delete_color"], fg=STYLE_CONFIG["text_color"],
                                 relief=STYLE_CONFIG["button_relief"], width=15, height=2)
        self.btn_delete.grid(row=0, column=0, sticky="w")

        self.btn_keep = Button(decision_frame, text="Keep", command=self.app.keep_image,
                               bg=STYLE_CONFIG["keep_color"], fg=STYLE_CONFIG["text_color"],
                               relief=STYLE_CONFIG["button_relief"], width=15, height=2)
        self.btn_keep.grid(row=0, column=1, sticky="e")

        # --- Status Bar ---
        self.status_label = Label(parent_frame, text="Welcome! Please select a folder to begin.", bd=1,
                                  relief=tk.SUNKEN, anchor=tk.W, bg="#3c3c3c", fg=STYLE_CONFIG["text_color"],
                                  font=STYLE_CONFIG["font_main"])
        self.status_label.grid(row=3, column=0, sticky="ew", ipady=4)

    def show_placeholder_image(self):
        """Displays a placeholder image on startup or when no images are loaded."""
        try:
            placeholder = Image.new('RGB', (800, 600), color=STYLE_CONFIG["image_bg_color"])
            self.placeholder_img = ImageTk.PhotoImage(placeholder)
            self.image_label.config(image=self.placeholder_img)
        except Exception as e:
            self.set_status(f"Error creating placeholder: {e}")

    def _create_text_widget_context_menu(self):
        """Creates the right-click context menu for text widgets."""
        self.text_context_menu = tk.Menu(self.root, tearoff=0)
        self.text_context_menu.add_command(label="Cut", command=lambda: self.root.focus_get().event_generate("<<Cut>>"))
        self.text_context_menu.add_command(label="Copy", command=lambda: self.root.focus_get().event_generate("<<Copy>>"))
        self.text_context_menu.add_command(label="Paste", command=lambda: self.root.focus_get().event_generate("<<Paste>>"))

    def _show_text_context_menu(self, event):
        """
        Displays the context menu at the cursor's position for text widgets.
        
        Args:
            event: The event object containing the cursor coordinates.
        """
        try:
            self.text_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.text_context_menu.grab_release()

    def set_status(self, text):
        """Updates the status bar text."""
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def update_image(self, image_path, rotation_angle):
        """
        Loads and displays an image from a file path, applying a specified rotation.

        Args:
            image_path (str): The path to the image file.
            rotation_angle (int): The angle (0, 90, 180, 270) to rotate the image.
        """
        try:
            with Image.open(image_path) as img:
                if rotation_angle != 0:
                    img = img.rotate(-rotation_angle, expand=True)

                frame_width = self.image_frame.winfo_width()
                frame_height = self.image_frame.winfo_height()
                
                if frame_width < 50 or frame_height < 50:
                    # Fallback to a default size if the frame hasn't been rendered yet.
                    frame_width, frame_height = 800, 600

                img.thumbnail((frame_width, frame_height), Image.Resampling.LANCZOS)

                self.photo_image = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.photo_image)
        except Exception as e:
            messagebox.showerror("Error Loading Image", f"Could not load image: {os.path.basename(image_path)}\n\nError: {e}")
            self.set_status(f"Error loading {os.path.basename(image_path)}")

    def update_tags(self, tags):
        """
        Updates the content of the tag text box.

        Args:
            tags (str): The new text to display in the tag box.
        """
        self.tag_text.delete("1.0", tk.END)
        self.tag_text.insert("1.0", tags)

    def get_tags(self):
        """
        Returns the current content of the tag text box.

        Returns:
            str: The current text in the tag box, stripped of whitespace.
        """
        return self.tag_text.get("1.0", tk.END).strip()

    def set_commit_button_state(self, state):
        """
        Sets the state of the commit button (enabled or disabled).

        Args:
            state (str): tk.NORMAL or tk.DISABLED.
        """
        self.btn_commit.config(state=state)

    def set_record_button_color(self, color):
        """
        Sets the background color of the record button, used to indicate state.

        Args:
            color (str): The color to set as the background.
        """
        self.btn_record.config(bg=color)
    
    def add_ai_tags(self, tags):
        """
        Adds AI-generated tags to the tag pill container.
        
        Args:
            tags (str or list): Comma-separated string or list of tags to add
        """
        if isinstance(tags, str):
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        else:
            tag_list = tags
        
        self.ai_tag_container.add_tags(tag_list)
    
    def clear_ai_tags(self):
        """Clears all AI-generated tags from the pill container."""
        self.ai_tag_container.clear_all_tags()
    
    def get_ai_tags(self):
        """
        Returns all current AI-generated tags.
        
        Returns:
            list: List of tag strings currently in the AI tag container
        """
        return self.ai_tag_container.get_all_tags()
