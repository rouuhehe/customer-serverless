import base64
import hashlib
import hmac
import json
import os
from time import time
import boto3
from botocore.exceptions import ClientError

SECRET_KEY = os.environ["JWT_SECRET"]

def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)

def verify_token(token):
    try:
        header_b64, body_b64, signature = token.split(".")
        expected_sig = b64url_encode(
            hmac.new(SECRET_KEY.encode(), f"{header_b64}.{body_b64}".encode(), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(expected_sig, signature):
            return None
        payload = json.loads(b64url_decode(body_b64))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except:
        return None

# en realidad no lo elimina solo lo oculta
def lambda_handler(event, context):
    headers = event.get("headers", {})
    auth = headers.get("authorization") or headers.get("Authorization") or ""
    if not auth.startswith("Bearer "):
        return {"statusCode": 401, "body": "missing token"}
    token = auth.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        return {"statusCode": 401, "body": "invalid token"}        

    if user.get("tenant_id"):
        if user.get("role") != "manager":
            return {"statusCode": 403, "body": "forbidden"}

    if "body" in event:
        body = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
    else:
        body = event  
    table_name = os.environ["TABLE_NAME"]
    customer_id = body['customer_id']
    now = str(int(time()))

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

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

        log_info = {
            "action": "deactivate_customer",
            "customer_id": customer_id,
            "performed_by": user.get("staff_id") if user.get("role") == "manager" else customer_id,
            "timestamp": now
        }

        print("INFO:", log_info)

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