import requests
import dotenv
dotenv.load_dotenv()
import os 
from datetime import datetime

# Configuration
MONTH = datetime.now().month
YEAR = datetime.now().year
API_KEY = os.getenv("API_KEY")

# Fetch and Process
async def fetch_and_process(circle_id):
    full_url = f"{API_KEY}?circle_id={circle_id}&year={YEAR}&month={MONTH}" 
    print(f"Fetching data from API... ")
    try:
        response = requests.get(full_url)
        response.raise_for_status() # Check for HTTP errors
        data = response.json()
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
