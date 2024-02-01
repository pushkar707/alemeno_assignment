from pydantic import BaseModel

class CustomerCreate(BaseModel):
    first_name:str
    last_name:str
    age: int
    monthly_income: int
    phone_number: int

class CheckEligibility(BaseModel):
    customer_id: int
    loan_amount: float
    interest_rate: float
    tenure: int