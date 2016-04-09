
# Set up logging
import logging
import logging.handlers
import sys

if '-d' in sys.argv:
    level = logging.DEBUG
else:
    level = logging.INFO

# create logger
logger = logging.getLogger('knxsonos')
logger.setLevel(level)

# create console handler
ch = logging.StreamHandler()
ch.setLevel(level)

fh = logging.handlers.RotatingFileHandler('/tmp/knxsonos.log', maxBytes=1024*1024, backupCount=5)
fh.setLevel(level)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch and fh
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# add handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)
