import re

# Function to check password strength
def check_password_strength(password):
    # Check length
    if len(password) < 8:
        return "Password is too short. Minimum length is 8 characters."

    # Check for lowercase, uppercase, digits, and special characters
    if not re.search(r'[a-z]', password):
        return "Password should contain at least one lowercase letter."
    if not re.search(r'[A-Z]', password):
        return "Password should contain at least one uppercase letter."
    if not re.search(r'[0-9]', password):
        return "Password should contain at least one digit."
    if not re.search(r'[@$!%*?&]', password):
        return "Password should contain at least one special character."

    return "Password is strong!"

# Test the function
password = "Passw0rd!"
print(check_password_strength(password))

