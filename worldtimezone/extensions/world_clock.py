import datetime
from typing import Optional

import hikari
import lightbulb
import pytz

from worldtimezone.extensions import world_clock_data

plugin = lightbulb.Plugin("WorldClock")


@plugin.command
@lightbulb.add_cooldown(5, 1, lightbulb.UserBucket)
@lightbulb.option(
    "timezone", "Your TimeZone", type=str, required=False, choices=pytz.all_timezones
)
@lightbulb.command("set", description="Set your TimeZone", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def setIt(ctx: lightbulb.SlashContext, timezone: Optional[str] = None) -> None:
    res = ctx.bot.d.data.set_member_tz(ctx.guild_id, ctx.user.id, timezone)
    if res is False:
        await ctx.respond(
            f"Failed, please provide a working timezone ('{timezone}' is unknow)"
        )
        return
    await ctx.respond("Your TimeZone as been set!")


@plugin.command
@lightbulb.add_cooldown(2, 1, lightbulb.GuildBucket)
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
        for u in ctx.bot.d.data.get_members_list(ctx.guild_id):
            member = ctx.bot.d.data.get_member(ctx.guild_id, u)
            if "tz" in member:
                add_field(u, member["tz"])
    else:
        member = ctx.bot.d.data.get_member(ctx.guild_id, user.id)
        if "tz" in member:
            add_field(f"{user.id}", member["tz"])
        else:
            ctx.respond("This user has no timezone set.")
            return
    await ctx.respond(embed)


@plugin.command
@lightbulb.option("hour", "hour in your timezone", type=int, required=True)
@lightbulb.option("minute", "minute", type=int, required=False, default=0)
@lightbulb.option(
    "day",
    "day",
    type=int,
    required=False,
    default=datetime.datetime.now().day,
)
@lightbulb.option(
    "month",
    "month",
    type=int,
    required=False,
    default=datetime.datetime.now().month,
)
@lightbulb.option(
    "year",
    "year",
    type=int,
    required=False,
    default=datetime.datetime.now().year,
)
@lightbulb.option(
    "timezone" "timezone of the time|date (default is yours)",
    type=str,
    required=False,
    choices=pytz.all_timezones,
)
@lightbulb.command(
    "convert",
    description="convert a specific time to others timezone",
    pass_options=True,
)
@lightbulb.implements(lightbulb.SlashCommand)
async def convertIt(
    ctx: lightbulb.SlashContext,
    hour: int,
    minute: int,
    day: int,
    month: int,
    year: int,
    timezone: Optional[str],
) -> None:
    if timezone is not None and timezone not in pytz.all_timezones:
        await ctx.respond(
            f"Failed, please provide a working timezone ('{timezone}' is unknow)"
        )
        return
    message = ""
    user_info = ctx.bot.d.data.get_member(ctx.guild_id, ctx.user.id)
    if "tz" not in user_info:
        await ctx.respond("Please set your timezone first")
        return
    now = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    if timezone is None:
        now = pytz.timezone(user_info["tz"]).localize(now)
    else:
        now = pytz.timezone(timezone).localize(now)
    for u in ctx.bot.d.data.get_members_list(ctx.guild_id):
        member_info = ctx.bot.d.data.get_member(ctx.guild_id, u)
        if "tz" in member_info:
            user_ = ctx.bot.cache.get_member(ctx.guild_id, int(u))
            new_tz = pytz.timezone(member_info["tz"])
            new_now = now.astimezone(new_tz)
            message += f"**{user_.display_name}**: {new_now}\n"
    await ctx.respond(message)


@plugin.command
@lightbulb.add_cooldown(10, 1, lightbulb.GuildBucket)
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
    message = await ctx.bot.rest.create_message(
        channel, "This message will be edited in no time... Please wait..."
    )
    status = ctx.bot.d.data.set_world_clock(ctx.guild_id, channel.id, message.id)
    if status is False:
        await message.delete()
        ctx.respond("Sorry, an error occured.")
        return
    await ctx.respond(
        "All Set! A message has been sent to the channel, it will be edited soon."
    )


def load(bot: lightbulb.BotApp):
    bot.d.data = world_clock_data.WorldClockData()
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
