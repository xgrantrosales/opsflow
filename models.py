from pydantic import BaseModel, Field, field_validator, EmailStr, model_validator
from validators import clean_full_name, clean_phone_number

class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=1)
    email: EmailStr
    phone_number: str = Field(min_length=1)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls,full_name:str) -> str:

        return clean_full_name(full_name)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls,phone_number:str) -> str:

        return clean_phone_number(phone_number)
        
class CustomerResponse(BaseModel):
    id: int
    full_name: str   
    email: str
    phone_number: str

class CustomerUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None  

    @model_validator(mode="after")
    def validate_update_request(self):

        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for update.")

        for name in self.model_fields_set:

            if getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null.")

        return self

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls,full_name:str|None) -> str|None:

        if full_name is None:
            return None

        else:
            return clean_full_name(full_name)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls,phone_number:str|None) -> str|None:

        if phone_number is None:
            return None

        else:
            return clean_phone_number(phone_number)    



             

