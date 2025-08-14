import uuid
import json
import requests
import boto3
import os
from datetime import datetime
from decimal import Decimal

iot_client = boto3.client('iot-data')
message_payload = {
    "pin": 16,
    "action": "open"
}
# Inicializa el cliente de DynamoDB.
# boto3 ya viene incluido en los runtimes de Python en Lambda.
dynamodb = boto3.resource('dynamodb')
table_name = 'actions' # Usa una variable de entorno para el nombre de la tabla
table = dynamodb.Table(table_name)


def json_serial(obj):
    """
    Función para serializar objetos no estándar a JSON.
    Extiende para manejar Decimal y datetime.
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        # Decide cómo quieres manejar los Decimales:
        # 1. Convertir a int si es un número entero exacto (ej. count, maxCount)
        if obj % 1 == 0:
            return int(obj)
        # 2. Convertir a float para números con decimales (ej. precios, etc.)
        else:
            return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def lambda_handler(event, context):
    params = event.get('queryStringParameters', {})
    uuid_to_find = params.get('code') if params else None
    try:
        if not uuid_to_find:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'UUID no proporcionado'})
            }
        response = table.get_item(
            Key={
                'uuid': uuid_to_find
            }
        )


        item = response.get('Item')

        if item:
            topic = "devices/" + item.get("thingName") +"/commands" 

            payload_str = json.dumps(message_payload)
            response = iot_client.publish(
                topic=topic,
                qos=1, # Calidad de Servicio: 0 (At most once) o 1 (At least once)
                payload=  payload_str.encode('utf-8') # El payload debe ser bytes
            )
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(item, default=json_serial) # ¡Usa 'default' aquí!
            }
        else:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'message': 'Code not found'})
            }
    except Exception as e:
        print(f"Error al leer el registro: {e}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'message': 'Error interno del servidor', 'error': str(e)})
        }