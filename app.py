import streamlit as st
import os
import base64
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Local diagnosis logic
from diagnosis import diagnose, set_language

# Optional third-party imports
try:
    from gtts import gTTS
    has_gtts = True
except Exception:
    gTTS = None
    has_gtts = False

try:
    import whisper
    has_whisper = True
except Exception:
    whisper = None
    has_whisper = False

try:
    from streamlit_mic_recorder import mic_recorder
    has_recorder = True
except Exception:
    mic_recorder = None
    has_recorder = False

try:
    import requests
    has_requests = True
except Exception:
    requests = None
    has_requests = False

# Yarngpt TTS configuration
YARNGPT_API_KEY = os.environ.get('YARNGPT_API_KEY')
YARNGPT_TTS_URL = os.environ.get('YARNGPT_TTS_URL')
has_yarngpt = has_requests and bool(YARNGPT_API_KEY and YARNGPT_TTS_URL)

# ============================================================================
# PAGE CONFIGURATION & CUSTOM CSS/ANIMATIONS
# ============================================================================

st.set_page_config(
    page_title="🌱 Tuber DSS",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Modern, Nature-Inspired CSS with Animations
custom_css = """
<style>
    /* Root Color Variables */
    :root {
        --primary-green: #2E7D32;
        --light-green: #A5D6A7;
        --accent-green: #66BB6A;
        --background: #F5F7F6;
        --card-bg: #FFFFFF;
        --text-dark: #1B5E20;
        --text-light: #558B2F;
        --accent-yellow: #FFB300;
        --shadow: 0 4px 15px rgba(46, 125, 50, 0.1);
        --shadow-hover: 0 8px 25px rgba(46, 125, 50, 0.2);
    }

    /* Global Styles */
    body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #F5F7F6 0%, #E8F0E8 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .stApp {
        background: transparent;
    }

    /* Typography */
    h1, h2, h3 {
        color: var(--text-dark);
        font-weight: 600;
        letter-spacing: -0.5px;
    }

    /* Disable default streamlit header */
    [data-testid="stHeader"] {
        background: transparent;
        display: none;
    }

    /* Hide sidebar */
    [data-testid="collapsedControl"] {
        display: none;
    }

    /* Main container padding */
    [data-testid="stAppViewContainer"] > .main > .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 600px;
    }

    /* ===== ANIMATIONS ===== */

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.05);
            opacity: 0.9;
        }
    }

    @keyframes pulseLarge {
        0%, 100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(46, 125, 50, 0.4);
        }
        50% {
            transform: scale(1.02);
            box-shadow: 0 0 0 20px rgba(46, 125, 50, 0);
        }
    }

    @keyframes spin {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }

    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }

    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-8px);
        }
    }

    /* ===== HEADER SECTION ===== */

    .header-container {
        text-align: center;
        margin-bottom: 2.5rem;
        animation: slideInDown 0.6s ease-out;
    }

    .header-bg {
        background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%);
        border-radius: 20px;
        padding: 2.5rem 1.5rem;
        box-shadow: var(--shadow-hover);
        position: relative;
        overflow: hidden;
    }

    .header-bg::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
        pointer-events: none;
    }

    .leaf-icon {
        font-size: 3rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
        margin-bottom: 0.5rem;
    }

    .header-title {
        color: #FFFFFF;
        font-size: 2rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .header-subtitle {
        color: #E8F5E9;
        font-size: 1rem;
        font-weight: 400;
        margin: 0;
        letter-spacing: 0.3px;
    }

    /* ===== VOICE SECTION ===== */

    .voice-section {
        background: var(--card-bg);
        border-radius: 20px;
        padding: 2rem 1.5rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
        animation: fadeIn 0.6s ease-out 0.2s both;
    }

    .voice-label {
        text-align: center;
        color: var(--text-light);
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 1.5rem;
        letter-spacing: 0.5px;
    }

    .mic-button-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1.5rem;
    }

    .mic-button {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%);
        border: none;
        color: white;
        font-size: 3rem;
        cursor: pointer;
        box-shadow: var(--shadow-hover);
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        animation: pulseLarge 2s infinite;
    }

    .mic-button:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 30px rgba(46, 125, 50, 0.3);
    }

    .mic-button:active {
        transform: scale(0.95);
    }

    .recording-indicator {
        text-align: center;
        font-size: 0.9rem;
        color: var(--text-dark);
        font-weight: 500;
        min-height: 1.5rem;
    }

    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        animation: slideUp 0.4s ease-out;
    }

    .status-recording {
        background: #FFECB3;
        color: #F57F17;
    }

    .status-processing {
        background: #E1F5FE;
        color: #01579B;
    }

    .status-success {
        background: #C8E6C9;
        color: #1B5E20;
    }

    .spinner {
        display: inline-block;
        width: 1.2rem;
        height: 1.2rem;
        border: 2px solid rgba(46, 125, 50, 0.2);
        border-top: 2px solid #2E7D32;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-right: 0.5rem;
    }

    /* ===== LANGUAGE SELECTOR ===== */

    .language-section {
        margin-bottom: 2rem;
        animation: fadeIn 0.6s ease-out 0.3s both;
    }

    .language-label {
        color: var(--text-dark);
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        display: block;
    }

    .language-pills {
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
        justify-content: center;
    }

    .language-pill {
        padding: 0.6rem 1.2rem;
        border: 2px solid var(--light-green);
        border-radius: 25px;
        background: white;
        color: var(--text-light);
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .language-pill:hover {
        border-color: var(--accent-green);
        background: #F1F8E9;
        transform: translateY(-2px);
    }

    .language-pill.active {
        background: var(--primary-green);
        color: white;
        border-color: var(--primary-green);
        box-shadow: 0 4px 12px rgba(46, 125, 50, 0.2);
    }

    /* ===== TEXT INPUT SECTION ===== */

    .text-section {
        margin-bottom: 2rem;
        animation: fadeIn 0.6s ease-out 0.4s both;
    }

    .input-label {
        color: var(--text-dark);
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
        display: block;
    }

    .text-input {
        width: 100%;
        padding: 1rem;
        border: 2px solid var(--light-green);
        border-radius: 12px;
        font-size: 0.95rem;
        font-family: 'Segoe UI', sans-serif;
        background: white;
        color: var(--text-dark);
        transition: all 0.3s ease;
        resize: vertical;
        min-height: 100px;
    }

    .text-input:focus {
        outline: none;
        border-color: var(--primary-green);
        box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.1);
    }

    /* ===== RESULT CARD ===== */

    .result-card {
        background: white;
        border-left: 5px solid var(--primary-green);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow);
        animation: slideUp 0.5s ease-out;
    }

    .result-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--background);
    }

    .result-icon {
        font-size: 2.5rem;
        margin-right: 1rem;
    }

    .result-title {
        color: var(--text-dark);
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0;
    }

    .result-subtitle {
        color: var(--text-light);
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0;
    }

    .result-section {
        margin-bottom: 1rem;
    }

    .result-section:last-child {
        margin-bottom: 0;
    }

    .result-label {
        color: var(--text-light);
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .result-value {
        color: var(--text-dark);
        font-size: 1.05rem;
        font-weight: 500;
        line-height: 1.6;
        padding: 0.8rem;
        background: var(--background);
        border-radius: 8px;
        border-left: 3px solid var(--accent-yellow);
    }

    /* ===== BUTTONS ===== */

    .button-container {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin-bottom: 1.5rem;
        animation: fadeIn 0.6s ease-out 0.5s both;
        flex-wrap: wrap;
    }

    .custom-button {
        padding: 0.85rem 2rem;
        border: none;
        border-radius: 12px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: var(--shadow);
    }

    .btn-primary {
        background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%);
        color: white;
        flex: 1;
        min-width: 150px;
    }

    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }

    .btn-primary:active {
        transform: translateY(0);
    }

    .btn-secondary {
        background: white;
        color: var(--primary-green);
        border: 2px solid var(--primary-green);
    }

    .btn-secondary:hover {
        background: #F1F8E9;
        transform: translateY(-2px);
    }

    .btn-reset {
        background: #FFF3E0;
        color: #E65100;
        padding: 0.6rem 1.2rem;
        font-size: 0.9rem;
    }

    .btn-reset:hover {
        background: #FFE0B2;
    }

    /* ===== AUDIO PLAYER ===== */

    .audio-section {
        background: var(--background);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        text-align: center;
        animation: slideUp 0.5s ease-out 0.1s both;
    }

    .audio-label {
        color: var(--text-light);
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        display: block;
    }

    .audio-player {
        width: 100%;
        border-radius: 8px;
    }

    /* ===== MESSAGE ALERTS ===== */

    .alert-box {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        animation: slideUp 0.4s ease-out;
    }

    .alert-warning {
        background: #FFF9C4;
        border-left: 4px solid #FBC02D;
        color: #F57F17;
    }

    .alert-success {
        background: #C8E6C9;
        border-left: 4px solid #2E7D32;
        color: #1B5E20;
    }

    .alert-error {
        background: #FFCDD2;
        border-left: 4px solid #C62828;
        color: #B71C1C;
    }

    /* ===== MOBILE RESPONSIVE ===== */

    @media (max-width: 640px) {
        [data-testid="stAppViewContainer"] > .main > .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
            max-width: 100%;
        }

        .header-bg {
            padding: 2rem 1rem;
        }

        .header-title {
            font-size: 1.6rem;
        }

        .header-subtitle {
            font-size: 0.9rem;
        }

        .voice-section {
            padding: 1.5rem 1rem;
        }

        .mic-button {
            width: 100px;
            height: 100px;
            font-size: 2.5rem;
        }

        .button-container {
            flex-direction: column;
        }

        .btn-primary {
            width: 100%;
        }

        .custom-button {
            width: 100%;
            justify-content: center;
        }

        .language-pills {
            gap: 0.4rem;
        }

        .result-card {
            padding: 1.2rem 1rem;
        }

        .result-icon {
            font-size: 2rem;
        }

        .result-title {
            font-size: 1.1rem;
        }

        .form-element {
            margin-bottom: 1.2rem !important;
        }
    }

    /* Style Streamlit Buttons */
    .stButton > button {
        width: 100%;
        padding: 0.85rem 1.5rem !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.1) !important;
        background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%) !important;
        color: white !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(46, 125, 50, 0.2) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Language selector buttons - first 4 columns of buttons */
    [data-testid="column"]:nth-child(1) .stButton > button,
    [data-testid="column"]:nth-child(2) .stButton > button,
    [data-testid="column"]:nth-child(3) .stButton > button,
    [data-testid="column"]:nth-child(4) .stButton > button {
        padding: 0.6rem 1rem !important;
        font-size: 0.9rem !important;
        background: white !important;
        color: #558B2F !important;
        border: 2px solid #A5D6A7 !important;
        border-radius: 25px !important;
        width: 100% !important;
    }

    [data-testid="column"]:nth-child(1) .stButton > button:hover,
    [data-testid="column"]:nth-child(2) .stButton > button:hover,
    [data-testid="column"]:nth-child(3) .stButton > button:hover,
    [data-testid="column"]:nth-child(4) .stButton > button:hover {
        background: #F1F8E9 !important;
        border-color: #66BB6A !important;
    }

    /* Diagnose button styling */
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 100%) !important;
        color: white !important;
        flex: 1 !important;
    }

    /* Reset button styling */
    .stButton > button:has-text("🔄") {
        background: #FFF3E0 !important;
        color: #E65100 !important;
        border: 2px solid #FFB300 !important;
    }

    .stButton > button:has-text("🔄"):hover {
        background: #FFE0B2 !important;
    }

    /* Style Streamlit Text Area */
    .stTextArea > div > div > textarea {
        border: 2px solid #A5D6A7 !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
        font-family: 'Segoe UI', sans-serif !important;
        background: white !important;
        color: #1B5E20 !important;
        resize: vertical !important;
        min-height: 100px !important;
    }

    .stTextArea > div > div > textarea:focus {
        outline: none !important;
        border-color: #2E7D32 !important;
        box-shadow: 0 0 0 3px rgba(46, 125, 50, 0.1) !important;
    }

    /* Hide text area label */
    .stTextArea > label {
        display: none !important;
    }

    /* Mic recorder styling */
    .stAudio {
        width: 100% !important;
        border-radius: 12px !important;
    }

    /* Column adjustments for buttons */
    .stColumns {
        gap: 1rem !important;
    }

    /* Close button styling */
    button[kind="header"] {
        display: none !important;
    }

    /* Footer */
    footer {
        display: none !important;
    }

    /* Spinner styling */
    .stSpinner > div {
        border-color: #A5D6A7 !important;
        border-top-color: #2E7D32 !important;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def save_recorder_audio(audio_obj, out_path):
    """Normalize recorder output and write raw bytes to out_path."""
    try:
        data = None
        if isinstance(audio_obj, dict):
            if 'bytes' in audio_obj and isinstance(audio_obj['bytes'], (bytes, bytearray)):
                data = audio_obj['bytes']
            elif 'blob' in audio_obj and isinstance(audio_obj['blob'], (bytes, bytearray)):
                data = audio_obj['blob']
            elif 'base64' in audio_obj and isinstance(audio_obj['base64'], str):
                data = base64.b64decode(audio_obj['base64'])
            elif 'dataUrl' in audio_obj or 'data_url' in audio_obj:
                s = audio_obj.get('dataUrl') or audio_obj.get('data_url')
                if isinstance(s, str) and s.startswith('data:'):
                    _, b64 = s.split(',', 1)
                    data = base64.b64decode(b64)
        elif isinstance(audio_obj, (bytes, bytearray)):
            data = bytes(audio_obj)
        elif isinstance(audio_obj, str):
            if audio_obj.startswith('data:'):
                _, b64 = audio_obj.split(',', 1)
                data = base64.b64decode(b64)
            elif os.path.exists(audio_obj):
                with open(audio_obj, 'rb') as f:
                    data = f.read()

        if data is None:
            return False, 'Unsupported audio format'

        with open(out_path, 'wb') as f:
            f.write(data)
        return True, None
    except Exception as e:
        return False, str(e)

def yarngpt_synthesize(text: str, lang: str, out_path: str) -> bool:
    """Call Yarngpt TTS API."""
    if not has_yarngpt:
        return False
    headers = {
        'Authorization': f'Bearer {YARNGPT_API_KEY}',
        'Accept': 'application/octet-stream'
    }
    payload = {'text': text, 'lang': lang}
    try:
        resp = requests.post(YARNGPT_TTS_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        content_type = resp.headers.get('Content-Type', '')
        if content_type.startswith('audio') or content_type == 'application/octet-stream':
            with open(out_path, 'wb') as f:
                f.write(resp.content)
            return True
        try:
            j = resp.json()
            b64 = j.get('audio') or j.get('audio_base64')
            if b64:
                with open(out_path, 'wb') as f:
                    f.write(base64.b64decode(b64))
                return True
        except Exception:
            pass
        return False
    except Exception:
        return False

def speak(text, language="English", already_translated=False):
    """Generate TTS audio response with multi-fallback support."""
    try:
        requested = language_codes.get(language, "en")
        translated_text = text
        file_path = "audio/response.mp3"

        # For non-English languages, try translation
        if not already_translated and language != "English":
            try:
                from deep_translator import GoogleTranslator
                translated_text = GoogleTranslator(source='auto', target=requested).translate(text)
            except Exception:
                # If translation fails, use original text
                translated_text = text

        # Priority 1: Use Yarngpt for African languages (preferred when configured)
        if has_yarngpt and requested in ("yo", "ig", "ha"):
            try:
                ok = yarngpt_synthesize(translated_text, requested, file_path)
                if ok:
                    return file_path
            except Exception:
                pass

        # Priority 2: Try gTTS (best quality for supported languages like English/Hausa)
        if has_gtts:
            try:
                from gtts.lang import tts_langs
                supported = tts_langs()
                # Check if language is supported by gTTS
                if supported and requested in supported:
                    tts = gTTS(text=translated_text, lang=requested, slow=False)
                    tts.save(file_path)
                    return file_path
            except Exception:
                pass

        # Priority 3: Use pyttsx3 as offline fallback for any language
        try:
            import pyttsx3
            engine = pyttsx3.init()
            # pyttsx3 typically writes WAV files; write to WAV then convert if needed
            wav_path = file_path.replace('.mp3', '.wav')
            engine.save_to_file(translated_text, wav_path)
            engine.runAndWait()
            if os.path.exists(wav_path):
                return wav_path
        except Exception:
            pass

        # Priority 4: Try Yarngpt as a secondary fallback if not tried above
        if has_yarngpt:
            try:
                ok = yarngpt_synthesize(translated_text, requested, file_path)
                if ok:
                    return file_path
            except Exception:
                pass

        # Priority 5: English fallback for gTTS
        if has_gtts and language != "English":
            try:
                tts = gTTS(text=translated_text, lang="en", slow=False)
                tts.save(file_path)
                return file_path
            except Exception:
                pass

        return None
    except Exception:
        return None

# ============================================================================
# CONFIGURATION
# ============================================================================

os.makedirs("audio", exist_ok=True)
os.makedirs("recordings", exist_ok=True)

# Load Whisper model once
model = None
if has_whisper:
    @st.cache_resource
    def load_model():
        try:
            return whisper.load_model("base")
        except Exception:
            return None
    model = load_model()

# Language configuration
language_codes = {
    "English": "en",
    "Yoruba": "yo",
    "Hausa": "ha",
    "Igbo": "ig"
}

translations = {
    "English": {
        "tap_to_speak": "🎤 Tap to Speak",
        "listening": "🎤 Listening...",
        "processing": "⚙️ Processing...",
        "select_language": "Select Language",
        "or_type_symptoms": "Or type symptoms...",
        "diagnose": "Diagnose",
        "reset": "Reset",
        "warning": "Please enter symptoms or record your voice.",
        "transcribing": "Transcribing audio...",
        "disease": "Disease",
        "treatment": "Treatment",
        "confidence": "Confidence",
        "audio_response": "🔊 Listen to Treatment",
        "audio_unavailable": "TTS is unavailable for your selected language.",
        "success": "Diagnosis Complete!"
    },
    "Yoruba": {
        "tap_to_speak": "🎤 Kọ Ọrọ",
        "listening": "🎤 N gbọ...",
        "processing": "⚙️ N ṣiṣẹ...",
        "select_language": "Yan Ede",
        "or_type_symptoms": "Tabi kọ aami aisan...",
        "diagnose": "Ṣayẹwo",
        "reset": "Tunbẹrẹ",
        "warning": "Jọwọ kọ tabi sọ aami aisan.",
        "transcribing": "N yi ohun pada si ọrọ...",
        "disease": "Arun",
        "treatment": "Itọ",
        "confidence": "Idaniloju",
        "audio_response": "🔊 Gbo Itọ",
        "audio_unavailable": "TTS ko ṣiṣẹ fun ede ti a yan.",
        "success": "Ayẹwo Pari!"
    },
    "Hausa": {
        "tap_to_speak": "🎤 Yi Magana",
        "listening": "🎤 Na sauraro...",
        "processing": "⚙️ Aiki...",
        "select_language": "Zaɓi Harshe",
        "or_type_symptoms": "Ko rubuta alamomi...",
        "diagnose": "Bincika",
        "reset": "Sake Saiti",
        "warning": "Da fatan a rubuta ko yi magana.",
        "transcribing": "Mayar da magana...",
        "disease": "Cuta",
        "treatment": "Maganin",
        "confidence": "Tabbas",
        "audio_response": "🔊 Sauraro Maganin",
        "audio_unavailable": "Babu TTS don yaren da aka zaɓa.",
        "success": "Bincika Gama!"
    },
    "Igbo": {
        "tap_to_speak": "🎤 Kụọ Olu",
        "listening": "🎤 Na-ege olu...",
        "processing": "⚙️ Na-arụ ọrụ...",
        "select_language": "Họrọ Asụsụ",
        "or_type_symptoms": "Ma ọ bụ tinye ...",
        "diagnose": "Chọpụta",
        "reset": "Malite Ọzọ",
        "warning": "Biko tinye ma ọ bụ kwuo mgbaàmà.",
        "transcribing": "Na-agbanwe olu...",
        "disease": "Ọrịa",
        "treatment": "Ọgwu",
        "confidence": "Amamihe",
        "audio_response": "🔊 Gee Ọgwu",
        "audio_unavailable": "TTS adịghị maka asụsụ ahọpụtara.",
        "success": "Atụmatụ Gara!"
    }
}

# Initialize session state
if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"
if "diagnosis_result" not in st.session_state:
    st.session_state.diagnosis_result = None
if "recording_status" not in st.session_state:
    st.session_state.recording_status = ""

selected_language = st.session_state.selected_language
set_language(selected_language)

# ============================================================================
# UI RENDERING
# ============================================================================

# HEADER
st.markdown(
    """
    <div class="header-container">
        <div class="header-bg">
            <div class="leaf-icon">🌱</div>
            <div class="header-title">Tuber DSS</div>
            <div class="header-subtitle">Voice-Based Crop Disease Assistant</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# LANGUAGE SELECTOR
st.markdown('<div class="language-section">', unsafe_allow_html=True)
st.markdown(f'<label class="language-label">{translations[selected_language]["select_language"]}</label>', unsafe_allow_html=True)

cols = st.columns(4)
languages = ["English", "Yoruba", "Hausa", "Igbo"]
for i, lang in enumerate(languages):
    with cols[i]:
        active_class = "active" if lang == selected_language else ""
        if st.button(
            lang,
            key=f"lang_{lang}",
            use_container_width=True,
            help=f"Switch to {lang}"
        ):
            st.session_state.selected_language = lang
            selected_language = lang
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

selected_language = st.session_state.selected_language

# VOICE SECTION
st.markdown(
    f"""
    <div class="voice-section">
        <div class="voice-label">{translations[selected_language]["tap_to_speak"]}</div>
        <div class="mic-button-container">
            <div class="mic-button">🎤</div>
        </div>
        <div class="recording-indicator" id="status-indicator"></div>
    </div>
    """,
    unsafe_allow_html=True
)

if has_recorder:
    audio_data = mic_recorder(
        start_prompt="Start",
        stop_prompt="Stop",
        key="recorder"
    )
else:
    audio_data = None
    st.markdown(
        '<div class="alert-box alert-warning">Microphone recorder not available. Please install: pip install streamlit-mic-recorder</div>',
        unsafe_allow_html=True
    )

if audio_data is not None:
    st.session_state.recording_status = translations[selected_language]["transcribing"]
    st.rerun()

if st.session_state.recording_status:
    audio_file_path = "recordings/input.wav"
    if audio_data:
        ok, err = save_recorder_audio(audio_data, audio_file_path)
        if ok and model is not None:
            try:
                result = model.transcribe(audio_file_path)
                st.session_state.voice_text = result.get("text", "").strip()
                st.session_state.recording_status = ""
                st.rerun()
            except Exception:
                st.session_state.recording_status = ""
                st.markdown(
                    '<div class="alert-box alert-error">Error transcribing audio. Please try again.</div>',
                    unsafe_allow_html=True
                )

# TEXT INPUT SECTION
st.markdown(
    f"""
    <div class="text-section">
        <label class="input-label">{translations[selected_language]["or_type_symptoms"]}</label>
    </div>
    """,
    unsafe_allow_html=True
)

user_input = st.text_area(
    "symptoms_input",
    value="",
    height=100,
    label_visibility="collapsed",
    placeholder=translations[selected_language]["or_type_symptoms"]
)

# Combine voice and text input
final_input = st.session_state.voice_text if st.session_state.voice_text else user_input

# BUTTONS
col1, col2 = st.columns([2, 1])

with col1:
    diagnose_clicked = st.button(
        f"🔍 {translations[selected_language]['diagnose']}",
        use_container_width=True,
        key="diagnose_btn"
    )

with col2:
    reset_clicked = st.button(
        f"🔄",
        use_container_width=True,
        key="reset_btn",
        help=translations[selected_language]["reset"]
    )

# DIAGNOSIS LOGIC
if diagnose_clicked:
    if final_input.strip() == "":
        st.markdown(
            f'<div class="alert-box alert-warning">{translations[selected_language]["warning"]}</div>',
            unsafe_allow_html=True
        )
    else:
        # Show processing status
        with st.spinner(translations[selected_language]["processing"]):
            try:
                result = diagnose(final_input)
                if result and isinstance(result, dict):
                    st.session_state.diagnosis_result = result
                else:
                    st.error("Error: Invalid diagnosis result")
            except Exception as e:
                st.error(f"Diagnosis error: {str(e)}")
                st.session_state.diagnosis_result = {
                    "disease": "Error",
                    "treatment": "Please try again or consult an agricultural extension officer."
                }

if st.session_state.diagnosis_result:
    result = st.session_state.diagnosis_result
    
    # Display result card
    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-header">
                <div class="result-icon">🦠</div>
                <div>
                    <div class="result-title">{result.get('disease', 'Unknown')}</div>
                    <div class="result-subtitle">{translations[selected_language]['success']}</div>
                </div>
            </div>
            <div class="result-section">
                <div class="result-label">💊 {translations[selected_language]['treatment']}</div>
                <div class="result-value">{result.get('treatment', 'No treatment information available.')}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Audio response
    response_text = f"{result.get('disease', 'Unknown disease')}. Treatment: {result.get('treatment', 'Consult extension officer.')}"
    audio_file = speak(response_text, selected_language)
    
    if audio_file:
        st.markdown(
            f"""
            <div class="audio-section">
                <label class="audio-label">{translations[selected_language]['audio_response']}</label>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.audio(audio_file)
    else:
        st.warning(translations[selected_language]['audio_unavailable'])

# RESET
if reset_clicked:
    st.session_state.voice_text = ""
    st.session_state.diagnosis_result = None
    st.session_state.recording_status = ""
    st.rerun()

# Footer spacing
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)