import logging

from osscla import settings

logging.basicConfig()
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(settings.LOG_LEVEL)
