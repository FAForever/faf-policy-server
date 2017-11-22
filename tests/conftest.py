import pytest

import server
import server.server


@pytest.fixture
def app():
    server.app = server.app
    server.app.debug = True

    with server.app.app_context():
        yield server.app


@pytest.fixture
def client(app):
    return app.test_client()
