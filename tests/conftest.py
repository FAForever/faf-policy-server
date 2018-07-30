import pytest

import server
import server.server


@pytest.fixture
def app():
    server.app = server.server.app
    server.app.debug = True
    return server.app


@pytest.fixture
def client(app):
    return app.test_client
