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

INTENTS = Intents.GUILD_MEMBERS | Intents.GUILDS

bot = lightbulb.BotApp(
    os.environ["BOT_TOKEN"],
    intents=INTENTS,
    banner=None,
)


async def edit_world_clock() -> None:

    embeds = []

    def add_field(guild_id, u, tz):
        user_ = bot.cache.get_member(guild_id, int(u))
        embed = hikari.Embed(
            title=f"WorldTimeClock - {user_.display_name}",
            description=f"Timezone: {tz}",
        ).set_author(name=f"{user_.display_name}", url=user_.avatar_url)
        now = datetime.datetime.now()
        new_tz = pytz.timezone(tz)
        new_now = now.astimezone(new_tz)
        embed.add_field("Time", f"{new_now}", inline=False)
        embeds.append(embed)

    for guild_id in bot.d.data.get_guilds_list():
        guild_world_clock = bot.d.data.get_world_clock(guild_id)
        channel_world_clock = guild_world_clock["channel_id"]
        message_world_clock = guild_world_clock["message_id"]

        for u in bot.d.data.get_members_list(guild_id):
            member = bot.d.data.get_member(guild_id, u)
            if "tz" in member:
                add_field(guild_id, u, member["tz"])
        await bot.rest.edit_message(
            channel_world_clock, message_world_clock, None, embeds=embeds
        )


@bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    bot.d.data = Data()
    bot.d.sched = AsyncIOScheduler()
    bot.d.sched.start()
    bot.d.sched.add_job(edit_world_clock, CronTrigger(minute="*/5"))


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
    await ctx.respond("Your TimeZone as been set!")


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
        embed.add_field(f"{user_.display_name}", f"{new_now}", inline=False)

    if user is None:
        for u in bot.d.data.get_members_list(ctx.guild_id):
            member = bot.d.data.get_member(ctx.guild_id, u)
            if "tz" in member:
                add_field(u, member["tz"])
    else:
        member = bot.d.data.get_member(ctx.guild_id, user.id)
        if "tz" in member:
            add_field(f"{user.id}", member["tz"])
        else:
            ctx.respond("This user has no timezone set.")
            return
    await ctx.respond(embed)


@bot.command
@lightbulb.option(
    "channel",
    "where the bot will edit the same message",
    type=hikari.OptionType.CHANNEL,
    required=True,
)
@lightbulb.command(
    "setupchannel",
    description="edit the same message every 5 minutes",
    pass_options=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def setupIt(
    ctx: lightbulb.SlashContext, channel: hikari.OptionType.CHANNEL
) -> None:
    message = await bot.rest.create_message(
        channel, "This message will be edited in no time... Please wait..."
    )
    status = bot.d.data.set_world_clock(ctx.guild_id, channel.id, message.id)
    if status is False:
        await message.delete()
        ctx.respond("Sorry, an error occured.")
        return
    await ctx.respond(
        "All Set! A message has been sent to the channel, it will be edited soon."
    )


if __name__ == "__main__":
    bot.run()
