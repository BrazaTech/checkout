# Flow of Checkout v2

- presenting a new release of flow of request on checkout v2.
- All endpoint of operation are versioned, we start with v1 some else

## Step one POST (Login):
### Request
- Some informations are required at this moment username and password
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
- In this case we save accessToken and refreshToken, we use in some request on this flow

## Step two POST (Rates)
### Request to create a quotation
After we save a some information on response of login, use a accessToken on header authorization (JWT Authentication).

```bash
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
Now after we receive a response, save the code of quotation in this case "2b1e6e2a-184c-11ef-941b-0a58a9feac02". So, this information is necessary to generate a pix.

## Step Three GET (Customer)
### Request to validate a CPF (a official brazilian social number)
```bash
curl -L 'https://sandbox-client.brazacheckout.com.br/v1' \
-H 'X-CLIENT-CPF: 999.999.999-99' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og'
```
### Response of client (success)

```JSON
{
    "clientId": "67f84c46-1216-4240-986d-2bbcc1b6d80a",
    "enabled": true
}
```

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

### If have a pending information call this:
First we call

```bash
curl -L 'https://viacep.com.br/ws/66813420/json/'
```
use this some fields of this response on next request body:
```JSON
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

So we use this value of clientId and id on Rates request (with alias name codQuote) to generate our pix:

## Step Four POST (PIX)
### Request to Create a PIX

```bash
curl -L 'https://sandbox-pix.brazacheckout.com.br/v1/pix' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og' \
-d '{
  "codQuote": "2b1e6e2a-184c-11ef-941b-0a58a9feac02",
  "codCustomer": "67f84c46-1216-4240-986d-2bbcc1b6d80a"
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
Now save de id, with alias invoiceIdPix.

### Request GET status of pix
```bash
curl -L 'https://sandbox-pix.brazacheckout.com.br/v1/pix/1dc3c366-2417-4531-9c24-aa928b7add59/status' \
-H 'Accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og' 
```
This endpoint respose a same of response above, but, adding some fields, (codPartner and CodBranchOffice):

### Response of status of pix.
We have three status on response (CREATED, PAID, PENDING, EXPIRED, REFUND)
```JSON 
{
  "id": "b481b93b-01f3-4f8d-865b-a4b265ee6cf5",
  "key": "de31d0d0-129e-45e5-b7ed-2176b416c005",
  "qrcode": "00020101021226990014br.gov.bcb.pix2577pix-h.bpp.com.br/23114447/qrs1/v2/01YBsrpuoS8OhU1yq58aXQ9GeMHlDvdL7mL4AtzI7vK520400005303986540550.005802BR5921BRAZA B S B DE CAMBIO6009SAO PAULO62070503***6304BD9E",
  "receiverName": "Braza Bank SA",
  "receiverFinancialInstitutionName": "Flagship",
  "expirationDate": "2023-11-29T21:42:29.260Z",
  "status": "CREATED" | "PAID" | "PENDING" | "EXPIRED" | "REFUND",
  "codPartner": "b481b93b-01f3-4f8d-865b-a4b265ee6cf5",
  "codBranchOffice": "b481b93b-01f3-4f8d-865b-a4b265ee6cf5",
  "amountPixToPay": "46.52",
  "quoteValue": "5.76",
  "amountFee": "0.49",
  "iof": "0.38",
  "iofPercentage": "0.2"
}
```
### End of cicle. That's All. Thank you.

#### Any Questions open a issue.

### Track bonus - Accreditor, Partner and Branch Office information

#### Request of information of Partner
```bash
curl -L 'https://sandbox-api.brazacheckout.com.br/v1/partner/e5db089c-f1e8-47a3-9572-dd11dd47fd34' \
-H 'accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og' 
```

#### Response

```JSON
{
  "migrationId": "1234567890",
  "legalName": "Example & Partner Ltd.",
  "tradeName": "Store XYZ",
  "wpsAccountNumber": "99999.9999",
  "observations": "This partner requires an exception on ...",
  "description": "This partner is responsible for the sale of ...",
  "logoImageUrl": "https://domain.com/my/image.jpg",
  "address": {
    "uuid": "string",
    "streetName": "string",
    "number": 0,
    "city": "string",
    "countryCod": 0,
    "country": "string"
  },
  "accreditedFlag": true,
  "webhookId": "bd3638b8-798d-4245-bcfc-f91da3e527d6"
}
```

#### Request informations about accreditor by id
```bash
curl -L 'https://sandbox-api.brazacheckout.com.br/v1/accreditor/593facf1-93ad-42a0-8f37-1010f705c1d2' \
-H 'accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og'
```
#### Response
```JSON
{
  "id": "123e4567-e89b-12d3-a456-426655440000",
  "officialName": "Example & Partner Ltd",
  "displayName": "Braza On",
  "brazaAccountUk": "312",
  "relationshipManagerPartnerId": "1234567890",
  "internalDisclosure": "This partner requires an exception on ...",
  "logoPath": "https://domain.com/my/image.jpg",
  "aboutAccreditor": "This partner requires an exception on ...",
  "accreditorId": "123e4567-e89b-12d3-a456-426655440000",
  "typeContact": 0,
  "contentContact": "example@example.com",
  "flagDeleted": 0,
  "isDeleted": true
}
```

#### List a sales by Id
For this request we use a id of quotation to get a Sales information

#### Request
```bash
curl -L 'https://sandbox-sales.brazacheckout.com.br/v1/2b1e6e2a-184c-11ef-941b-0a58a9feac02' \
-H 'accept: application/json'
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og'
```
#### Response
```JSON
{
  "id": "2b1e6e2a-184c-11ef-941b-0a58a9feac02",
  "identifier": "NF-1234567890",
  "clientName": "Michael Scott",
  "clientCPF": "***.999.999-**",
  "currency": "USDBRL",
  "amount": 151.75,
  "mdrValue": 1.75,
  "liquidValue": 868.34,
  "statusLabel": "Holding",
  "statusName": "Aguardando",
  "statusDescription": "O QR Code ainda não foi pago e o tempo de expiração ainda não foi alcançado.",
  "date": "2024-01-01",
  "time": "13:12:01"
}
```
