#!/usr/bin/env python
import asyncio
import logging
import os
import requests
from telethon import TelegramClient, events

import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = TelegramClient(config.SESSION_NAME, config.API_ID, config.API_HASH)
client.start()

RELAY_MAP = {}

# Oz
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1027861275474141185/ld0wF95unPF4DPcikRQ-oe0CD_YdUyb7zTyiDs13OisQUvkkAJormNN0GzgN05uOhaJq"

def send_discord_message(message):
    req = requests.post(DISCORD_WEBHOOK_URL, data={"content":message})

def send_discord_image(file_path, message):
    files = {"file":(file_path, open(file_path, "rb"),'application-type')}
    payload={"content": message}
    req = requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files)


async def setup():
    user = await client.get_me()
    logger.info('Started serving as {}'.format(user.first_name))
    await client.get_dialogs()

    for x in config.RELAY_MAP.split(';'):
        if not x:
            return

        key, values = x.split(':', 1)
        values = values.split(',')
        RELAY_MAP[int(key)] = [int(x) for x in values]


@client.on(events.NewMessage)
async def my_event_handler(event):
    for chat_id, relays in RELAY_MAP.items():
        if event.chat and event.chat.id == chat_id:
            for relay in relays:
                logger.info('Sending message from {} to {}'.format(event.chat.id, relay))
                if event.message.media:
                    file_name = await client.download_media(event.message.media)
                    send_discord_image(file_name, event.message.text)
                    # await client.send_message(relay, event.message.text, file=file_name)
                    if os.path.exists(file_name):
                        os.remove(file_name)
                        logger.info(f'remove {file_name}')
                else:
                    send_discord_message(event.message.text)
            break
    else:
        for relay in RELAY_MAP.get('default', []):
            logger.info('Sending message from {} to {}'.format(event.chat.id, relay))
            if event.message.media:
                file_name = await client.download_media(event.message.media)
                send_discord_image(file_name, event.message.text)
                # await client.send_message(relay, event.message.text, file=file_name)
                if os.path.exists(file_name):
                    os.remove(file_name)
                    logger.info(f'remove {file_name}')
            else:
                send_discord_message(event.message.text)

loop = asyncio.get_event_loop()
loop.run_until_complete(setup())
client.run_until_disconnected()