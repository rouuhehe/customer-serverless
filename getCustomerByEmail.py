import json, os, boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    try:
        body = event["body"]

        email = body.get("email")
        if not email:
            return {"statusCode": 400, "body": json.dumps({"error": "Email requerido"})}

        table_name = os.environ["TABLE_NAME"]
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)

        response = table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(email)
        )

        if not response.get('Items'):
            return {"statusCode": 404, "body": json.dumps({"error": "Customer not found"})}

        return {
            "statusCode": 200,
            "body": json.dumps({"customer": response['Items'][0]})
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
