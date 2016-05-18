import logging
import datetime

appName = "log"
logger = logging.getLogger(appName)
logger.setLevel("DEBUG")
# create file handler which logs even debug messages
fh = logging.FileHandler(appName + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
#fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

logger.info("test INFO")
logger.debug("DEBUG")
logger.warning("WARNING")
