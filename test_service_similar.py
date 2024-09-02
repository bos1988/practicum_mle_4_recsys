import requests

service_url = 'http://127.0.0.1:8010'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

params = {"item_id": 17245, 'k': 3}
resp = requests.post(service_url + "/similar_items", headers=headers, params=params)

print("test 1:")

if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs)
