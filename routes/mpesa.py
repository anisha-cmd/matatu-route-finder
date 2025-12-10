import requests
from decouple import config
from requests.auth import HTTPBasicAuth
import datetime
import base64

# Load credentials from .env
CONSUMER_KEY = config('CONSUMER_KEY')
CONSUMER_SECRET = config('CONSUMER_SECRET')
MPESA_SHORT_CODE = config('MPESA_SHORT_CODE')
PASSKEY = config('PASSKEY')
CALLBACK_URL = config('CALLBACK_URL')
ENVIRONMENT = config('ENVIRONMENT')

# Determine API URL based on environment
if ENVIRONMENT.lower() == 'sandbox':
    BASE_URL = "https://sandbox.safaricom.co.ke"
else:
    BASE_URL = "https://api.safaricom.co.ke"

def get_access_token():
    """
    Get OAuth token from Safaricom
    """
    auth_url = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(auth_url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    response.raise_for_status()
    data = response.json()
    return data['access_token']

def lipa_na_mpesa(phone_number, amount, account_ref, transaction_desc):
    """
    Perform M-Pesa STK Push
    """
    access_token = get_access_token()
    stk_push_url = f"{BASE_URL}/mpesa/stkpush/v1/processrequest"

    # Timestamp in format YYYYMMDDHHMMSS
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password_str = MPESA_SHORT_CODE + PASSKEY + timestamp
    password = base64.b64encode(password_str.encode()).decode()

    payload = {
        "BusinessShortCode": MPESA_SHORT_CODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,        # Customer's phone number
        "PartyB": MPESA_SHORT_CODE,    # Your short code
        "PhoneNumber": phone_number,   # Customer phone
        "CallBackURL": CALLBACK_URL,
        "AccountReference": account_ref,
        "TransactionDesc": transaction_desc
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(stk_push_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # Always return a consistent dict even on failure
        return {"ResponseDescription": f"Payment failed: {str(e)}"}