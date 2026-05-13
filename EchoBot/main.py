"""
Entry point: python main.py

Starts the Uvicorn ASGI server with settings from AppConfig.
"""

import logging
import uvicorn
from app.config import config

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)

if __name__ == "__main__":
    uvicorn.run(
        "app.server:app",
        host=config.server.host,
        port=config.server.port,
        log_level=config.server.log_level,
        reload=False,
    )