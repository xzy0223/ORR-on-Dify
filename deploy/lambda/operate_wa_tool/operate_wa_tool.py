import json
import boto3
import os
import secrets
from botocore.exceptions import ClientError

# Initialize the Well-Architected Tool client
wellarchitected = boto3.client('wellarchitected')

def lambda_handler(event, context):
    # Determine the HTTP method and path
    http_method = event['httpMethod']
    path = event['path']
    
    print(event)
    
    if http_method == 'POST' and path == '/workload':
        return create_workload(event)
    elif http_method == 'PUT' and path == '/workload/review':
        return update_workload_review(event)
    else:
        return {
            'statusCode': 404,
            'body': json.dumps('Not Found')
        }

def create_workload(event):
    try:
        # Parse the request body
        body = json.loads(event['body'])
        
        # Extract workload details from the request
        workload_name = body['workloadName']
        description = body.get('description', '')
        environment = body.get('environment', 'PRODUCTION')
        lenses = body.get('lenses', '')
        client_request_token = body.get('clientRequestToken', secrets.token_hex(8))
        review_owner = body.get('reviewOwner', 'testuser')
        
        # Create the workload
        response = wellarchitected.create_workload(
            WorkloadName=workload_name,
            Description=description,
            Environment=environment,
            Lenses=lenses,
            ReviewOwner=review_owner,
            ClientRequestToken=client_request_token,
            AwsRegions=["us-east-1"]
        )
        
        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Workload created successfully',
                'workloadId': response['WorkloadId']
            })
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

def update_workload_review(event):
    try:
        # Parse the request body
        body = json.loads(event['body'])
        
        # Extract review details from the request
        workload_id = body['workloadId']
        lens_alias = body['lensAlias']
        question_id = body['questionId']
        choice_updates = body['choiceUpdates']
        
        print(choice_updates.get('selectedChoices', []))
        
        # Update the workload review
        response = wellarchitected.update_answer(
            WorkloadId=workload_id,
            LensAlias=lens_alias,
            QuestionId=question_id,
            SelectedChoices=choice_updates.get('selectedChoices', []),
            Notes=choice_updates.get('notes', '')
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Workload review updated successfully',
                'answer': response['Answer']
            })
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
