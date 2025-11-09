import json, boto3
from time import time
from botocore.exceptions import ClientError

def lambda_handler(event, context):
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('t_customers')

        # a diferencia de los otros lambdas, aqui los parametros vienen por pathParameters
        customer_id = event['pathParameters']['customerID']
        body = json.loads(event['body'])

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