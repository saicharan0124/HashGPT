import requests
import json

# Specify the URL for the FastAPI application
base_url = "http://127.0.0.1:8000"

# Example URL to add documents
url_to_add_documents = "https://blog.developerdao.com/near-chain-abstraction-explained"

# Create a dictionary with the URL parameter
data = {"url": url_to_add_documents}

# Make a POST request to add documents
response = requests.post(f"{base_url}/add_document", data=json.dumps(data), headers={'Content-Type': 'application/json'})

# Print the response
print(response.status_code)
print(response.json())
