import threading
import requests
import json
import logging

class TagProcessor:
    """
    Handles processing of text-based tags using a language model.
    This class is responsible for taking raw text (from voice or vision AI),
    constructing a prompt, sending it to the text-processing AI, and returning
    a cleaned-up, comma-separated list of keywords.
    """
    def __init__(self, config):
        """
        Initializes the TagProcessor with a given configuration.

        Args:
            config (dict): A dictionary containing configuration values,
                           including the model name and prompt template.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)

    def process_tags_with_ai(self, image_path, manual_tags, transcribed_text, callback, advance_on_complete=False):
        """
        Starts the AI tag cleaning process in a non-blocking background thread.

        Args:
            image_path (str): The path to the image file, used for context in callbacks.
            manual_tags (str): Any tags manually entered by the user.
            transcribed_text (str): The raw text from voice transcription or vision analysis.
            callback (function): The function to call upon completion.
            advance_on_complete (bool): Flag to indicate if the app should move to the
                next image after processing.
        """
        if not transcribed_text:
            self.logger.warning(f"process_tags_with_ai called for {image_path} with no transcribed_text. Skipping.")
            callback(image_path, manual_tags, "", None, advance_on_complete)
            return

        self.logger.info(f"Creating AI text processing thread for {image_path}.")
        ai_thread = threading.Thread(target=self._send_to_ollama, args=(image_path, manual_tags, transcribed_text, callback, advance_on_complete))
        ai_thread.daemon = True
        ai_thread.start()

    def _send_to_ollama(self, image_path, manual_tags, transcribed_text, callback, advance_on_complete):
        """
        Sends the transcribed text to the Ollama API for cleaning and keyword extraction.

        This function runs in a separate thread.

        Args:
            image_path (str): The path to the image file for context.
            manual_tags (str): Manually entered tags.
            transcribed_text (str): The text to be processed.
            callback (function): The function to call upon completion or error.
            advance_on_complete (bool): A flag passed through to the callback.
        """
        prompt = self._build_prompt(transcribed_text)
        self.logger.info(f"Starting Ollama text request for {image_path}. Input: '{transcribed_text[:50]}...'")
        
        try:
            response = requests.post(
                self.config["OLLAMA_API_URL"],
                json={
                    "model": self.config["TEXT_MODEL_NAME"],
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.config["API_TIMEOUT"]
            )
            response.raise_for_status()

            response_data = response.json()
            cleaned_text = response_data.get('response', '').strip().replace('"', '')
            
            # Strip common AI preambles that ignore instructions
            preambles_to_remove = [
                "Here are the keywords:",
                "Here are the keywords",
                "Keywords:",
                "The keywords are:",
                "Tags:",
                "Here you go:",
            ]
            
            for preamble in preambles_to_remove:
                if cleaned_text.lower().startswith(preamble.lower()):
                    cleaned_text = cleaned_text[len(preamble):].strip()
                    break
            
            # Remove leading/trailing colons or commas
            cleaned_text = cleaned_text.strip(':,').strip()
            
            self.logger.info(f"Successfully received text response for {image_path}. Cleaned text: '{cleaned_text[:50]}...'")
            
            callback(image_path, manual_tags, cleaned_text, None, advance_on_complete)

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Ollama connection error for text processing: {e}")
            callback(image_path, manual_tags, None, "AI Error: Could not connect to Ollama server.", advance_on_complete)
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ollama request failed for text processing: {e}")
            callback(image_path, manual_tags, None, f"AI Error: Request failed: {e}", advance_on_complete)
        except (KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to decode Ollama text response: {e}. Response: {response.text}")
            callback(image_path, manual_tags, None, "AI Error: Unexpected response format from server.", advance_on_complete)
        except Exception as e:
            self.logger.error(f"An unexpected error occurred in text processing thread: {e}", exc_info=True)
            callback(image_path, manual_tags, None, f"An unexpected AI error occurred: {e}", advance_on_complete)

    def _build_prompt(self, raw_tags):
        """Constructs the full prompt for the AI model."""
        template = self.config.get("TEXT_MODEL_PROMPT_TEMPLATE", "You are a helpful assistant. Clean up this text: {text_input}")
        return template.format(text_input=raw_tags)
