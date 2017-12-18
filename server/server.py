import importlib
import logging
import os
import pymysql

from flask import Flask

from flask import request, jsonify

app = Flask(__name__)
app.config.from_object(__name__)

verifier = None
verifier_module = None
db_connection = None


def init_db():
    global db_connection

    db_connection = pymysql.connect(host=os.environ.get('DATABASE_HOST'),
                                    port=int(os.environ.get('DATABASE_PORT')),
                                    user=os.environ.get('DATABASE_USER'),
                                    password=os.environ.get('DATABASE_PASSWORD'),
                                    db=os.environ.get('DATABASE_NAME'),
                                    cursorclass=pymysql.cursors.DictCursor)

    def get_cursor(cursor=None):
        """
        Ping the connection every time we get a cursor, will reconnect if the connection is dead.
        """
        db_connection.ping()
        return pymysql.connections.Connection.cursor(db_connection, cursor)

    db_connection.cursor = get_cursor


@app.route('/health')
def health():
    return jsonify({'status': 'up'})


@app.route('/reload')
def reload():
    global verifier
    global verifier_module

    if verifier_module is None:
        try:
            verifier_module = importlib.import_module('verifier.verifier')
            verifier_class = getattr(verifier_module, 'Verifier')
            verifier = verifier_class(db_connection.cursor)
        except ImportError:
            logging.exception("Module could not be loaded")
            return "Module not available"
    else:
        importlib.reload(verifier_module)

    return "Reloaded"


@app.route('/verify', methods=['POST'])
def verify():
    if not verifier:
        logging.info("No verifier available")
        return jsonify(dict(result='honest'))

    result = jsonify(verifier.verify(request.json))
    logging.debug("Verification result: %s", result)

    return result


init_db()
reload()

if __name__ == '__main__':
    app.run(port=int(os.environ.get('APP_PORT', 8097)))
