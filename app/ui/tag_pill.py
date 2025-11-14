"""
Tag pill UI components for displaying AI-generated tags with delete functionality.
"""
import tkinter as tk
from tkinter import Frame, Label, Button
from app.config import STYLE_CONFIG


class TagPill(Frame):
    """
    A single tag pill widget displaying a tag with a delete button.
    
    This widget appears as a rounded rectangle (pill shape) containing
    tag text and a small 'x' button for removal.
    """
    
    def __init__(self, parent, tag_text, on_delete_callback, **kwargs):
        """
        Initializes a TagPill widget.
        
        Args:
            parent: The parent Tkinter widget
            tag_text (str): The tag text to display
            on_delete_callback (callable): Function to call when delete button is clicked
            **kwargs: Additional Frame configuration options
        """
        super().__init__(parent, **kwargs)
        
        self.tag_text = tag_text
        self.on_delete_callback = on_delete_callback
        
        # Configure pill styling
        self.config(
            bg="#5a5a5a",  # Slightly lighter than widget background
            relief=tk.RAISED,
            bd=1,
            padx=8,
            pady=4
        )
        
        # Tag label
        self.label = Label(
            self,
            text=tag_text,
            bg="#5a5a5a",
            fg="white",
            font=("Arial", 9)
        )
        self.label.pack(side=tk.LEFT, padx=(0, 4))
        
        # Delete button
        self.delete_btn = Button(
            self,
            text="×",  # Unicode multiplication sign looks like an X
            command=self._on_delete_clicked,
            bg="#5a5a5a",
            fg="#ff6b6b",  # Light red for visibility
            font=("Arial", 12, "bold"),
            relief=tk.FLAT,
            bd=0,
            padx=2,
            pady=0,
            cursor="hand2"
        )
        self.delete_btn.pack(side=tk.LEFT)
        
        # Hover effects
        self.delete_btn.bind("<Enter>", self._on_hover_enter)
        self.delete_btn.bind("<Leave>", self._on_hover_leave)
    
    def _on_delete_clicked(self):
        """Handles delete button click by calling the callback and destroying the widget."""
        if self.on_delete_callback:
            self.on_delete_callback(self.tag_text)
        self.destroy()
    
    def _on_hover_enter(self, event):
        """Changes delete button appearance on hover."""
        self.delete_btn.config(bg="#ff6b6b", fg="white")
    
    def _on_hover_leave(self, event):
        """Restores delete button appearance when not hovering."""
        self.delete_btn.config(bg="#5a5a5a", fg="#ff6b6b")


class AITagContainer(Frame):
    """
    Container widget that manages a collection of AI-generated tag pills.
    
    This widget displays tags in a flowing layout that wraps to multiple
    rows as needed. Each tag has an individual delete button.
    """
    
    def __init__(self, parent, **kwargs):
        """
        Initializes the AI tag container.
        
        Args:
            parent: The parent Tkinter widget
            **kwargs: Additional Frame configuration options
        """
        super().__init__(parent, **kwargs)
        
        # Configure container styling
        self.config(
            bg=STYLE_CONFIG["widget_bg_color"],
            relief=tk.SUNKEN,
            bd=2,
            padx=10,
            pady=10
        )
        
        # Store current tags and their pill widgets
        self.tag_pills = {}  # {tag_text: TagPill widget}
        
        # Create a flow container for pills
        self.flow_container = Frame(self, bg=STYLE_CONFIG["widget_bg_color"])
        self.flow_container.pack(fill=tk.BOTH, expand=True)
        
        # Current row frame for flow layout
        self.current_row = None
        self.current_row_width = 0
        self.max_row_width = 600  # Approximate max width before wrapping
    
    def add_tag(self, tag_text):
        """
        Adds a new tag pill to the container.
        
        Args:
            tag_text (str): The tag text to add
        """
        # Don't add duplicate tags
        if tag_text in self.tag_pills:
            return
        
        # Create new row if needed
        if self.current_row is None or self.current_row_width > self.max_row_width:
            self._create_new_row()
        
        # Create the pill
        pill = TagPill(
            self.current_row,
            tag_text,
            on_delete_callback=self._on_tag_deleted
        )
        pill.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Store the pill
        self.tag_pills[tag_text] = pill
        
        # Update row width estimate (rough calculation)
        self.current_row_width += len(tag_text) * 8 + 40  # char width + padding
    
    def add_tags(self, tag_list):
        """
        Adds multiple tags to the container.
        
        Args:
            tag_list (list): List of tag strings to add
        """
        for tag in tag_list:
            if tag.strip():  # Only add non-empty tags
                self.add_tag(tag.strip())
    
    def remove_tag(self, tag_text):
        """
        Removes a specific tag from the container.
        
        Args:
            tag_text (str): The tag text to remove
        """
        if tag_text in self.tag_pills:
            self.tag_pills[tag_text].destroy()
            del self.tag_pills[tag_text]
    
    def clear_all_tags(self):
        """Removes all tags from the container."""
        for pill in self.tag_pills.values():
            pill.destroy()
        self.tag_pills.clear()
        
        # Clear row containers
        for widget in self.flow_container.winfo_children():
            widget.destroy()
        
        self.current_row = None
        self.current_row_width = 0
    
    def get_all_tags(self):
        """
        Returns all current tags as a list.
        
        Returns:
            list: List of tag strings currently displayed
        """
        return list(self.tag_pills.keys())
    
    def _create_new_row(self):
        """Creates a new row frame for the flow layout."""
        self.current_row = Frame(self.flow_container, bg=STYLE_CONFIG["widget_bg_color"])
        self.current_row.pack(anchor=tk.W, pady=2)
        self.current_row_width = 0
    
    def _on_tag_deleted(self, tag_text):
        """
        Callback when a tag's delete button is clicked.
        
        Args:
            tag_text (str): The tag that was deleted
        """
        if tag_text in self.tag_pills:
            del self.tag_pills[tag_text]
            # Note: The pill widget destroys itself in its _on_delete_clicked method
