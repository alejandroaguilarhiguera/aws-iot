import json
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Función Lambda para obtener todos los dispositivos (Things) de AWS IoT Core.
    """
    # Inicializa el cliente de Boto3 para IoT
    iot_client = boto3.client('iot')
    
    # Lista para almacenar todos los dispositivos encontrados
    all_things = []
    
    try:
        # Crea un paginador para la operación list_things
        paginator = iot_client.get_paginator('list_things')
        
        # Itera sobre cada página de resultados
        for page in paginator.paginate():
            all_things.extend(page['things'])
            
        # Prepara la respuesta exitosa
        response = {
            'statusCode': 200,
            'body': json.dumps(all_things),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
    except ClientError as e:
        # Maneja errores específicos de Boto3/AWS
        print(f"Error de cliente de AWS: {e}")
        response = {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
    except Exception as e:
        # Maneja cualquier otro error inesperado
        print(f"Error inesperado: {e}")
        response = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Ocurrió un error interno.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
    return response