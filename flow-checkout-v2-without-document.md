- [Return to readme](readme.md)
# Flow of Checkout v2 (Without Official Document)
- Presenting a new release of the flow of requests on checkout v2 without official documents (CPF and/or CNPJ).
- All endpoints of operation are versioned, starting with v1.

## Step one POST (Login):
### Request
- Some information is required at this moment: username and password.
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
    "accessToken":"eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og",
    "refreshToken":"eyJjdHki <<.. Supressed Content..>> YIYb3YAyFN9u4F4V_m8R-w",
    "ttl":3600,
    "username":"usernameSampleRegistered"
}
```
In this case, save the accessToken and refreshToken. We will use them in some requests in this flow.

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
After receiving the response, save the quotation code, in this case, "2b1e6e2a-184c-11ef-941b-0a58a9feac02". This information is necessary to generate a PIX.

## Step Three POST (PIX)
### Request to Create a PIX
```bash
curl -L 'https://sandbox-pix.brazacheckout.com.br/v1/pix' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og' \
-d '{
    "codQuote": "6afd291c-1ae6-11f0-bcfe-0a58a9feac02",
    "codCustomer": "",
    "numberOfInstallments": 1  <- always 1 on pix
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
Now save the id, with the alias invoiceIdPix.

### Request GET status of pix
```bash
curl -L 'https://sandbox-pix.brazacheckout.com.br/v1/pix/3904ce7a-69f9-41c7-b1e5-7665ba49b41b/status' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og' 
```
This endpoint respose a same of response above, but, adding some fields, (codPartner and CodBranchOffice):

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

### How to Simulate a Paid PIX
We have an endpoint to simulate a paid PIX. Use the invoiceIdPix on this service.

#### Request (JUST FOR SANDBOX MODE)
```bash
curl --location --request POST 'https://sandbox-api.brazacheckout.com.br/utils/v1/pay/{invoiceIdPix}' \
--header 'Content-Type: application/json' \
--data-raw '{
  "taxId":"{cpfOfCustomer}" //Request a CPF or CNPJ from the Braza development team
}'
```
### End of cicle. That's All.
#### Any Questions open a issue.
### Other links
- [Flow Checkout v2 with document](flow-checkout-v2.md)
- [Additional requests](flow-checkout-v2-additional-request.md) NEW
- [Base Url by environment](base-url-by-environment.md) NEW