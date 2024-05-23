# Flow of Checkout v2

- presenting a new release of flow of request on checkout v2.
- All endpoint of operation are versioned, we start with v1 some else

## Step one (Login):
### Request
- Some informations are required at this moment username and password
```Shell
curl -L 'https://sandbox-authentication.brazacheckout.com.br/auth/login' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-d '{
  "username": "username_example",
  "password": "ComplexityPassW0rDEx@mpl3"
}'
```
### Response
```Javascript
{
    "accessToken":"eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og",
    "refreshToken":"eyJjdHki <<.. Supressed Content..>> YIYb3YAyFN9u4F4V_m8R-w",
    "ttl":3600,
    "username":"usernameSampleRegistered"
}
```
- In this case we save accessToken and refreshToken, we use in some request on this flow

## Step two (Rates)
### Request to create a quotation
After we save a some information on response of login, use a accessToken on header authorization (JWT Authentication).

```Shell
curl -L 'https://sandbox-api.brazacheckout.com.br/rates/v1/quotes' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og' \
-d '{
  "amount": 150.75,
  "currency": "USDBRL",
  "externalId": "20240522114740205"
}'
```
### Response of Quotes
```Javascript
{
    "pix": {
        "id": "2b1e6e2a-184c-11ef-941b-0a58a9feac02",
        "fgnQuantity": "151.75",
        "brlQuantity": "868.34",
        "quote": "5.31",
        "iof": "9.45",
        "iofPercentage": "1.1",
        "vet": "5.7222",
        "feesAmount": "53.10",
        "mdrPayer": "1.75"
    },
    "internationalCard": {
        "id": "2b1e6e2a-184c-11ef-941b-0a58a9feac02",
        "fgnQuantity": "151.75",
        "brlQuantity": "882.99",
        "quote": "5.31",
        "iof": "36.89",
        "iofPercentage": "1.1",
        "vet": "731.24",
        "feesAmount": "40.31",
        "mdrPayer": "1.75"
    }
}
```
Now after we receive a response, save the code of quotation in this case "2b1e6e2a-184c-11ef-941b-0a58a9feac02". So, this information is necessary to generate a pix.

## Step Three (Customer)
### Request to validate a CPF (a official brazilian social number)
```Shell
curl -L 'https://sandbox-client.brazacheckout.com.br/v1' \
-H 'X-CLIENT-CPF: 999.999.999-99' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og'
```
### Response of client (success)

```Javascript
{
    "clientId": "67f84c46-1216-4240-986d-2bbcc1b6d80a",
    "enabled": true
}
```

### Response of client (success, however, with pending registration)
- This situation occurs when our service is unable to obtain information about the consumer.
```Javascript
{
  "clientId": "67f84c46-1216-4240-986d-2bbcc1b6d80a",
  "enabled": false,
  "pendent": [
    "phone",
    "email",
    "address",
    "street-number",
    "neighborhood",
    "city",
    "state",
    "cep",
    "complement"
  ],
  "code": "CPF001"
}
```
For more informations read [here](https://sandbox-client.brazacheckout.com.br/docs#/Client/AppController_validateCpf)

### If have a pending information call this:
First we call

```Shell
curl -L 'https://viacep.com.br/ws/66813420/json/'
```
use this some fields of this response on next request body:
```Javascript
{
  "cep": "66813-420", //zipCode
  "logradouro": "Rua Sargento Joaquim Resende", //address
  "complemento": "", //complement
  "bairro": "Campina de Icoaraci (Icoaraci)", //neighborhood
  "localidade": "Belém", // city
  "uf": "PA", //state
  "ibge": "1501402", //code
  "gia": "",
  "ddd": "91",
  "siafi": "0427"
}
```

```Shell
curl -L -X PATCH 'https://sandbox-client.brazacheckout.com.br/v1' \
-H 'X-CLIENT-CPF: 999.999.999-99' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og' \
-d '{
  "cep": "66813-420",
  "state": "PA",
  "city": "Belém",
  "code": "1501402",
  "neighborhood": "Campina de Icoaraci (Icoaraci)",
  "address": "Rua Sargento Joaquim Resende",
  "number": "366",
  "complement": "",
  "phone": "+5591992664715",
  "email": "angelo.reis@braza.com.br"
}'
```