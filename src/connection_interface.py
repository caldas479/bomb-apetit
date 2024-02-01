import requests
from security_library.algos import create_timestamp
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress only the InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

link = "https://192.168.2.10:443"

s = requests.Session()
s.cert = ('ssl/user.crt', 'ssl/user.key')
s.verify = False  # Only add this line if you have a self-signed certificate

def login(username, password):
    timestamp = create_timestamp()
    data = {"usr": username, "pswd": password, "timestamp" : timestamp}
    response = s.post(link + "/login", json=data, verify=False)
    return response

def keys():
    timestamp = create_timestamp()
    data = {"timestamp" : timestamp}
    response = s.get(link + '/keys',  json=data,verify=False)
    return response.json()

def vouchers():
    timestamp = create_timestamp()
    headers = {'Accept': 'application/json'}
    data = {"timestamp" : timestamp}
    response = s.get(link + '/documents', headers=headers, json=data,verify=False)
    return response.json()

def review(restaurant, review, signature):
    timestamp = create_timestamp()
    data = {"restaurant": restaurant, "review" : review, "signature" : signature, "timestamp" : timestamp}
    response = s.post(link + "/review", json=data, verify=False)
    return response.json()

def listReviews(restaurant):
    timestamp = create_timestamp()
    data = {"restaurant": restaurant, "timestamp" : timestamp}
    response = s.get(link + "/reviews", json=data, verify=False)
    return response.json()

def listUsers():
    timestamp = create_timestamp()
    headers = {'Accept': 'application/json'}
    data = {"timestamp" : timestamp}
    response = s.get(link + '/users', headers=headers, json=data, verify=False)
    return response.json()

def use_voucher(restaurant):
    timestamp = create_timestamp()
    data = {"restaurant" : restaurant, "timestamp" : timestamp}
    response = s.delete(link + '/voucher', json=data, verify=False)
    return response.json()

def transfer_voucher(restaurant, voucher, user, signature):
    timestamp = create_timestamp()
    data = {"restaurant" : restaurant, "voucher" : voucher, "user": user, "signature" : signature, "timestamp" : timestamp}
    response = s.put(link + "/transfer_voucher", json=data, verify=False)
    return response.json()

def requestUserPublicKey(user):
    timestamp = create_timestamp()
    data = {"user" : user, "timestamp" : timestamp}
    response = s.get(link + "/user", json=data, verify=False)
    return response.json()

def requestRestaurantPublicKey(restaurant):
    timestamp = create_timestamp()
    data = {"restaurant" : restaurant, "timestamp" : timestamp}
    response = s.get(link + "/restaurant", json=data, verify=False)
    return response.json()