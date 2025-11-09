import json, boto3
from time import time
from botocore.exceptions import ClientError
from datetime import datetime

def lambda_handler(event, context):
        if "body" in event:
            body = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
        else:
            body = event  
         
        customer_id = body['customer_id']
        email = body['email']
        now = str(int(time()))

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_customers')

        try:
                response = table.update_item(
                    Key = {
                            'customerID': customer_id,
                            'email': email
                    },
                    UpdateExpression = "set isActive = :tilin , updatedAt = :v",
                    ExpressionAttributeValues = {
                            ':tilin': True,
                            ':v': now
                    },
                    ConditionExpression="attribute_exists(customerID)",
                    ReturnValues="UPDATED_NEW"
                )

                return {
                    'statusCode': 200,
                    'body': {
                        'message': 'Customer activated successfully'
                    }
                }
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return {
                      "statusCode": 404, 
                      "body": json.dumps({"error": "Customer not found"})
                }
            else:
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": str(e)})
                }