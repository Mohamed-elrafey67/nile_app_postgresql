import pandas as pd
path = r'C:\Users\Eng.Mohamed El-Rafey\Downloads\جدول_مقابل_الانتفاع_149_2026.xlsx'
df = pd.read_excel(path, sheet_name='القرار 148 - ترخيص (مختصر)', header=None)

print("Sheet shape:", df.shape)
print()
for r in range(df.shape[0]):
    vals = [str(df.iloc[r,c])[:40] for c in range(df.shape[1])]
    print(f"Row {r}: {vals}")
