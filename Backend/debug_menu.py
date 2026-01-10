
from app import app
import json

def test_menu():
    with app.test_client() as client:
        response = client.get('/menu/1')
        print(f"Status Code: {response.status_code}")
        try:
            data = response.get_json()
            print("Data Type:", type(data))
            if isinstance(data, list) and len(data) > 0:
                print("First Item Sample:", data[0])
                print("Price Type:", type(data[0].get('price')))
            else:
                print("Data:", data)
        except Exception as e:
            print("Error parsing JSON:", e)
            print("Raw Data:", response.data)

if __name__ == "__main__":
    test_menu()
