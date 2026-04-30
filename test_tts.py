import os
import tempfile
from gtts import gTTS
import pygame
import time

def speak(text, language='en'):
    """
    Convert text to speech and play it.
    Supports multiple languages.
    """
    try:
        # Map language codes to gTTS language codes
        lang_map = {
            'en': 'en',
            'yo': 'yo',  # Yoruba
            'ha': 'ha',  # Hausa
            'ig': 'ig'   # Igbo
        }

        tts_lang = lang_map.get(language, 'en')

        # Create TTS object
        tts = gTTS(text=text, lang=tts_lang, slow=False)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_filename = temp_file.name
            tts.save(temp_filename)

        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Load and play the audio
        pygame.mixer.music.load(temp_filename)
        pygame.mixer.music.play()

        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        # Clean up
        pygame.mixer.music.stop()
        os.unlink(temp_filename)

        return True

    except Exception as e:
        print(f"TTS Error: {e}")
        return False

# Test TTS with different languages
languages = ['en', 'yo', 'ha', 'ig']
test_text = 'Test message for TTS'

for lang in languages:
    try:
        result = speak(test_text, lang)
        print(f'TTS test for {lang}: Success')
    except Exception as e:
        print(f'TTS test for {lang}: Failed - {e}')