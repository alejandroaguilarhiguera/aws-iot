# Variables
PROFILE=default
EVENTS_DIR=events

# Levantar API en modo escucha
start-api:
	sam local start-api --profile $(PROFILE)

# Invocar Lambdas individuales
invoke-createcode:
	sam local invoke CreateCode --event $(EVENTS_DIR)/create_code_event.json --profile $(PROFILE)

invoke-getalldevices:
	sam local invoke GetAllDevices --event $(EVENTS_DIR)/get_all_devices_event.json --profile $(PROFILE)

invoke-publish:
	sam local invoke Publish --event $(EVENTS_DIR)/publish_event.json --profile $(PROFILE)

invoke-validationcode:
	sam local invoke ValidationCode --event $(EVENTS_DIR)/validation_code_event.json --profile $(PROFILE)
