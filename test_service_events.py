import requests

service_url = 'http://127.0.0.1:8020'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

print("test 1:")

params = {"user_id": 1337055, "item_id": 17245}
resp = requests.post(service_url + "/put", headers=headers, params=params)

if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs)

print("test 2:")

params = {"user_id": 1337055, "k": 3}
resp = requests.post(service_url + "/get", headers=headers, params=params)

if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs)
