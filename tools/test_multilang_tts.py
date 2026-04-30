from gtts import gTTS
from gtts.lang import tts_langs
import os

os.makedirs('audio', exist_ok=True)

langs = tts_langs()

samples = {
    'en': "Hello! This is an English test.",
    'ha': "Sannu! Wannan gwajin murya ne na Hausa.",
    'yo': "Pẹlẹ o! Eyi ayẹwo ohun Yoruba ni.",
    'ig': "Ndewo! Nke a bụ ule olu Igbo."
}

for code, text in samples.items():
    out_path = f'audio/{code}_test.mp3'
    try:
        if code in langs:
            tts = gTTS(text=text, lang=code)
            tts.save(out_path)
            print(f'SUCCESS: {out_path} (lang={code})')
        else:
            # fallback to English
            tts = gTTS(text=samples['en'], lang='en')
            tts.save(out_path)
            print(f'FALLBACK: {out_path} (requested {code} not supported, saved English audio)')
    except Exception as e:
        print(f'ERROR generating {out_path} for lang={code}: {e}')
