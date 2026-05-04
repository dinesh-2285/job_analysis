from loguru import logger


def configure_logging() -> None:
    logger.remove()
    logger.add(
        sink=lambda message: print(message, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "{message}",
    )
