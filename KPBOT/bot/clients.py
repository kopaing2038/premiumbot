import asyncio
import logging
from TechKP.config.config import Config
from TechKP.utils.cache import Cache
from pyrogram import Client
from KPBOT.bot import multi_clients, work_loads, TechKPBot


from os import environ
from typing import Dict, Optional


class TokenParser:
    def __init__(self, config_file: Optional[str] = None):
        self.tokens = {}
        self.config_file = config_file

    def parse_from_env(self) -> dict:
        self.tokens = dict(
            (c + 1, t)
            for c, (_, t) in enumerate(
                filter(
                    lambda n: n[0].startswith("MULTI_TOKEN"), sorted(environ.items())
                )
            )
        )
        return self.tokens

async def initialize_clients():
    multi_clients[0] = TechKPBot
    work_loads[0] = 0

    all_tokens = TokenParser().parse_from_env()
    if not all_tokens:
        print("No additional clients found, using default client")
        return

    async def start_client(client_id, token):
        try:
            print(f"Starting - Client {client_id}")
            if client_id == len(all_tokens):
                await asyncio.sleep(2)
                print("This will take some time, please wait...")
            client = await Client(
                name=str(client_id),
                api_id=Config.API_ID,
                api_hash=Config.API_HASH,
                bot_token=token,
                sleep_threshold=SLEEP_THRESHOLD,
                no_updates=True,
                in_memory=True
            ).start()
            work_loads[client_id] = 0
            return client_id, client
        except Exception:
            logging.error(f"Failed starting Client - {client_id} Error:", exc_info=True)
    
    clients = await asyncio.gather(*[start_client(i, token) for i, token in all_tokens.items()])
    multi_clients.update(dict(clients))
    if len(multi_clients) != 1:
        print("Multi-Client Mode Enabled")
    else:
        print("No additional clients were initialized, using default client")
