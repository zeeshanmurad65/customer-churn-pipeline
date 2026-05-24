# 🚀 Customer Churn Prediction Pipeline

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-orange)

An end-to-end, full-stack machine learning pipeline designed to predict customer churn risk and drive actionable retention strategies. 

This application goes beyond simply serving a model; it integrates a **Scikit-Learn** predictive engine with a **FastAPI** backend, logs interventions in a **MySQL** database for historical ROI tracking, and provides an interactive, state-aware **Streamlit** frontend for business stakeholders.

---

## 🏗️ System Architecture

* **Frontend (UI):** Streamlit & Plotly (Interactive data collection, risk visualization, and state-locked action logging).
* **Backend (API):** FastAPI & Uvicorn (Robust RESTful API architecture enforcing strict Pydantic data contracts).
* **Machine Learning:** Scikit-Learn (Logistic Regression Pipeline with native encoders and probability scoring).
* **Database:** MySQL & SQLAlchemy (ORM-based relational data storage for tracking retention interventions).

---

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