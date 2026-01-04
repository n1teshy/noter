import logging


def add_sql_logging() -> None:
    logger = logging.getLogger("sqlalchemy.engine")
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler("sql.log")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    logger.addHandler(handler)
    logger.propagate = False
