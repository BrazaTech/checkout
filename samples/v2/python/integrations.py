import requests
import time
import json
from typing import Literal
import urllib3

from config import URL_AUTH, URL_RATES, URL_PIX, URL_SALE, URL_CLIENT_API, USERNAME, PASSWORD

#If you have problem with SSL certificate, you can set this variable to False
VALIDATE_INSECURE_REQUEST = True

if not VALIDATE_INSECURE_REQUEST:
    #To disable the warning of SSL certificate
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_auth_token():
    """
    This function get a access token to use in the API.

    Returns:
        dict: A dictionary with the following keys:
            accessToken (str): access token
            refreshToken (str): refresh token
            ttl (int): time to live in seconds
            username (str): username used
    """
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'username': USERNAME,
        'password': PASSWORD
    }
    response = requests.post(URL_AUTH, headers = headers, data = json.dumps(data), verify = VALIDATE_INSECURE_REQUEST)
    return response.json()

def get_quote(token: str, currency: Literal['USDBRL', 'EURBRL', 'GBPBRL', 'CADBRL'], 
              amount: int, external_id: str, accreditedName: str = None, accreditedCountry: str = None):
    """ 
    This method is used to get the quote for the exchange.

    Args:
        token (str):  access token generated by get_auth_token
        currency (str):  currency to exchange - ex: 'USDBRL'
        amount (float): amount to exchange - ex: 100.12
        external_id (str):  external id to the exchange - optional
        accreditedName (str):  name of the accredited. Defaults to None.  *
        accreditedCountry (str):  country of the accredited. Defaults to None.  *
            Used on for accreditor, needs a specific congifuration on the API to accept this parameter

    Returns:
        dict: A dict with payments methods availables for the exchange:
            pix (dict): dict with the pix information:
                id (str): quote id, is the mostly important parameter, user to reference the exchange, sales and create payment
                fgnQuantity (int): amount of currency to exchange
                brlQuantity (int): amount of BRL to pay
                quote (int): quote value
                iof (int): IOF value
                iofPercentage (int): IOF percentage
                vet (int): VET value
                feesAmount (int): fees amount
                mdrPayer (int): Tax included in the amount currency
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    body = {
        'currency': currency,
        'amount': amount,
        'externalId': external_id
    }
    if accreditedName is not None:
        body['accreditedName'] = accreditedName
        body['accreditedCountry'] = accreditedCountry

    response = requests.post(URL_RATES, headers = headers, json = body, verify = VALIDATE_INSECURE_REQUEST)
    return response.json() 

def generate_payment(token, quote_id, client_id):
    """
    This method is used to generate and get the payment information to make the exchange/

    Args:
        token (str): access token generated by get_auth_token
        quote_id (str): quote id generated by get_quote
        client_id (str): client id obtained by validate_client
    Returns:
        dict: A dict with the payment information:
            id (str): id of pix (in DEVELOPMENT used to simulate the payment)
            key (str): key of pix
            qrCode (str): qrCode of pix
            receiverName (str): name of the receiver the payment
            receiverFinancialInstitutionName (str): Name of financial institution of the receiver
            expirationDate (str): Expiration date of the pix
            status (str): Status of payment
    """
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    body = {
        'codQuote': quote_id,
        'codCustomer': client_id,
    }

    response = requests.post(URL_PIX, headers = headers, json = body, verify = VALIDATE_INSECURE_REQUEST)
    return response.json()

def simulate_pay_pix(token, pix_id):
    """
    This method is used to simulate the payment of the pix.
    >>> Available only in the SANDBOX environment <<<

    Args:
        token (str): access token generated by get_auth_token
        pix_id (str): pix id generated by generate_payment
    """

    url = f"{URL_PIX}/webhook"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {token}'
    }
    body = {
        'invoiceIdentifier': pix_id,
        'status': 'ACCEPT',
        'notificationType': 'RECEIVE'
    }

    response = requests.post(url, headers = headers, json = body, verify = VALIDATE_INSECURE_REQUEST)
    return response.json()

def get_sale_information(token, sale_id):
    """
    This method is used to get the sale information.

    Args:
        token (str): access token generated by get_auth_token
        sale_id (str): sale id is same that quote id, obtained by get_quote
    Returns:
        
    """

    url = f"{URL_SALE}/{sale_id}"
    headers = {
        'Authorization': f'Bearer {token}'
    }

    response = requests.get(url, headers = headers, verify = VALIDATE_INSECURE_REQUEST)
    return response.json()

def validate_client(token: str, client_cpf: str):
    """
    This method is used to validate if the client is already registered.

    Args:
        token (str): access token generated by get_auth_token
        client_cpf (str): cpf of the client in format: 000.000.000-00
    
    Returns:
        dict: a dictionary with the client status:
            clientId (str): the client id used to generate the payment
            enabled (bool): if the client is enabled to make the exchange
            pendent (List[str]): a array of string idenfitying the information pending to the client
    """
    url = f"{URL_CLIENT_API}"
    headers = {
        'Authorization': f'Bearer {token}',
        'X-CLIENT-CPF': client_cpf
    }

    response = requests.get(url, headers = headers, verify = VALIDATE_INSECURE_REQUEST)
    return response.json()

def update_client(token:str, client_cpf: str, client_information: dict):
    """
    This method is used to update the client information.

    Args:
        token (str): access token generated by get_auth_token
        client_cpf (str): cpf of the client in format: 000.000.000-00
        client_information (dict): a dictionary with the client information to update
    
    Returns:
        dict: a dictionary with the client status:
            clientId (str): the client id used to generate the payment
            enabled (bool): if the client is enabled to make the exchange
            pendent (List[str]): a array of string idenfitying the information pending to the client
    """
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'X-CLIENT-CPF': client_cpf
    }

    response = requests.patch(URL_CLIENT_API, headers= headers, json= client_information, verify= False)
    return response.json()


def await_payment_of_pix(token, quote_id):
    """
    This method is used to await the payment of the pix.
    >>> Available only in the SANDBOX environment <<<

    Args:
        token (str): access token generated by get_auth_token
        quote_id (str): quote id generated by get_quote
    """
    awaiting = True
    iteration = 0

    while (awaiting and iteration < 10):
        sale = get_sale_information(token, quote_id)
        if sale['statusLabel'] == 'success':
            awaiting = False
        time.sleep(0.5)
        iteration += 1

    return iteration < 10

def await_execute_exchange(token, quote_id):
    """
    This method is used to await the exchange execution.
    >>> Available only in the SANDBOX environment <<<

    Args:
        token (str): access token generated by get_auth_token
        quote_id (str): quote id generated by get_quote
    """
    awaiting = True
    iteration = 0

    while (awaiting and iteration < 150):
        sale = get_sale_information(token, quote_id)
        
        if sale['statusName'] == 'Processado':
            awaiting = False
        time.sleep(0.5)
        iteration += 1

    return iteration < 150