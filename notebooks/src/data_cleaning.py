import pandas as pd

# Load dataset
df = pd.read_csv("data/raw/phishing_dataset.csv")

# Show first rows
print("First 5 rows:")
print(df.head())

# Basic info
print("\nDataset Info:")
print(df.info())

# Remove missing values
df = df.dropna()

# Remove duplicates
df = df.drop_duplicates()

# Rename columns (if needed)
df.columns = ['url', 'label']

# Check distribution
print("\nLabel Distribution:")
print(df['label'].value_counts())

# Add feature (optional)
df['url_length'] = df['url'].apply(len)

# Save cleaned dataset
df.to_csv("data/processed/cleaned_data.csv", index=False)

print("\n✅ Data cleaned and saved successfully!")