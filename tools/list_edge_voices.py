import asyncio
import edge_tts

async def main():
    voices = await edge_tts.list_voices()
    # Print voices that mention Yoruba or Igbo or have language codes
    found = []
    for v in voices:
        if 'yor' in v.get('locale', '').lower() or 'yo' in v.get('locale', '').lower() or 'ig' in v.get('locale', '').lower() or 'igbo' in v.get('name','').lower() or 'yoruba' in v.get('name','').lower():
            found.append(v)
    print('Matches:', len(found))
    for v in found[:50]:
        print(v)

    # Also print summary of locales available for quick check
    locales = set(v.get('locale') for v in voices if v.get('locale'))
    locales_sorted = sorted(locales)
    print('\nTotal locales:', len(locales_sorted))
    for loc in locales_sorted[:200]:
        print(loc)

asyncio.run(main())
