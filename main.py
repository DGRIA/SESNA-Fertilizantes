import logging
import config

# Incluir estas líneas en cada script para registrar los logs
logger = logging.getLogger("Fertilizantes")
logger.setLevel(logging.INFO)

if __name__ == '__main__':
    logger.info("Inicio de Ejecución")
    logger.info("Fin de Ejecución")
