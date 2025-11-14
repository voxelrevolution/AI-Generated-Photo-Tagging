import threading
import speech_recognition as sr

from app.config import AUDIO_CONFIG, STYLE_CONFIG

class AudioHandler:
    """
    Handles background audio listening and transcription.
    """
    def __init__(self, main_app):
        self.app = main_app
        self.is_listening = threading.Event()
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = AUDIO_CONFIG["pause_threshold"]
        
        self.audio_thread = threading.Thread(target=self._background_listener)
        self.audio_thread.daemon = True
        self.audio_thread.start()

    def start_listening(self):
        """Signals the background audio thread to start listening."""
        if not self.is_listening.is_set():
            self.app.ui.set_record_button_color(STYLE_CONFIG["listening_color"])
            self.is_listening.set()

    def _background_listener(self):
        """
        A long-running thread that waits for a signal to listen for audio.
        """
        while True:
            self.is_listening.wait() # Block until start_listening() is called

            try:
                with sr.Microphone() as source:
                    self.app.ui.set_status("Listening...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    
                    try:
                        audio = self.recognizer.listen(source, phrase_time_limit=AUDIO_CONFIG["phrase_time_limit"])
                        self.app.ui.set_status("Transcribing...")
                        
                        self.is_listening.clear() # Stop listening after capturing audio

                        text = self.recognizer.recognize_google(audio)
                        self.app.handle_transcription(text)

                    except sr.UnknownValueError:
                        self.app.ui.set_status("Could not understand audio. Try again.")
                    except sr.RequestError as e:
                        self.app.ui.set_status(f"Speech service error: {e}")
                    except Exception as e:
                        self.app.ui.set_status(f"Audio error: {e}")
                    finally:
                        self.app.ui.set_record_button_color(STYLE_CONFIG["widget_bg_color"])
                        if self.is_listening.is_set():
                            self.is_listening.clear()

            except Exception as e:
                self.app.ui.set_status(f"Microphone error: {e}. Retrying...")
                self.app.ui.set_record_button_color(STYLE_CONFIG["widget_bg_color"])
                self.is_listening.clear()
                threading.Event().wait(2) # Pause before retrying
