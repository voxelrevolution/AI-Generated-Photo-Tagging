"""
Configuration for the Photo Sorter V2 application.
"""

# Centralized style configuration for easy theming and maintenance
STYLE_CONFIG = {
    "bg_color": "#2e2e2e",
    "image_bg_color": "#1e1e1e",
    "widget_bg_color": "#4a4a4a",
    "text_color": "white",
    "button_relief": "flat",
    "font_main": ("Arial", 10),
    "font_nav": ("Arial", 20),
    "keep_color": "#006400",
    "delete_color": "#8B0000",
    "listening_color": "#990000" # Dark red for listening indicator
}

# Tag Pill UI Configuration
TAG_PILL_STYLE = {
    "pill_bg_color": "#5a5a5a",  # Slightly lighter than widget background
    "pill_text_color": "white",
    "pill_font": ("Arial", 9),
    "delete_btn_color": "#ff6b6b",  # Light red for delete button
    "delete_btn_hover_bg": "#ff6b6b",
    "delete_btn_hover_fg": "white",
    "delete_btn_font": ("Arial", 12, "bold"),
    "container_bg_color": "#4a4a4a",  # Match widget background
    "container_padding": 10,
    "pill_padding_x": 8,
    "pill_padding_y": 4,
    "pill_spacing": 2,
    "max_row_width": 600  # Max width before wrapping to new row
}

# AI Configuration
AI_CONFIG = {
    "ENABLED_BY_DEFAULT": True,
    "OLLAMA_API_URL": "http://localhost:11434/api/generate",
    "VISION_MODEL_NAME": "llava:7b",
    "TEXT_MODEL_NAME": "llama3.1:8b",
    "API_TIMEOUT": 15, # in seconds
    "VISION_MODEL_PROMPT": (
        "Your sole task is to analyze the provided image and generate a concise, comma-separated list of 3 to 5 descriptive keywords. "
        "Focus on the main subjects, setting, and any notable actions or attributes. Do not add any introductory text, explanations, or any text other than the keywords themselves. "
        "For example, if you see a picture of a dog on a beach, your output should be: dog, beach, sunny, playing, water"
    ),
    "TEXT_MODEL_PROMPT_TEMPLATE": (
        "Convert this text into a comma-separated list of keywords. "
        "Output ONLY the keywords with commas between them. "
        "Do NOT include ANY other text. "
        "Do NOT say 'Here are the keywords' or any similar phrase. "
        "Do NOT add explanations or introductions. "
        "ONLY output the keywords themselves.\n\n"
        "Example Input: 'I think this is a picture of my friend Mason and his dog, a golden retriever, playing at the park on a sunny day.'\n"
        "Example Output: mason, dog, golden retriever, park, sunny day, playing\n\n"
        "Input Text: '{text_input}'\n"
        "Keywords:"
    )
}

# Directory Configuration
DIR_CONFIG = {
    "kept_dir_name": "sorted_kept",
    "deleted_dir_name": "sorted_deleted",
    "log_filename": "photo_log.json"
}

# Audio Configuration
AUDIO_CONFIG = {
    "pause_threshold": 2.0,
    "phrase_time_limit": 12
}

# Application settings
APP_CONFIG = {
    "title": "Rapid Photo Sorter V2",
    "geometry": "1200x800"
}
