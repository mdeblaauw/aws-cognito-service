import os
import unittest
import boto3
from unittest.mock import patch
from copy import copy
from moto import mock_secretsmanager, mock_cognitoidp
from cf_cognito_secret.cf_cognito_secret.handler import \
    lambda_handler


class TestLambdaHandler(unittest.TestCase):
    mock_secret = mock_secretsmanager()
    mock_cognito = mock_cognitoidp()

    @classmethod
    def setUpClass(cls):
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'

        cls.update_event = {

        }

        cls.delete_event = {

        }

    def setUp(self):
        self.mock_secret.start()
        self.mock_cognito.start()

        client_cognito = boto3.client('cognito-idp')

        user_pool_id = client_cognito.create_user_pool(
            PoolName='first'
        )['UserPool']['Id']
        client_id = client_cognito.create_user_pool_client(
            UserPoolId=user_pool_id,
            ClientName='second',
            GenerateSecret=True
        )['UserPoolClient']['ClientId']

        self.create_event = {
            'RequestType': 'Create',
            'ResponseURL': 'dummy',
            'StackId': 'asddasd/uberStack/12323',
            'ResourceType': 'Custom:CustomResource',
            'LogicalResourceId': 'MyCustomResource',
            'ResourceProperties': {
                'UserPoolId': user_pool_id,
                'AppClientId': client_id
            }
        }

    def tearDown(self):
        self.mock_secret.stop()
        self.mock_cognito.stop()

    @patch('cf_cognito_secret.cf_cognito_secret.handler.cfnresponse')
    @patch('cf_cognito_secret.cf_cognito_secret.handler.logging.error')
    def test_correct_handler_create_secret(
        self,
        mock_logging,
        mock_cfnresponse
    ):
        lambda_handler(
            event=self.create_event,
            context={}
        )

        mock_cfnresponse.send.assert_called_once()
        mock_logging.assert_not_called()

    @patch('cf_cognito_secret.cf_cognito_secret.handler.cfnresponse')
    @patch('cf_cognito_secret.cf_cognito_secret.handler.logging.error')
    def test_exception_handler_create_secret(
        self,
        mock_logging,
        mock_cfnresponse
    ):
        event = copy(self.create_event)
        event['ResourceProperties']['UserPoolId'] = 'wrong'

        lambda_handler(
            event=event,
            context={}
        )

        mock_logging.assert_called_once()
