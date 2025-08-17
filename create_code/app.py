import os
import uuid
import json
import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# Inicializa clientes de AWS
endpoint_url = "http://dynamodb-local:8000"  # Debe apuntar a tu DynamoDB Local
dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint_url)
if os.environ.get("LOCAL", "false").lower() == "true":
    dynamodb = boto3.resource("dynamodb", endpoint_url=endpoint_url)
else:
    dynamodb = boto3.resource("dynamodb", region_name=os.environ["AWS_REGION"])

# iot_client = boto3.client(
#     "iot",
#     region_name="us-east-1",
#     config=boto3.session.Config(connect_timeout=3, read_timeout=3)
# )

if os.environ.get("LOCAL", "false").lower() == "true":
    print("TODO: local iot")
    # iot_client = boto3.client("iot", endpoint_url="http://localhost:1234")
    iot_client = boto3.client("iot", region_name=os.environ["AWS_REGION"])

else:
    iot_client = boto3.client("iot", region_name=os.environ["AWS_REGION"])


# Nombre de la tabla desde variable de entorno
table_name = os.environ["TABLE_NAME"]
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    try:
        # 1. Leer y parsear el body
        message_body = json.loads(event.get("body", '{}'))
    except (TypeError, json.JSONDecodeError) as e:
        print(f"Error parseando el body: {e}")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Cuerpo de la petición inválido o ausente."})
        }

    # Validar que venga thingName
    thing_name = message_body.get("thingName")
    if not thing_name:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "El campo thingName es requerido."})
        }

    # 2. Verificar si el thingName existe en IoT Core
    try:
        iot_client.describe_thing(thingName=thing_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return {
                "statusCode": 404,
                "body": json.dumps({"error": f"El dispositivo {thing_name} no existe en IoT Core."})
            }
        else:
            print(f"Error consultando IoT Core: {e}")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "Error consultando IoT Core."})
            }

    # 3. Insertar en DynamoDB
    try:
        generated_uuid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        ttl_seconds = int((datetime.utcnow() + timedelta(days=7)).timestamp())

        item = {
            "id": generated_uuid,
            "thingName": thing_name,
            "count": 0,
            "createdAt": now,
            "updatedAt": now,
            "ttl": ttl_seconds
        }

        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Code created",
                "code": item
            })
        }

    except Exception as e:
        print(f"Error guardando en DynamoDB: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
