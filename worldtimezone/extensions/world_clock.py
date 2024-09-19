import datetime
from typing import Optional

import hikari
import lightbulb
import pytz
from extensions import world_clock_data

plugin = lightbulb.Plugin("WorldClock")


@lightbulb.add_checks(lightbulb.human_only)
@plugin.command
@lightbulb.add_cooldown(5, 1, lightbulb.UserBucket)
@lightbulb.option(
    "timezone", "Your TimeZone", type=str, required=False, autocomplete=True
)
@lightbulb.command("set", description="Set your TimeZone", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def setIt(ctx: lightbulb.SlashContext, timezone: Optional[str] = None) -> None:
    wcd = ctx.bot.d.world_clock_data
    user = wcd.get_member(ctx.guild_id, ctx.user.id)
    if user is None:
        guild = wcd.get_guild(ctx.guild_id)
        if guild is None:
            guild = wcd.create_guild(ctx.guild_id)
        user = wcd.create_member(guild, ctx.user.id)
    res = wcd.set_member_tz(user, timezone)
    if res is False:
        await ctx.respond(
            f"Failed, please provide a working timezone ('{timezone}' is unknow)"
        )
        return
    await ctx.respond("Your TimeZone as been set!")


@setIt.autocomplete("timezone")
async def setIt_autocomplete_timezone(opt, inter):
    return world_clock_data.match_timezone(opt.value)


@lightbulb.add_checks(lightbulb.human_only)
@plugin.command
@lightbulb.add_cooldown(5, 1, lightbulb.UserBucket)
@lightbulb.command("timezone", description="List common timezones")
@lightbulb.implements(lightbulb.SlashCommand)
async def timezoneIt(ctx: lightbulb.SlashContext) -> None:
    ctx.respond(
        f"{world_clock_data.COMMON_TIMEZONES}\nFor all timezones: <https://github.com/stub42/pytz/blob/master/tz/zone.tab>"
    )


@lightbulb.add_checks(lightbulb.human_only)
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
    embed = hikari.Embed(
        title="WorldTimeZone Clock",
        description="",
    ).set_thumbnail(ctx.user.avatar_url)
    wcd = ctx.bot.d.world_clock_data

    def add_field(member_id, tz):
        user_ = ctx.bot.cache.get_member(ctx.guild_id, int(member_id))
        now = datetime.datetime.now()
        new_tz = pytz.timezone(tz)
        new_now = now.astimezone(new_tz)
        embed.add_field(f"{user_.display_name}", f"{new_now}", inline=False)

    if user is None:
        for member in wcd.get_members_list(ctx.guild_id):
            if member.tz != "":
                add_field(member.discord_id, member.tz)
    else:
        member = wcd.get_member(ctx.guild_id, user.id)
        if member is None or member.tz == "":
            ctx.respond("This user has no timezone set.")
            return
        add_field(f"{user.id}", member.tz)
    await ctx.respond(embed)


@lightbulb.add_checks(lightbulb.human_only)
@plugin.command
@lightbulb.option("hour", "hour", type=int, required=True)
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
    "timezone",
    "timezone of the time|date (default is yours)",
    type=str,
    required=False,
    autocomplete=True,
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
    wcd = ctx.bot.d.world_clock_data
    message = ""
    user_info = wcd.get_member(ctx.guild_id, ctx.user.id)
    if user_info is None or user_info.tz == "":
        await ctx.respond("Please set your timezone first")
        return
    now = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    if timezone is None:
        now = pytz.timezone(user_info.tz).localize(now)
    else:
        now = pytz.timezone(timezone).localize(now)
    for member_info in wcd.get_members_list(ctx.guild_id) or []:
        if member_info.tz != "":
            user_ = ctx.bot.cache.get_member(ctx.guild_id, int(member_info.discord_id))
            new_tz = pytz.timezone(member_info.tz)
            new_now = now.astimezone(new_tz)
            message += f"**{user_.display_name}**: {new_now} [{member_info.tz}]\n"
    if len(message) == 0:
        await ctx.respond("No timezone to convert to (use `/set` SlashCommand)")
        return
    await ctx.respond(message)


@convertIt.autocomplete("timezone")
async def convertIt_autocomplete_timezone(opt, inter):
    return world_clock_data.match_timezone(opt.value)


@lightbulb.add_checks(lightbulb.human_only)
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
    wcd = ctx.bot.d.world_clock_data
    message = await ctx.bot.rest.create_message(
        channel, "This message will be edited in no time... Please wait..."
    )
    guild = wcd.get_guild(ctx.guild_id)
    if guild is None:
        guild = wcd.create_guild(ctx.guild_id)
    status = wcd.set_guild_world_clock(guild, channel.id, message.id)
    if status is False:
        await message.delete()
        ctx.respond("Sorry, an error occured.")
        return
    await ctx.respond(
        "All Set! A message has been sent to the channel, it will be edited soon."
    )


def load(bot: lightbulb.BotApp):
    bot.d.world_clock_data = world_clock_data.WorldClockData()
    bot.load_extensions("extensions.world_clock_tasks")
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
