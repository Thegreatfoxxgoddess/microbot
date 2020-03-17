# SPDX-License-Identifier: GPL-2.0-or-later

import io
from random import choice

import praw

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

REDDIT = praw.Reddit(client_id='-fmzwojFG6JkGg',
                     client_secret=None,
                     user_agent='TG_Userbot')

VALID_ENDS = (".mp4", ".jpg", ".jpeg", ".png", ".gif")


async def imagefetcherfallback(sub):
    hot = REDDIT.subreddit(sub).hot()
    hot_list = list(hot.__iter__())

    for _ in range(10):
        post = choice(hot_list)

        if post.url:
            if post.url.endswith(VALID_ENDS):
                return post.url, post.title

    return None, None


async def titlefetcherfallback(sub):
    hot = REDDIT.subreddit(sub).hot()
    hot_list = list(hot.__iter__())

    return choice(hot_list).title


async def imagefetcher(event, sub):
    image_url = False

    for _ in range(10):
        post = REDDIT.subreddit(sub).random()

        if not post:
            image_url, title = await imagefetcherfallback(sub)
            break

        if post.url:
            if post.url.endswith(VALID_ENDS):
                image_url = post.url
                title = post.title
                break

    if not image_url:
        await event.reply(f"`Failed to find any valid content on `**r/{sub}**`!`")
        return

    try:
        await event.reply(title, file=image_url)
    except:
        await event.reply(f"`Failed to download content from `**r/{sub}**`!`\n`Title: `**{title}**\n`URL: `{image_url}")


async def titlefetcher(event, sub):
    post = REDDIT.subreddit(sub).random()

    if not post:
        title = await titlefetcherfallback(sub)
    else:
        title = post.title

    await event.reply(title)


@ldr.add(pattern="redi")
async def redimg(event):
    sub = event.pattern_match.group(1)

    if sub:
        await imagefetcher(event, sub)
    else:
        await event.reply("Syntax: .redi <subreddit name>")


@ldr.add(pattern="redt")
async def redtit(event):
    sub = event.pattern_match.group(1)

    if sub:
        await titlefetcher(event, sub)
    else:
        await event.reply("Syntax: .redt <subreddit name>")


@ldr.add(pattern="suffer")
async def makemesuffer(event):
    await imagefetcher(event, "MakeMeSuffer")


@ldr.add(pattern="snafu")
async def coaxedintoasnafu(event):
    await imagefetcher(event, "CoaxedIntoASnafu")


@ldr.add(pattern="aita")
async def amitheasshole(event):
    await titlefetcher(event, "AmITheAsshole")


@ldr.add(pattern="jon(x|)")
async def imsorryjon(event):
    if "x" in event.pattern_match.group(0):
        sub = "ImReallySorryJon"
    else:
        sub = "ImSorryJon"

    await imagefetcher(event, sub)


@ldr.add(pattern="tihi")
async def thanksihateit(event):
    await imagefetcher(event, "TIHI")
