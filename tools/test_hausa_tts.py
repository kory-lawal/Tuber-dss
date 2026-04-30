from gtts import gTTS
import os

os.makedirs('audio', exist_ok=True)
text = "Sannu! Wannan gwajin murya ne na Hausa."
try:
    tts = gTTS(text=text, lang='ha')
    path = 'audio/hausa_test.mp3'
    tts.save(path)
    print('SUCCESS:', path)
except Exception as e:
    print('ERROR:', e)
