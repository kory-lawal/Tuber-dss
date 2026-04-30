from pathlib import Path
p = Path('audio')
count = 0
for f in p.glob('*.mp3'):
    if not f.name.startswith('yarngpt_'):
        f.unlink()
        count += 1
print('Removed', count, 'non-yarngpt mp3 files')
