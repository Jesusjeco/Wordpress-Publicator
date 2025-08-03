import requests
import base64

url = "https://wordpress.jesusjeco.dev/wp-json/wp/v2/users/me"
username = "jesusenrique.carrero@gmail.com"
password = "Ados(yv7VcaGzra!vEI4mDt*"

credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
headers = {
    "Authorization": f"Basic {credentials}"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    print("Authentication successful!")
    print(response.json())
else:
    print(f"Failed: {response.status_code}")