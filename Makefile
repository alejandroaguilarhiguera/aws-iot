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
	docker network inspect aws_local_network >/dev/null 2>&1 || docker network create aws_local_network
	docker ps -a | grep $(DDB_CONTAINER) >/dev/null 2>&1 && docker start $(DDB_CONTAINER) || \
	docker run -d --name $(DDB_CONTAINER) --network aws_local_network -p $(DDB_PORT):8000 amazon/dynamodb-local
	aws dynamodb list-tables --endpoint-url http://localhost:$(DDB_PORT) | grep $(TABLE_NAME) >/dev/null 2>&1 || \
	aws dynamodb create-table \
		--table-name $(TABLE_NAME) \
		--attribute-definitions AttributeName=id,AttributeType=S \
		--key-schema AttributeName=id,KeyType=HASH \
		--billing-mode PAY_PER_REQUEST \
		--endpoint-url http://localhost:$(DDB_PORT)

stop-dynamodb:
	docker stop $(DDB_CONTAINER) || true
	docker rm $(DDB_CONTAINER) || true

# -----------------------------
# SAM Local
# -----------------------------

start-api: start-dynamodb
	AWS_ENDPOINT_URL=http://localhost:$(DDB_PORT) sam local start-api --docker-network aws_local_network --host 0.0.0.0 --profile $(PROFILE) --env-vars env.json
# -----------------------------
# Lambdas
# -----------------------------

invoke-createcode:
	sam local invoke CreateCode --event ./events/create_code_event.json  --env-vars env.json

invoke-getalldevices:
	sam local invoke GetAllDevices --event ./events/get_all_devices_event.json --env-vars env.json

invoke-publish:
	sam local invoke Publish --event ./events/publish_event.json --env-vars env.json

invoke-validationcode:
	sam local invoke ValidationCode --event ./events/validation_code_event.json --env-vars env.json

invoke-list_streams:
	sam local invoke ListStreams --event ./events/list_streams_event.json --env-vars env.json

invoke-stream_live:
	sam local invoke StreamLive --event ./events/stream_live_event.json --env-vars env.json
