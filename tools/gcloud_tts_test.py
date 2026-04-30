import os
from pathlib import Path

print('GOOGLE_APPLICATION_CREDENTIALS:', os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))

try:
    from google.cloud import texttospeech
    from google.cloud import translate_v2 as translate
except Exception as e:
    print('Google Cloud libraries not available:', e)
    raise SystemExit(1)

# Initialize clients
try:
    tts_client = texttospeech.TextToSpeechClient()
    translate_client = translate.Client()
    print('Initialized Google Cloud clients successfully')
except Exception as e:
    print('Failed to initialize Google Cloud clients:', e)
    raise SystemExit(1)

# List voices and look for Yoruba/Igbo
voices = tts_client.list_voices().voices
print(f'Total voices available: {len(voices)}')
found_yo = []
found_ig = []
for v in voices:
    for lc in v.language_codes:
        low = lc.lower()
        if 'yo' in low or 'yor' in low or 'yoruba' in v.name.lower():
            found_yo.append((v.name, lc))
        if 'ig' in low or 'ibo' in low or 'igbo' in v.name.lower():
            found_ig.append((v.name, lc))

print('Yoruba-like voices found:', found_yo)
print('Igbo-like voices found:', found_ig)

# Try translating a sample text
sample = 'Disease: Cassava Mosaic Disease. Recommended Treatment: Use resistant varieties.'
try:
    tr_yo = translate_client.translate(sample, target_language='yo')
    tr_ig = translate_client.translate(sample, target_language='ig')
    print('Sample translation (yo):', tr_yo.get('translatedText'))
    print('Sample translation (ig):', tr_ig.get('translatedText'))
except Exception as e:
    print('Translation failed:', e)

# If voices exist, synthesize a short sample for each found language code (first match)
out_dir = Path('audio')
out_dir.mkdir(exist_ok=True)

def synthesize(text, lang_code, out_path):
    try:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice_params = texttospeech.VoiceSelectionParams(language_code=lang_code, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = tts_client.synthesize_speech(input=synthesis_input, voice=voice_params, audio_config=audio_config)
        with open(out_path, 'wb') as f:
            f.write(response.audio_content)
        print('Wrote', out_path)
    except Exception as e:
        print('Synthesis failed for', lang_code, e)

if found_yo:
    name, lc = found_yo[0]
    synthesize('Pẹlẹ o! Eyi ayẹwo ohun Yoruba.', lc, out_dir / 'gcloud_yo_test.mp3')
else:
    print('No Yoruba voices available in Google Cloud TTS')

if found_ig:
    name, lc = found_ig[0]
    synthesize('Ndewo! Nke a bụ ule olu Igbo.', lc, out_dir / 'gcloud_ig_test.mp3')
else:
    print('No Igbo voices available in Google Cloud TTS')

print('Done')
