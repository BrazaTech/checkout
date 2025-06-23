- [Return to readme](readme.md)
# Flow of Checkout v2
- Presenting a new release of the request flow in checkout v2.
- All operation operation are versioned, starting with v1.

## Step one POST (Login):
## PART 1
### Request
- Some informations is required at this moment: username and password
```bash
curl -L 'https://sandbox-authentication.brazacheckout.com.br/auth/login' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-d '{
  "username": "<YOUR_USERNAME_HERE>",
  "password": "<YOUR_PASSWORD_HERE>"
}'
```
### Response
```JSON
{
    "accessToken":"eyJraWQiO <<.. Suppressed Content..>> ASaygAXt8Og",
    "refreshToken":"eyJjdHki <<.. Suppressed Content..>> YIYb3YAyFN9u4F4V_m8R-w",
    "ttl": 3600,
    "username":"usernameSampleRegistered"
}
```
- In this case, save the accessToken and refreshToken, as they will be used in some requests in this flow.

## PART 2
### Request
Para que as configurações a respeito do seu usuário e loja sejam entendido, nos disponibilizamos um endpoint com estas informações

```bash
curl 'https://sandbox-authentication.brazacheckout.com.br/users/information/details' \
  -H 'accept: application/json' \
  -H 'authorization: Bearer <YOUR_ACCESS_TOKEN_HERE>'
```

```JSON
{
    "userFullName": "Angelo Sá de Oliveira dos Reis",
    "email": "angelo.reis@braza.com.br",
    "typeUser": 2,
    "isAdmin": 1,
    "canCancelSale": true,
    "flagCanRefund": false,
    "partnerCod": "e872001c-8e96-4dd3-bbd4-8580e9c41eb3",
    "partnerName": "AVILAC INC",
    "accreditorName": "AVILAC",
    "accreditorId": "631a3e3d-a920-4c09-83e6-2b6ecd1bc05b",
    "filialCod": "f0ded7a8-b33b-4470-bf87-f2c19efce95b",
    "filialName": "AVILAC INC [UAT] (COM DOCUMENTO)",
    "liquidationType": 2,
    "flowType": 0,
    "typeExternalCode": 2,
    "isExternalCodeEditable": true,
    "canAdminBranchSell": true,
    "isRefundEnabled": true,
    "showOptionalClientRegisterData": true,
    "salesListRefetchTime": 30000,
    "language": "pt-br",
    "timeZone": "-04:00",
    "isSummerTime": false,
    "currencies": [
        {
            "id": "1",
            "name": "Dolar Americano",
            "iso": "USD",
            "symbol": "US$",
            "flagPath": "https://flagcdn.com/us.png",
            "region": null
        },
        {
            "id": "3",
            "name": "Dolar Canadense",
            "iso": "CAD",
            "symbol": "C$",
            "flagPath": "https://flagcdn.com/ca.svg",
            "region": null
        },
        {
            "id": "4",
            "name": "Libra",
            "iso": "GBP",
            "symbol": "£",
            "flagPath": "https://flagcdn.com/gb.svg",
            "region": null
        },
        {
            "id": "2",
            "name": "Euro",
            "iso": "EUR",
            "symbol": "E$",
            "flagPath": "https://flagcdn.com/eu.png",
            "region": null
        }
    ],
    "paymentMethods": [
        {
            "cod": "f37c2967-7af6-4485-82ef-21bad38b2e5d",
            "name": "Pix",
            "isDisabled": false
        },
        {
            "cod": "ea3cfb07-670a-4180-a8b0-63f5ff68bb70",
            "name": "Cartão de Crédito",
            "isDisabled": false
        }
    ]
}
```

## Step two POST (Rates)
### Request to create a quotation
After saving some information from the login response, use the accessToken in the authorization header (JWT Authentication).

```bash
curl 'https://sandbox-rates.brazacheckout.com.br/v1/quotes' \
  -H 'accept: application/json' \
  -H 'authorization: Bearer <YOUR_ACCESS_TOKEN_HERE>' \
  -H 'content-type: application/json' \
  --data-raw '
  {
    "amount":155,
    "currency":"USDBRL",
    "externalId":"251989"
  }'
```
### Response of Quotes
```JSON
{
    "pix": {
        "id": "12413a8a-4c45-11f0-8dd2-0a58a9feac02",
        "fgnQuantity": "172.93",
        "brlQuantity": "1012.01",
        "quote": "5.83",
        "iof": "3.83",
        "iofPercentage": "0.38",
        "vet": "5.8521",
        "feesAmount": "0.00",
        "mdrPayer": 0.53,
        "partnerFee": 0.55,
        "withdrawalFee": 16.85
    },
    "credit_card": {
        "id": "1251f4a6-4c45-11f0-8dd2-0a58a9feac02",
        "fgnQuantity": "169.48",
        "quote": "5.83",
        "iof": "3.75",
        "iofPercentage": "0.38",
        "feesAmount": "0.00",
        "mdrPayer": 14.48,
        "partnerFee": 0,
        "withdrawalFee": 0,
        "installments": [
            {
                "installment": 1, <- Minimum installments accepted by Checkout 2.0
                "brlQuantity": 1080.04,
                "installmentValue": 1080.04,
                "amountFee": 88.22,
                "vet": 6.37
            },
            [...]
            {
                "installment": 12, <- Maximum installments accepted by Checkout 2.0
                "brlQuantity": 1155.02,
                "installmentValue": 96.25,
                "amountFee": 163.2,
                "vet": 6.82
            }
        ]
    },
    "internationalCard": {
        "id": "12413a8a-4c45-11f0-8dd2-0a58a9feac02",
        "brlQuantity": "1090.37",
        "iof": "31.76",
        "vet": "917.44",
        "feesAmount": "50.43",
        "partnerFee": 0.55,
        "withdrawalFee": 16.85
    }
}
```
After receiving the response, save the quotation code, in this case pix.id "12413a8a-4c45-11f0-8dd2-0a58a9feac02". This information is necessary to generate a PIX. Para que seja gerado pagamento via cartão de crédito, use a id que é fornecida na chave credit_card.id "12413a8a-4c45-11f0-8dd2-0a58a9feac02"

## Step Three GET (Customer)
### Request to validate a CPF (a official brazilian social number)
*Note: send X-CLIENT-CPF value masked*

```bash
curl -L 'https://sandbox-client.brazacheckout.com.br/v1' \
-H 'X-CLIENT-CPF: 999.999.999-99' \
-H 'Accept: application/json' \
-H 'authorization: Bearer <YOUR_ACCESS_TOKEN_HERE>'
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
- When our information bureau does not find enough data for customer validation, the endpoint returns the necessary fields within the pending fields. These fields are presented according to the needs for customer registration, generally it requests information regarding email, telephone/cell phone and address, confirm in the example below:
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
- First, the query below will be performed and we must pay attention to the following fields
  - The fields: cep (zip code), logradouro (street), bairro (neighborhood), cidade (city) and uf (state), are mandatory when requested
  - These fields will be in the pending array of the request prior to this one
- Another point, the paying customer must provide the zip code for the query to be performed

```bash
curl -X 'GET' \
  'https://sandbox-address.brazacheckout.com.br/v1/cep/66813-720' \
  -H 'accept: application/json'
```

The highlighted fields will be used in the next request, if they are in the pending field of the previous request (client validation)
```JSON
{
  "cep_indice": 66813420,
  "cep": "66813-420", -> required field
  "logradouro": "Rua Sargento Joaquim Resende", -> address
  "complemento": "", 
  "unidade": "",
  "bairro": "Campina de Icoaraci (Icoaraci)", -> neighborhood
  "localidade": "Belém", -> City
  "uf": "PA", -> state
  "estado": "Pará",
  "regiao": "Norte",
  "ibge": "1501402",
  "gia": "",
  "ddd": "91",
  "siafi": "0427"
}
```

The other fields in this answer above can be ignored!
Since we have the necessary values, we should enter them as follows in the example below:
```bash
curl -L -X PATCH 'https://sandbox-client.brazacheckout.com.br/v1' \
-H 'X-CLIENT-CPF: 999.999.999-99' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H 'authorization: Bearer <YOUR_ACCESS_TOKEN_HERE>' \
-d '{
  "cep": "66813-420",
  "state": "PA",
  "city": "Belém",
  "code": "1501402",
  "neighborhood": "Campina de Icoaraci (Icoaraci)",
  "address": "Rua Sargento Joaquim Resende",
  "number": "366",
  "complement": "",
  "phone": "+5599999999999",
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

# Here we will separate the payment process
Up until a certain point, checkout only had one payment method **(PIX)**, so let's introduce one more: **Credit Card**

## Payment Method: Credit Card
Now that we have the customer ID and the quote ID, let's go to session generation to then generate the payment for Credit Card.

### Apresentando a quantidade de parcelas disponíveis e suas taxas
Remember that when we made the quote we had two important fields **pix** and **credit_card**, right?
In the case of the credit card, we will use **credit_card**, so use this data to generate the number of installments that the customer can request! Therefore, when selecting **credit_card.installments**, you will have these values ​​here:

```JSON
{
    "installments": [
        {
                "installment": 1, <- Minimum installments accepted by Checkout 2.0
                "brlQuantity": 1080.04,
                "installmentValue": 1080.04,
                "amountFee": 88.22,
                "vet": 6.37
            },
            [...]
            {
                "installment": 12, <- Maximum installments accepted by Checkout 2.0
                "brlQuantity": 1155.02,
                "installmentValue": 96.25,
                "amountFee": 163.2,
                "vet": 6.82
            }
    ]
}
```
With these values, we can display it as follows:

```Typescript
`${credit_card.installments[x].installment}x R$ ${credit_card.installments[x].brlQuantity} (+ R$ ${credit_card.installments[x].amountFee} com juros) `
```
Okay, we have this information and we can put it on the front, which would be visually readable for the Brazilian consumer:

```bash
1x R$ 1080,04 (+ R$ 88,22 com juros)
```
In addition, we need to set aside two values ​​for another time. What needs to be set aside is: 
```Typescript
`${credit_card.installments[x].installment}`
```
and
```Typescript
`${credit_card.installments[x].brlQuantity}`
```

With this we will be able to...

### Create credit card payment session
```bash
curl 'https://sandbox-cc.brazacheckout.com.br/credit-card/session' \
  -H 'accept: application/json' \
  -H 'authorization: Bearer <YOUR_ACCESS_TOKEN_HERE>' \
  -d '{
        "codQuote": "12413a8a-4c45-11f0-8dd2-0a58a9feac02",
        "codCustomer": "67f84c46-1216-4240-986d-2bbcc1b6d80a",
        "numberOfInstallments": 12
    }'
```

Request response:
```json
{
    "uuid": "f005003d-06df-49ba-95c9-a54689a20dc1",
    "codClient": {
        "uuid": "ffb4d135-a834-40f2-9d8b-b641afe5657d",
        "name": "ANGELO SA DE OLIVEIRA DOS REIS",
        "email": "angelo.desenvolvedor@gmail.com",
        "cpf": "***.559.322-**",
        "cpfIndex": 99955932299,
        "motherName": "IZALENA LOPES DE SA",
        "phone": "(99) 99999-9999",
        "address": {
            "uuid": "3395d95d-fbd1-4a0e-866d-b66e96e6f366",
            "streetName": "WE 61",
            "number": 712,
            "complement": "CS A",
            "neighborhood": "Cidade Nova",
            "city": "Ananindeua",
            "state": "PA",
            "zipCode": "67140-030",
            "country": "Brasil",
            "countryCod": 55
        },
        "sex": 1,
        "birthday": "1988-05-20T03:00:00.000Z",
        "isComplete": true,
        "isActive": true,
        "isPendent": false,
        "dateActivateAt": "2025-06-11T03:00:00.000Z",
        "type": 0
    },
    "codQuote": "12413a8a-4c45-11f0-8dd2-0a58a9feac02",
    "installments": 12,
    "adyenIdentification": "CS18084609169ABD6D",
    "session": "Ab02b4c0!BQABAgAD5KaB6GKb0YaEv7IeIQA5rLYMfbac14tBXC<<..conteudo suprimido..>>XLODh3jmu6UCEc0981/TDo4or8",
    "amount": "1080.04",
    "codBranchOffice": "f0ded7a8-b33b-4470-bf87-f2c19efce95b",
    "codPartner": "e872001c-8e96-4dd3-bbd4-8580e9c41eb3",
    "expirationDate": "2025-06-23T23:13:53.000Z"
}
```
Well, armed with vital information to make the payment via credit card, we can see how the URL that the customer will access to make the payment is created:

### Building the Payment URL
In order to facilitate credit card integration with its partners, Checkout has created a specific page so that customers can fill in their credit card details. Therefore, we will need some information.

1 - We save two values ​​in the quote:
```Typescript
`${credit_card.installments[x].installment}`
```
and
```Typescript
`${credit_card.installments[x].brlQuantity}`
```

2 - In the session response we had a new record for the credit card, we will use the value that is in uuid **f005003d-06df-49ba-95c9-a54689a20dc1**
Okay, with this we can create our URL that will be sent to the end customer.

The structure is as follows:

```bash
https://:{ambiente-}app.brazacheckout.com.br/payment/cc-checkout/:{uuid}?brlQuantity=:{brlQuantity}&installments=:{installments}
```
#### The url will look like this with the values:
In sandbox:
```bash
https://sandbox-app.brazacheckout.com.br/payment/cc-checkout/f005003d-06df-49ba-95c9-a54689a20dc1?brlQuantity=16.4&installments=12
```
In production:
```bash
https://app.brazacheckout.com.br/payment/cc-checkout/f005003d-06df-49ba-95c9-a54689a20dc1?brlQuantity=16.4&installments=12
```
After that, the customer can make the payment by credit card.

### How to test?
For testing, we recommend using the Google Chrome plugin called [Adyen Test Cards](https://chromewebstore.google.com/detail/icllkfleeahmemjgoibajcmeoehkeoag?utm_source=item-share-cb). With this plugin, you can test credit cards in the application.

### Check status
Still with the credit card session uuid data, it is possible to obtain the payment status with the following request:

This request can be made every 5 seconds.
```bash
curl -L 'https://sandbox-cc.brazacheckout.com.br/credit-card/status/f005003d-06df-49ba-95c9-a54689a20dc1' \
  -H 'Accept: application/json' \
  -H 'authorization: Bearer <YOUR_ACCESS_TOKEN_HERE>'
```


The answer we have is this one:
#### Expired
```JSON
{
    "uuid": "f005003d-06df-49ba-95c9-a54689a20dc1",
    "codQuote": "bbcd796c-504e-11f0-a96a-0a58a9feac02",
    "codBranchOffice": "f0ded7a8-b33b-4470-bf87-f2c19efce95b",
    "codPartner": "e872001c-8e96-4dd3-bbd4-8580e9c41eb3",
    "session": "Ab02b4c0!BQABAgAD5KaB6GKb0YaEv7IeIQA5rLYMfbac14tBXC/<<... Content Supressed.. >>/XLODh3jmu6UCEc0981/TDo4or8",
    "adyenIdentification": "CS18084609169ABD6D",
    "amount": "1080.04",
    "installments": 12,
    "isApproved": false,
    "isCanceled": false,
    "dateApproved": null,
    "isFinalized": false,
    "dateFinalized": null,
    "pspReference": null,
    "expirationDate": "2025-06-23T23:13:53.000Z", <- look this field
    "isCaptured": false
}
```

#### Paid
```JSON
{
    "uuid": "f005003d-06df-49ba-95c9-a54689a20dc1",
    "codQuote": "bbcd796c-504e-11f0-a96a-0a58a9feac02",
    "codBranchOffice": "f0ded7a8-b33b-4470-bf87-f2c19efce95b",
    "codPartner": "e872001c-8e96-4dd3-bbd4-8580e9c41eb3",
    "session": "Ab02b4c0!BQABAgAD5KaB6GKb0YaEv7IeIQA5rLYMfbac14tBXC/<<... Content Supressed.. >>/XLODh3jmu6UCEc0981/TDo4or8",
    "adyenIdentification": "CS18084609169ABD6D",
    "amount": "1080.04",
    "installments": 12,
    "isApproved": true, <- Look this field
    "isCanceled": false,
    "dateApproved": null,
    "isFinalized": false,
    "dateFinalized": null,
    "pspReference": null,
    "expirationDate": "2025-06-23T23:13:53.000Z",
    "isCaptured": false
}
```


## Payment Method: PIX
Use this value of clientId and id on Rates request (with alias name codQuote) to generate our PIX:

### Request to Create a PIX
```bash
curl -L 'https://sandbox-pix.brazacheckout.com.br/v1/pix' \
-H 'Content-Type: application/json' \
-H 'Accept: application/json' \
-H 'authorization: Bearer <YOUR_ACCESS_TOKEN_HERE>' \
-d '{
  "codQuote": "6afd291c-1ae6-11f0-bcfe-0a58a9feac02",
  "codCustomer": "67f84c46-1216-4240-986d-2bbcc1b6d80a",
  "numberOfInstallments": 1 <- always 1 for pix
}'
```

### Response of PIX (success)
```JSON
{
    "expirationDate": "2025-06-18 13:32:48",
    "id": "e0c1c7ed-e638-4b9e-8d5b-4d0f991b2e87",
    "key": "a5480a17-6922-4606-ac18-f00a217ed771",
    "qrcode": "00020101021226990014br.gov.bcb.pix2577pix-h.bpp.com.br/23114447/qrs1/v2/01Cq4qJ7ywwVnuUI0NWOoCulKDO9XbY2GMCnSMST6y352040000530398654071012.015802BR5921BRAZA B S B DE CAMBIO6009SAO PAULO62070503***6304572B",
    "receiverFinancialInstitutionName": "FLAGSHIP INSTITUICAO DE PAGAMENTOS LTDA",
    "receiverName": "Braza Bank SA",
    "qrCodeImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARQAAAEUCAYA{{supressed content}}AAAASUVORK5CYII=",
    "status": "CREATED",
    "codPartner": "e872001c-8e96-4dd3-bbd4-8580e9c41eb3",
    "codBranchOffice": "f0ded7a8-b33b-4470-bf87-f2c19efce95b",
    "quantityBRL": "1012.01",
    "quantityFGN": "172.93",
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
    "expirationDate": "2025-06-18 13:32:48",
    "id": "e0c1c7ed-e638-4b9e-8d5b-4d0f991b2e87",
    "key": "a5480a17-6922-4606-ac18-f00a217ed771",
    "qrcode": "00020101021226990014br.gov.bcb.pix2577pix-h.bpp.com.br/23114447/qrs1/v2/01Cq4qJ7ywwVnuUI0NWOoCulKDO9XbY2GMCnSMST6y352040000530398654071012.015802BR5921BRAZA B S B DE CAMBIO6009SAO PAULO62070503***6304572B",
    "receiverFinancialInstitutionName": "FLAGSHIP INSTITUICAO DE PAGAMENTOS LTDA",
    "receiverName": "Braza Bank SA",
    "qrCodeImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAARQAAAEUCAYA{{supressed content}}AAAASUVORK5CYII=",
    "codQuote": "5e3d98c0-4c45-11f0-8dd2-0a58a9feac02",
    "status": "PENDING", // Possibles values: CREATED, PAID, PENDING, EXPIRED, REFUNDED
    "codPartner": "e872001c-8e96-4dd3-bbd4-8580e9c41eb3",
    "codBranchOffice": "f0ded7a8-b33b-4470-bf87-f2c19efce95b",
    "quantityBRL": "1012.01",
    "quantityFGN": "172.93",
    "currency": "USDBRL",
    "quoteValue": "5.83",
    "finalQuote": "5.83",
    "amountFee": "0.00",
    "iof": "3.83",
    "amountPixToPay": "1012.01",
    "iofPercentage": "0.38"
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