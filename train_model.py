import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier

# Load dataset
df = pd.read_csv("Churn_Modelling.csv")

# Drop unnecessary columns safely
columns_to_drop = ["dirRowNumber", "CustomerId", "Surname"]
df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

# Encode categorical variables
df = pd.get_dummies(df, columns=["Geography", "Gender"], drop_first=True)

# Rename target column
df = df.rename(columns={"Exited": "churn"})

# Features and target
X = df.drop("churn", axis=1)
y = df["churn"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = GradientBoostingClassifier()
model.fit(X_train, y_train)

# Save model and column structure
joblib.dump((model, X.columns.tolist()), "saved_model.pkl")

print("✅ Model trained successfully on your dataset and saved.")