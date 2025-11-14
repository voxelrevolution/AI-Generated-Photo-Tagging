import logging
import base64
import threading
import requests
import json

class VisionAnalyzer:
    """
    Handles analyzing image content using a vision-capable AI model.
    Encodes images, sends them to an AI for analysis, and returns descriptive tags.
    """
    def __init__(self, config):
        """
        Initializes the VisionAnalyzer with a given configuration.

        Args:
            config (dict): A dictionary containing configuration values like
                           API URL, model name, and prompts.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    def analyze_image_with_vision(self, image_path, callback):
        """
        Starts the vision analysis in a non-blocking background thread.

        Args:
            image_path (str): The path to the image to be analyzed. This is passed
                to the callback for context verification.
            callback (function): The function to call with the analysis results.
                It should accept (image_path, generated_tags, error).
        """
        if not image_path:
            self.logger.error("analyze_image_with_vision called with no image path.")
            callback(None, None, "Error: No image path provided.")
            return

        self.logger.info(f"Creating vision analysis thread for {image_path}.")
        vision_thread = threading.Thread(target=self._send_to_ollama, args=(image_path, callback))
        vision_thread.daemon = True
        vision_thread.start()

    def _encode_image(self, image_path):
        """
        Encodes an image file into a Base64 string.

        Args:
            image_path (str): The path to the image file.

        Returns:
            str or None: The Base64 encoded string of the image, or None on error.
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            self.logger.error(f"Image file not found at {image_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error encoding image {image_path}: {e}", exc_info=True)
            return None

    def _build_vision_prompt(self):
        """Constructs the prompt for the vision model from the config."""
        return self.config.get("VISION_MODEL_PROMPT", "Describe this image in 5 comma-separated keywords.")

    def _send_to_ollama(self, image_path, callback):
        """
        Encodes the image, sends it to the Ollama API for analysis, and invokes the callback.

        This function runs in a separate thread to avoid blocking the main UI.

        Args:
            image_path (str): The path to the image to be analyzed. Passed to the
                callback for context.
            callback (function): The callback to handle the response.
        """
        self.logger.info(f"Starting vision analysis for {image_path}.")
        encoded_image = self._encode_image(image_path)
        if not encoded_image:
            callback(image_path, None, f"Error: Could not read or encode image at {image_path}.")
            return

        prompt = self._build_vision_prompt()

        try:
            response = requests.post(
                self.config["OLLAMA_API_URL"],
                json={
                    "model": self.config.get("VISION_MODEL_NAME", "llava:7b"),
                    "prompt": prompt,
                    "images": [encoded_image],
                    "stream": False
                },
                timeout=self.config["API_TIMEOUT"]
            )
            response.raise_for_status()

            response_data = response.json()
            generated_tags = response_data.get('response', '').strip().replace('"', '')
            self.logger.info(f"Successfully received vision response for {image_path}. Tags: '{generated_tags[:50]}...'")
            
            callback(image_path, generated_tags, None)

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Ollama connection error for vision analysis: {e}")
            callback(image_path, None, "Vision Error: Could not connect to Ollama server.")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ollama request failed for vision analysis: {e}")
            callback(image_path, None, f"Vision Error: Request failed: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to decode Ollama vision response: {e}. Response: {response.text}")
            callback(image_path, None, "Vision Error: Unexpected response format.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred in vision analysis thread: {e}", exc_info=True)
            callback(image_path, None, f"An unexpected vision error occurred: {e}")

import logging
import base64
import threading
import requests
import json

class VisionAnalyzer:
    """
    Handles analyzing image content using a vision-capable AI model.
    Encodes images, sends them to an AI for analysis, and returns descriptive tags.
    """
    def __init__(self, config):
        """
        Initializes the VisionAnalyzer with a given configuration.

        Args:
            config (dict): A dictionary containing configuration values like
                           API URL, model name, and prompts.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    def analyze_image_with_vision(self, image_path, callback):
        """
        Starts the vision analysis in a non-blocking background thread.

        Args:
            image_path (str): The path to the image to be analyzed. This is passed
                to the callback for context verification.
            callback (function): The function to call with the analysis results.
                It should accept (image_path, generated_tags, error).
        """
        if not image_path:
            self.logger.error("analyze_image_with_vision called with no image path.")
            callback(None, None, "Error: No image path provided.")
            return

        self.logger.info(f"Creating vision analysis thread for {image_path}.")
        vision_thread = threading.Thread(target=self._send_to_ollama, args=(image_path, callback))
        vision_thread.daemon = True
        vision_thread.start()

    def _encode_image(self, image_path):
        """
        Encodes an image file into a Base64 string.

        Args:
            image_path (str): The path to the image file.

        Returns:
            str or None: The Base64 encoded string of the image, or None on error.
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except FileNotFoundError:
            self.logger.error(f"Image file not found at {image_path}")
            return None
        except Exception as e:
            self.logger.error(f"Error encoding image {image_path}: {e}", exc_info=True)
            return None

    def _build_vision_prompt(self):
        """Constructs the prompt for the vision model from the config."""
        return self.config.get("VISION_MODEL_PROMPT", "Describe this image in 5 comma-separated keywords.")

    def _send_to_ollama(self, image_path, callback):
        """
        Encodes the image, sends it to the Ollama API for analysis, and invokes the callback.

        This function runs in a separate thread to avoid blocking the main UI.

        Args:
            image_path (str): The path to the image to be analyzed. Passed to the
                callback for context.
            callback (function): The callback to handle the response.
        """
        self.logger.info(f"Starting vision analysis for {image_path}.")
        encoded_image = self._encode_image(image_path)
        if not encoded_image:
            callback(image_path, None, f"Error: Could not read or encode image at {image_path}.")
            return

        prompt = self._build_vision_prompt()

        try:
            response = requests.post(
                self.config["OLLAMA_API_URL"],
                json={
                    "model": self.config.get("VISION_MODEL_NAME", "llava:7b"),
                    "prompt": prompt,
                    "images": [encoded_image],
                    "stream": False
                },
                timeout=self.config["API_TIMEOUT"]
            )
            response.raise_for_status()

            response_data = response.json()
            generated_tags = response_data.get('response', '').strip().replace('"', '')
            self.logger.info(f"Successfully received vision response for {image_path}. Tags: '{generated_tags[:50]}...'")
            
            callback(image_path, generated_tags, None)

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Ollama connection error for vision analysis: {e}")
            callback(image_path, None, "Vision Error: Could not connect to Ollama server.")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ollama request failed for vision analysis: {e}")
            callback(image_path, None, f"Vision Error: Request failed: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to decode Ollama vision response: {e}. Response: {response.text}")
            callback(image_path, None, "Vision Error: Unexpected response format.")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred in vision analysis thread: {e}", exc_info=True)
            callback(image_path, None, f"An unexpected vision error occurred: {e}")
