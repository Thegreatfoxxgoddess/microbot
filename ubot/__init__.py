import sys
from logging import INFO, basicConfig, getLogger

import telethon
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from telethon.network.connection.tcpabridged import \
    ConnectionTcpAbridged as CTA

from .custom import ExtendedEvent
from .loader import Loader
from .settings import Settings

if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 6):
    print("This program requires at least Python 3.6.0 to work correctly, exiting.")
    sys.exit(1)


class MicroBot():
    client = None
    settings = Settings()
    logger = None
    loader = None

    def __init__(self):
        self.start_logger()
        self.start_client()
        self.start_loader()

    def run_until_done(self):
        self.loader.load_all_modules()
        self.logger.info("Client successfully started.")
        self.client.run_until_disconnected()
        self.client.loop.run_until_complete(self.loader.aioclient.close())

    def start_loader(self):
        self.loader = Loader(self.client, self.logger, self.settings)

    def start_logger(self):
        basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=INFO)
        self.logger = getLogger(__name__)

    def _check_config(self):
        session_name = self.settings.get_config("session_name")
        api_key = self.settings.get_config("api_key")
        api_hash = self.settings.get_config("api_hash")

        while not api_key:
            api_key = input("Enter your API key: ")

        self.settings.set_config("api_key", api_key)

        while not api_hash:
            api_hash = input("Enter your API hash: ")

        self.settings.set_config("api_hash", api_hash)

        if not session_name:
            session_name = "user0"
            self.settings.set_config("session_name", session_name)

        return api_key, api_hash, session_name

    def start_client(self):
        api_key, api_hash, session_name = self._check_config()

        self.client = telethon.TelegramClient(session_name, api_key, api_hash, connection=CTA)

        try:
            self.client.start()
        except PhoneNumberInvalidError:
            self.logger.error("The phone number provided is invalid, exiting.")
            sys.exit(2)

    async def stop_client(self, reason=None):
        if reason:
            self.logger.info("Stopping client for reason: %s", reason)
        else:
            self.logger.info("Stopping client.")

        await self.loader.aioclient.close()
        await self.client.disconnect()


telethon.events.NewMessage.Event = ExtendedEvent

micro_bot = MicroBot()
ldr = micro_bot.loader
client = micro_bot.client
logger = micro_bot.logger

try:
    micro_bot.run_until_done()
except:
    micro_bot.client.loop.run_until_complete(micro_bot.stop_client())
