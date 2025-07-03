import os
import dotenv
import requests

dotenv.load_dotenv()


def get_access_token():
   body = {
       "client_id": os.getenv("CLIENT_ID"),
       "client_secret": os.getenv("CLIENT_SECRET"),
       "refresh_token": os.getenv("REFRESH_TOKEN"),
       "grant_type": "refresh_token",
   }
   try:
       response = requests.post("https://accounts.zoho.com/oauth/v2/token",data=body)
       data = response.json()
       access_token = data["access_token"]
       return access_token
   except Exception as e:
       return None

if __name__ == '__main__':
    get_access_token()