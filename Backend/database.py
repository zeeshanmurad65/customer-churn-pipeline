import os
from sqlalchemy import create_engine, Column, Integer, String, Float ,DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
# 1. The Dynamic PostgreSQL Connection String
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://zeeshanmurad65:246892@db:5432/churn_db"
)

# 2. Engine and Session Initialization
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



# 3. The Corrected Table Definition
class CustomerRecord(Base):
    __tablename__ = "customers" # FIXED: Two underscores

    # Accommodates the MIS001 format constraint
    Mis_id = Column(String(20), primary_key=True, index=True)
    Customer_id = Column(String(50), nullable=True)
    
    # Demographics
    gender = Column(String(20))
    SeniorCitizen = Column(String(10))
    Partner = Column(String(10))
    Dependents = Column(String(10))
    
    # Account details
    tenure = Column(Integer)
    Contract = Column(String(50))
    PaperlessBilling = Column(String(10))
    PaymentMethod = Column(String(50))
    MonthlyCharges = Column(Float)
    TotalCharges = Column(Float)
    
    # Services
    PhoneService = Column(String(10))
    MultipleLines = Column(String(20))
    InternetService = Column(String(20))
    OnlineSecurity = Column(String(25))
    OnlineBackup = Column(String(25))
    DeviceProtection = Column(String(25))
    TechSupport = Column(String(25))
    StreamingTV = Column(String(25))
    StreamingMovies = Column(String(25))
    
    # Model Output
    churn_prediction = Column(String(10)) # FIXED: Categorical output


# Assuming 'Base' is already imported and defined in this file

class InterventionLog(Base):
    __tablename__ = "intervention_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    mis_id = Column(String, index=True)
    action_taken = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)