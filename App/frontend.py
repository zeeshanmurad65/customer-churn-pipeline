import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="Churn Predictor", layout="wide")
st.title("Customer Churn Prediction Portal")

# Use forms to prevent the app from reloading on every single click
with st.form("customer_form"):
    st.subheader("Demographics")
    col1, col2, col3, col4 = st.columns(4)
    customer_id = st.text_input("Customer ID", value="0001-XXXXX")
    with col1: gender = st.selectbox("Gender", ["Male", "Female"])
    with col2: senior_citizen = st.selectbox("Senior Citizen", ["Yes", "No"])
    with col3: partner = st.selectbox("Partner", ["Yes", "No"])
    with col4: dependents = st.selectbox("Dependents", ["Yes", "No"])

    st.subheader("Services Subscribed")
    col5, col6, col7 = st.columns(3)
    with col5:
        phone_service = st.selectbox("Phone Service", ["Yes", "No"])
        multiple_lines = st.selectbox("Multiple Lines", ["Yes", "No"])
        internet_service = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
    with col6:
        online_security = st.selectbox("Online Security", ["Yes", "No"])
        online_backup = st.selectbox("Online Backup", ["Yes", "No"])
        device_protection = st.selectbox("Device Protection", ["Yes", "No",])
    with col7:
        tech_support = st.selectbox("Tech Support", ["Yes", "No",])
        streaming_tv = st.selectbox("Streaming TV", ["Yes", "No"])
        streaming_movies = st.selectbox("Streaming Movies", ["Yes", "No"])

    st.subheader("Account & Billing")
    col8, col9, col10 = st.columns(3)
    with col8:
        contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
        paperless_billing = st.selectbox("Paperless Billing", ["Yes", "No"])
        payment_method = st.selectbox("Payment Method", [
            "Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"
        ])
    with col9:
        tenure = st.number_input("Tenure (Months)", min_value=0, value=1)
        # Note: If avg_historical_charge is not calculable from raw inputs, you must ask for it here.
        avg_historical_charge = st.number_input("Avg Historical Charge", min_value=0.0, value=50.0)
    with col10:
        monthly_charges = st.number_input("Monthly Charges", min_value=0.0, value=50.0)
        total_charges = st.number_input("Total Charges", min_value=0.0, value=50.0)

    submitted = st.form_submit_button("Predict Churn Risk")

if submitted:
    # This payload must match your Pydantic schema exactly.
    # If your Pydantic schema expects engineered features here, your backend design is flawed.
    payload = {
        "gender": gender,
        "SeniorCitizen": senior_citizen,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": tenure,
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless_billing,
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges,
        "avg_historical_charge": avg_historical_charge
    }

if submitted:
    # Your payload mapping here...
    
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            
            prediction = result.get("churn_prediction")
            probability = result.get("churn_probability", 0.0)
            
            st.markdown("---")
            st.subheader("Prediction Results")
            
            res_col1, res_col2 = st.columns(2)
            
            with res_col1:
                if prediction == 1:
                    st.error("🚨 HIGH FLIGHT RISK: Customer is likely to churn.")
                else:
                    st.success("✅ SAFE: Customer is expected to stay.")
                    
            with res_col2:
                st.metric(label="Churn Probability", value=f"{probability * 100:.2f}%")
                
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
            
    # This is the mandatory exception handling for API requests
    except requests.exceptions.ConnectionError:
        st.error("🚨 Connection Failed: Cannot reach the FastAPI backend. Ensure your Uvicorn server is running in a separate terminal.")
    except Exception as e:
        st.error(f"🚨 An unexpected error occurred: {e}")