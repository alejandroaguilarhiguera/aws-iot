import json
import boto3
import time

iot_client = boto3.client('iot-data')

def lambda_handler(event, context):
    try:
        # 1. Carga el cuerpo de la petición
        message_body = json.loads(event['body'])
    except (TypeError, json.JSONDecodeError) as e:
        print(f"Error: Cuerpo de la petición inválido o ausente. {e}")
        return {
            'statusCode': 400, # Bad Request
            'body': json.dumps('Cuerpo de la petición inválido o ausente.')
        }
    
    # 2. Extrae el nombre del dispositivo y valida que exista
    thingName = message_body.get('thingName')
    if not thingName:
        return {
            'statusCode': 400,
            'body': json.dumps("El campo 'thingName' es requerido en el cuerpo de la petición.")
        }
    
    # 3. (Opcional pero recomendado) Remueve el thingName del payload final
    # para no enviar información redundante al dispositivo.
    # Esta línea se puede comentar si el dispositivo necesita saber su propio nombre.
    if 'thingName' in message_body:
        del message_body['thingName']

    # --- MEJORA PRINCIPAL: TEMA DINÁMICO ---
    # Crea un tema específico para los comandos de este dispositivo.
    # Esto evita que todos los dispositivos reciban todos los comandos.
    topic = f"devices/{thingName}/commands"
    
    payload_str = json.dumps(message_body)
    
    try:
        # 4. Publica el mensaje en el tema específico
        iot_client.publish(
            topic=topic,
            qos=1, # Calidad de Servicio 1 (At least once)
            payload=payload_str.encode('utf-8')
        )
        
        print(f"Mensaje publicado con éxito en el tema: {topic}")
        return {
           'statusCode': 200,
            'body': json.dumps({
                'message': 'Mensaje publicado con éxito!',
                'topic': topic,
                'payload_sent': message_body
            })
        }
    except Exception as e:
        print(f"Error al publicar mensaje IoT: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error interno al publicar en AWS IoT: {str(e)}")
        }