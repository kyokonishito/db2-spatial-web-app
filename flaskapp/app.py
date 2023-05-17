from flask import Flask, request
import os
from os.path import join, dirname
from dotenv import load_dotenv
from db2data import Db2dataTool
from sqlalchemy import create_engine
from urllib.parse import quote
import atexit
from urllib.parse import quote_plus
import sys
from db2data import Db2dataTool
import signal

engine = None

def close_process():
    app.logger.info("engine.dispose()")
    engine.dispose()

def sig_handler(signum, frame) -> None:
    sys.exit(1)

signal.signal(signal.SIGTERM, sig_handler)

app = Flask(__name__, static_url_path='')
if os.getenv('APP_CONFIG_FILE'):
    app.config.from_envvar('APP_CONFIG_FILE')

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

if os.environ.get("FLASK_CONFIG") == "DEV":
    app.config.from_object('config.debug')
else:
    app.config.from_object('config.default')
    

db2info = {}
db2info['DBNAME']= os.environ.get("DBNAME");
db2info['USERID']= os.environ.get("USERID");
db2info['PASSWD']= quote_plus(os.environ.get("PASSWD"));
db2info['HOSTNAME']= os.environ.get("HOSTNAME");
db2info['PORT']= str(os.environ.get("PORT"));
db2info['TABLENAME']= str(os.environ.get("TABLENAME"));

# SQLAlchemyのエンジンを作成
url = f"ibm_db_sa://{db2info['USERID']}:{db2info['PASSWD']}@{db2info['HOSTNAME']}:{db2info['PORT']}/{db2info['DBNAME']};SECURITY=SSL;CONNECTTIMEOUT=5"
# print(url)
engine = create_engine(url, pool_pre_ping=True, pool_recycle=180, pool_timeout=5)
atexit.register(close_process)


@app.route('/')
def root():
    return app.send_static_file('index.html')

@app.route('/getLoc', methods=['POST'])
def getLoc():
    response = {}
    req = request.json
    lat = req.get("lat")
    lon = req.get("lon")
    dist = req.get("dist")
    db2data = Db2dataTool(engine, db2info['TABLENAME'])
    response = db2data.getData(lat, lon, dist)      
    app.logger.info("response retun")
    return response


@app.after_request
def apply_caching(response):
    if os.environ.get("FLASK_CONFIG") == "DEV":  #add CORS only DEV mode
        # response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5174')
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == "__main__":
    if app.config["HOST"]:
        app.run(debug=app.config["DEBUG"], host='0.0.0.0', port=app.config["PORT"], threaded=True)
    else:
        app.run(debug=app.config["DEBUG"], port=app.config["PORT"], threaded=True)