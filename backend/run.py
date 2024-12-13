import logging
from app import create_app

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    app = create_app()
    
    if __name__ == '__main__':
        logger.info('Starting the application...')
        app.run(debug=True, port=4000)  # Run on port 4000
except Exception as e:
    logger.error(f'Failed to start application: {str(e)}')
