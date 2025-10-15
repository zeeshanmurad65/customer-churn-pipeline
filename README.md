# Customer Churn Prediction Project

This project uses a dataset from Kaggle to predict whether a customer will churn (leave the service) based on their account information and services.

## Dataset
The dataset is `WA_Fn-UseC_-Telco-Customer-Churn.csv` from a Kaggle dataset. It contains customer information such as tenure, contract type, monthly charges, and more.

## Analysis & Modeling
- **Data Cleaning:** Handled missing values in the `TotalCharges` column.
- **Exploratory Data Analysis (EDA):** Visualizations show that churn is highly correlated with contract type (Month-to-Month), tenure, and payment method (Electronic check).
- **Modeling:** Several classification models were tested. The AdaBoost and Logistic Regression models performed well after handling the class imbalance with SMOTE.

## Libraries Used
- pandas
- numpy
- matplotlib
- seaborn
- scikit-learn
- xgboost
- imblearn