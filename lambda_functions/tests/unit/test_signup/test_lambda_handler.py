import unittest
import json
from unittest.mock import patch
from signup.signup.handler import lambda_handler
from aws_lambda_powertools.utilities.parser import ValidationError


class TestLambdaHandler(unittest.TestCase):
    @patch('signup.signup.handler.signup')
    def test_lambda_handler_200_response(self, mock_signup):
        mock_signup.return_value = {
            'status_code': 200
        }

        response = lambda_handler(
            event={
                'path': '/api/sign-up',
                'httpMethod': 'POST',
                'body': json.dumps(
                    {
                        'username': 'mark@gmail.com',
                        'password': '1mMark!blaauw'
                    }
                )
            },
            context={}
        )

        self.assertEqual(response, {'status_code': 200})
        mock_signup.assert_called_once_with(
            username='mark@gmail.com',
            password='1mMark!blaauw'
        )

    @patch('signup.signup.handler.signup')
    def test_lambda_handler_invalid_password(self, mock_signup):
        mock_signup.return_value = {
            'status_code': 200
        }

        response = lambda_handler(
            event={
                'path': '/api/sign-up',
                'httpMethod': 'POST',
                'body': json.dumps(
                    {
                        'username': 'mark@gmail.com',
                        'password': 'mark'
                    }
                )
            },
            context={}
        )

        self.assertEqual(
            response,
            {
                "status_code": 400,
                "message": 'Invalid password'
            }
        )
        self.assertEqual(mock_signup.call_count, 0)

    @patch('signup.signup.handler.signup')
    def test_lambda_handler_invalid_email(self, mock_signup):
        mock_signup.return_value = {
            'status_code': 200
        }

        response = lambda_handler(
            event={
                'path': '/api/sign-up',
                'httpMethod': 'POST',
                'body': json.dumps(
                    {
                        'username': 'markgmail.com',
                        'password': '213Mar!aseas'
                    }
                )
            },
            context={}
        )

        self.assertEqual(
            response,
            {
                "status_code": 400,
                "message": 'Invalid email'
            }
        )
        self.assertEqual(mock_signup.call_count, 0)
