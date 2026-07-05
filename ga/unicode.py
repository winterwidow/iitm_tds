import pandas as pd

TARGETS = {"‘", "–", "Ž"}

total = 0

# CP-1252 CSV
df1 = pd.read_csv("data1.csv", encoding="cp1252")
total += df1[df1["symbol"].isin(TARGETS)]["value"].sum()

# UTF-8 CSV
df2 = pd.read_csv("data2.csv", encoding="utf-8")
total += df2[df2["symbol"].isin(TARGETS)]["value"].sum()

# UTF-16 TSV
df3 = pd.read_csv(
    "data3.txt",
    encoding="utf-16",
    sep="\t"
)
total += df3[df3["symbol"].isin(TARGETS)]["value"].sum()

print(total)