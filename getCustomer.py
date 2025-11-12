import json
import os
import boto3
def lambda_handler(event, context):
        body = event['body']
        customer_id = body['customer_id']
        table_name = os.environ["TABLE_NAME"]
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        response = table.get_item(
                Key = {
                    'customer_id': customer_id
                }
        )

        if 'Item' not in response:
            return {
                "statusCode": 404, 
                "body": json.dumps({"error": "Customer not found"})
            }
        
        return {
            'statusCode': 200,
            'body': {
                'customer': json.dumps(response['Item'])
            }
        }