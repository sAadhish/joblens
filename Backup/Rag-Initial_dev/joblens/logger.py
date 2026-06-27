# joblens/logger.py

import logging
import os
from datetime import datetime

# Create logs folder
os.makedirs("logs", exist_ok=True)

# Log filename with today's date
log_file = f"logs/joblens_{datetime.now().strftime('%Y%m%d')}.log"

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