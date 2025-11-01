import requests
import json

# Test the API

test_data = {
    "name": "John Doe",
    "age": 35,
    "emp_length": 5,
    "employment_status": "employed",
    "annual_inc": 800000,
    "existing_debt": 100000,
    "credit_score": 750,
    "loan_amnt": 500000,
    "loan_type": "Personal",
    "loan_tenure": "1 year tenure"
}

try:
    response = requests.post("http://127.0.0.1:8081/predict", json=test_data)
    print("Status Code:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
except Exception as e:
    print("Error:", e)
    
