# LN Automatic Debit
This Python script automates monthly payments using LNBits wallets. It creates an invoice on a specified day of each month and pays it if not already paid.

# Prerequisites:

* Python 3.x installed
* Requests module installed:
  ```pip install requests```
* Ensure payment_status_file path exists and is writable

# Clone this repository:
```git clone https://github.com/emtll/ln-automatic-debit.git```

# Configuration

```cd ln-automatic-debit```
```sudo nano app.py```

### 1. Before running the script, modify the variables in app.py to suit your environment:
```
# File path to store payment logs
payment_status_file = "/path/to/payment_logs.txt"

# Recipient LNBits wallet URL and API key for creating invoices
urlc = "https://<LNBits_wallet_domain>/api/v1/payments"
api_key_create = "<invoice_key>"

# Payer LNBits wallet URL and admin API key
urlp = "https://<LNBits_wallet_domain>/api/v1/payments"
api_key_pay = "<admin_key>"

# Amount to pay monthly. It depends on the unit of account you choose
amount_usd = "<amount>"

# Invoice unit of account (e.g., sat, usd, eur, etc.)
unit = "<unit>"

# Invoice duration time until expiration
expiry = "<time>"

# Message to include in payment. You can leave it blank ex: ""
name = "<message>"

# Day you want to execute the payment every month. Default: 1
check_day = 1
```

### 2. Run the script:
```
python3 app.py
```

# Systemd Service
To run the script as a systemd service for automatic execution:

### 1. Create a systemd service file automatic-debit.service:
```
[Unit]
Description=Automatic Payment Service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/app.py
Restart=always
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 2. Save the file and enable the service:
```
sudo cp pay-to-jvx.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable automatic-debit.service
sudo systemctl start automatic-debit.service
```

### 3. Check the service status:
```
sudo systemctl status automatic-debit.service
```
This will start the script automatically on system boot and restart it if it fails.
Check the logs with:
```
journalctl -fu automatic-debit
```
