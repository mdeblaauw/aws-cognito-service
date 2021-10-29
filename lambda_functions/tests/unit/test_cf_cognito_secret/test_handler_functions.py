import os
import json
import unittest
import boto3
from moto import mock_s3, mock_secretsmanager
from cf_cognito_secret.cf_cognito_secret.handler import \
    create_secret, update_secret, delete_secret, \
    generate_secret_name


class TestHandlerFunctions(unittest.TestCase):
    mock_secret = mock_secretsmanager()

    @classmethod
    def setUpClass(cls):
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'

    def setUp(self):
        self.mock_secret.start()
        self.secret_client = boto3.client('secretsmanager')

    def tearDown(self):
        self.mock_secret.stop()

    def test_correct_create_secret(self):
        payload = {
            'userPoolId': '99999',
            'clientId': 'zweq',
            'clientSecret': '000000'
        }

        response = create_secret(
            payload=payload,
            secret_name='12345-abcdef',
            stack_name='dummy',
            secret_client=self.secret_client
        )

        response = self.secret_client.get_secret_value(
            SecretId='12345-abcdef'
        )

        self.assertEqual(
            payload,
            json.loads(response['SecretString'])
        )

    def test_correct_update_secret(self):
        payload = {
            'userPoolId': '99999',
            'clientId': 'zweq',
            'clientSecret': '000000'
        }

        response = create_secret(
            payload=payload,
            secret_name='12345-abcdef',
            stack_name='dummy',
            secret_client=self.secret_client
        )

        response = self.secret_client.get_secret_value(
            SecretId='12345-abcdef'
        )

        self.assertEqual(
            payload,
            json.loads(response['SecretString'])
        )

        payload_update = {
            'userPoolId': '99999',
            'clientId': 'zweq',
            'clientSecret': '111111'
        }

        update_secret(
            payload=payload_update,
            secret_name='12345-abcdef',
            stack_name='dummy',
            secret_client=self.secret_client
        )

        response_update = self.secret_client.get_secret_value(
            SecretId='12345-abcdef'
        )

        self.assertEqual(
            payload_update,
            json.loads(response_update['SecretString'])
        )

    def test_correct_delete_secret(self):
        payload = {
            'userPoolId': '99999',
            'clientId': 'zweq',
            'clientSecret': '000000'
        }

        response = create_secret(
            payload=payload,
            secret_name='12345-abcdef',
            stack_name='dummy',
            secret_client=self.secret_client
        )

        response = self.secret_client.get_secret_value(
            SecretId='12345-abcdef'
        )

        self.assertEqual(
            payload,
            json.loads(response['SecretString'])
        )

        delete_secret(
            secret_name='12345-abcdef',
            secret_client=self.secret_client
        )

        self.assertRaises(
            self.secret_client.exceptions.ResourceNotFoundException,
            self.secret_client.get_secret_value,
            SecretId='12345-abcdef'
        )

    def test_correct_generate_secret_name(self):
        stack_name = 'abc123'
        resource_id = '123abc'

        output = generate_secret_name(
            stack_name=stack_name,
            resource_id=resource_id
        )

        self.assertEqual(
            len(output),
            len(stack_name + resource_id) + 14
        )

        self.assertTrue(stack_name in output)
        self.assertTrue(resource_id in output)
