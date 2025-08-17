import json
from get_all_devices.app import lambda_handler, MOCK_DEVICES


def test_lambda_handler_local(monkeypatch):
    """
    Testea el modo local de lambda_handler.
    """
    # Fuerza el entorno LOCAL=true
    monkeypatch.setenv("LOCAL", "true")

    # Ejecuta la lambda con un evento vacío
    response = lambda_handler({}, {})

    # Verifica el status code
    assert response["statusCode"] == 200

    # Verifica que el body sea JSON válido y que coincida con MOCK_DEVICES
    body = json.loads(response["body"])
    assert body == MOCK_DEVICES

    # Verifica headers
    assert response["headers"]["Content-Type"] == "application/json"
