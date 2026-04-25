import re


class ValidationError(ValueError):
    pass


class Validator:
    MAX_TASK_LENGTH = 200
    MAX_NOTES_LENGTH = 1000
    MAX_MILEAGE = 999_999

    @staticmethod
    def sanitize_text(value: str) -> str:
        return re.sub(r'\s+', ' ', value.strip())

    @staticmethod
    def validate_task(task: str) -> str:
        task = Validator.sanitize_text(task)
        if not task:
            raise ValidationError("Task description cannot be empty.")
        if len(task) > Validator.MAX_TASK_LENGTH:
            raise ValidationError(f"Task too long (max {Validator.MAX_TASK_LENGTH} characters).")
        return task

    @staticmethod
    def validate_mileage(new_km: int, current_km: int) -> int:
        if new_km < 0:
            raise ValidationError("Mileage cannot be negative.")
        if new_km > Validator.MAX_MILEAGE:
            raise ValidationError(f"Mileage exceeds maximum ({Validator.MAX_MILEAGE:,} km).")
        if new_km < current_km:
            raise ValidationError(
                f"New mileage ({new_km:,}) cannot be less than current ({current_km:,} km)."
            )
        return new_km

    @staticmethod
    def validate_fuel_entry(liters: float, price: float) -> None:
        if liters <= 0:
            raise ValidationError("Liters must be greater than zero.")
        if price < 0:
            raise ValidationError("Price cannot be negative.")
