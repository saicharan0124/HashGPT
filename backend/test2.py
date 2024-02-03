import requests
import json

# Specify the URL for the FastAPI application
base_url = "http://127.0.0.1:8000"

# Example query for generating an answer
query_to_generate_answer = "what does uploadFileToArweave  funcion do"

# Create a dictionary with the query parameter
data = {"query": query_to_generate_answer}

# Make a POST request to generate an answer
response = requests.post(f"{base_url}/answergen", data=json.dumps(data), headers={'Content-Type': 'application/json'})

# Print the response
print(response.status_code)
print(response.content)  # Print the raw content
try:
    print(response.json())  # Try to parse JSON
except json.decoder.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")
