from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
import joblib
import os

app = FastAPI(title="Smart Customer Churn Platform")

# Allow frontend calls (safe for production here)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------
# Load Model
# --------------------------------------------
model, feature_columns = joblib.load("saved_model.pkl")

# --------------------------------------------
# Load Dataset
# --------------------------------------------
df = pd.read_csv("Churn_Modelling.csv")
df_original = df.copy()

columns_to_drop = ["dirRowNumber", "CustomerId", "Surname"]
df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

df = pd.get_dummies(df, columns=["Geography", "Gender"], drop_first=True)

for col in feature_columns:
    if col not in df.columns:
        df[col] = 0

df = df[feature_columns]

df_original["churn_probability"] = model.predict_proba(df)[:, 1]

# --------------------------------------------
# API ENDPOINTS
# --------------------------------------------

@app.get("/risk-summary")
def get_risk_summary():
    high = len(df_original[df_original["churn_probability"] > 0.7])
    medium = len(
        df_original[
            (df_original["churn_probability"] > 0.4)
            & (df_original["churn_probability"] <= 0.7)
        ]
    )
    low = len(df_original[df_original["churn_probability"] <= 0.4])

    return {
        "total": len(df_original),
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low,
    }

@app.get("/high-risk")
def get_high_risk():
    high_risk_df = df_original[df_original["churn_probability"] > 0.7]
    high_risk_df = high_risk_df.sort_values(
        by="churn_probability", ascending=False
    )
    return high_risk_df.head(20).to_dict(orient="records")

# --------------------------------------------
# Serve Frontend
# --------------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_home():
    return FileResponse("static/index.html")

# --------------------------------------------
# Render requires this
# --------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)