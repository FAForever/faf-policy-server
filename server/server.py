import asyncio
import importlib
import logging
import os
import sys

import aiomysql
from sanic import Sanic
from sanic.response import json
from sanic.response import text

verifier = None
verifier_module = None
db_pool = None

log = logging.getLogger('policy-server')
log.setLevel(logging.DEBUG)
stdout_handler = logging.StreamHandler(stream=sys.stdout)
stdout_handler.setFormatter(logging.Formatter('%(levelname)-8s %(name)-30s %(message)s'))
log.addHandler(stdout_handler)

app = Sanic("policy-server")


async def init_all():
    await init_db()
    await init_verifier()


async def init_db():
    global db_pool

    log.info("Creating database connection pool")

    db_pool = await aiomysql.create_pool(minsize=1,
                                         maxsize=5,
                                         host=os.environ.get('DATABASE_HOST', "localhost"),
                                         port=int(os.environ.get('DATABASE_PORT', 3306)),
                                         user=os.environ.get('DATABASE_USER'),
                                         password=os.environ.get('DATABASE_PASSWORD'),
                                         db=os.environ.get('DATABASE_NAME'),
                                         loop=asyncio.get_event_loop(),
                                         cursorclass=aiomysql.cursors.DictCursor)


async def init_verifier():
    global db_pool
    global verifier
    global verifier_module

    if verifier_module is None:
        log.info("Loading verifier")
        try:
            verifier_module = importlib.import_module('verifier.verifier')
            verifier_class = getattr(verifier_module, 'Verifier')
            verifier = verifier_class(db_pool)
        except ImportError:
            log.exception("Module could not be loaded")
            return "Module not available"
    else:
        log.info("Reloading verifier")
        importlib.reload(verifier_module)


@app.route('/health')
async def health(request):
    return json({'status': 'up'})


@app.route('/reload')
async def reload(request):
    global verifier
    global verifier_module

    await init_verifier()

    return text("Reloaded")


@app.route('/verify', methods=['POST'])
async def verify(request):
    if not verifier:
        log.info("No verifier available")
        return json(dict(result='honest'))

    data = request.json

    result = await verifier.verify(data.get('player_id'), data.get('uid_hash'), data.get('session'))

    log.debug("Verification result: %s", result)
    return json(result)


if __name__ == '__main__':
    app.add_task(init_all)
    app.run(host='0.0.0.0', port=int(os.environ.get('APP_PORT', 8097)))
