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
  "amount": 150.75,
  "currency": "USDBRL",
  "externalId": "202501141131125"
}'
```
### Response of Quotes
```JSON
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
After receiving the response, save the quotation code, in this case, "2b1e6e2a-184c-11ef-941b-0a58a9feac02". This information is necessary to generate a PIX.

## Step Three POST (PIX)
### Request to Create a PIX
```bash
curl -L 'https://sandbox-pix.brazacheckout.com.br/v1/pix' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og' \
-d '{
  "codQuote": "2b1e6e2a-184c-11ef-941b-0a58a9feac02",
  "codCustomer": "",
  "numberOfInstallments": 1 <- always 1 on pix
}'
```

### Response of PIX (success)
```JSON
{
    "id": "1dc3c366-2417-4531-9c24-aa928b7add59",
    "key": "a5480a17-6922-4606-ac18-f00a217ed771",
    "qrcode": "00020101021226990014br.gov.bcb.pix2577pix-h.bpp.com.br/23114447/qrs1/v2/01iAwGlSpkZJPOJfjoMCKLGf2ZTk2lsgiOZu3l9DFlF52040000530398654071076.485802BR5921BRAZA B S B DE CAMBIO6009SAO PAULO62070503***63048296",
    "receiverName": "Braza Bank SA",
    "receiverFinancialInstitutionName": "FLAGSHIP INSTITUICAO DE PAGAMENTOS LTDA",
    "expirationDate": "2024-05-23T21:03:53.880Z",
    "status": "CREATED"
}
```
Now save the id, with the alias invoiceIdPix.

### Request GET status of pix
```bash
curl -L 'https://sandbox-pix.brazacheckout.com.br/v1/pix/1dc3c366-2417-4531-9c24-aa928b7add59/status' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og' 
```
This endpoint respose a same of response above, but, adding some fields, (codPartner and CodBranchOffice):

### Response of status of pix.
```JSON 
{
  "id": "b481b93b-01f3-4f8d-865b-a4b265ee6cf5",
  "key": "de31d0d0-129e-45e5-b7ed-2176b416c005",
  "qrcode": "00020101021226990014br.gov.bcb.pix2577pix-h.bpp.com.br/23114447/qrs1/v2/01YBsrpuoS8OhU1yq58aXQ9GeMHlDvdL7mL4AtzI7vK520400005303986540550.005802BR5921BRAZA B S B DE CAMBIO6009SAO PAULO62070503***6304BD9E",
  "receiverName": "Braza Bank SA",
  "receiverFinancialInstitutionName": "Flagship",
  "expirationDate": "2023-11-29T21:42:29.260Z",
  "status": "PENDING", // Possibles values: CREATED, PAID, PENDING, EXPIRED, REFUNDED
  "codPartner": "b481b93b-01f3-4f8d-865b-a4b265ee6cf5",
  "codBranchOffice": "b481b93b-01f3-4f8d-865b-a4b265ee6cf5",
  "amountPixToPay": "46.52",
  "quoteValue": "5.76",
  "amountFee": "0.49",
  "iof": "0.38",
  "iofPercentage": "0.2"
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