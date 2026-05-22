# Customer Churn Prediction Pipeline

An end-to-end, full-stack machine learning pipeline that predicts customer churn risk. This application integrates a Scikit-Learn predictive model with a FastAPI backend, a MySQL database for historical tracking, and an interactive Streamlit frontend for business users.

## 🏗️ Architecture

* **Frontend (UI):** Streamlit & Plotly (Interactive data collection and visualization)
* **Backend (API):** FastAPI & Uvicorn (RESTful API architecture)
* **Machine Learning:** Scikit-Learn (Logistic Regression Pipeline with native encoders)
* **Database:** MySQL & SQLAlchemy (ORM-based relational data storage)

## 📂 Project Structure

```text
customer-churn-pipeline/
├── Data/
│   └── model/
│       └── Pipeline_lr_model.pkl   # Serialized Scikit-Learn model pipeline
├── database.py                     # SQLAlchemy ORM and DB connection logic
├── main.py                         # FastAPI application and prediction endpoints
├── frontend.py                     # Streamlit user interface and dashboard
├── requirements.txt                # Python dependencies
├── .gitignore                      # Security and environment exclusions
└── README.md                       # Project documentation