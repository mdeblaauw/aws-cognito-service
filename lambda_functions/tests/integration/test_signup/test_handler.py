import unittest
import json
from signup.signup.handler import \
    lambda_handler


class TestLambdaHandler(unittest.TestCase):
    def test_lambda_handler(self):
        test_event = {
                'path': '/api/generate-image',
                'httpMethod': 'POST',
                'body': json.dumps(
                    {
                        'username': 'mark@gmail.com',
                        'password': '1mMark!blaauw'
                    }
                )
            }

        # out = lambda_handler(event=test_event, context={})
        # print(out)
