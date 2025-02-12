import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import asyncio
import threading
import gradio_interface
from app import run_bot

async def main():
    logger.debug("Starting Telegram bot...")
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    logger.debug("Launching Gradio interface...")
    gradio_interface

if __name__ == "__main__":
    logger.debug("Running main.py...")
    asyncio.run(main())
#main.py