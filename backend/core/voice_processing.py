import os
import logging
from typing import Optional, Dict, Any

# Import necessary libraries for voice processing
try:
    import speech_recognition as sr
    from vosk import Model, KaldiRecognizer
    import json
    from langdetect import detect
    import pyttsx3
except ImportError:
    logging.error("Required libraries for voice processing not installed.")
    logging.error("Please run: pip install vosk langdetect speechrecognition pyttsx3")

class VoiceProcessor:
    """Handles all voice-related processing including wake word detection,
    speech-to-text, and text-to-speech functionality."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the voice processor with configuration settings.
        
        Args:
            config: Dictionary containing configuration parameters
                - wake_word: The wake word to listen for (default: "Hey JARVIS")
                - vosk_models_path: Path to Vosk model directory
                - tts_model: Text-to-speech model to use
        """
        self.config = config
        self.wake_word = config.get("wake_word", "Hey JARVIS")
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Initialize Vosk models
        try:
            self.en_model = Model("vosk-model-small-en-us-0.15")
            self.hi_model = Model("vosk-model-small-hi-0.22")
            self.current_model = self.en_model  # Default to English
        except Exception as e:
            logging.error(f"Failed to initialize Vosk models: {e}")
            raise
        
        # Initialize TTS engine using pyttsx3
        try:
            self.tts_engine = pyttsx3.init()
            # Configure voice properties
            voices = self.tts_engine.getProperty('voices')
            self.tts_engine.setProperty('voice', voices[0].id)  # Index 0 is usually the default voice
            self.tts_engine.setProperty('rate', 150)  # Speed of speech
            self.tts_engine.setProperty('volume', 0.9)  # Volume level
            logging.info("TTS engine initialized successfully using pyttsx3")
        except Exception as e:
            logging.error(f"Failed to initialize TTS engine: {str(e)}")
            self.tts_engine = None
            # Attempt to initialize with a different model as fallback
            try:
                self.tts_engine = TTS(model_name="tts_models/en/vctk/vits", 
                                    progress_bar=False, gpu=False)
                logging.info("TTS engine initialized with fallback model")
            except Exception as e:
                logging.error(f"Failed to initialize fallback TTS engine: {str(e)}")
                self.tts_engine = None
    
    def detect_wake_word(self, audio_stream) -> bool:
        """Listen for the wake word in the audio stream.
        
        Args:
            audio_stream: Audio data to process
            
        Returns:
            bool: True if wake word detected, False otherwise
        """
        try:
            text = self.recognizer.recognize_google(audio_stream)
            return self.wake_word.lower() in text.lower()
        except:
            return False
    
    async def transcribe(self, audio_data) -> str:
        """Convert speech to text using Vosk with automatic language detection.
        
        Args:
            audio_data: Audio data to transcribe
            
        Returns:
            str: Transcribed text
        """
        try:
            # First attempt with English model
            rec = KaldiRecognizer(self.en_model, 16000)
            rec.AcceptWaveform(audio_data)
            result = json.loads(rec.FinalResult())
            text = result.get("text", "")
            
            # Detect language
            if text and len(text.strip()) > 0:
                try:
                    lang = detect(text)
                    if lang == "hi":  # If Hindi detected, retry with Hindi model
                        rec = KaldiRecognizer(self.hi_model, 16000)
                        rec.AcceptWaveform(audio_data)
                        result = json.loads(rec.FinalResult())
                        text = result.get("text", "")
                except Exception as e:
                    logging.error(f"Language detection error: {e}")
            
            return text
        except Exception as e:
            logging.error(f"Transcription error: {e}")
            return ""
    
    def synthesize_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech using TTS engine.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            bytes: Audio data or None if synthesis failed
        """
        if not self.tts_engine:
            logging.error("TTS engine not initialized")
            return None
        
        try:
            # Generate speech and return audio data
            output_path = "temp_speech.wav"
            self.tts_engine.tts_to_file(text=text, file_path=output_path)
            
            # Read the file and return bytes
            with open(output_path, "rb") as f:
                audio_data = f.read()
            
            # Clean up temporary file
            if os.path.exists(output_path):
                os.remove(output_path)
                
            return audio_data
        except Exception as e:
            logging.error(f"Speech synthesis error: {e}")
            return None

    async def process_voice_input(self, audio_data) -> str:
        """Process voice input from microphone.
        
        Args:
            audio_data: Audio data from microphone
            
        Returns:
            str: Transcribed text from the audio
        """
        return await self.transcribe(audio_data)

    def listen_for_command(self):
        """Listen for a command using the microphone.
        
        Returns:
            str: Transcribed command or empty string if no command detected
        """
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            logging.info("Listening for command...")
            try:
                audio = self.recognizer.listen(source, timeout=5)
                return self.recognizer.recognize_google(audio)
            except sr.WaitTimeoutError:
                return ""
            except sr.UnknownValueError:
                return ""
            except Exception as e:
                logging.error(f"Error listening for command: {e}")
                return ""