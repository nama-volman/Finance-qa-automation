import uuid

from api.base_api import rpc
from api.wallets_api import get_balance
from utilities import config


def test_tokens_received(token_yael, token_naama):
    print("Yael: ", token_yael[:20])
    print("Naama:", token_naama[:20])

    assert token_yael.startswith("eyJ")
    assert token_naama.startswith("eyJ")
    assert token_yael != token_naama



def test_read_yael_wallets(api_yael):
    response = api_yael.get("/rest/v1/wallets?select=currency,balance_minor")
    assert response.status == 200

    wallets = response.json()
    print(wallets)

    assert len(wallets) > 0    # בודק שיש לפחות ארנק אחד 


def test_lookup_recipient_found(api_yael):
    response = rpc(api_yael, "lookup_recipient", {"p_email": config.EMAIL_NAAMA})
    assert response.status == 200

    result = response.json()[0]
    print(result)

    assert result["status"] == "found"
    assert result["email"] == config.EMAIL_NAAMA.lower()

# def test_naama_fixture(naama):
#     print(naama["user_id"], naama["preferred_currency"])


def test_send_money_success(api_yael, api_naama, naama):
    wallets = api_yael.get("/rest/v1/wallets?select=currency,balance_minor").json()
    funded = [w for w in wallets if w["balance_minor"] >= config.AMOUNT_TO_SEND]
    assert funded, f"Yael has no wallet with at least {config.AMOUNT_TO_SEND}: {wallets}"
    wallet = funded[0]
    print(wallet)
    yael_before = wallet["balance_minor"]

    naama_currency = naama["preferred_currency"]
    naama_before = get_balance(api_naama, naama_currency)

    print("Yael before: ", yael_before, wallet["currency"])
    print("Naama before:", naama_before, naama_currency)

    quote_response = rpc(api_yael, "create_transfer_quote", {
        "p_recipient_id": naama["user_id"],
        "p_sending_currency": wallet["currency"],
        "p_amount_minor": config.AMOUNT_TO_SEND,
        "p_input_side": "send",
    })
    assert quote_response.status == 200, quote_response.text()
    quote_result = quote_response.json()
    print(quote_result)

    assert quote_result["sending_amount_minor"] == config.AMOUNT_TO_SEND
    assert quote_result["sending_currency"] == wallet["currency"]
    assert quote_result["receiving_currency"] == naama_currency
    assert quote_result["recipient_user_id"] == naama["user_id"]

    execute_response = rpc(api_yael, "execute_transfer", {
        "p_quote_id": quote_result["quote_id"],
        "p_idempotency_key": str(uuid.uuid4()),
    })
    assert execute_response.status == 200, execute_response.text()
    transaction = execute_response.json()
    print(transaction)

    assert transaction["status"] == "completed"

    
    yael_after = get_balance(api_yael, wallet["currency"])
    naama_after = get_balance(api_naama, naama_currency)
    print("Yael after: ", yael_after)
    print("Naama after:", naama_after)

    assert yael_after == yael_before - quote_result["sending_amount_minor"]
    assert naama_after == naama_before + quote_result["receiving_amount_minor"]