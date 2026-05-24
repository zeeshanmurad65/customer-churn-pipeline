import streamlit as st
import os
import requests
import pandas as pd

# Fetch from environment, fallback to the Docker service name 'backend'
API_URL = os.getenv("API_URL", "http://churn_backend:8000")
st.set_page_config(page_title="Churn Predictor", layout="wide")
st.title("Customer Churn Prediction Portal")

# --- ADMIN SIDEBAR ---
with st.sidebar:
    st.header("Admin Dashboard")
    if st.button("Fetch Intervention Logs"):
        try:
            with st.spinner("Querying database..."):
                log_response = requests.get(f"{API_URL}/logs")
                
            if log_response.status_code == 200:
                logs_data = log_response.json()
                if len(logs_data) > 0:
                    logs_df = pd.DataFrame(logs_data)
                    if "id" in logs_df.columns:
                        logs_df = logs_df.drop(columns=["id"])
                    st.success(f"Found {len(logs_data)} records.")
                    st.dataframe(logs_df, use_container_width=True)
                else:
                    st.info("The InterventionLog table is currently empty.")
            else:
                st.error(f"Failed to fetch logs. API returned: {log_response.status_code}")
                
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to the backend API.")

# --- MAIN INPUT FORM ---
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
        device_protection = st.selectbox("Device Protection", ["Yes", "No"])
    with col7:
        tech_support = st.selectbox("Tech Support", ["Yes", "No"])
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
    with col10:
        monthly_charges = st.number_input("Monthly Charges", min_value=0.0, value=50.0)
        total_charges = st.number_input("Total Charges", min_value=0.0, value=50.0)

    submitted = st.form_submit_button("Predict Churn Risk")

# --- INITIAL API REQUEST ---
if submitted:
    payload = {
        "customer_id": customer_id,
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
        "TotalCharges": total_charges
    }
    
    try:
        with st.spinner("Sending data to the backend..."):
            response = requests.post(f"{API_URL}/predict", json=payload)
        
        if response.status_code == 200:
            st.session_state['current_prediction'] = response.json()
        else:
            st.error(f"🚨 Backend Rejected Request! Status Code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        st.error(f"🚨 Connection Failed: Streamlit cannot reach {API_URL}.")
    except Exception as e:
        st.error(f"🚨 An unexpected error occurred: {e}")

# --- UI RENDERING (STATE AWARE) ---
if 'current_prediction' in st.session_state:
    result = st.session_state['current_prediction']
    
    try:
        prediction = result["churn_prediction"]
        mis_id = result.get("Mis_id", "N/A")
        probability = result.get("churn_probability", 0.0)

        st.markdown("---")
        st.subheader(f"Prediction Results | Record: {mis_id}")
        
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            if prediction == 1:
                st.error("🚨 HIGH FLIGHT RISK: Intervention required.")
            else:
                st.success("✅ SAFE: Customer is expected to stay.")
                
        with res_col2:
            st.metric(label="Calculated Churn Probability", value=f"{probability * 100:.1f}%")

        factors = result.get("top_risk_factors", [])

        if len(factors) > 0:
            st.subheader("Primary Retention Drivers & Actions")
            for idx, driver in enumerate(factors):
                with st.container():
                    weight = driver.get('relative_weight_percentage', 0)
                    feature = driver.get('feature', 'Unknown Feature')
                    action = driver.get('recommended_action', 'No action recommended.')
                    
                    st.markdown(f"### #{idx + 1}. {feature} ({weight}%)")
                    st.info(f"**Recommended Action:** {action}")
                    
                    # Lock Logic
                    action_lock_key = f"logged_{mis_id}_{idx}"
                    
                    if st.session_state.get(action_lock_key):
                        st.success(f"✅ Action successfully recorded for {mis_id}. Locked.")
                    else:
                        if st.button(f"Log Action: {feature}", key=f"btn_{mis_id}_{idx}"):
                            log_payload = {
                                "mis_id": mis_id,
                                "action_taken": action
                            }
                            try:
                                log_res = requests.post(f"{API_URL}/log_intervention", json=log_payload)
                                if log_res.status_code == 200:
                                    st.session_state[action_lock_key] = True
                                    st.rerun() 
                                else:
                                    st.error(f"🚨 Failed to log intervention. Status: {log_res.status_code}")
                            except requests.exceptions.ConnectionError:
                                st.error("🚨 API Connection Failed.")
        else:
            st.warning("No standard drivers isolated. Review account manually.")

    except KeyError as e:
        st.error(f"🚨 Backend Failure: Missing key {e} in the JSON response.")