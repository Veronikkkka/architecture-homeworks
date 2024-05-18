import requests
import time
import json

# URL ендпоінта для отримання API ключа
api_key_url = "http://localhost:8000/apikey"

# Функція для отримання API ключа
def get_api_key():
    response = requests.get(api_key_url)
    if response.status_code == 200:
        return response.json()["api_key"]
    else:
        print("Failed to get API key:", response.text)
        return None

# Функція для виконання запитів GET
def send_get_request(api_key):
    url = f"http://localhost:8000/tickets?api_key={api_key}"
    response = requests.get(url)
    print("GET request status code:", response.status_code)
    print("GET request response:", response.text)

# Функція для виконання запитів POST
def send_post_request(api_key):
    url = f"http://localhost:8000/tickets/?api_key={api_key}"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        "event_id": 0,
        "type": "string",
        "price": 0,
        "status": "available",
        "user_id": 0
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("POST request status code:", response.status_code)
    print("POST request response:", response.text)


if __name__ == "__main__":
    
    api_key = get_api_key()

    if api_key:
        
        for i in range(10):
            send_get_request(api_key)
            send_post_request(api_key)
            # time.sleep(0.1) 

        
        for i in range(5):
            send_post_request(api_key)
            time.sleep(0.2)  


