import os
import json
import unittest
import boto3
from unittest.mock import patch
from moto import mock_cognitoidp, mock_secretsmanager
from signup.signup.handler import signup


class TestSignup(unittest.TestCase):
    mock_cognito = mock_cognitoidp()
    mock_secretsmanager = mock_secretsmanager()

    @classmethod
    def setUpClass(cls):
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'

    def setUp(self):
        self.mock_cognito.start()
        self.mock_secretsmanager.start()

        secret_client = boto3.client('secretsmanager')
        cognito_client = boto3.client('cognito-idp')

        pool_response = cognito_client.create_user_pool(
            PoolName='testing',
            Policies={
                'PasswordPolicy': {
                    'MinimumLength': 8,
                    'RequireUppercase': True,
                    'RequireLowercase': True,
                    'RequireNumbers': True,
                    'RequireSymbols': True,
                    'TemporaryPasswordValidityDays': 123
                }
            },
        )

        user_pool_id = pool_response['UserPool']['Id']

        pool_client = cognito_client.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName='testing2',
            GenerateSecret=True,
            ExplicitAuthFlows=['ALLOW_ADMIN_USER_PASSWORD_AUTH'],
        )

        self.client_id = pool_client['UserPoolClient']['ClientId']
        secret_string = json.dumps(
            {
                'userPoolId': user_pool_id,
                'clientId': self.client_id,
                'clientSecret': pool_client['UserPoolClient']['ClientSecret']
            }
        )
        self.secret_name = 'signup_testing'

        secret_client.create_secret(
            Name=self.secret_name,
            SecretString=secret_string
        )

    def tearDown(self):
        self.mock_cognito.stop()
        self.mock_secretsmanager.stop()

    def test_signup_200_response(self):
        with patch.dict(
            'signup.signup.handler.os.environ',
            {
                'secret_name': self.secret_name,
                'client_id': self.client_id
            }
        ):
            response = signup(
                username='mark@dummy.nl',
                password='markdeblaauw'
            )

        self.assertEqual(
            response,
            {
                "status_code": 200,
                "message": 'signup succesful'
            }
        )

    def test_signup_missing_secret_key(self):
        with patch.dict(
            'signup.signup.handler.os.environ',
            {
                'secret_name': 'no_name',
                'client_id': self.client_id
            }
        ):
            response = signup(
                username='mark@dummy.nl',
                password='markdeblaauw'
            )

        self.assertEqual(response['status_code'], 500)

    def test_signup_username_already_exist(self):
        with patch.dict(
            'signup.signup.handler.os.environ',
            {
                'secret_name': self.secret_name,
                'client_id': self.client_id
            }
        ):
            response1 = signup(
                username='mark@dummy.nl',
                password='markdeblaauw'
            )

            response2 = signup(
                username='mark@dummy.nl',
                password='markdeblaauw'
            )

        self.assertEqual(
            response1,
            {
                "status_code": 200,
                "message": 'signup succesful'
            }
        )

        self.assertEqual(
            response2,
            {
                "status_code": 400,
                "message": "This username already exists"
            }
        )
