import argparse
import asyncio
import logging
from logging import Logger
import sys
from asyncio import sleep
from datetime import datetime, time
from typing import Union, Dict

from socks import SOCKS5
from telethon import TelegramClient

from config import APP_API_HASH, APP_API_ID, PHONE_NUMBER, EXCEPTION_CHATS, REMOVING_TIME


async def delete_read_messages(client: TelegramClient, logger: Logger) -> None:

    dialogs = await client.get_dialogs()

    for dialog in dialogs:
        if dialog.title in EXCEPTION_CHATS:
            continue

        messages = await client.get_messages(dialog, limit=10000)
        message_ids = [message.id for message in messages if not message.media_unread]
        logger.info(f'In dialog {dialog.title} will remove {len(message_ids)} messages')
        await client.delete_messages(dialog, message_ids)
        logger.info(f'Messages from dialog {dialog.title} removed')


async def enable_watcher(client: TelegramClient, logger: Logger) -> None:
    removing_time = datetime.strptime(REMOVING_TIME, "%H:%M:%S")

    while True:
        if now_time() == removing_time.time():
            logger.info("It's message removing time!")
            try:
                await delete_read_messages(client, logger)
            except Exception:
                logger.exception('Exception during message removing has occurred')
        await sleep(0.6)


async def main(client: TelegramClient, logger: Logger, remove_now=False) -> None:
    await client.start()
    logger.info('Telegram client started')

    if remove_now:
        await delete_read_messages(client, logger)
        logger.exception('Exception during message removing has occurred')
    else:
        await enable_watcher(client, logger)


def configure_config() -> Logger:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='/tmp/message_remover_log')
    logger = logging.getLogger()
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def parse_arguments() -> Dict[str, Union[str, int, bool]]:
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--remove-now',
                        type=bool, required=False,
                        help='If true -> messages remove now')

    return vars(parser.parse_args())


def now_time() -> time:
    now = datetime.now().time()
    now = now.replace(microsecond=0)

    return now


if __name__ == "__main__":
    bot_logger = configure_config()
    (remove_now,) = parse_arguments().values()

    proxy = None
    telegram_client = TelegramClient(PHONE_NUMBER.strip('+'),
                                     APP_API_ID,
                                     APP_API_HASH,
                                     proxy=proxy)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(telegram_client, bot_logger, remove_now=remove_now))
