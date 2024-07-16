# Prerequisites to run this script:
# - Python 3.x installed
# - requests module installed (`pip install requests`)
# - Ensure `payment_status_file` path exists and is writable

import requests
import time
from datetime import datetime

#                           PLEASE MODIFY THE VARIABLES BELOW FOR YOUR USE CASE: 
#_______________________________________________________________________________________________________________#
payment_status_file = "/path/to/payment_logs.txt" # File path to store payment logs                             |
urlc = "https://<LNBits_wallet_domain>/api/v1/payments" # Recipent LNBits wallet URL                            |
api_key_create = "<invoice_key>" # Recipient LNBits wallet invoice key                                          |
urlp = "https://<LNBits_wallet_domain>/api/v1/payments" # Payer LNBits wallet URL                               |
api_key_pay = "<admin_key>" # Payer LNBits wallet admin key                                                     |
amount_pay = "<amount>" # Amount to pay monthly. It depends on the unit of account you choose                   |
name = "<message>" # Message to include in payment. You can leave it blank ex: ""                               |
unit = "<unit>" # Invoice unit of account (e.g. sat, usd, eur, etc.)                                            |
expiry = "<time>" # Invoice duration time until expiration                                                      |
check_day = "<day>" # Day you want to execute the payment every month                                           |
#_______________________________________________________________________________________________________________#

# Function to create an invoice
def create_invoice(api_key, amount, memo, unit, expiry):
    headers = {
        "X-Api-Key": api_key,
        "Content-type": "application/json"
    }
    payload = {
        "out": False,
        "amount": amount,
        "memo": memo,
        "unit": unit,
        "expiry": expiry,
        "webhook": "", 
        "internal": False
    }
    
    response = requests.post(urlc, json=payload, headers=headers)
    if response.status_code == 201:
        data = response.json()
        return data["payment_request"]
    else:
        print(f"Failed to create invoice. Status code: {response.status_code}")
        return None

# Function to pay an invoice
def pay_invoice(api_key, bolt11):
    headers = {
        "X-Api-Key": api_key,
        "Content-type": "application/json"
    }
    payload = {
        "out": True,
        "bolt11": bolt11
    }
    
    response = requests.post(urlp, json=payload, headers=headers)
    if response.status_code == 201:
        data = response.json()
        return data["payment_hash"]
    else:
        print(f"Failed to pay invoice. Status code: {response.status_code}")
        return None

# Function to check if it's the 1st day of the month
def is_first_day_of_month():
    today = datetime.now()
    return today.day == check_day

# Function to check if payment has already been done today
def is_payment_done_today():
    try:
        with open(payment_status_file, "r") as file:
            last_payment_entry = file.read().strip()
            if last_payment_entry:
                last_payment_date, last_payment_hash = last_payment_entry.split(" - payment hash: ")
                today = datetime.now().strftime("%Y-%m-%d")
                return last_payment_date == today
            else:
                return False
    except FileNotFoundError:
        return False

# Function to mark payment as done today, including payment hash
def mark_payment_done_today(payment_hash):
    today = datetime.now().strftime("%Y-%m-%d")
    with open(payment_status_file, "w") as file:
        file.write(f"{today} - payment hash: {payment_hash}")

# Main function to automate monthly payment
def main():
    memo = f"{name} - {datetime.now().strftime('%m/%Y')}"
    while True:
        # Check if it's the 1st day of the month and payment hasn't been done today
        if is_first_day_of_month() and not is_payment_done_today():
            # Create invoice
            invoice = create_invoice(api_key_create, amount_pay, memo)
            if invoice:
                print(f"Invoice created successfully: {invoice}")
                
                # Pay invoice and check status
                payment_hash = pay_invoice(api_key_pay, invoice)
                if payment_hash:
                    print("Payment successful!")
                    # Mark payment as done today
                    mark_payment_done_today(payment_hash)
                    # Store payment details for verification
                else:
                    print("Failed to pay invoice.")
            else:
                print("Failed to create invoice.")
        
        # Wait 1 hour before checking again
        print(f"Waiting until the {check_day}th day of the month...")
        time.sleep(60 * 60)

if __name__ == "__main__":
    main()
