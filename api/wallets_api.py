def get_balance(api_context, currency: str) -> int:
    wallets = api_context.get(
        f"/rest/v1/wallets?select=balance_minor&currency=eq.{currency}"
    ).json()
    return wallets[0]["balance_minor"]