from playwright.sync_api import Playwright

from utilities import config


def get_token(playwright: Playwright, email: str, password: str) -> str:
        context = playwright.request.new_context(
        base_url=config.SUPABASE_URL,
        extra_http_headers={"apikey": config.SUPABASE_ANON_KEY},
    )

        response = context.post(
        "/auth/v1/token?grant_type=password",
        data={"email": email, "password": password},
    )
        assert response.status == 200, f"Login failed: {response.status} {response.text()}"

        token = response.json()["access_token"]
        context.dispose()
        return token



def create_api_context(playwright: Playwright, token: str):
    return playwright.request.new_context(
        base_url=config.SUPABASE_URL,
        extra_http_headers={
            "apikey": config.SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {token}",
        },
    )
