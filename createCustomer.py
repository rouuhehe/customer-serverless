import json
from time import time
import uuid
import boto3
from botocore.exceptions import ClientError
import bcrypt

def lambda_handler(event, context):
    try:
        if "body" in event:
            body = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
        else:
            body = event  

        customer_id = str(uuid.uuid4())
        password_hashed = bcrypt.hashpw(str(body['password']).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        now = str(int(time()))

        customer_data = {
            'customer_id': customer_id,
            'name': body['name'].lower(),
            'email': body['email'].lower(),
            'createdAt': now,
            'updatedAt': now,
            'isActive': True,
            'password_hashed': password_hashed,
            'phoneNumber': str(body['phone_number'])
        }

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_customers')
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