import uuid
import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

iot_client = boto3.client('iot-data')

message_payload = {
    "pin": 16,
    "action": "open"
}

# Inicializa el cliente de DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = 'actions'
table = dynamodb.Table(table_name)

def json_serial(obj):
    """Serializa objetos no estándar a JSON."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def lambda_handler(event, context):
    print("Evento recibido:", event)  # Log para depuración

    try:
        # Verificar que hay un body
        if not event.get("body"):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Body vacío"})
            }

        # Parsear el body (viene como string JSON)
        try:
            body_data = json.loads(event["body"])
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Body no es JSON válido"})
            }

        uuid_to_find = body_data.get("code")

        if not uuid_to_find:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "UUID no proporcionado"})
            }

        # Buscar en DynamoDB
        response = table.get_item(Key={"id": uuid_to_find})
        item = response.get("Item")

        if item:
            # Publicar mensaje en IoT Core
            topic = f"devices/{item.get('thingName')}/commands"
            payload_str = json.dumps(message_payload)
            iot_client.publish(
                topic=topic,
                qos=1,
                payload=payload_str.encode("utf-8")
            )

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(item, default=json_serial)
            }
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Code not found"})
            }

    except Exception as e:
        print(f"Error en Lambda: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Error interno del servidor", "error": str(e)})
        }
