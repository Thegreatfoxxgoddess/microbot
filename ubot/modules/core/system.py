# SPDX-License-Identifier: GPL-2.0-or-later

import asyncio
from os import remove
from os.path import dirname
from platform import python_version
from time import time_ns

from telethon import version
from ubot import ldr, micro_bot


@ldr.add("reload")
async def reload_modules(event):
    await event.edit("`Reloading modules…`")

    errors = ldr.reload_all_modules()

    if errors:
        await event.edit(errors)
    else:
        try:
            await event.delete()
        except:
            pass


@ldr.add("help")
async def help_cmd(event):
    if event.args:
        for key, value in ldr.help_dict.items():
            for info in value:
                if event.args == info[0]:
                    if info[1]:
                        await event.edit(f"Help for **{info[0]}**: __{info[1]}__")
                        return

                    await event.edit(f"**{info[0]}** doesn't have a help string.")
                    return

    help_string = ""

    for key, value in ldr.help_dict.items():
        help_string += f"\n**{key}**: "
        for info in value:
            help_string += f"{info[0]}, "
        help_string = help_string.rstrip(", ")

    await event.edit(f"**Available commands:**\n{help_string}")


@ldr.add("sysd")
async def sysd(event):
    try:
        neo = "neofetch --stdout"

        fetch = await asyncio.create_subprocess_shell(
            neo,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await fetch.communicate()

        await event.edit(f"`{stdout.decode().strip()}{stderr.decode().strip()}`")
    except FileNotFoundError:
        await event.edit("`Neofetch not found!`")


@ldr.add("alive")
async def alive(event):
    alive_format = "μBot is running!\n" \
                   "**Telethon version:** {0}\n" \
                   "**Python version:** {1}"

    await event.edit(alive_format.format(version.__version__, python_version()))


@ldr.add("shutdown")
async def shutdown(event):
    await event.edit("`Goodbye…`")
    await micro_bot.stop_client()


@ldr.add("ping")
async def ping(event):
    start = time_ns()
    await event.edit("`Ping…`")
    time_taken_ms = int((time_ns() - start) / 1000000)
    await event.edit(f"`Ping… Pong! -> `**{time_taken_ms}**`ms`")


@ldr.add("prefix")
async def change_prefix(event):
    new_prefix = event.args

    if not new_prefix:
        await event.edit("`Please specify a valid command prefix!`")
        return

    micro_bot.settings.set_config("cmd_prefix", new_prefix)

    await event.edit(f"`Command prefix successfully changed to `**{new_prefix}**`!`")


@ldr.add("repo")
async def bot_repo(event):
    await event.edit("https://github.com/Nick80835/microbot")


@ldr.add("showmods")
async def show_modules(event):
    await event.edit(f"Loaded user modules: {', '.join(ldr.all_modules.get('user'))}")


@ldr.add("insmod")
async def install_module(event):
    if not event.is_reply:
        await event.edit("Please reply to a valid module file!")
        return

    reply = await event.get_reply_message()

    if reply.file.name and reply.file.name.endswith(".py"):
        await event.client.download_media(reply.media.document, f"{ldr.user_mod_dir}{reply.file.name}")

        try:
            ldr.load_user_module(reply.file.name[:-3])
            await event.edit(f"Successfully loaded module: {reply.file.name[:-3]}")
        except:
            remove(f"{ldr.user_mod_dir}{reply.file.name}")
            await event.edit(f"Failed to load module: {reply.file.name[:-3]}")
    else:
        await event.edit("Please reply to a valid module file!")


@ldr.add("delmod")
async def delete_module(event):
    try:
        ldr.uninstall_user_module(event.args)
        await event.edit(f"Successfully uninstalled module: {event.args}")
    except:
        await event.edit(f"Failed to uninstall module: {event.args}")
