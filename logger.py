import logging
import os
import config


class CustomFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        # Fixer la largeur du niveau de log à 8 caractères
        if len(levelname) < 12:
            levelname = levelname + " " * (8 - len(levelname))
        record.levelname = levelname
        return super().format(record)

    # Configuration de base du logger


handler = logging.FileHandler("scanner.log")
handler.setFormatter(CustomFormatter("%(asctime)s   %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

console_handler = logging.StreamHandler()
console_handler.setFormatter(CustomFormatter("%(asctime)s   %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        
logging.basicConfig(level=logging.DEBUG, handlers=[handler, console_handler])

logger = logging.getLogger()
