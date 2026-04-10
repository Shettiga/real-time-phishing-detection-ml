import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load cleaned dataset
df = pd.read_csv("data/processed/cleaned_data.csv")

print("Dataset Loaded Successfully")

# Separate features and target
X = df.drop("label", axis=1)
y = df["label"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("Data split done")

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

print("Model training completed")

# Predictions
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.2f}%")

# Save model
joblib.dump(model, "phishing_model.pkl")

print("✅ Model saved as phishing_model.pkl")