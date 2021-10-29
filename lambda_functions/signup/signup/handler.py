import os
import re
import boto3
import botocore.exceptions
import logging
from lambda_utils import secret_cognito_hash
from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.parser import BaseModel, parse, \
    ValidationError, validator
from pydantic import EmailStr


class Credentials(BaseModel):
    """Event request clase.
    """
    username: EmailStr
    password: str

    @validator('password')
    def password_minimal_length(cls, value: str) -> str:
        """Validation for supplied password.

        Args:
            value ([str]): Password value.

        Raises:
            ValueError: If password does not satisfies the
                constraints.

        Returns:
            [str]: Password value.
        """
        match = re.search(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,32}$',
            value
        )
        if not match:
            raise ValueError('Invalid password')

        return value


def lambda_handler(
    event: dict,
    context: dict
) -> dict:
    """Event handler to process incoming requests for
    signing up.

    Args:
        event (dict): Request information from the client.
        context (dict): Runtime information from the Lambda
            function.

    Returns:
        dict: Response of the request.
    """
    parsed_event = APIGatewayProxyEvent(event)
    try:
        parsed_body: Credentials = parse(
            event=parsed_event.body,
            model=Credentials
        )
    except ValidationError as e:
        for an_error in e.errors():
            if an_error['msg'] == 'Invalid password':
                return {
                    "status_code": 400,
                    "message": 'Invalid password'
                }
            elif an_error['type'] == 'value_error.email':
                return {
                    "status_code": 400,
                    "message": 'Invalid email'
                }
        return {
            "status_code": 400,
            "message": "Invalid request"
        }

    return signup(
        username=parsed_body.username,
        password=parsed_body.password
    )


def signup(username: str, password: str) -> dict:
    """Signs up a user into a Cognito pool.

    Args:
        username (str): The username of the client.
        password (str): The password of the client.

    Returns:
        dict: Response on the request.
    """
    secret_client = boto3.client('secretsmanager')
    cognito_client = boto3.client('cognito-idp')

    # Retrieve the Cognito secret for hash secret
    try:
        cognito_secret = secret_client.get_secret_value(
            SecretId=os.environ['secret_name'],
        )['SecretString']
    except Exception as e:
        logging.error(e)
        return {
            "status_code": 500,
            "message": "An internal error has occurered"
        }

    try:
        response = cognito_client.sign_up(
            ClientId=os.environ['client_id'],
            SecretHash=secret_cognito_hash(
                username=username,
                cognito_client_id=os.environ['client_id'],
                cognito_secret=cognito_secret
            ),
            Username=username,
            Password=password,
        )
    except cognito_client.exceptions.UsernameExistsException as e:
        return {
            "status_code": 400,
            "message": "This username already exists"
        }
    except cognito_client.exceptions.InvalidPasswordException as e:
        return {
            "status_code": 400,
            "message": "Invalid password"
        }
    except cognito_client.exceptions.UserLambdaValidationException as e:
        return {
            "status_code": 400,
            "message": "This email already exists"
        }
    except Exception as e:
        logging.error(e)
        return {
            "status_code": 400,
            "message": str(e)
        }
    return {
        "status_code": 200,
        "message": 'signup succesful'
    }
