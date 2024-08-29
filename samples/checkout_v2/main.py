from faker import Faker
import logging

from integrations import *
from config import FAKER_LOCALE, BASIC_TOKEN_SIMULATE_PAY_PIX

faker = Faker(FAKER_LOCALE)

logging.basicConfig(level=logging.INFO)

def main():
    logging.info("1. Getting the access token")
    auth_api_response = get_auth_token()
    logging.debug(auth_api_response)

    logging.info("2. Getting the quote")
    access_token = auth_api_response.get('accessToken')
    pair_of_currency_to_exchange = 'USDBRL' 
    amount_of_operation_in_partner_currency = 123.45
    identifier_of_partner_transaction = faker.uuid4() # Here needs to be a partner transaction identifier

    # Case you have a accreditor to use. To use this feature needs a specific permition on the API
    accredited_name = None
    accredited_country = None
    quote = get_quote(access_token, pair_of_currency_to_exchange,amount_of_operation_in_partner_currency, 
                      identifier_of_partner_transaction, accredited_name, accredited_country)
    logging.debug(quote)

    logging.info("3. Validate the Client")
    client_cpf = faker.cpf() # Here needs to be the client CPF
    validate_client_response = validate_client(access_token, client_cpf)
    logging.debug(validate_client_response)

    is_client_valid = validate_client_response.get('enabled')
    if not is_client_valid:
        logging.info("3.1   Update the Client information")
        """ Note: The informations that be update is only returned in the field "pendent" on validate_client_response
                  But here we are updating all the informations using a faker library"""
        client_information_to_update = {
            "cep": faker.postcode(),
            "state": faker.state_abbr(),
            "city": faker.city(),
            "code": faker.random_number(digits=5),
            "neighborhood": faker.neighborhood(),
            "address": faker.street_name(),
            "streetNumber": faker.random_number(digits=4),
            "complement": "",
            "phone": faker.phone_number(),
            "email": faker.email(),
        }
        update_client_response = update_client(access_token, client_cpf, client_information_to_update)
        logging.debug(update_client_response)

    logging.info("4. Generate the payment")
    quote_id = quote.get('pix').get('id')
    client_id = validate_client_response.get('clientId')
    payment_information = generate_payment(access_token, quote_id, client_id)
    logging.debug(payment_information)

    logging.info("4.1. Simulating the payment - Only in SANDBOX environment")
    pix_id = payment_information.get('id')
    token_simulator = BASIC_TOKEN_SIMULATE_PAY_PIX
    simulate_payment_response = simulate_pay_pix(token_simulator, pix_id)
    logging.debug(simulate_payment_response)

    logging.info("5. Wait for the payment confirmation")
    await_payment_of_pix(access_token, quote_id)

    logging.info("6. Get the sale information")
    sale_information = get_sale_information(access_token, quote_id)
    logging.debug(sale_information)

    if sale_information.get('statusLabel') == 'success':
        logging.info("The sale was successfully completed - The payment was confirmed")
        """ Note: In this case de partner can delivery the product or service to the client, 
                but the exchange was not completed yet """

    logging.info("6. Wait for the exchange confirmation")
    await_execute_exchange(access_token, quote_id)

    sale_information = get_sale_information(access_token, quote_id)
    logging.debug(sale_information)

    if sale_information.get('statusName') == 'Processado':
        logging.info("The exchange was successfully completed")
    else:
        logging.info("The exchange was not completed - contact the support")
    return


if __name__ == '__main__':
    main()