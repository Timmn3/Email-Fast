from loguru import logger
import os

path = os.path.dirname(os.path.abspath(__file__))
logger.add(path + '/debug_logs.log', format='{time} {level} {message}', level='DEBUG',
           rotation="12:00", compression='zip')

logger.add(path + '/error_logs.log', format='{time} {level} {message}', level='ERROR',
           rotation="12:00", compression='zip')
