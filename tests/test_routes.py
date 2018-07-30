import importlib
import pytest
import server


def test_verify(client):
    importlib.reload(server)
    request, response = client.post(server.app.url_for('verify'))

    assert response.status == 200
    assert response.json == {"result": "honest"}


def test_health(client):
    importlib.reload(server)
    request, response = client.get(server.app.url_for('health'))

    assert response.status == 200
    assert response.json == {"status": "up"}
