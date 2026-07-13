# Tuber DSS

## Abstract

Tuber crop diseases remain a major challenge to agricultural productivity, especially among smallholder farmers who often lack timely access to extension services and expert diagnosis. This project presents Tuber DSS, a multilingual voice-enabled decision support system designed to provide accessible, real-time guidance for common tuber crop diseases. The system is implemented as a Streamlit-based application that allows users to enter symptoms through text or voice, select a preferred language, and receive a likely disease name, treatment recommendation, and audio response. Diagnosis is performed by matching user symptoms against language-specific disease datasets stored in CSV files, while speech output is generated through a multilingual text-to-speech pipeline that combines Yarngpt, gTTS, and pyttsx3 as fallback options. By supporting English, Yoruba, Hausa, and Igbo, the system aims to improve access to agricultural advisory support for farmers who may prefer or rely on indigenous languages and voice interaction. The current implementation focuses on practical, low-cost deployment and ease of use, making it suitable for early disease detection and basic decision support in resource-constrained settings.

## System Implementation and Result

### Project Overview
Tuber DSS is a voice-enabled crop disease diagnosis assistant built with Streamlit. The system accepts either typed symptom descriptions or recorded speech and returns:
- a likely disease name
- a recommended treatment
- an audio response in the selected language

Supported languages:
- English
- Yoruba
- Hausa
- Igbo

The system is designed for farmers or agricultural users who need quick guidance about tuber crop symptoms, particularly in West African languages.

---

## System Architecture

The application is composed of three main layers:

1. **User Interface**
   - Built using `streamlit` in `app.py`
   - Supports language selection, text input, voice recording, diagnosis trigger, and audio playback
2. **Diagnosis Engine**
   - Implemented in `diagnosis.py`
   - Loads disease symptom data from CSV files under `data/`
   - Matches user-provided symptoms to known diseases using keyword similarity
3. **Text-to-Speech (TTS) & Audio**
   - Uses `gTTS` where available
   - Uses `pyttsx3` as an offline fallback
   - Can optionally use Yarngpt TTS if configured with `YARNGPT_API_KEY` and `YARNGPT_TTS_URL`
   - Saves generated audio to `audio/`

---


















## Algorithm

This section describes the step-by-step algorithm used by the Diagnosis Engine to convert user symptoms into a likely disease and recommended treatment.

- **Input:** user symptom text (typed or transcribed), selected language
- **Output:** `disease_name`, `treatment`, `confidence_score`

Algorithm steps:

1. Normalize input
  - Convert to lowercase, remove punctuation, and normalize whitespace
  - Perform simple language-specific token mapping (e.g., common synonyms)

2. Tokenize and extract keywords
  - Split normalized text into tokens
  - Remove stopwords for the selected language
  - Optionally stem or lemmatize tokens (lightweight rule-based)

3. Load disease database for language
  - Attempt to load the CSV for the chosen language from `data/`
  - If not available, fall back to `data/diseases_english.csv`

4. Compute matching scores for each disease
  - For each disease row, normalize and tokenize the disease `Symptoms` field
  - Compute an overlap score: number of matched tokens between input and disease symptoms
  - Optionally weight matches for rarer or more specific symptom tokens
  - Compute `confidence_score = overlap_count / max(len(input_tokens), len(symptom_tokens))`

5. Select best match
  - Choose the disease with the highest `confidence_score`
  - If `confidence_score >= THRESHOLD` (e.g., 0.4), return the disease and treatment
  - If no disease passes the threshold, return a fallback response asking for clarification

6. Post-processing and output
  - Construct a human-readable response in the selected language
  - Translate fallback or elaboration text if needed
  - Generate audio via the TTS pipeline (Yarngpt → gTTS → pyttsx3 fallbacks)

Pseudocode (high level):

```
input_text = normalize(user_input)
tokens = tokenize_and_filter(input_text, lang)
db = load_csv_for_language(lang)  # fallback to English
best = (None, 0.0)
for row in db:
   symptom_tokens = tokenize_and_filter(row.Symptoms, lang)
   overlap = count_overlap(tokens, symptom_tokens)
   score = overlap / max(len(tokens), len(symptom_tokens), 1)
   if score > best.score:
      best = (row, score)
if best.score >= THRESHOLD:
   return best.row.Disease, best.row.Treatment, best.score
else:
   return fallback_response(lang)
```

Notes and tuning:
- Choose `THRESHOLD` empirically using `test_diagnosis.py` and sample inputs
- Improve recall by expanding synonyms and using language-specific stopword lists
- Consider fuzzy matching (edit distance) or TF-IDF cosine similarity for better accuracy
- For ambiguous results, return the top-N matches and ask the user for clarifying symptoms


## Implementation Details

### 1. Data and Diagnosis Logic

`diagnosis.py` contains the core diagnosis logic.

- `LANGUAGE_CSV_FILES` maps each supported language to a CSV file:
  - `data/diseases_english.csv`
  - `data/diseases_yoruba.csv`
  - `data/diseases_hausa.csv`
  - `data/diseases_igbo.csv`
- `set_language(language)` loads the selected disease database and falls back to English if needed.
- `diagnose(symptoms)` analyses symptom text and finds the best disease match.
- The diagnosis algorithm:
  - normalizes user input
  - tokenizes symptom keywords
  - compares keywords to disease symptom words from the CSV
  - computes a matching score
  - returns the best disease if the score passes a threshold
  - returns a fallback response when the disease cannot be confidently identified

### 2. User Interface and Streamlit Flow

`app.py` does the following:

- loads environment variables with `python-dotenv`
- attempts to import optional packages for TTS, speech transcription, and recording
- applies modern custom CSS for a polished experience
- sets up Streamlit session state to preserve:
  - voice input
  - selected language
  - diagnosis result
  - recording status
- renders UI sections for language selection, voice recording, symptom entry, diagnosis, and audio playback

#### Language Selection

- Users choose among English, Yoruba, Hausa, and Igbo.
- The UI text and labels update to the selected language using translation mappings.

#### Voice Recording

- If `streamlit_mic_recorder` is available, the app renders a microphone recorder.
- The recorder saves audio into `recordings/input.wav`.
- If Whisper is installed and available, the app transcribes recorded audio into text.

#### Symptom Input

- The user may either type symptoms or speak them.
- The app uses voice text when available, otherwise it uses typed text.

#### Diagnosis Execution

- When the user clicks the Diagnose button:
  - the app checks that symptoms exist
  - it calls `diagnose(final_input)` from `diagnosis.py`
  - it stores and renders the diagnosis result

#### Result Display

- The app shows a result card containing:
  - disease name
  - treatment recommendation
- It also plays an audio response when TTS is available.

### 3. Text-to-Speech and Audio Output

The `speak()` function in `app.py` implements a multi-tier fallback strategy:

1. **Yarngpt TTS** (if configured and preferred for African languages)
2. **gTTS** for supported languages like English and Hausa
3. **pyttsx3** offline fallback for any language
4. **Yarngpt** secondary fallback if the first attempt fails
5. **English gTTS fallback** as a last resort

The function uses `deep_translator` to translate the response text into the selected language before generating audio.

If audio is generated successfully, it is played inside the Streamlit app using `st.audio()`.

---

## System Result

### Expected Output
After providing symptoms and clicking Diagnose, the system produces:
- a disease diagnosis label
- a recommended treatment or care advice
- an audio message with the disease and treatment

### Response Examples
- Input: `yellow leaves mosaic pattern`
  - Possible output: `Cassava Mosaic Disease`
  - Treatment: `Use resistant varieties and remove infected plants`
- Input: `black spots leaf blight`
  - Possible output: `Yam Anthracnose`
  - Treatment: `Apply fungicide and improve field sanitation`

### Supported Interaction Modes
- **Text entry** for symptom description
- **Voice recording** that is transcribed and diagnosed
- **Multilingual UI labels** for each supported language
- **Audio feedback** for treatment recommendations

### Result Artifacts
- `audio/response.mp3` or `audio/response.wav` after TTS generation
- `recordings/input.wav` for recorded voice input
- `data/` CSV files supporting each language

---

## Installation and Setup

### Prerequisites
- Python 3.8+ recommended
- `pip` package manager

### Install dependencies

```bash
pip install streamlit pandas gtts pyttsx3 python-dotenv
```

Optional packages for full functionality:

```bash
pip install whisper streamlit-mic-recorder deep-translator
```

### Configure optional Yarngpt TTS

Add the following environment variables if you want Yarngpt audio support:

```bash
YARNGPT_API_KEY=your_api_key
YARNGPT_TTS_URL=https://your-yarngpt-api-endpoint
```

### Run the app

```bash
streamlit run app.py
```

---

## Notes and Future Improvements

### Known behavior
- Yoruba and Igbo may use `pyttsx3` if gTTS does not support those languages.
- The system is designed to gracefully degrade: audio may still be available even when some services are unavailable.

### Suggested improvements
- Add a dedicated dataset of tuber disease symptoms for richer matching
- Improve model confidence scoring for ambiguous symptom sets
- Add a true audio recording button with feedback history
- Add caching for repeated diagnoses and audio generation
- Add a screen capture or demo video for user onboarding

---

## Where to Add Images

Include screenshots in the README at these locations:

1. **After the Project Overview**
   - Add an image showing the main app interface and language selector.
   - Example placeholder: `![App Interface](images/interface.png)`

2. **After the Voice Recording section**
   - Add an image showing the recorder in action and the transcription result.
   - Example placeholder: `![Voice Recording](images/voice-recording.png)`

3. **After the Result Display section**
   - Add a screenshot showing the diagnosis result card and the audio player.
   - Example placeholder: `![Diagnosis Result](images/diagnosis-result.png)`

4. **After the System Result section**
   - Add another screenshot or flow diagram showing the end-to-end response.
   - Example placeholder: `![System Workflow](images/system-workflow.png)`

> Tip: Create an `images/` directory in the repo and place your screenshot files there. Use the exact file names referenced above or update the markdown accordingly.

---

## Files Summary

- `app.py` — Streamlit front-end and TTS/voice handling
- `diagnosis.py` — diagnosis engine and language-specific CSV loading
- `data/` — language-specific disease symptom datasets
- `audio/` — generated audio output files
- `recordings/` — captured user voice recordings
- `TTS_FIXES.md` — TTS support investigation and fix notes
- `test_diagnosis.py` — simple diagnosis validation tests

---

## Usage Guide

1. Launch the application with `streamlit run app.py`
2. Choose a language from the top buttons
3. Enter symptoms in the text area or record symptoms by microphone
4. Click `Diagnose`
5. Review the disease and treatment results
6. Listen to the audio response if available

---

## Contact

For questions or further enhancements, inspect `app.py` and `diagnosis.py` to extend the diagnosis logic and multilingual support.
