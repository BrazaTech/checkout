- [Return to readme](readme.md)
# Additional requests (optional)
- Request to
  - information about user of session
  - List of sales 
  
##### Note: All endpoint of operation are versioned, we start with v1 some else
#### Get information about user and configs of session
```bash
curl -L 'https://sandbox-authentication.brazacheckout.com.br/users/information/details' \
-H 'accept: application/json' \
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og' 
```
#### Response
```JSON
{
    "userFullName": "Angelo Sá de Oliveira dos Reis",
    "email": "angelo.reis@braza.com.br",
    "typeUser": 2, // 1 - Main Partner, 2 - Manager of BranchOffice, 3 - PDV, 4 - Accreditor Level
    "isAdmin": 1, //If is admin or not
    "partnerCod": "e872001c-8e96-4dd3-bbd4-8580e9c41eb3",
    "partnerName": "AVILAC INC",
    "accreditorName": "AVILAC",
    "accreditorId": "631a3e3d-a920-4c09-83e6-2b6ecd1bc05b",
    "filialCod": "4eec80cf-945b-460c-a1d2-e3ff7325821e",
    "filialName": "AVILAC (SEM DOCUMENTO)",
    "liquidationType": 2, //1 - Manual, 2 Automatic
    "flowType": 1, //0 - with Document, 1 - Without document
    "typeExternalCode": 1, //Number of transation or Invoice of partner
    "isExternalCodeEditable": true,
    "canAdminBranchSell": true, //Enable sell for user of session
    "language": "pt-br",
    "timeZone": "-03:00",
    "isSummerTime": false,
    "currencies": [ // array of currency enable for this store
        {
            "id": "1",
            "name": "Dolar Americano",
            "iso": "USD",
            "symbol": "US$",
            "flagPath": "https://flagcdn.com/us.png",
            "region": null
        }
    ],
    "paymentMethods": [ //array payment methods enable for this account
        {
            "cod": "f37c2967-7af6-4485-82ef-21bad38b2e5d",
            "name": "Pix",
            "isDisabled": false
        }
    ]
}
```
#### List a sales
List all sales of Store

#### Request
```bash
curl -L 'https://sandbox-sales.brazacheckout.com.br/v1/all?dateStart=2025-01-13&dateEnd=2025-01-14&offset=0' \
-H 'accept: application/json'
-H 'Authorization: Bearer eyJraWQiO <<.. Supressed Content..>> ASaygAXt8Og'
```
Where:
dateStart and dateEnd is range date of sales, offset to paginate data response

#### Response
```JSON
{
  "data": [
    {
      "id": "2b1e6e2a-184c-11ef-941b-0a58a9feac02",
      "identifier": "NF-1234567890",
      "clientName": "Michael Scott",
      "clientCPF": "***.999.999-**",
      "currency": "USDBRL",
      "amount": 151.75,
      "mdrValue": 1.75,
      "liquidValue": 868.34,
      "statusLabel": "Holding", //Expected values: success, holding and canceled
      "statusName": "Aguardando", //Expected values: Recebido, Processado, Aguardando, Expirado, Devolvido, Inválido
      "statusDescription": "O QR Code ainda não foi pago e o tempo de expiração ainda não foi alcançado.",
      "date": "2024-01-01",
      "time": "13:12:01",
      "statusId": 1,
      "isExchangeExecuted": 0, //Expected values: 0 or 1
      "executionMethod": 1, //Just for internal use of Braza Checkout
      "paymentMethod": "pix" 
    }
  ],
  "offset": 0,
  "totalItems": 1
}
```

#### List of sale by id (quotation id)
If the PIX query endpoint is no longer possible because it has expired, there is another endpoint for individual consultation by ID for the generated sale. 
Just use the quotation ID to check the details of this transaction.

#### Request
```bash
curl -L 'https://sandbox-sales.brazacheckout.com.br/v3/2b1e6e2a-184c-11ef-941b-0a58a9feac02' \
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
  "statusLabel": "Holding", //Expected values: success, holding and canceled
  "statusName": "Aguardando", //Expected values: Recebido, Processado, Aguardando, Expirado, Devolvido, Inválido
  "statusDescription": "O QR Code ainda não foi pago e o tempo de expiração ainda não foi alcançado.",
  "date": "2024-01-01",
  "time": "13:12:01",
  "statusId": 1,
  "isExchangeExecuted": 0, //Expected values: 0 or 1
  "executionMethod": 1, //Just for internal use of Braza Checkout
  "paymentMethod": "pix" 
}
```

# Webhook
### Notification REST
When configured for events to be sent via request, a **POST** will be made with the payloads informed below depending on each type of notification.
REST notifications can be configured with a ***Basic Header*** to be used as an authenticator.
Any return other than ***2XX will be considered an error when sending***.

Example of notification on webhook

#### OK PAYMENT:
```JSON
{
  "codQuote": "ad4e9ae4-e571-11ef-9b7f-0a58a9feac02",
  "status": "PAID"
}
```

#### NOT OK PAYMENT (REFUNDED):
```JSON
{
  "codQuote": "ad4e9ae4-e571-11ef-9b7f-0a58a9feac02",
  "status": "REFUNDED"
}
``` 

#### NOT OK PAYMENT (EXPIRED):
```JSON
{
  "codQuote": "ad4e9ae4-e571-11ef-9b7f-0a58a9feac02",
  "status": "EXPIRED"
}
```
