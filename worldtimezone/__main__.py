import os
from typing import Optional
import json
import datetime

import hikari
import lightbulb
from hikari import Intents

import pytz


FILE_INFO = ".data.json"
try:
    with open(FILE_INFO) as f:
        _ = json.load(f)
except FileNotFoundError:
    with open(FILE_INFO, mode="w") as f:
        json.dump({}, f)

INTENTS = Intents.GUILD_MEMBERS | Intents.GUILDS

bot = lightbulb.BotApp(
    os.environ["BOT_TOKEN"],
    intents=INTENTS,
    banner=None,
)


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
    if timezone is None or timezone not in pytz.all_timezones:
        print(timezone)
        await ctx.respond(
            f"Failed, please provide a working timezone ('{timezone}' is unknow)"
        )
        return
    with open(FILE_INFO) as f:
        file = json.load(f)
    file[f"{ctx.user.id}"] = timezone
    with open(FILE_INFO, mode="w") as f:
        json.dump(file, f)
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
    _ = await ctx.bot.request_guild_members(ctx.guild_id, query='', limit=0)

    with open(FILE_INFO) as f:
        file = json.load(f)
    embed = hikari.Embed(
        title="WorldTimeZone Clock",
        description="",
    ).set_thumbnail(ctx.user.avatar_url)

    def add_field(u, tz):
        print(u)
        user_ = ctx.bot.cache.get_member(ctx.guild_id, int(u))
        print(user_)
        now = datetime.datetime.now()
        new_tz = pytz.timezone(tz)
        new_now = now.astimezone(new_tz)
        embed.add_field(f"{user_.display_name}", f"{new_now}", inline=True)

    if user is None:
        for u, tz in file.items():
            add_field(u, tz)
    else:
        add_field(f"{ctx.user.id}", file[f"{ctx.user.id}"])
    await ctx.respond(embed)


if __name__ == "__main__":
    bot.run()
