


def rpc(api_context, function_name: str, params: dict):
    return api_context.post(f"/rest/v1/rpc/{function_name}", data=params)
