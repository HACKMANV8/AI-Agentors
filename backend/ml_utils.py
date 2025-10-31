import numpy as np
import pandas as pd

def predict_and_recommend(customer_data, model, scaler, feature_columns, banks_df):
    """
    customer_data: dict from frontend (age, income, etc.)
    """
    df = pd.DataFrame([customer_data])
    scaled = scaler.transform(df[feature_columns])
    risk = model.predict_proba(scaled)[0][1]

    # Compute EMI (simplified)
    
    amount = customer_data["loan_amnt"]
    rate = customer_data["int_rate"] / 100 / 12
    term = 12
    emi = (amount * rate * (1 + rate)*term) / ((1 + rate)*term - 1)
    # Recommend banks
    loan_tenure = "1 year tenure"
    banks = banks_df[banks_df[loan_tenure].notna()].copy()
    banks["suitability_score"] = 1 - abs(banks[loan_tenure] - customer_data["int_rate"]) / banks[loan_tenure].max()
    top_banks = banks.sort_values("suitability_score", ascending=False).head(5)

    return {
        "risk_score": round(risk * 100, 2),
        "monthly_emi": round(emi, 2),
        "banks": top_banks[["Bank Name", loan_tenure, "Highest Slab"]].to_dict(orient="records"),
    }
