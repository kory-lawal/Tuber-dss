import importlib, sys
mods = ["streamlit","gtts","whisper","streamlit_mic_recorder","googletrans","torch"]
print('Python executable:', sys.executable)
for m in mods:
    try:
        mod = importlib.import_module(m)
        ver = getattr(mod, '__version__', None)
        print(f"{m}: OK", ver)
    except Exception as e:
        print(f"{m}: ERROR -> {e!r}")
