from flask import Flask
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Print Python version and path
logger.info(f"Python version: {sys.version}")
logger.info(f"Python path: {sys.executable}")

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    try:
        logger.info('Starting minimal app...')
        app.run(debug=True, port=4000)  # Remove host binding to only listen on localhost
    except Exception as e:
        logger.error(f'Error: {str(e)}', exc_info=True)
