# Show first rows
import pandas as pd

# Load dataset
df = pd.read_csv("data/raw/PhishingData.csv")

print("First 5 rows:")
print(df.head())

print("\nDataset Info:")
print(df.info())

# Clean data
df = df.dropna()
df = df.drop_duplicates()

# Rename target column
df = df.rename(columns={"Result": "label"})

# Check distribution
print("\nLabel Distribution:")
print(df['label'].value_counts())

# Save cleaned dataset
df.to_csv("data/processed/cleaned_data.csv", index=False)

print("\n✅ Data cleaned successfully!")