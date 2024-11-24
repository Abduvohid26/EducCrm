import re
from rest_framework.exceptions import ValidationError

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
phone_regex = r'^\+998([- ])?(90|91|93|94|95|98|99|33|97|71|88|)([- ])?(\d{3})([- ])?(\d{2})([- ])?(\d{2})$'

def check_username_or_phone(email_or_phone):
    if re.fullmatch(phone_regex, email_or_phone):
        email_or_phone = 'phone'
    else:
        email_or_phone = 'username'
    return email_or_phone