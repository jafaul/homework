from flask_project.app.config import config
from app.routers import *

if __name__ == "__main__":
    app.run(debug=config.DEBUG, host=config.APP_HOST, port=config.APP_PORT)
