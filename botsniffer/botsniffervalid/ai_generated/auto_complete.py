import openai

openai.api_key = "your-api-key"

def complete_code(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"]

# Example usage
user_code = "def fibonacci(n):"
completion = complete_code(user_code)
print(completion)

