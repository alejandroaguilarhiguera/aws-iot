import json
import os
import pytest
from create_code.app import lambda_handler

@pytest.mark.parametrize(
    "event,expected_status",
    [
        ({"body": json.dumps({"thingName": "esp32_dev"})}, 200),
        ({"body": json.dumps({"thingName": "notFoundDevice"})}, 404),
        ({"body": json.dumps({})}, 400),
    ]
)
def test_lambda_handler_with_body(event, expected_status):
    context = {}  # puedes dejarlo vacío si no lo usas
    response = lambda_handler(event, context)

    assert response["statusCode"] == expected_status
    if response["statusCode"] == 200:
        # Parseamos el body como JSON
        body = json.loads(response["body"])

        # Verifica que body sea un diccionario
        assert isinstance(body, dict)

        assert "message" in body
        assert body["message"] == "Code created"

        assert "code" in body
        assert isinstance(body["code"], dict)

        assert "id" in body["code"]
        assert "thingName" in body["code"]
        assert "count" in body["code"]
