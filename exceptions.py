class DuplicateConfirmationRequired(Exception):
    def __init__(self, existing_customers):
        self.existing_customers = existing_customers
        super().__init__("Possible duplicate customers found. Confirmation required.")
        