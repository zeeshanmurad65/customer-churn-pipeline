# Customer Churn Prediction Pipeline

An end-to-end, full-stack machine learning pipeline that predicts customer churn risk. This application integrates a Scikit-Learn predictive model with a FastAPI backend, a MySQL database for historical tracking, and an interactive Streamlit frontend for business users.

## 🏗️ Architecture

* **Frontend (UI):** Streamlit & Plotly (Interactive data collection and visualization)
* **Backend (API):** FastAPI & Uvicorn (RESTful API architecture)
* **Machine Learning:** Scikit-Learn (Logistic Regression Pipeline with native encoders)
* **Database:** MySQL & SQLAlchemy (ORM-based relational data storage)

## 📂 Project Structure

```text customer-churn-pipeline/ ├── Data/ │ └── model/ │ └── Pipeline_lr_model.pkl # Serialized Scikit-Learn model pipeline...

## 🚀 Local Installation & Setup

### 1. Clone the Repository
\`\`\`bash
git clone https://github.com/zeeshanmurad65/customer-churn-pipeline.git
cd customer-churn-pipeline
\`\`\`

### 2. Environment Setup
Create and activate a virtual environment:
\`\`\`bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
\`\`\`

Install the required dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`
*(Note: Ensure your requirements.txt includes fastapi, uvicorn, scikit-learn, pandas, sqlalchemy, pymysql, streamlit, and plotly).*

### 3. Database Configuration
This application requires a running MySQL server. 
1. Create a database named `churn_db` in your MySQL instance.
2. Update the `SQLALCHEMY_DATABASE_URL` in `database.py` with your local credentials.
   *Format:* `mysql+pymysql://username:password@localhost:3306/churn_db`

### 4. Booting the Application

**Terminal 1: Start the Backend API**
\`\`\`bash
uvicorn main:app --reload
\`\`\`
*FastAPI will automatically generate the required database tables on startup. The API will be available at `http://127.0.0.1:8000`.*

**Terminal 2: Start the Frontend UI**
\`\`\`bash
streamlit run frontend.py
\`\`\`
*The Streamlit dashboard will open in your default browser at `http://localhost:8501`.*

## ⚙️ Features
* **Real-time Inference:** Users can input customer demographics and account details to receive an instant churn probability score.
* **Automated Data Processing:** Raw string inputs are automatically encoded via the integrated Scikit-Learn pipeline.
* **Visual Dashboards:** Plotly gauge charts visually assess the severity of flight risk.
* **Historical Tracking:** Every prediction is committed to the MySQL database and can be queried dynamically through the Streamlit history tab.

## 🗺️ Deployment Roadmap
* [ ] Containerize services via Docker (Backend, Frontend, Database).
* [ ] Orchestrate containers using Docker Compose.
* [ ] Deploy to AWS EC2 / RDS instances for production access.