import requests
import dotenv
dotenv.load_dotenv()
import os 

# Configuration
YEAR = os.getenv("YEAR")
MONTH = os.getenv("MONTH")
API = os.getenv("API_KEY")

def fetch_and_process():
    print(f"Fetching data from API...")
    try:
        response = requests.get(API)
        response.raise_for_status() # Check for HTTP errors
        data = response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return
