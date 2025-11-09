import json
import boto3
def lambda_handler(event, context):
        body = json.loads(event['body'])
         
        customer_id = body['customer_id']

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_customers')

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