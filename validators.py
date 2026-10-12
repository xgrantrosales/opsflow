def clean_full_name(full_name: str) -> str:

    if len(full_name.strip()) == 0:
                
                raise ValueError("Full name cannot be blank.")
    
    return full_name.strip()

def clean_phone_number(phone_number: str) -> str:
        
        valid_phone_number = phone_number.strip()
        
        if len(valid_phone_number) == 0:
                raise ValueError("Phone number cannot be blank.")
                
        if valid_phone_number.startswith("+"):
            
            phone_digits = valid_phone_number[1:]

        else:
            phone_digits = valid_phone_number   
        
        if not(
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