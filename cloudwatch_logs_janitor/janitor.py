import os
from typing import Dict, Any

import boto3
from botocore.exceptions import ClientError

LambdaDict = Dict[str, Any]


class LambdaCognitoIdentity:
    cognito_identity_id: str
    cognito_identity_pool_id: str


class LambdaClientContextMobileClient:
    installation_id: str
    app_title: str
    app_version_name: str
    app_version_code: str
    app_package_name: str


class LambdaClientContext:
    client: LambdaClientContextMobileClient
    custom: LambdaDict
    env: LambdaDict


class LambdaContext:
    function_name: str
    function_version: str
    invoked_function_arn: str
    memory_limit_in_mb: int
    aws_request_id: str
    log_group_name: str
    log_stream_name: str
    identity: LambdaCognitoIdentity
    client_context: LambdaClientContext

    @staticmethod
    def get_remaining_time_in_millis() -> int:
        return 0


# TODO: Error handling if environment variable is empty or not type int
retention_in_days: int = int(os.getenv('RETENTION_IN_DAYS'))

logs = boto3.client('logs')
apigateway = boto3.client('apigateway')
aws_lambda = boto3.client('lambda')


def set_new_log_group_retention(event: LambdaDict, context: LambdaContext) -> None:
    log_group: str = event['detail']['requestParameters']['logGroupName']
    logs.put_retention_policy(logGroupName=log_group, retentionInDays=retention_in_days)

    print(f'Successfully update retention - logGroup: {log_group}, retention: {retention_in_days}')


def set_existing_log_groups_retention(event: LambdaDict, context: LambdaContext) -> None:
    token = ''
    while token is not None:
        response = logs.describe_log_groups(limit=50) if token == '' \
            else logs.describe_log_groups(limit=50, nextToken=token)
        for group in response['logGroups']:
            if 'retentionInDays' not in group:
                logs.put_retention_policy(logGroupName=group['logGroupName'], retentionInDays=retention_in_days)
                print(f'Successfully update retention - logGroup: {group["logGroupName"]}, retention: {retention_in_days}')

        token = response.get('nextToken')


def delete_log_groups(event: LambdaDict, context: LambdaContext) -> None:
    token = ''
    while token is not None:
        groups = logs.describe_log_groups(limit=50) if token == '' \
            else logs.describe_log_groups(limit=50, nextToken=token)

        for group in groups['logGroups']:
            log_group: str = group['logGroupName']

            if log_group.startswith('API-Gateway-Execution-Logs'):
                api_id = log_group.split('/')[0].split('_')[-1]
                stage = log_group.split('/')[-1]
                try:
                    apigateway.get_stage(restApiId=api_id, stageName=stage)
                except ClientError as e:
                    if e.response['Error']['Code'] == 'NotFoundException':
                        print(f'Found the log group to delete - logGroup: {log_group}')
                        logs.delete_log_group(logGroupName=log_group)
                    else:
                        print(f'Unexpected error: {e}')
                        raise e
                    
            if log_group.startswith('/aws/lambda/'):
                prefix_length = len('/aws/lambda/')
                function_name = log_group[prefix_length:]
                try:
                    aws_lambda.get_function(FunctionName=function_name)
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ResourceNotFoundException':
                        print(f'Found the log group to delete - logGroup: {log_group}')
                        logs.delete_log_group(logGroupName=log_group)
                    else:
                        print(f'Unexpected error: {e}')
                        raise e

        token = groups.get('nextToken')

    print('Finished log group deletion')
