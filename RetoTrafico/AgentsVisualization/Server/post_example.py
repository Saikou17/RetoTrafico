import requests
import json

url = "http://52.1.3.19:8585/api/attempts"
endpoint = "validate_attempt"

data = {
    "year" : 2023,
    "classroom" : 301,
    "name" : "Juan Pablos Morenos",
    "num_cars": 50
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url+endpoint, data=json.dumps(data), headers=headers)

print("Request " + "successful" if response.status_code == 200 else "failed", "Status code:", response.status_code)
print("Response:", response.json())