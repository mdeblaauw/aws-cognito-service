import json
import boto3
import cfnresponse
import logging
from random import randint


def lambda_handler(
    event: dict,
    context: dict
) -> dict:
    cognito_client = boto3.client('cognito-idp')
    secret_manager_client = boto3.client('secretsmanager')

    userPoolId = event['ResourceProperties']['UserPoolId']
    appClientId = event['ResourceProperties']['AppClientId']
    stack_name = event['StackId'].split('/')[1]
    resource_id = event['LogicalResourceId']

    if event.get('RequestType', None) == 'Create':
        try:
            response = cognito_client.describe_user_pool_client(
                UserPoolId=userPoolId,
                ClientId=appClientId
            )

            secret_name = generate_secret_name(
                stack_name=stack_name,
                resource_id=resource_id
            )

            response_secret = create_secret(
                payload={
                    'userPoolId': userPoolId,
                    'clientId': appClientId,
                    'clientSecret': response['UserPoolClient']['ClientSecret']
                },
                secret_name=secret_name,
                stack_name=stack_name,
                secret_client=secret_manager_client
            )
        except Exception as e:
            logging.error(e)
            cfnresponse.send(
                event=event,
                context=context,
                responseStatus=cfnresponse.FAILED,
                responseData={
                    'Data': str(e)
                }
            )
            return None

        response_data = {
            'SecretArn': response_secret['ARN'],
            'SecretName': response_secret['Name'],
            'SecretVersionId': response_secret['VersionId']
        }
    elif event.get('RequestType', None) == 'Update':
        try:
            response = cognito_client.describe_user_pool_client(
                UserPoolId=userPoolId,
                ClientId=appClientId
            )
            print(event)

            update_secret(
                payload={
                    'userPoolId': userPoolId,
                    'clientId': appClientId,
                    'clientSecret': response['ClientSecret']
                },
                secret_name='dummy',
                stack_name=stack_name,
                event=event,
                context=context,
                secret_client=secret_manager_client
            )
        except Exception as e:
            logging.error(e)
            cfnresponse.send(
                event=event,
                context=context,
                responseStatus=cfnresponse.FAILED,
                responseData={
                    'Data': str(e)
                }
            )
        response_data = {
            'SecretArn': response['ARN'],
            'SecretName': response['Name'],
            'SecretVersionId': response['VersionId']
        }
    elif event.get('RequestType', None) == 'Delete':
        try:
            response = delete_secret(
                secret_name='dummy',
                secret_client=secret_manager_client
            )
        except Exception as e:
            logging.error(e)
            cfnresponse.send(
                event=event,
                context=context,
                responseStatus=cfnresponse.FAILED,
                responseData={
                    'Data': str(e)
                }
            )
        response_data = {
            'SecretArn': response['ARN'],
            'SecretName': response['Name']
        }
    else:
        cfnresponse.send(
            event=event,
            context=context,
            responseStatus=cfnresponse.FAILED,
            responseData={
                'Data': 'Unknown RequestType'
            }
        )

    cfnresponse.send(
        event=event,
        context=context,
        responseStatus=cfnresponse.SUCCESS,
        responseData=response_data
    )


def create_secret(
    payload: dict,
    secret_name: str,
    stack_name: str,
    secret_client
) -> dict:
    """Create a secret in AWS secret manager.

    Args:
        payload (dict): Dictionary with secret.
        secret_name (str): Name of the secret.
        stack_name (str): Name of the Cloudformation stack.
        secret_client ([type]): Secret manger SDK.

    Returns:
        dict: Response from secret manager SDK.
    """
    response = secret_client.create_secret(
        Name=secret_name,
        Description=(
            f'App client secret for app {payload["clientId"]} '
            f'of Cognito user pool {payload["userPoolId"]} for CF '
            f'stack {stack_name}'
        ),
        SecretString=json.dumps(payload),
    )
    return response


def update_secret(
    payload: dict,
    secret_name: str,
    stack_name: str,
    secret_client
) -> dict:
    """Update a secret in AWS secret manager.

    Args:
        payload (dict): The new secret to update the current secret with.
        secret_name (str): The name of the secret.
        stack_name (str): The name of the CloudFormation stack.
        secret_client ([type]): Secret manager SDK.

    Returns:
        dict: The response of the call to update the secret.
    """
    response = secret_client.update_secret(
        SecretId=secret_name,
        Description=(
            f'App client secret for app {payload["clientId"]} '
            f'of Cognito user pool {payload["userPoolId"]} for CF '
            f'stack {stack_name}'
        ),
        SecretString=json.dumps(payload)
    )

    return response


def delete_secret(
    secret_name: str,
    secret_client
) -> dict:
    """Delete a secret from AWS secret manager.

    Args:
        secret_name (str): The secret name.
        secret_client ([type]): Secret manager SDK.

    Returns:
        dict: Response from the SDK call.
    """
    response = secret_client.delete_secret(
        SecretId=secret_name,
        ForceDeleteWithoutRecovery=True
    )

    return response


def generate_secret_name(stack_name: str, resource_id: str) -> str:
    """Create unique name with random characters.

    Args:
        stack_name (str): Cloudformation stack name.
        resource_id (str): Name of resource in Cloudformation stack.

    Returns:
        str: Unique name.
    """
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    name_extension = ''.join(
        [
            characters[randint(0, len(characters)-1)]
            for i
            in range(12)
        ]
    )

    return f'{stack_name}-{resource_id}-{name_extension}'
