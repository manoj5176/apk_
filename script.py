import os

# Access the secret from the environment variable
secret = os.getenv('SECRET_GITHUB')

# Use the secret in your Python code
print(f"The secret is: {secret}")

# Example of using the secret in a request or other logic
