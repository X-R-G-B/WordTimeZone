import datetime

import hikari
import lightbulb
import pytz
from extensions import world_clock_data

plugin = lightbulb.Plugin("WorldClock")


@lightbulb.add_checks(lightbulb.human_only)
@plugin.command
@lightbulb.add_cooldown(5, 1, lightbulb.UserBucket)
@lightbulb.option(
    "timezone", "Your TimeZone", type=str, required=True, autocomplete=True
)
@lightbulb.command("set", description="Set your TimeZone", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def setIt(ctx: lightbulb.SlashContext, timezone: str) -> None:
    wcd = ctx.bot.d.world_clock_data  # pyright: ignore[reportAny]
    assert isinstance(wcd, world_clock_data.WorldClockData)
    assert ctx.guild_id is not None
    user = wcd.get_member(ctx.guild_id, ctx.user.id)
    if user is None:
        guild = wcd.get_guild(ctx.guild_id)
        if guild is None:
            guild = wcd.create_guild(ctx.guild_id)
        user = wcd.create_member(guild, ctx.user.id)
    res = wcd.set_member_tz(user, timezone)
    if res is False:
        _ = await ctx.respond(
            f"Failed, please provide a working timezone ('{timezone}' is unknow)"
        )
        return
    _ = await ctx.respond("Your TimeZone as been set!")


@setIt.autocomplete("timezone")
async def setIt_autocomplete_timezone(
    opt,  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    inter,  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType, reportUnusedParameter]
):
    return world_clock_data.match_timezone(
        opt.value  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
    )


@lightbulb.add_checks(lightbulb.human_only)
@plugin.command
@lightbulb.add_cooldown(5, 1, lightbulb.UserBucket)
@lightbulb.command("timezone", description="List common timezones")
@lightbulb.implements(lightbulb.SlashCommand)
async def timezoneIt(ctx: lightbulb.SlashContext) -> None:
    _ = ctx.respond(
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
async def listIt(ctx: lightbulb.SlashContext, user: hikari.User | None) -> None:
    embed = hikari.Embed(
        title="WorldTimeZone Clock",
        description="",
    ).set_thumbnail(ctx.user.avatar_url)
    wcd = ctx.bot.d.world_clock_data  # pyright: ignore[reportAny]
    assert isinstance(wcd, world_clock_data.WorldClockData)
    assert ctx.guild_id is not None

    async def add_field(member_id: int, tz: str):
        assert ctx.guild_id is not None
        user_ = ctx.bot.cache.get_member(ctx.guild_id, member_id)
        if user_ is None:
            user_ = await ctx.bot.rest.fetch_member(ctx.guild_id, member_id)
        now = datetime.datetime.now()
        new_tz = pytz.timezone(tz)
        new_now = now.astimezone(new_tz)
        _ = embed.add_field(f"{user_.display_name}", f"{new_now}", inline=False)

    if user is None:
        for member in wcd.get_members_list(ctx.guild_id) or []:
            if member.tz != "":
                await add_field(
                    member.discord_id,  # pyright: ignore[reportArgumentType]
                    member.tz,  # pyright: ignore[reportArgumentType]
                )
    else:
        member = wcd.get_member(ctx.guild_id, user.id)
        if member is None or member.tz == "":
            _ = ctx.respond("This user has no timezone set.")
            return
        await add_field(user.id, member.tz)  # pyright: ignore[reportArgumentType]
    _ = await ctx.respond(embed)


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
    timezone: str | None,
) -> None:
    if timezone is not None and timezone not in pytz.all_timezones:
        _ = await ctx.respond(
            f"Failed, please provide a working timezone ('{timezone}' is unknow)"
        )
        return
    wcd = ctx.bot.d.world_clock_data  # pyright: ignore[reportAny]
    assert isinstance(wcd, world_clock_data.WorldClockData)
    assert ctx.guild_id is not None
    message = ""
    user_info = wcd.get_member(ctx.guild_id, ctx.user.id)
    if user_info is None or user_info.tz == "":
        _ = await ctx.respond("Please set your timezone first")
        return
    now = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
    if timezone is None:
        now = pytz.timezone(
            user_info.tz  # pyright: ignore[reportArgumentType]
        ).localize(now)
    else:
        now = pytz.timezone(timezone).localize(now)
    for member_info in wcd.get_members_list(ctx.guild_id) or []:
        if member_info.tz != "":
            user_ = ctx.bot.cache.get_member(
                ctx.guild_id,
                int(member_info.discord_id),  # pyright: ignore[reportArgumentType]
            )
            if user_ is None:
                user_ = await ctx.bot.rest.fetch_member(
                    ctx.guild_id,
                    int(member_info.discord_id),  # pyright: ignore[reportArgumentType]
                )
            new_tz = pytz.timezone(
                member_info.tz  # pyright: ignore[reportArgumentType]
            )
            new_now = now.astimezone(new_tz)
            message += f"**{user_.display_name}**: {new_now} [{member_info.tz}]\n"
    if len(message) == 0:
        _ = await ctx.respond("No timezone to convert to (use `/set` SlashCommand)")
        return
    _ = await ctx.respond(message)


@convertIt.autocomplete("timezone")
async def convertIt_autocomplete_timezone(
    opt,  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    inter,  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType, reportUnusedParameter]
):
    return world_clock_data.match_timezone(
        opt.value  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
    )


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
    ctx: lightbulb.SlashContext, channel: hikari.GuildTextChannel
) -> None:
    wcd = ctx.bot.d.world_clock_data  # pyright: ignore[reportAny]
    assert isinstance(wcd, world_clock_data.WorldClockData)
    assert ctx.guild_id is not None
    message = await ctx.bot.rest.create_message(
        channel, "This message will be edited in no time... Please wait..."
    )
    guild = wcd.get_guild(ctx.guild_id)
    if guild is None:
        guild = wcd.create_guild(ctx.guild_id)
    status = wcd.set_guild_world_clock(guild, channel.id, message.id)
    if status is False:
        await message.delete()
        _ = ctx.respond("Sorry, an error occured.")
        return
    _ = await ctx.respond(
        "All Set! A message has been sent to the channel, it will be edited soon."
    )


def load(bot: lightbulb.BotApp):
    bot.d.world_clock_data = world_clock_data.WorldClockData()
    bot.load_extensions("extensions.world_clock_tasks")
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
