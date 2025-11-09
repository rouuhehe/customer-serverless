import json
from time import time
import boto3
from botocore.exceptions import ClientError

# en realidad no lo elimina solo lo oculta
def lambda_handler(event, context):
        if "body" in event:
            body = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
        else:
            body = event  
         
        customer_id = body['customer_id']
        now = str(int(time()))

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_customers')

        try:
                response = table.update_item(
                    Key = {
                            'customer_id': customer_id
                    },
                    UpdateExpression = "set isActive = :tilin , updatedAt = :v",
                    ExpressionAttributeValues = {
                            ':tilin': False,
                            ':v': now
                    },
                    ConditionExpression="attribute_exists(customer_id)",
                    ReturnValues="UPDATED_NEW"
                )

                return {
                    'statusCode': 200,
                    'body': {
                        'message': 'Customer deactivated successfully'
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