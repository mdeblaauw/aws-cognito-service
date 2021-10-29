import hmac
import hashlib
import base64


def secret_cognito_hash(
    username: str,
    cognito_client_id: str,
    cognito_secret: str
) -> str:
    """Secret hash that is required for the AWS Cognito
    API to approve messages in the requests.

    Args:
        username (str): The username of the client request.
        cognito_client_id (str): The Cognito pool client ID.
        cognito_secret (str): The Cognito pool client secret.

    Returns:
        str: The secret hash.
    """
    message = bytes(username + cognito_client_id, encoding='utf-8')
    key = bytes(cognito_secret, encoding='utf-8')

    secret_hash = base64.b64encode(
        hmac.new(
            key=key,
            msg=message,
            digestmod=hashlib.sha256
        ).digest()
    ).decode()

    return secret_hash
