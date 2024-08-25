import requests

service_url = 'http://127.0.0.1:8000'
events_store_url = "http://127.0.0.1:8020"
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

print("test 1:")

params = {"user_id": 1353637, 'k': 3}
resp = requests.post(service_url + "/recommendations_offline", headers=headers, params=params)

if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs)

print("test 2 (empty answer):")

params = {"user_id": 100, 'k': 3}
resp = requests.post(service_url + "/recommendations_online", headers=headers, params=params)

if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs)

print("test 3 (add events):")

params = {"user_id": 1291248, "item_id": 17245}
resp = requests.post(events_store_url + "/put", headers=headers, params=params)

if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs)

print("test 4 (good answer):")

params = {"user_id": 1291248, 'k': 3}
resp = requests.post(service_url + "/recommendations_online", headers=headers, params=params)

if resp.status_code == 200:
    recs = resp.json()
else:
    recs = []
    print(f"status code: {resp.status_code}")
    
print(recs)

print("test 5 (few events):")

user_id = 1291248
event_item_ids = [41899, 102868, 5472, 5907]

for event_item_id in event_item_ids:
    resp = requests.post(
        events_store_url + "/put", 
        headers=headers, 
        params={"user_id": user_id, "item_id": event_item_id}
    )
                         
params = {"user_id": user_id, 'k': 5}
resp = requests.post(service_url + "/recommendations_online", headers=headers, params=params)
online_recs = resp.json()
    
print(online_recs) 

print("test 6 (online + offline):")

user_id = 1291250
event_item_ids =  [7144, 16299, 5907, 18135]

for event_item_id in event_item_ids:
    resp = requests.post(
        events_store_url + "/put", 
        headers=headers, 
        params={"user_id": user_id, "item_id": event_item_id}
    )

params = {"user_id": 1291250, 'k': 10}
resp_offline = requests.post(service_url + "/recommendations_offline", headers=headers, params=params)
resp_online = requests.post(service_url + "/recommendations_online", headers=headers, params=params)
resp_blended = requests.post(service_url + "/recommendations", headers=headers, params=params)

recs_offline = resp_offline.json()["recs"]
recs_online = resp_online.json()["recs"]
recs_blended = resp_blended.json()["recs"]

print(recs_offline)
print(recs_online)
print(recs_blended)
