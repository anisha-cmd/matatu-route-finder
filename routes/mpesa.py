import requests
from requests.auth import HTTPBasicAuth
import base64
import datetime

# Daraja sandbox credentials
CONSUMER_KEY = "YOUR_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONSUMER_SECRET"
PASSKEY = "YOUR_PASSKEY"

def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json().get('access_token')

def lipa_na_mpesa(phone_number, amount, account_reference="Test", transaction_desc="Route Payment", shortcode=""):
    access_token = get_access_token()
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password_str = f"{shortcode}{PASSKEY}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://your-callback-url.com/",
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                             json=payload, headers=headers)
    return response.json()
