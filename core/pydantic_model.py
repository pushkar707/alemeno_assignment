from pydantic import BaseModel

class CustomerCreate(BaseModel):
    pass

class LoanCreate(BaseModel):
    pass

class CheckEligibility(BaseModel):
    customer_id: int
    loan_amount: float
    interest_rate: float
    tenure: int