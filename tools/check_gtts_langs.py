from gtts.lang import tts_langs
langs = tts_langs()
for code in ['yo','ha','ig','en']:
    print(f"{code} ->", code in langs, langs.get(code))
print('\nTotal languages:', len(langs))
