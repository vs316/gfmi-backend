# Quick check script - check_csv.py
import pandas as pd

df = pd.read_csv(
    "C:\\Users\\VachanShetty\\Downloads\\17198ac2-ff74-5bcd-422b-f465b409db00.csv"
)

print("Columns:", list(df.columns))
print("\nSample row:")
print(df.iloc[0])
print(
    "\nUnique countries:",
    (
        df["country_geo_id"].dropna().unique()
        if "country_geo_id" in df.columns
        else "Column not found"
    ),
)
print(
    "\nSample name:", df["name"].iloc[0] if "name" in df.columns else "Column not found"
)
print(
    "Sample msl_name:",
    df["msl_name"].iloc[0] if "msl_name" in df.columns else "Column not found",
)
