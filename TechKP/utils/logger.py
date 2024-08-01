from logging.handlers import RotatingFileHandler
import logging
import os

if not os.path.exists("./TechKP/logs"):
    os.mkdir("./TechKP/logs")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("./TechKP/logs/botlogs.log", maxBytes=500000, backupCount=10),
        logging.StreamHandler(),
    ],
)


logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("imdbpy").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
