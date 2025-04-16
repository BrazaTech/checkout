- [Return to readme](readme.md)
# Flow of Checkout v2
- Presenting a new release of the request flow in checkout v2.
- All operation operation are versioned, starting with v1.

## Step one POST (Login):
### Request
- Some informations is required at this moment: username and password
```bash
curl -L 'https://sandbox-authentication.brazacheckout.com.br/auth/login' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-d '{
  "username": "username_example",
  "password": "ComplexityPassW0rDEx@mpl3"
}'
```
### Response
```JSON
{
    "accessToken":"eyJraWQiO <<.. Suppressed Content..>> ASaygAXt8Og",
    "refreshToken":"eyJjdHki <<.. Suppressed Content..>> YIYb3YAyFN9u4F4V_m8R-w",
    "ttl":3600,
    "username":"usernameSampleRegistered"
}
```
- In this case, save the accessToken and refreshToken, as they will be used in some requests in this flow.

## Step two POST (Rates)
### Request to create a quotation
After saving some information from the login response, use the accessToken in the authorization header (JWT Authentication).

```bash
curl -L 'https://sandbox-rates.brazacheckout.com.br/v1/quotes' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og' \
-d '{
    "amount": 15.22,
    "currency": "USDBRL",
    "externalId": "20250416141532808"
}'
```
### Response of Quotes
```JSON
{
    "pix": {
        "id": "6afd291c-1ae6-11f0-bcfe-0a58a9feac02",
        "fgnQuantity": "15.45",
        "brlQuantity": "93.65",
        "quote": "5.85",
        "iof": "0.35",
        "iofPercentage": "0.38",
        "vet": "6.0615",
        "feesAmount": "2.92",
        "mdrPayer": "0.23"
    },
    "internationalCard": {
        "id": "6afd291c-1ae6-11f0-bcfe-0a58a9feac02",
        "brlQuantity": "97.74",
        "iof": "2.85",
        "vet": "82.29",
        "feesAmount": "4.51"
    }
}
```
After receiving the response, save the quotation code, in this case "2b1e6e2a-184c-11ef-941b-0a58a9feac02". This information is necessary to generate a PIX.
## Step Three GET (Customer)
### Request to validate a CPF (a official brazilian social number)
*Note: send X-CLIENT-CPF value masked*

```bash
curl -L 'https://sandbox-client.brazacheckout.com.br/v1' \
-H 'X-CLIENT-CPF: 999.999.999-99' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og'
```
### Response of client (success)
*Note: which CPF after validation have a unique clienId*
```JSON
{
    "clientId": "67f84c46-1216-4240-986d-2bbcc1b6d80a",
    "enabled": true
}
```

#### IMPORTANT: *SAVE clientId value*
### Response of client (success, however, with pending registration)
- This situation occurs when our service is unable to obtain information about the consumer.
```JSON
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

### If have a pending information, call this:
- First, call

```bash
curl -X 'GET' \
  'https://sandbox-address.brazacheckout.com.br/v1/cep/66813-720' \
  -H 'accept: application/json'
```
Use some fields of this response in the next request body:
```JSON
{
  "cep_indice": 66813420,
  "cep": "66813-420",
  "logradouro": "Rua Sargento Joaquim Resende",
  "complemento": "",
  "unidade": "",
  "bairro": "Campina de Icoaraci (Icoaraci)",
  "localidade": "Belém",
  "uf": "PA",
  "estado": "Pará",
  "regiao": "Norte",
  "ibge": "1501402",
  "gia": "",
  "ddd": "91",
  "siafi": "0427"
}
```

```bash
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
Response of patch

```JSON
{
    "clientId": "67f84c46-1216-4240-986d-2bbcc1b6d80a",
    "enabled": true
}
```

Use this value of clientId and id on Rates request (with alias name codQuote) to generate our PIX:

## Step Four POST (PIX)
### Request to Create a PIX

```bash
curl -L 'https://sandbox-pix.brazacheckout.com.br/v1/pix' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og' \
-d '{
  "codQuote": "6afd291c-1ae6-11f0-bcfe-0a58a9feac02",
  "codCustomer": "67f84c46-1216-4240-986d-2bbcc1b6d80a",
  "numberOfInstallments": 1 <- always 1 for pix
}'
```

### Response of PIX (success)
```JSON
{
    "expirationDate": "2025-04-16 17:35:42",
    "id": "3904ce7a-69f9-41c7-b1e5-7665ba49b41b",
    "key": "0195adce-e084-f419-55e9-e01cce7cc513",
    "qrcode": "00020101021226810014br.gov.bcb.pix2559brcode-h.sandbox.trio.com.br/cob/01JRZSJTSN2QR5NDB{{supressed content}}0496EB",
    "receiverFinancialInstitutionName": "TRIO_NOVA",
    "receiverName": "Braza Cripto SA",
    "qrCodeImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARQAAAEUCAYA{{supressed content}}AAAASUVORK5CYII=",
    "status": "CREATED",
    "codPartner": "e872001c-8e96-4dd3-bbd4-8580e9c41eb3",
    "codBranchOffice": "7ec80e31-2735-4c4c-ac05-cc06ca8216c2",
    "quantityBRL": "93.65",
    "quantityFGN": "15.45",
    "currency": "USDBRL"
}
```
Now save the id, with alias invoiceIdPix.

### Request GET status of pix
```bash
curl -L 'https://sandbox-pix.brazacheckout.com.br/v1/pix/3904ce7a-69f9-41c7-b1e5-7665ba49b41b/status' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og' 
```
This endpoint responds similarly to the response above, but adds some fields (codPartner and codBranchOffice):

### Response of status of pix.
```JSON
{
    "expirationDate": "2025-04-16 17:35:42",
    "id": "3904ce7a-69f9-41c7-b1e5-7665ba49b41b",
    "key": "0195adce-e084-f419-55e9-e01cce7cc513",
    "qrcode": "00020101021226810014br.gov.bcb.pix2559brcode-h.sandbox.trio.com.br/cob/01JRZSJTSN2QR5NDB{{supressed content}}0496EB",
    "receiverFinancialInstitutionName": "TRIO_NOVA",
    "receiverName": "Braza Cripto SA",
    "qrCodeImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARQAAAEUCAYA{{supressed content}}AAAASUVORK5CYII=",
    "status": "PENDING", // Possibles values: CREATED, PAID, PENDING, EXPIRED, REFUNDED
    "codPartner": "e872001c-8e96-4dd3-bbd4-8580e9c41eb3",
    "codBranchOffice": "7ec80e31-2735-4c4c-ac05-cc06ca8216c2",
    "quantityBRL": "93.65",
    "quantityFGN": "15.45",
    "currency": "USDBRL"
} 
```
### How to simulate a paid pix
We have an endpoint to simulate a paid PIX, so just use the invoiceIdPix on this service

#### Request (JUST FOR SANDBOX MODE)
```bash
curl --location --request POST 'https://sandbox-api.brazacheckout.com.br/utils/v1/pay/{invoiceIdPix}' \
--header 'Content-Type: application/json' \
--data-raw '{
  "taxId":"{cpfOfCustomer}" //Request a CPF or CNPJ to braza Team development
}'
```

### End of cicle. That's All.
- Any Questions open a issue.
### Other links
- [Flow Checkout v2 - without request document](flow-checkout-v2-without-document.md) NEW
- [Additional requests](flow-checkout-v2-additional-request.md) NEW
- [Base Url by environment](base-url-by-environment.md) NEW