from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from model_loader import load_model_and_data
from ml_utils import predict_and_recommend

app = FastAPI(title="LoanGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model & data once
model, scaler, feature_columns, banks_df = load_model_and_data()

@app.get("/")
def root():
    return {"status": "OK", "message": "LoanGuard API is live"}

@app.post("/api/predict")
def predict(data: dict):
    try:
        result = predict_and_recommend(data, model, scaler, feature_columns, banks_df)
        return result
    except Exception as e:
        return {"error": str(e)}

if _name_ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
