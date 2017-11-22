import importlib

from flask import url_for

import server


def test_verify(client):
    importlib.reload(server)
    response = client.get(url_for('verify'))

    assert response.status_code == 200
    assert response.json == "False"


def test_health(client):
    importlib.reload(server)
    response = client.get(url_for('health'))

    assert response.status_code == 200
    assert response.json == {"status": "up"}
