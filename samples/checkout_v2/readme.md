# Checkout V2 - Simple Example using Python3

This script has a flow of sell and validate of status

You should include the credentials in config.py file. Contact our support to get ones.

## Running Project

### To Run (Linux):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requeriments.txt
python main.py
```

### To Run with docker:

```bash
docker build --tag integration-checkout2 .
docker run integration-checkout2
```


## Troubleshoot

### Problem with SSL certificate (Insecure Request)

In sandbox maybe you have a problem to validate the certificate, in this case, change to **False** the variable **VALIDATE_INSECURE_REQUEST** in **integrations.py** file.
