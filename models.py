from pydantic import BaseModel, Field, field_validator, EmailStr

class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=1)
    email: EmailStr
    phone_number: str = Field(min_length=1)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls,full_name:str) -> str:

        if len(full_name.strip()) == 0:
            raise ValueError("Full name cannot be blank.")

        return full_name.strip()

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls,phone_number:str) -> str:

        valid_phone_number = phone_number.strip()

        if len(valid_phone_number) == 0:
            raise ValueError("Phone number cannot be blank.")
        
        if valid_phone_number.startswith("+"):
            phone_digits = valid_phone_number[1:]
        else:
            phone_digits = valid_phone_number   

        if not (
            valid_phone_number.isdigit() 
            or (
            valid_phone_number.startswith("+") 
            and valid_phone_number[1:].isdigit()
            )
        ):
            raise ValueError("Invalid phone number.")

        if len(phone_digits) < 7 or len(phone_digits) > 15:
            raise ValueError("Phone number must contain between 7 and 15 digits.") 

        return valid_phone_number
        
class CustomerResponse(BaseModel):
    id: int
    full_name: str   
    email: str
    phone_number: str


             

