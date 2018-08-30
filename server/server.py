import asyncio
import importlib
import logging
import os

import aiomysql
from sanic import Sanic
from sanic.response import json
from sanic.response import text

app = Sanic(__name__)
app.config.from_object(__name__)

verifier = None
verifier_module = None
db_pool = None


async def init_db():
    global db_pool

    db_pool = await aiomysql.create_pool(minsize=1,
                                         maxsize=5,
                                         host=os.environ.get('DATABASE_HOST', "localhost"),
                                         port=int(os.environ.get('DATABASE_PORT', 3306)),
                                         user=os.environ.get('DATABASE_USER'),
                                         password=os.environ.get('DATABASE_PASSWORD'),
                                         db=os.environ.get('DATABASE_NAME'),
                                         loop=loop,
                                         cursorclass=aiomysql.cursors.DictCursor)


@app.route('/health')
async def health(request):
    return json({'status': 'up'})


@app.route('/reload')
async def reload(request):
    global verifier
    global verifier_module

    if verifier_module is None:
        try:
            await init_db()
            verifier_module = importlib.import_module('verifier.verifier')
            verifier_class = getattr(verifier_module, 'Verifier')
            verifier = verifier_class(db_pool)
        except ImportError:
            logging.exception("Module could not be loaded")
            return "Module not available"
    else:
        importlib.reload(verifier_module)

    return text("Reloaded")


@app.route('/verify', methods=['POST'])
async def verify(request):
    if not verifier:
        logging.info("No verifier available")
        return json(dict(result='honest'))

    data = request.json

    result = await verifier.verify(data.get('player_id'), data.get('uid_hash'), data.get('session'))

    json_result = json(result)
    logging.debug("Verification result: %s", json_result)

    return json_result


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(reload(None))
    server = app.create_server(host='0.0.0.0', port=int(os.environ.get('APP_PORT', 8097)))
    asyncio.ensure_future(server)

    try:
        loop.run_forever()
    except:
        loop.stop()
