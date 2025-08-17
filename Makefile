# Variables
PROFILE=default
EVENTS_DIR=events
DDB_CONTAINER=dynamodb-local
DDB_PORT=8000
TABLE_NAME=actions

# -----------------------------
# DynamoDB Local
# -----------------------------

# Levantar DynamoDB Local
start-dynamodb:
	# Si el contenedor ya existe, lo reinicia; si no, lo crea
	docker ps -a | grep $(DDB_CONTAINER) >/dev/null 2>&1 && docker start $(DDB_CONTAINER) || \
	docker run  -d --name $(DDB_CONTAINER) --network aws_local_network -p $(DDB_PORT):8000 amazon/dynamodb-local
	# Crear tabla si no existe
	aws dynamodb list-tables --endpoint-url http://localhost:$(DDB_PORT) | grep $(TABLE_NAME) >/dev/null 2>&1 || \
	aws dynamodb create-table \
		--table-name $(TABLE_NAME) \
		--attribute-definitions AttributeName=id,AttributeType=S \
		--key-schema AttributeName=id,KeyType=HASH \
		--billing-mode PAY_PER_REQUEST \
		--endpoint-url http://localhost:$(DDB_PORT)

# Detener y eliminar DynamoDB Local
stop-dynamodb:
	docker stop $(DDB_CONTAINER) || true
	docker rm $(DDB_CONTAINER) || true

# -----------------------------
# SAM Local
# -----------------------------

# Levantar API SAM Local (depende de DynamoDB)
start-api: start-dynamodb
	AWS_ENDPOINT_URL=http://localhost:$(DDB_PORT) sam local start-api --docker-network aws_local_network --profile $(PROFILE) --env-vars env.json

# -----------------------------
# Invocar Lambdas individualmente
# -----------------------------

invoke-createcode:
	sam local invoke CreateCode --event $(EVENTS_DIR)/create_code_event.json --profile $(PROFILE)  --env-vars env.json

invoke-getalldevices:
	sam local invoke GetAllDevices --event $(EVENTS_DIR)/get_all_devices_event.json --profile $(PROFILE) --env-vars env.json

invoke-publish:
	sam local invoke Publish --event $(EVENTS_DIR)/publish_event.json --profile $(PROFILE) --env-vars env.json

invoke-validationcode:
	sam local invoke ValidationCode --event $(EVENTS_DIR)/validation_code_event.json --profile $(PROFILE) --env-vars env.json
