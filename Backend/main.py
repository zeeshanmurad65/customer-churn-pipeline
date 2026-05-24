from fastapi import FastAPI, HTTPException ,Depends
from database import SessionLocal, engine, Base, CustomerRecord, InterventionLog
from pydantic import BaseModel, Field, computed_field ,field_validator
from typing import Annotated, Optional ,Literal
from contextlib import asynccontextmanager
import joblib
from pathlib import Path
from sqlalchemy.orm import Session
from database import SessionLocal
import pandas as pd
from sqlalchemy import desc
Base.metadata.create_all(bind=engine)

ml_models = {}
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Get the absolute path to the directory where api.py lives (the App folder)
    # 1. Dynamically get the directory where main.py actually lives
    current_dir = Path(__file__).resolve().parent

    # 2. Point to the sibling 'model' folder directly (NO .parent)
    model_path = current_dir / "model" / "Pipeline_lr_model.pkl"
    # 3. Load the model using the dynamic path
    ml_models['Lr_model'] = joblib.load(model_path)
    yield
    ml_models.clear()
app = FastAPI(lifespan=lifespan)
@app.get("/")
def root():
    return {"Hello":"Welcome to Check Customer will Leave or Not"}
class Customers(BaseModel):
    # Notice the colons (:). This is the ONLY valid way to use Annotated
    Customer_id: Optional[str] = None
    # Strict binaries
    gender: Annotated[Literal["Male", "Female"], Field(default="Male", description="Gender")]
    SeniorCitizen: Annotated[Literal["Yes", "No"], Field(default="Yes", description="Senior Citizen")]
    Partner: Annotated[Literal["Yes", "No"], Field(default="Yes", description="Partner")]
    Dependents: Annotated[Literal["Yes", "No"], Field(default="Yes", description="Dependents")]
    PhoneService: Annotated[Literal["Yes", "No"], Field(default="Yes", description="PhoneService")]
    PaperlessBilling: Annotated[Literal["Yes", "No"], Field(default="Yes", description="Paperless Billing")]
    
    # Services with potentially 3 categories depending on your exact dataset 
    # (If your dataset includes "No internet service", add it to these Literals)
    OnlineSecurity: Annotated[Literal["Yes", "No"], Field(default="Yes", description="OnlineSecurity")]
    OnlineBackup: Annotated[Literal["Yes", "No"], Field(default="Yes", description="OnlineBackup")]
    DeviceProtection: Annotated[Literal["Yes", "No"], Field(default="Yes", description="DeviceProtection")]
    TechSupport: Annotated[Literal["Yes", "No"], Field(default="Yes", description="Tech Support")]
    StreamingTV: Annotated[Literal["Yes", "No"], Field(default="Yes", description="StreamingTV")]
    StreamingMovies: Annotated[Literal["Yes", "No"], Field(default="Yes", description="Streaming Movies")]
    MultipleLines: Annotated[Literal["Yes", "No"], Field(default="Yes", description="Multiple Lines")]
    
    # Multi-class categorical fields
    InternetService: Annotated[Literal["DSL", "Fiber optic", "No"], Field(default="DSL")]
    Contract: Annotated[Literal["Month-to-month", "One year", "Two year"], Field(default="One year", description="Contract")]
    PaymentMethod: Annotated[Literal["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"], Field(default="Electronic check", description="Payment Method")]
    
    # Numerical fields
    tenure: Annotated[int, Field(ge=0, le=120, default=1, description="Tenure in months")]
    MonthlyCharges: Annotated[float, Field(ge=0, default=30.0, description="Monthly Charges")]
    TotalCharges: Annotated[float, Field(ge=0, default=30.0, description="Total Charges")]
    
    @field_validator('TotalCharges')
    @classmethod
    def check_total_charges_logic(cls, total, info):
        monthly = info.data.get('MonthlyCharges')
        tenure = info.data.get('tenure')
        
        if monthly and tenure and tenure > 0 and total < monthly:
            raise ValueError("TotalCharges cannot be less than a single month's charge for an active user.")
        return total

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

class InterventionRequest(BaseModel):
    mis_id: str
    action_taken: str
# THIS is the function your endpoint is asking for.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.post("/predict", response_model=dict)
def predict_customers(customer: Customers, db: Session = Depends(get_db)):
    if 'Lr_model' not in ml_models:
        raise HTTPException(status_code=404, detail="Model has not been found")
        
    # 1. Construct the DataFrame ONCE
    inference_df = pd.DataFrame([{
        "gender": customer.gender,
        "SeniorCitizen": customer.SeniorCitizen,
        "Partner": customer.Partner,
        "Dependents": customer.Dependents,
        "tenure": customer.tenure,
        "PhoneService": customer.PhoneService,
        "MultipleLines": customer.MultipleLines,
        "InternetService": customer.InternetService,
        "OnlineSecurity": customer.OnlineSecurity,
        "OnlineBackup": customer.OnlineBackup,
        "DeviceProtection": customer.DeviceProtection,
        "TechSupport": customer.TechSupport,
        "StreamingTV": customer.StreamingTV,
        "StreamingMovies": customer.StreamingMovies,
        "Contract": customer.Contract,
        "PaperlessBilling": customer.PaperlessBilling,
        "PaymentMethod": customer.PaymentMethod,
        "MonthlyCharges": customer.MonthlyCharges,
        "TotalCharges": customer.TotalCharges,
        # Computed engineered features
        "tenure_safe": customer.tenure_safe,
        "is_month_to_month": customer.is_month_to_month,
        "cost_to_loyalty_ratio": customer.cost_to_loyalty_ratio,
        "m2m_flight_risk": customer.m2m_flight_risk,
        "avg_historical_charge": customer.avg_historical_charge,
        "charge_spike": customer.charge_spike
    }])
    
    # 2. Predict Classification AND Probability
    model = ml_models['Lr_model']
    prediction = int(model.predict(inference_df)[0])
    
    # Extract the probability of class 1 (Churn)
    probability = float(model.predict_proba(inference_df)[0][1])
    
    # Determine the business logic label
    risk_label = "🚨 HIGH FLIGHT RISK" if prediction == 1 else "✅ STABLE"

    # 3. Handle the MIS Sequence
    last_record = db.query(CustomerRecord).order_by(desc(CustomerRecord.Mis_id)).first()
    
    if last_record and last_record.Mis_id and last_record.Mis_id.startswith("MIS"):
        try:
            last_number = int(last_record.Mis_id.replace("MIS", ""))
            new_mis_id = f"MIS{last_number + 1:03d}"
        except ValueError:
            new_mis_id = "MIS001"
    else:
        new_mis_id = "MIS001"

    # 4. Save to Database
    db_record = CustomerRecord(
        Mis_id=new_mis_id,
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
        churn_prediction=prediction
    )
    
    try:
        db.add(db_record)
        db.commit()          
        db.refresh(db_record) 
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database insertion failed: {e}")
   
    # 5. Return the finalized JSON Payload (Variables now match)
    top_risk_factors = []
    
    # Only calculate drivers if they are actually a churn risk
    if prediction == 1:
        total_risk_weight = 0
        raw_factors = []
        
        # Rule 1: Contract Type
        if customer.is_month_to_month == 1:
            raw_factors.append({
                "feature": "Unstable Contract (Month-to-Month)",
                "raw_weight": 3.5,
                "recommended_action": "Offer a 1-year contract with a 10% discount."
            })
            
        # Rule 2: Lack of Support
        if customer.TechSupport == "No":
            raw_factors.append({
                "feature": "Lacks Technical Support",
                "raw_weight": 2.0,
                "recommended_action": "Provide a 1-month free trial of Premium Support."
            })
            
        # Rule 3: High Cost vs Loyalty
        if customer.MonthlyCharges > 70.0 and customer.tenure < 6:
            raw_factors.append({
                "feature": "High Cost / Low Tenure (Bill Shock)",
                "raw_weight": 2.5,
                "recommended_action": "Audit data usage; suggest a cost-optimized tier."
            })
            
        # The Fallback Catch-All
        if len(raw_factors) == 0:
            raw_factors.append({
                "feature": "Complex Multivariate Risk (Non-Standard)",
                "raw_weight": 1.0,
                "recommended_action": "Conduct a manual account review. Trigger is outside standard heuristics."
            })


            
            
        # Normalize the weights so they equal 100% for the frontend
        total_risk_weight = sum(factor["raw_weight"] for factor in raw_factors)
        
        for factor in raw_factors:
            normalized_pct = round((factor["raw_weight"] / total_risk_weight) * 100, 1) if total_risk_weight > 0 else 0
            top_risk_factors.append({
                "feature": factor["feature"],
                "relative_weight_percentage": normalized_pct,
                "recommended_action": factor["recommended_action"]
            })
            
        # Sort by highest impact
        top_risk_factors = sorted(top_risk_factors, key=lambda x: x["relative_weight_percentage"], reverse=True)

    # 6. RETURN THE FINALIZED CONTRACT
    return {
        "Mis_id": new_mis_id,
        "churn_prediction": prediction,
        "churn_probability": round(probability, 3),
        "risk_label": risk_label,
        "top_risk_factors": top_risk_factors # <-- THIS IS WHAT YOUR UI IS BEGGING FOR
    }
@app.post("/log_intervention")
def log_intervention(request: InterventionRequest, db: Session = Depends(get_db)):
    try:
        # WRONG: new_log = InterventionRequest(...)
        # CORRECT: Use the database model
        new_log = InterventionLog(
            mis_id=request.mis_id,
            action_taken=request.action_taken
        )
        db.add(new_log)
        db.commit()
        return {"status": "success", "message": f"Intervention logged for {request.mis_id}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database insertion failed: {e}")

@app.get("/logs")
def get_intervention_logs(db: Session = Depends(get_db)):
    try:
        # 1. Query the SQLALCHEMY MODEL, not the Pydantic schema
        logs = db.query(InterventionLog).order_by(desc(InterventionLog.timestamp)).limit(50).all()
        
        # 2. Serialize to clean JSON dictionaries
        return [
            {
                "mis_id": log.mis_id,
                "action_taken": log.action_taken,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None
            }
            for log in logs
        ]
    except Exception as e:
        print(f"Backend Query Error: {e}") 
        raise HTTPException(status_code=500, detail=f"Database query failed: {e}")