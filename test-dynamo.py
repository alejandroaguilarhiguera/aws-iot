import boto3

dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
table = dynamodb.Table("actions")

# Obtener un ítem por id
response = table.get_item(Key={'id': '123'})
item = response.get('Item')
print(item)

# Listar todos los registros
response = table.scan()
for item in response.get('Items', []):
    print(item)
