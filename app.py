# Prerequisites to run this script:
# - Python 3.x installed
# - requests module installed (`pip install requests`)
# - Ensure `payment_status_file` path exists and is writable

import requests
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
check_day = 1 # Day you want to execute the payment every month. Default: 1                                     |
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
        logging.info(f"Invoice created successfully: {data['payment_request']}")
        return data["payment_request"]
    else:
        logging.error(f"Failed to create invoice. Status code: {response.status_code}")
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
        logging.info(f"Payment successful! Payment hash: {data['payment_hash']}")
        return data["payment_hash"]
    else:
        logging.error(f"Failed to pay invoice. Status code: {response.status_code}")
        return None

# Function to check if it's the pay day
def is_first_day_of_month():
    today = datetime.now()
    logging.debug(f"Checking if today is the {check_day}th day of the month...")
    return today.day == check_day

# Function to check if payment has already been done today
def is_payment_done_today():
    logging.debug("Checking if payment has been done today...")
    try:
        with open(payment_status_file, "r") as file:
            last_payment_entry = file.read().strip()
            if last_payment_entry:
                last_payment_date, last_payment_hash = last_payment_entry.split(" - payment hash: ")
                today = datetime.now().strftime("%Y-%m-%d")
                logging.debug(f"Last payment date: {last_payment_date}, Today: {today}")
                return last_payment_date == today
            else:
                return False
    except FileNotFoundError:
        logging.debug("Payment status file not found.")
        return False

# Function to mark payment as done today, including payment hash
def mark_payment_done_today(payment_hash):
    today = datetime.now().strftime("%Y-%m-%d")
    logging.debug(f"Marking payment done for today: {today}")
    with open(payment_status_file, "w") as file:
        file.write(f"{today} - payment hash: {payment_hash}")
    logging.info(f"Payment marked as done for today: {today} - payment hash: {payment_hash}")

# Main function to automate monthly payment
def main():
    logging.info("Starting the automatic payment script.")
    memo = f"{name} - {datetime.now().strftime('%m/%Y')}"
    while True:
        # Check if it's the 1st day of the month and payment hasn't been done today
        if is_first_day_of_month() and not is_payment_done_today():
            # Create invoice
            invoice = create_invoice(api_key_create, amount_usd, memo, unit, expiry)
            if invoice:
                print(f"Invoice created successfully: {invoice}")

                # Pay invoice and check status
                payment_hash = pay_invoice(api_key_pay, invoice)
                if payment_hash:
                    logging.info("Payment successful!")
                    # Mark payment as done today
                    mark_payment_done_today(payment_hash)
                    # Store payment details for verification
                else:
                    logging.error("Failed to pay invoice.")
            else:
                logging.error("Failed to create invoice.")

        # Wait 1 hour before checking again
        logging.info(f"Waiting until the next day {check_day} of the month...")
        time.sleep(60 * 60)

if __name__ == "__main__":
    main()
