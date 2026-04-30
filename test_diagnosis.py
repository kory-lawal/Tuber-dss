from diagnosis import diagnose
import pandas as pd

# Test English
result = diagnose('yellow leaves mosaic pattern')
print('English test:', result)

# Test Yoruba (if available in CSV)
try:
    df = pd.read_csv('data/diseases.csv', encoding='utf-8')
    print('CSV columns:', df.columns.tolist())
    print('Sample data:')
    print(df.head())
except Exception as e:
    print('CSV error:', e)

# Test with different symptoms
tests = [
    'yellow leaves',
    'black spots',
    'wilting plants',
    'stunted growth'
]

for test in tests:
    result = diagnose(test)
    print(f'Test "{test}": {result["disease"]}')