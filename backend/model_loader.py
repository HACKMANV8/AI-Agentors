import pickle
import pandas as pd

def load_model_and_data():
    with open("loan_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open("feature_columns.pkl", "rb") as f:
        features = pickle.load(f)
        
#Read csv file
    banks_df = pd.read_csv("banks_data.csv")
    return model, scaler, features, banks_df
