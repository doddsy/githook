import requests
import json

def dispatch(data, url):
    r = requests.post(
        url,
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'},
    )
    return r.status_code