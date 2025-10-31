from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np
import uvicorn
import os
# ---------- Load model, scaler, and feature columns ----------

def safe_load_pickle(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"❌ Missing required file: {filename}")
    with open(filename, "rb") as f:
        return pickle.load(f)

try:
    model = safe_load_pickle("loan_model.pkl")
    scaler = safe_load_pickle("scaler.pkl")
    feature_columns = safe_load_pickle("feature_columns.pkl")
except Exception as e:
    raise RuntimeError(f"❌ Failed to load model/scaler: {e}")

BANKS_FILE = "Banks-Interest-Rates_india.csv"
if not os.path.exists(BANKS_FILE):
    raise FileNotFoundError(f"❌ Missing banks data file: {BANKS_FILE}")

banks_df = pd.read_csv(BANKS_FILE)

# ---------- Initialize FastAPI ----------
app = FastAPI(
    title="LoanGuard API",
    description="Predict loan default risk and recommend banks based on interest rates.",
    version="1.0.0"
)

# ---------- Data model ----------
class LoanRequest(BaseModel):
    age: int
    emp_length: int
    annual_inc: float
    dti: float
    credit_score: float
    loan_amnt: float
    int_rate: float
    loan_tenure: str = "1 year tenure"

# ---------- Root endpoint ----------
@app.get("/")
def home():
    return {"message": "✅ LoanGuard API is running successfully!"}

# ---------- Predict endpoint ----------
@app.post("/predict")
def predict_loan(data: LoanRequest):
    try:
        customer_profile = {
            "age": data.age,
            "emp_length_clean": data.emp_length,
            "annual_inc": data.annual_inc,
            "dti": data.dti,
            "credit_score": data.credit_score,
            "loan_amnt": data.loan_amnt,
            "int_rate": data.int_rate,
            "loan_to_income": data.loan_amnt / data.annual_inc,
            "income_stability": 0.8 if data.emp_length >= 5 else (0.6 if data.emp_length >= 2 else 0.4),
        }

        customer_df = pd.DataFrame([customer_profile])
        scaled = scaler.transform(customer_df[feature_columns])

        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(scaled)
            default_risk = probs[0][1] if probs.shape[1] > 1 else 0.5
        else:
            default_risk = float(model.predict(scaled)[0])

        tenure_col = data.loan_tenure
        if tenure_col not in banks_df.columns:
            raise HTTPException(status_code=400, detail=f"Invalid loan tenure: {tenure_col}")

        eligible_banks = banks_df[banks_df[tenure_col].notna()].copy()
        if eligible_banks.empty:
            raise HTTPException(status_code=404, detail="No banks found for the selected tenure.")

        min_rate = eligible_banks[tenure_col].min()
        max_rate = eligible_banks[tenure_col].max()

        eligible_banks["int_rate_score"] = 1 - ((eligible_banks[tenure_col] - min_rate) / (max_rate - min_rate)).clip(0, 1)
        risk_factor = 0.85 if default_risk < 0.2 else (0.65 if default_risk < 0.4 else 0.45)
        eligible_banks["risk_score"] = risk_factor
        eligible_banks["lti_score"] = max(0, 1 - customer_profile["loan_to_income"])

        eligible_banks["suitability_score"] = (
            eligible_banks["int_rate_score"] * 0.5 +
            eligible_banks["risk_score"] * 0.3 +
            eligible_banks["lti_score"] * 0.2
        )

        recommendations = (
            eligible_banks.sort_values("suitability_score", ascending=False)
            .head(5)[["Bank Name", tenure_col, "suitability_score"]]
            .rename(columns={tenure_col: "Interest Rate (%)"})
            .to_dict(orient="records")
        )

        return {
            "risk_score (%)": round(default_risk * 100, 2),
            "recommended_banks": recommendations,
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# ---------- Run ----------
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
