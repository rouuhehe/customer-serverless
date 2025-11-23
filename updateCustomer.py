import base64
import hashlib
import hmac
import json, boto3, os
from time import time
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
    table_name = os.environ["TABLE_NAME"]
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # a diferencia de los otros lambdas, aqui los parametros vienen por pathParameters
    customer_id = event['pathParameters']['customerID']
    body = event['body']

    allowed = ['name', 'email', 'phoneNumber', 'password']
    update_fields = {k: v for k, v in body.items() if k in allowed}
    now = str(int(time()))

    if not update_fields:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No valid fields to update"})
        }

    # Ejemplo con email
    # set email = :email, updatedAt = :updatedAt
    expression = "set " + ", ".join(f"{k} = :{k}" for k in update_fields.keys())
    expression += ", updatedAt = :updatedAt"

    exp_attr_values = {f":{k}": v for k, v in update_fields.items()}
    exp_attr_values[':updatedAt'] = now
    try:
        response = table.update_item(
                Key={
                    'customerID': customer_id
                },
                UpdateExpression=expression,
                ExpressionAttributeValues=exp_attr_values,
                ConditionExpression="attribute_exists(customerID)",
                ReturnValues="ALL_NEW"
            )
        
        return {
                "satusCode": 200,
                "body": json.dumps({"customer": response['Attributes']})
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