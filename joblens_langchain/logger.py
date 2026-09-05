# joblens_langchain/logger.py

import logging
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Log filename with today's date — a FILE inside LOG_DIR, not LOG_DIR itself
log_file = os.path.join(LOG_DIR, f"joblens_{datetime.now().strftime('%Y%m%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("joblens")




'''
# joblens_langchain/logger.py

import logging
import os
from datetime import datetime
# Create logs folder
#os.makedirs("logs", exist_ok=True)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Log filename with today's date
#log_file = f"logs/joblens_{datetime.now().strftime('%Y%m%d')}.log"
log_file = LOG_DIR
# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(module)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file),    # save to file
        logging.StreamHandler()           # also print to terminal
    ]
)

logger = logging.getLogger("joblens")

'''