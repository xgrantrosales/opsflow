from pydantic import BaseModel

class CustomerCreate(BaseModel):
    full_name: str
    email: str
    phone_number: str

class CustomerResponse(BaseModel):
    id: int
    full_name: str   
    email: str
    phone_number: str


             

