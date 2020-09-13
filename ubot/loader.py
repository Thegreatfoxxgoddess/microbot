# SPDX-License-Identifier: GPL-2.0-or-later

import glob
from concurrent.futures import ThreadPoolExecutor
from importlib import import_module, reload
from os.path import basename, dirname, isfile

from aiohttp import ClientSession
from telethon.tl.types import DocumentAttributeFilename

from .command_handler import CommandHandler


class Loader():
    aioclient = ClientSession()
    thread_pool = ThreadPoolExecutor()

    help_dict = {}
    loaded_modules = []
    all_modules = {}

    def __init__(self, client, logger, settings):
        self.client = client
        self.logger = logger
        self.settings = settings
        self.command_handler = CommandHandler(client, settings)

    def load_all_modules(self):
        self.all_modules = self._find_all_modules()

        for module_type, module_list in self.all_modules.items():
            for module_name in module_list:
                try:
                    self.loaded_modules.append(import_module(f"ubot.modules.{module_type}.{module_name}"))
                except Exception as exception:
                    self.logger.error(f"Error while loading {module_type}.{module_name}: {exception}")

    def reload_all_modules(self):
        self.command_handler.outgoing_commands = []
        self.help_dict = {}

        errors = ""

        for module in self.loaded_modules:
            try:
                reload(module)
            except ModuleNotFoundError:
                pass
            except Exception as exception:
                errors += f"`Error while reloading {module.__name__} -> {exception}\n\n`"
                raise exception

        return errors or None

    def add(self, pattern: str = None, **args):
        pattern = args.get("pattern", pattern)
        pattern_extra = args.get("pattern_extra", "")

        def decorator(func):
            module_name = func.__module__.split(".")[-1]

            if module_name in self.help_dict:
                self.help_dict[module_name] += [[pattern, args.get('help', None)]]
            else:
                self.help_dict[module_name] = [[pattern, args.get('help', None)]]

            if func.__module__.split(".")[-1] in self.command_handler.outgoing_commands:
                self.command_handler.outgoing_commands[module_name].append({
                    "pattern": pattern,
                    "pattern_extra": pattern_extra,
                    "function": func,
                    "simple_pattern": args.get('simple_pattern', False),
                    "raw_pattern": args.get('raw_pattern', False),
                    "extra": args.get('extra', None)
                })
            else:
                self.command_handler.outgoing_commands[module_name] = [{
                    "pattern": pattern,
                    "pattern_extra": pattern_extra,
                    "function": func,
                    "simple_pattern": args.get('simple_pattern', False),
                    "raw_pattern": args.get('raw_pattern', False),
                    "extra": args.get('extra', None)
                }]

            return func

        return decorator

    def add_list(self, pattern: list = None, **args):
        pattern_list = args.get("pattern", pattern)
        pattern_extra = args.get("pattern_extra", "")

        def decorator(func):
            module_name = func.__module__.split(".")[-1]

            for pattern in pattern_list:
                if module_name in self.help_dict:
                    self.help_dict[module_name] += [[pattern, args.get('help', None)]]
                else:
                    self.help_dict[module_name] = [[pattern, args.get('help', None)]]

                if func.__module__.split(".")[-1] in self.command_handler.outgoing_commands:
                    self.command_handler.outgoing_commands[module_name].append({
                        "pattern": pattern,
                        "pattern_extra": pattern_extra,
                        "function": func,
                        "simple_pattern": args.get('simple_pattern', False),
                        "raw_pattern": args.get('raw_pattern', False),
                        "extra": args.get('extra', None)
                    })
                else:
                    self.command_handler.outgoing_commands[module_name] = [{
                        "pattern": pattern,
                        "pattern_extra": pattern_extra,
                        "function": func,
                        "simple_pattern": args.get('simple_pattern', False),
                        "raw_pattern": args.get('raw_pattern', False),
                        "extra": args.get('extra', None)
                    }]

            return func

        return decorator

    def add_dict(self, pattern: dict = None, **args):
        pattern_dict = args.get("pattern", pattern)
        pattern_extra = args.get("pattern_extra", "")

        def decorator(func):
            module_name = func.__module__.split(".")[-1]

            for pattern, extra in pattern_dict.items():
                if module_name in self.help_dict:
                    self.help_dict[module_name] += [[pattern, args.get('help', None)]]
                else:
                    self.help_dict[module_name] = [[pattern, args.get('help', None)]]

                if func.__module__.split(".")[-1] in self.command_handler.outgoing_commands:
                    self.command_handler.outgoing_commands[module_name].append({
                        "pattern": pattern,
                        "pattern_extra": pattern_extra,
                        "function": func,
                        "simple_pattern": args.get('simple_pattern', False),
                        "raw_pattern": args.get('raw_pattern', False),
                        "extra": args.get('extra', extra)
                    })
                else:
                    self.command_handler.outgoing_commands[module_name] = [{
                        "pattern": pattern,
                        "pattern_extra": pattern_extra,
                        "function": func,
                        "simple_pattern": args.get('simple_pattern', False),
                        "raw_pattern": args.get('raw_pattern', False),
                        "extra": args.get('extra', extra)
                    }]

            return func

        return decorator

    async def get_text(self, event, with_reply=True, return_msg=False, default=None):
        if event.args:
            if return_msg:
                if event.is_reply:
                    return event.args, await event.get_reply_message()

                return event.args, None

            return event.args
        elif event.is_reply and with_reply:
            reply = await event.get_reply_message()

            if return_msg:
                return reply.text, reply

            return reply.text
        else:
            if return_msg:
                return default, None

            return default

    async def get_image(self, event):
        if event and event.media:
            if event.photo:
                return event.photo
            elif event.document:
                if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in event.media.document.attributes:
                    return
                if event.gif or event.video or event.audio or event.voice:
                    return

                return event.media.document
            else:
                return
        else:
            return

    def prefix(self):
        return (self.settings.get_list('cmd_prefix') or ['.'])[0]

    def _find_all_modules(self):
        return {
            "core": [
                basename(f)[:-3] for f in glob.glob(dirname(__file__) + "/modules/core/*.py")
                if isfile(f) and f.endswith(".py")
            ],
            "default": [
                basename(f)[:-3] for f in glob.glob(dirname(__file__) + "/modules/default/*.py")
                if isfile(f) and f.endswith(".py")
            ],
            "user": [
                basename(f)[:-3] for f in glob.glob(dirname(__file__) + "/modules/user/*.py")
                if isfile(f) and f.endswith(".py")
            ]
        }
