from __init__ import app
import logging
import gunicorn.app.base

logging.basicConfig(
    filename='gunicorn.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

if __name__ == "__main__":
    app.run()

