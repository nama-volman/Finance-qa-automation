import uuid

import pytest

from api.base_api import rpc
from api.wallets_api import get_balance
from utilities import config


@pytest.mark.positive
@pytest.mark.api
def test_tokens_received(token_sender, token_receiver):
    print("Sender token (first 20 chars):  ", token_sender[:20])
    print("Receiver token (first 20 chars):", token_receiver[:20])

    assert token_sender.startswith("eyJ")
    assert token_receiver.startswith("eyJ")
    assert token_sender != token_receiver



@pytest.mark.positive
@pytest.mark.api
def test_read_sender_wallets(api_sender):
    response = api_sender.get("/rest/v1/wallets?select=currency,balance_minor")
    assert response.status == 200

    wallets = response.json()
    print("Sender wallets (balance in minor units):", wallets)

    assert len(wallets) > 0    # בודק שיש לפחות ארנק אחד


@pytest.mark.positive
@pytest.mark.api
def test_lookup_recipient_found(api_sender):
    response = rpc(api_sender, "lookup_recipient", {"p_email": config.EMAIL_NAAMA})
    assert response.status == 200

    result = response.json()[0]
    print("Recipient lookup result:", result)

    assert result["status"] == "found"
    assert result["email"] == config.EMAIL_NAAMA.lower()

# def test_receiver_fixture(receiver):
#     print(receiver["user_id"], receiver["preferred_currency"])

@pytest.mark.positive
@pytest.mark.api
def test_send_money_success(api_sender, api_receiver, receiver):
    wallets = api_sender.get("/rest/v1/wallets?select=currency,balance_minor&order=created_at.asc").json()
    funded = [w for w in wallets if w["balance_minor"] >= config.AMOUNT_TO_SEND]
    assert funded, f"Sender has no wallet with at least {config.AMOUNT_TO_SEND}: {wallets}"
    wallet = funded[0]
    print("\nSender wallet chosen for the transfer:", wallet)
    sender_before = wallet["balance_minor"]

    receiver_currency = receiver["preferred_currency"]
    receiver_before = get_balance(api_receiver, receiver_currency)

    print("\nSender balance BEFORE transfer:  ", sender_before, wallet["currency"], "(minor units)")
    print("\nReceiver balance BEFORE transfer:", receiver_before, receiver_currency, "(minor units)")

    quote_response = rpc(api_sender, "create_transfer_quote", {
        "p_recipient_id": receiver["user_id"],
        "p_sending_currency": wallet["currency"],
        "p_amount_minor": config.AMOUNT_TO_SEND,
        "p_input_side": "send",
    })
    assert quote_response.status == 200, quote_response.text()
    quote_result = quote_response.json()
    print("\nQuote created (valid for 60 seconds):", quote_result)

    assert quote_result["sending_amount_minor"] == config.AMOUNT_TO_SEND
    assert quote_result["sending_currency"] == wallet["currency"]
    assert quote_result["receiving_currency"] == receiver_currency
    assert quote_result["recipient_user_id"] == receiver["user_id"]

    execute_response = rpc(api_sender, "execute_transfer", {
        "p_quote_id": quote_result["quote_id"],
        "p_idempotency_key": str(uuid.uuid4()),
    })
    assert execute_response.status == 200, execute_response.text()
    transaction = execute_response.json()
    print("\nTransfer executed, transaction:", transaction)

    assert transaction["status"] == "completed"


    sender_after = get_balance(api_sender, wallet["currency"])
    receiver_after = get_balance(api_receiver, receiver_currency)
    print("\nSender balance AFTER transfer:  ", sender_after, wallet["currency"],
          f"(expected {sender_before} - {quote_result['sending_amount_minor']})")
    print("\nReceiver balance AFTER transfer:", receiver_after, receiver_currency,
          f"(expected {receiver_before} + {quote_result['receiving_amount_minor']})")

    assert sender_after == sender_before - quote_result["sending_amount_minor"]
    assert receiver_after == receiver_before + quote_result["receiving_amount_minor"]

    history = rpc(api_receiver, "list_my_transactions", {
        "p_direction": "received",
        "p_limit": 5,
    }).json()
    found = [t for t in history if t["id"] == transaction["id"]]
    print("\nTransfer found in receiver's history:", found)
    assert len(found) == 1, f"Transaction {transaction['id']} not in receiver's history"
    assert found[0]["receiving_amount_minor"] == quote_result["receiving_amount_minor"]


    notifications = api_receiver.get(
        f"/rest/v1/notifications?select=kind,amount_minor,currency"
        f"&transaction_id=eq.{transaction['id']}"
    ).json()
    print("\nReceiver notifications for this transfer:", notifications)
    assert len(notifications) == 1, f"Expected 1 notification, got: {notifications}"
    assert notifications[0]["kind"] == "payment_received"
    assert notifications[0]["amount_minor"] == quote_result["receiving_amount_minor"]
    assert notifications[0]["currency"] == receiver_currency


@pytest.mark.negative
@pytest.mark.api
def test_lookup_recipient_self(api_sender):
    response = rpc(api_sender, "lookup_recipient", {"p_email": config.EMAIL_YAEL})
    assert response.status == 200

    result = response.json()[0]
    print("\nSelf lookup result:", result)

    assert result["status"] == "self"
    assert result["user_id"] is None

@pytest.mark.negative
@pytest.mark.api
def test_lookup_recipient_not_registered(api_sender):
    response = rpc(api_sender, "lookup_recipient", {"p_email": config.NOT_REGISTERED_EMAIL})
    assert response.status == 200

    result = response.json()[0]
    print("\nNot-registered lookup result:", result)

    assert result["status"] == "not_found"
    assert result["user_id"] is None

@pytest.mark.negative
@pytest.mark.api
def test_lookup_recipient_invalid_email(api_sender):
    response = rpc(api_sender, "lookup_recipient", {"p_email": "not-an-email"})
    print("\nInvalid email lookup response:", response.status, response.text())

    assert response.status == 400
    assert response.json()["message"].startswith("INVALID_EMAIL")


@pytest.mark.negative
@pytest.mark.api
def test_quote_insufficient_funds(api_sender, receiver):
    # Step 1: choose a wallet (the first one the sender opened)
    wallets = api_sender.get(
        "/rest/v1/wallets?select=currency,balance_minor&order=created_at.asc"
    ).json()
    wallet = wallets[0]

    # Step 2: choose an amount based on this wallet - one more than its balance
    amount_too_big = wallet["balance_minor"] + 1

    # Step 3: try to create a quote from this wallet with the too-big amount
    quote_response = rpc(api_sender, "create_transfer_quote", {
        "p_recipient_id": receiver["user_id"],
        "p_sending_currency": wallet["currency"],
        "p_amount_minor": amount_too_big,
        "p_input_side": "send",
    })
    print(f"\nWallet {wallet['currency']} balance: {wallet['balance_minor']} trying to send: {amount_too_big}")
    print("Quote response:", quote_response.status, quote_response.text())

    # Step 4: the server must refuse because of insufficient funds
    assert quote_response.status == 400
    assert quote_response.json()["message"].startswith("INSUFFICIENT_FUNDS")
