import json, uuid, boto3, os
from time import time
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    try:
        if "body" in event:
            body = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
        else:
            body = event  

        table_name = os.environ["TABLE_NAME"]
        customer_id = str(uuid.uuid4())
        now = str(int(time()))

        customer_data = {
            'customer_id': customer_id,
            'name': body['name'].lower(),
            'email': body['email'].lower(),
            'createdAt': now,
            'updatedAt': now,
            'isActive': True,
            'password_hashed': body['password'],
            'phoneNumber': str(body['phone_number'])
        }

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        table.put_item(Item=customer_data)

        return_data = {k: v for k, v in customer_data.items() if k != 'password_hashed'}

        return {
            'statusCode': 200,
            'body': {
                'customer': json.dumps(return_data)
                }
        }
    
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': str(e)
        }