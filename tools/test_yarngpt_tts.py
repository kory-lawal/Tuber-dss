import os
import requests
import base64
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

API_URL = os.environ.get('YARNGPT_TTS_URL')
API_KEY = os.environ.get('YARNGPT_API_KEY')

print('YARNGPT_TTS_URL:', API_URL)
print('YARNGPT_API_KEY set:', bool(API_KEY))

if not API_URL or not API_KEY:
    print('Missing YARNGPT env vars; set YARNGPT_TTS_URL and YARNGPT_API_KEY')
    raise SystemExit(1)

headers = {'Authorization': f'Bearer {API_KEY}', 'Accept': 'application/octet-stream'}

samples = {
    'en': 'Hello! This is an English test from Yarngpt TTS.',
    'yo': 'Pẹlẹ o! Eyi ayẹwo ohun Yoruba lati Yarngpt.',
    'ig': 'Ndewo! Nke a bụ ule olu Igbo si Yarngpt.',
    'ha': 'Sannu! Wannan gwajin murya na Hausa daga Yarngpt.'
}

out_dir = Path('audio')
out_dir.mkdir(exist_ok=True)

for code, text in samples.items():
    out_path = out_dir / f'yarngpt_{code}_test.mp3'
    payload = {'text': text, 'lang': code}
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        ct = resp.headers.get('Content-Type','')
        if ct.startswith('audio') or ct == 'application/octet-stream':
            with open(out_path, 'wb') as f:
                f.write(resp.content)
            print('WROTE', out_path)
            continue
        # try parse json with base64
        j = resp.json()
        b64 = j.get('audio') or j.get('audio_base64')
        if b64:
            with open(out_path, 'wb') as f:
                f.write(base64.b64decode(b64))
            print('WROTE', out_path)
        else:
            print('No audio found in response for', code, 'response keys:', list(j.keys()))
    except Exception as e:
        print('ERROR for', code, e)

print('Done')
