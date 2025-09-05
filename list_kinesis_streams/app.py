import json
import boto3
import os
from datetime import datetime

kinesis_client = boto3.client("kinesisvideo", region_name=os.environ.get("AWS_REGION", "us-east-1"))

def default_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def lambda_handler(event, context):
    try:
        print("Evento recibido:", json.dumps(event))

        response = kinesis_client.list_streams(MaxResults=50)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(
                {"streams": response.get("StreamInfoList", [])},
                default=default_serializer
            )
        }

    except Exception as e:
        print("Error en Lambda:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }