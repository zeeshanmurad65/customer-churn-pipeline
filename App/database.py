# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:246892@localhost:3306/churn_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CustomerRecord(Base):
    __tablename__ = "customer_predictions"

    # Primary Key identifier - exactly as you specified previously
    Mis_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Optional ID from your Pydantic model
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
    churn_prediction = Column(Integer)
    churn_probability = Column(Float)