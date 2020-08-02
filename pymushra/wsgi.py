import os.path
from tinydb import TinyDB
from pymushra.service import app as application

application.config['webmushra_dir'] = os.path.join(os.getcwd(), "webmushra")

application.config['db'] = TinyDB(
    os.path.join(os.getcwd(), "db/webmushra.json")
)
