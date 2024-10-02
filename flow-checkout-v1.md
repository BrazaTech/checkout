- [Return to readme](readme.md)
# [Checkout BFF] Implementation guide [Deprecated]

## This version is locked to new integrators. [See version 2.0](flow-checkout-v2.md)

### Step by Step of Checkout
- Request /auth/login
``` SH
curl --location --request POST 'https://sandbox.bff.checkout.cloudbreak.com.br/auth/login' \
--header 'Authorization: Basic YW5nZWxvL...F3IUBRV2Fzcg=='
```
- Response of /auth/login
``` JSON
{
    "status": 200,
    "data": {
        "access_token": "eyJhbGciO...{{ Suppressed Content }}...7tQSaFKFw",
        "refresh_token": "qvm92ovkeNTw...{{ Suppressed Content }}...fdMV1N70A1",
        "ttl": 3600,
        "seller_cashier_name": "ANGELO REIS"
    },
    "errors": []
}
```
Now a developer need storage this values: **access_token** and **refresh_token**.

### Load data of Partner/Store
- Request [**REQUIRED**] /seller/info
``` SH
curl --location 'https://sandbox.bff.checkout.cloudbreak.com.br/seller/info' \
--header 'Authorization: Bearer {{content of access_token}}'
```

- Response of /seller/info 
``` JSON
{
    "status": 200,
    "data": {
        "checkout_history": [],
        "seller_data": {
            "id": 124,
            "name": "LOJA DE TEST",
            "email": "minhaloja-teste@braza.com.br",
            "dayLimit": 10000,
            "currencies": [
                {
                    "country": "en-US",
                    "id": 2,
                    "iso": "USD",
                    "img_country": "assets/images/bandeiras/united-states-of-america.png",
                    "name": "Dólar",
                    "symbol": "US$"
                }
            ],
            "ttl_pix": 1500,
            "ttl_quote": 900,
            "isInvoiceMdr": true,
            "isListMdr": true,
            "mdr": {
                "partner": {
                    "fixed": "1.00",
                    "percentage": "0.00",
                    "maximum": "999999.99",
                    "minimum": "0.00"
                },
                "client": {
                    "fixed": "2.00",
                    "percentage": "0.00",
                    "maximum": "999999.99",
                    "minimum": "0.00"
                }
            }
        }
    },
    "errors": []
}
```
The first request of the day, "checkout_history" will be an empty array, as sales progress it will be increased with information. In addition to other information such as currencies available for use and MDR data.

### Quotation

First we must make a quote to find out how much the customer will pay in the foreign currency selected at the cash register.

- Request /quotation/simulate
``` SH
curl --location --request PUT 'https://sandbox.bff.checkout.cloudbreak.com.br/quotation/simulate' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{content of access_token}}' \
--data '{
    "amount": 15.00,
    "currency_id": 2,
    "transaction": "202311TQASS155254"
}'
```

- "amount" is the total foreign currency that will be quoted
- "currency_id" for each item in the seller/info currencies there is an id, whatever is available in your registration is to be used in this parameter
- "transaction" of the partner's internal control, it can be the Invoice or Store Order number

- Response  /quotation/simulate
``` JSON
{
    "status": 201,
    "data": {
        "id": "80fe7c82-8007-11ee-aa39-02420a0a001a",
        "currency": "USDBRL",
        "quote": 5.1555,
        "preview_receipt": {
            "BRLquantity": 88.86,
            "FGNquantity": 17,
            "iof": 0.34,
            "fees": 0.88
        },
        "credit_card": {
            "BRLquantity": 96.98,
            "FGNquantity": 17,
            "iof": 5.82,
            "fees": 3.51
        },
        "mdr": 2
    },
    "errors": []
}
```
This response we can store the id [standard UUID v4] of the generated quote. It will be useful in the next request. If you want to show the customer when the value will be most profitable, show the preview_receipt and credit_card values, the first is how much will be on the pix and the second on the credit card. **Attention: MDR is a value only for the retailer, dont show this**.

To gain customer trust, a comparison of values ​​can be made using the Brazilian quick transfer method (PIX) and the traditional international credit card. use the **preview_receipt** and **credit_card** fields for this comparison.

- Request /client/validate
``` SH
curl --location 'https://sandbox.bff.checkout.cloudbreak.com.br/client/validate' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{content of access_token}}' \
--data '{
    "cpf": "77257537100",
    "quotation_id": "80fe7c82-8007-11ee-aa39-02420a0a001a"
}'
```

In the body of this request we will inform two unique parameters, **cpf** and **quotation_id**, the same id that we received in the previous request (see /quotation/simulate).

- Response /client/validate
``` JSON
{
    "status": 200,
    "data": {
        "founded": true,
        "has_limit": true,
        "daily_limit": true,
        "blocked": false,
        "is_valid": true,
        "already_registered": true,
        "toUpdate": false,
        "clientLiveInBrazil": true
    },
    "errors": []
}
```

founded is a typo, o correct has found... still with founded

If these fields return as they are, you can proceed to the next step (customer validation)

- Request pix/generate
```SH
curl --location --request PUT 'https://sandbox.bff.checkout.cloudbreak.com.br/pix/generate' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {{content of access_token}}' \
--data '{
    "cpf": "77257537100",
    "quotation_id": "80fe7c82-8007-11ee-aa39-02420a0a001a"
}'
```

We still have the same data as the previous request, we just changed the endpoint, in this one we are generating the pix.

## Only make this call if the response to the previous request is the same as the example.

- Response pix/generate
``` JSON
{
    "status": 200,
    "data": {
        "pix_id": 11421,
        "qrcode_content": "00020101021226990014br.gov.bcb.pix2577pix-h.bpp.com.br/23114447/qrs1/v2/01MFOIItMCerNqHRYXIQmcXA7Tof1UVZrH7sF53n5DZ520400005303986540588.865802BR5921BRAZA B S B DE CAMBIO6009SAO PAULO62070503***6304131E",
        "ttl": 1500,
        "expire_at": "2023-11-10T21:37:44.598Z",
        "image_url": "https://api-sandbox.brazabank.com.br/v1/pix/payments/11421/qr/f12395a0f00b264329a3cbf6?no-cache=142292398",
        "name": "ADRIANO DA SILVA MATIAS FONSECA",
        "doc": "***.575.371-**",
        "transaction": "202311TQASS155254-Ferneda"
    },
    "errors": []
}
```

- qrcode_content is the content of the Qr Code, which can be used in copy and paste
- expire_at is when the pix will expire (25 minutes)
- image_url is qr-code image

With this information you can set up the pix payment screen via QR-Code.

Now we need to know if this pix was paid, remember that we saved the quote ID, it was used in two previous endpoints, so it is still useful for this query below:

- Request consult/pix/{{quotation_id}}
```SH
curl --location 'https://sandbox.bff.checkout.cloudbreak.com.br/pix/consult/80fe7c82-8007-11ee-aa39-02420a0a001a' \
--header 'Authorization: Bearer {{content of access_token}}' \
```

- Reponse consult/pix/{{quotation_id}} when not paid
``` JSON
{
    "pix_id": 11421,
    "pix_status": null,
    "pix_uuid": "d09d0820-800d-11ee-be96-0242c0a85017",
    "external_id": "202311TQASS155254-Ferneda",
    "amount": 88.86
}
```

- Reponse consult/pix/{{quotation_id}} When Paid
``` JSON
{
    "pix_id": 11421,
    "pix_status": "paid",
    "pix_uuid": "d09d0820-800d-11ee-be96-0242c0a85017",
    "external_id": "202311TQASS155254-Ferneda",
    "amount": 88.86
}
```

- pix_status if it is paid it will be "paid" otherwise it is null,
- pix_uuid id pix,
- external_id is the order or NF ID passed in the quote request
- amount is the total





