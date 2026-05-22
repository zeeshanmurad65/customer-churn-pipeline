from fastapi import FastAPI, HTTPException ,Depends
from database import SessionLocal, engine, Base, CustomerRecord
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Optional ,Literal
from contextlib import asynccontextmanager
import joblib
from pathlib import Path
from sqlalchemy.orm import Session
# Ensure you have imported SessionLocal from your database.py file
from database import SessionLocal
# Ensure get_db and CustomerRecord are imported at the top of main.py
import pandas as pd
Base.metadata.create_all(bind=engine)

app=FastAPI()
@app.get("/")
def root():
    return {"Hello":"Welcome to Check Customer will Leave or Not"}
ml_models = {}
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Get the absolute path to the directory where api.py lives (the App folder)
    current_dir = Path(__file__).resolve().parent
    
    # 2. Go up one level to the root, then into the 'model' folder
    # Note: Ensure the file in your model folder actually has the .pkl extension!
    model_path = current_dir.parent / "model" / "Pipeline_lr_model.pkl"
    # 3. Load the model using the dynamic path
    ml_models['Lr_model'] = joblib.load(model_path)
    yield
    ml_models.clear()
app = FastAPI(lifespan=lifespan)    
class Customers(BaseModel):
    # Notice the colons (:). This is the ONLY valid way to use Annotated.
    Customer_id: Optional[str] = None
    gender: Annotated[str, Field(default="Male", description="Gender")]
    SeniorCitizen: Annotated[str, Field(max_length=3,min_length=2, default="Yes", description="Senior Citizen")]
    Partner: Annotated[Literal["Yes", "No"], Field(default="Yes", description="Partner")]
    Dependents: Annotated[str, Field(min_length=2, max_length=3, default="Yes", description="Dependents")]
    tenure: Annotated[int, Field(ge=0, default=1, description="Tenure in months")]
    PhoneService: Annotated[str, Field(min_length=2, max_length=3, default="Yes", description="PhoneService")]
    InternetService: Annotated[Literal["DSL", "Fiber optic", "No"], Field(default="DSL")]
    OnlineSecurity: Annotated[str, Field(min_length=2, max_length=3, default="Yes", description="OnlineSecurity")]
    OnlineBackup: Annotated[str, Field(min_length=2, max_length=3, default="Yes", description="OnlineBackup")]
    DeviceProtection: Annotated[str, Field(min_length=2, max_length=3, default="Yes", description="DeviceProtection")]
    TechSupport: Annotated[str, Field(min_length=2, max_length=3, default="Yes", description="Tech Support")]
    StreamingTV: Annotated[str, Field(min_length=2, max_length=3, default="Yes", description="StreamingTV")]
    Contract: Annotated[str, Field(default="One year", description="Contract")]
    PaperlessBilling: Annotated[str, Field(min_length=2, max_length=3, default="Yes", description="Paperless Billing")]
    PaymentMethod: Annotated[str, Field(default="Electronic check", description="Payment Method")]
    MonthlyCharges: Annotated[float, Field(ge=0, default=30.0, description="Monthly Charges")]
    TotalCharges: Annotated[float, Field(ge=0, default=30.0, description="Total Charges")]
    MultipleLines:Annotated[str, Field(min_length=2, default="Yes", description="Multiple Lines")]
    StreamingMovies:Annotated[str, Field(min_length=2, max_length=3, default="Yes", description="Streaming Movies")]
    

    @computed_field
    @property
    def tenure_safe(self) -> int:
        return 1 if self.tenure == 0 else self.tenure

    @computed_field
    @property
    def is_month_to_month(self) -> int:
        return 1 if self.Contract == "Month-to-month" else 0

    @computed_field
    @property
    def cost_to_loyalty_ratio(self) -> float:
        return self.MonthlyCharges / self.tenure_safe

    @computed_field
    @property
    def m2m_flight_risk(self) -> float:
        return self.is_month_to_month * self.MonthlyCharges
        
    @computed_field
    @property
    def avg_historical_charge(self) -> float:
        return self.TotalCharges / self.tenure_safe
        
    @computed_field
    @property
    def charge_spike(self) -> float:
        return self.MonthlyCharges - self.avg_historical_charge

# main.py



# THIS is the function your endpoint is asking for.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/predict", response_model=dict)
def predict_customers(customer: Customers, db: Session = Depends(get_db)): # <-- 1. MISSING DB SESSION INJECTED HERE
    if 'Lr_model' not in ml_models:
        raise HTTPException(status_code=404, detail="Model has not been found")
        
    input_df = pd.DataFrame([{
        "Customer_id": customer.Customer_id,
        "gender": customer.gender,
        "SeniorCitizen": customer.SeniorCitizen,
        "Partner": customer.Partner,
        "Dependents": customer.Dependents,
        "tenure": customer.tenure,
        "PhoneService": customer.PhoneService,
        "InternetService": customer.InternetService,
        "OnlineSecurity": customer.OnlineSecurity,
        "OnlineBackup": customer.OnlineBackup,
        "DeviceProtection": customer.DeviceProtection,
        "TechSupport": customer.TechSupport,
        "StreamingTV": customer.StreamingTV,
        "Contract": customer.Contract,
        "PaperlessBilling": customer.PaperlessBilling,
        "PaymentMethod": customer.PaymentMethod,
        "MonthlyCharges": customer.MonthlyCharges,
        "TotalCharges": customer.TotalCharges,
        "cost_to_loyalty_ratio": customer.cost_to_loyalty_ratio,
        "m2m_flight_risk": customer.m2m_flight_risk,
        "charge_spike": customer.charge_spike ,
        "MultipleLines":customer.MultipleLines ,
        "StreamingMovies":customer.StreamingMovies ,
        "avg_historical_charge":customer.avg_historical_charge ,
        "tenure_safe":customer.tenure_safe,
        "is_month_to_month":customer.is_month_to_month
    }])
    
    model = ml_models['Lr_model']
    prediction = int(model.predict(input_df)[0])
    probability = float(model.predict_proba(input_df)[0, 1])

    # 2. THE MISSING DATABASE INSERTION BLOCK
    # Note: Every single variable you pass here MUST exist in your database.py CustomerRecord class.
    # If you added new features like 'cost_to_loyalty_ratio' to your ML model, 
    # they must also be defined as Columns in your MySQL table, or this will crash.
    db_record = CustomerRecord(
        Customer_id=customer.Customer_id,
        gender=customer.gender,
        SeniorCitizen=customer.SeniorCitizen,
        Partner=customer.Partner,
        Dependents=customer.Dependents,
        tenure=customer.tenure,
        PhoneService=customer.PhoneService,
        MultipleLines=customer.MultipleLines,
        InternetService=customer.InternetService,
        OnlineSecurity=customer.OnlineSecurity,
        OnlineBackup=customer.OnlineBackup,
        DeviceProtection=customer.DeviceProtection,
        TechSupport=customer.TechSupport,
        StreamingTV=customer.StreamingTV,
        StreamingMovies=customer.StreamingMovies,
        Contract=customer.Contract,
        PaperlessBilling=customer.PaperlessBilling,
        PaymentMethod=customer.PaymentMethod,
        MonthlyCharges=customer.MonthlyCharges,
        TotalCharges=customer.TotalCharges,
        
        # Attach the model's output
        churn_prediction=prediction,
        churn_probability=probability
    )
    
    try:
        db.add(db_record)
        db.commit()          # <-- THIS IS WHAT ACTUALLY SAVES THE DATA
        db.refresh(db_record) 
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database insertion failed: {e}")

    # 3. RETURN AFTER COMMIT
    return {
        "Customer_id": customer.Customer_id,
        "churn_prediction": prediction,
        "churn_probability": round(probability, 4)
    }