import unittest
import hmac
from lambda_utils.secret_hash import secret_cognito_hash


class TestSecretHash(unittest.TestCase):
    def test_secret_cognito_hash_output(self):
        username = 'mark@dummy.com'
        client_id = 'ab123'
        secret = '123ab'

        output_hash = secret_cognito_hash(
            username=username,
            cognito_client_id=client_id,
            cognito_secret=secret
        )

        self.assertIsInstance(output_hash, str)
