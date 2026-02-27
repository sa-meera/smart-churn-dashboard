from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
import joblib
import os

app = FastAPI()

# Load model safely
model = None
try:
    if os.path.exists("saved_model.pkl"):
        model = joblib.load("saved_model.pkl")
        print("Model loaded successfully")
    else:
        print("Model file not found")
except Exception as e:
    print("Model loading error:", e)

# Load dataset safely
df = None
try:
    if os.path.exists("Churn_Modelling.csv"):
        df = pd.read_csv("Churn_Modelling.csv")
        print("CSV loaded successfully")
    else:
        print("CSV file not found")
except Exception as e:
    print("CSV loading error:", e)

# Serve static frontend
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
def read_index():
    return FileResponse("index.html")

@app.get("/dashboard-data")
def dashboard_data():
    if model is None or df is None:
        return {"error": "Model or data not loaded"}

    try:
        data = df.copy()

        # Drop unnecessary columns safely
        cols_to_drop = ["CustomerId", "Surname", "dirRowNumber"]
        for col in cols_to_drop:
            if col in data.columns:
                data = data.drop(col, axis=1)

        X = data.drop("Exited", axis=1)

        predictions = model.predict_proba(X)[:, 1]
        high_risk = sum(predictions > 0.6)
        low_risk = len(predictions) - high_risk

        return {
            "total_customers": len(predictions),
            "high_risk": int(high_risk),
            "low_risk": int(low_risk)
        }

    except Exception as e:
        return {"error": str(e)}