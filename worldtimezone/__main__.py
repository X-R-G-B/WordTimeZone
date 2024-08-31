import os
from typing import Optional
import datetime

from data import Data

import hikari
import lightbulb
from hikari import Intents

import pytz

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

CHANNEL_WORLD_CLOCK = 1279480935510966436
MESSAGE_EDIT_WORLD_CLOCK = 1279496427621322806
GUILD_WORLD_CLOCK = 1279015859502841927
INTENTS = Intents.GUILD_MEMBERS | Intents.GUILDS

bot = lightbulb.BotApp(
    os.environ["BOT_TOKEN"],
    intents=INTENTS,
    banner=None,
)


async def edit_world_clock() -> None:
    embed = hikari.Embed(
        title="WorldTimeZone Clock",
        description="",
    )

    def add_field(u, tz):
        user_ = bot.cache.get_member(GUILD_WORLD_CLOCK, int(u))
        now = datetime.datetime.now()
        new_tz = pytz.timezone(tz)
        new_now = now.astimezone(new_tz)
        embed.add_field(f"{user_.display_name}", f"{new_now}", inline=True)

    for u in bot.d.data.get_members_list(GUILD_WORLD_CLOCK):
        member = bot.d.data.get_member(GUILD_WORLD_CLOCK, u)
        if "tz" in member:
            add_field(u, member["tz"])
    await bot.rest.edit_message(CHANNEL_WORLD_CLOCK, MESSAGE_EDIT_WORLD_CLOCK, embed)


@bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    bot.d.data = Data()
    bot.d.sched = AsyncIOScheduler()
    bot.d.sched.start()
    bot.d.sched.add_job(edit_world_clock, CronTrigger(minute="*/1"))


@bot.command
@lightbulb.command("ping", description="The bot's ping.")
@lightbulb.implements(lightbulb.SlashCommand)
async def pingIt(ctx: lightbulb.SlashContext) -> None:
    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency * 1000:.2f}ms.")


@bot.command
@lightbulb.option("timezone", "Your TimeZone", type=str, required=False)
@lightbulb.command("set", description="Set your TimeZone", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def setIt(ctx: lightbulb.SlashContext, timezone: Optional[str] = None) -> None:
    res = bot.d.data.set_member_tz(ctx.guild_id, ctx.user.id, timezone)
    if res is False:
        await ctx.respond(
            f"Failed, please provide a working timezone ('{timezone}' is unknow)"
        )
        return
    await ctx.respond(f"Your TimeZone as been set!")


@bot.command
@lightbulb.option(
    "user", "to see only his/her time", type=hikari.OptionType.USER, required=False
)
@lightbulb.command(
    "list", description="see what time is it for others", pass_options=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def listIt(
    ctx: lightbulb.SlashContext, user: Optional[hikari.OptionType.USER]
) -> None:
    assert ctx.guild_id is not None

    embed = hikari.Embed(
        title="WorldTimeZone Clock",
        description="",
    ).set_thumbnail(ctx.user.avatar_url)

    def add_field(u, tz):
        user_ = ctx.bot.cache.get_member(ctx.guild_id, int(u))
        now = datetime.datetime.now()
        new_tz = pytz.timezone(tz)
        new_now = now.astimezone(new_tz)
        embed.add_field(f"{user_.display_name}", f"{new_now}", inline=True)

    if user is None:
        for u in bot.d.data.get_members_list(ctx.guild_id):
            member = bot.d.data.get_member(ctx.guild_id, u)
            if "tz" in member:
                add_field(u, member["tz"])
    else:
        add_field(f"{user.id}", file[f"{user.id}"])
    await ctx.respond(embed)


if __name__ == "__main__":
    bot.run()
