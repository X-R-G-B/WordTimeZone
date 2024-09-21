from extensions.world_clock_data import match_timezone
from extensions import calendar_data
import lightbulb
import datetime
import pytz

from worldtimezone.extensions import world_clock_data

plugin = lightbulb.Plugin("Calendar")


@lightbulb.add_checks(lightbulb.human_only)
@plugin.command
@lightbulb.add_cooldown(5, 1, lightbulb.UserBucket)
@lightbulb.option("title", "title of the event", type=str, required=True)
@lightbulb.option("start_hour", "start hour", type=int, required=True)
@lightbulb.option("start_minute", "start minute", type=int, required=False, default=0)
@lightbulb.option("start_day", "start day", type=int, required=False)
@lightbulb.option("start_month", "start month", type=int, required=False)
@lightbulb.option("start_year", "start year", type=int, required=False)
@lightbulb.option(
    "timezone",
    "timezone of the time|date (default is yours)",
    type=str,
    required=False,
    autocomplete=True,
)
@lightbulb.option("end_hour", "end hour", type=int, required=True)
@lightbulb.option("end_minute", "end minute", type=int, required=False, default=0)
@lightbulb.option("end_day", "end day", type=int, required=False)
@lightbulb.option("end_month", "end month", type=int, required=False)
@lightbulb.option("end_year", "end year", type=int, required=False)
@lightbulb.option("reminder_hour", "reminder hour", type=int, required=True)
@lightbulb.option(
    "reminder_minute", "reminder minute", type=int, required=False, default=0
)
@lightbulb.option("reminder_day", "reminder day", type=int, required=False)
@lightbulb.option("reminder_month", "reminder month", type=int, required=False)
@lightbulb.option("reminder_year", "reminder year", type=int, required=False)
@lightbulb.option(
    "reminder_number", "number of reminder", type=int, required=False, default=1
)
@lightbulb.option(
    "reminder_interval",
    "number of minutes between reminder",
    type=int,
    required=False,
    default=5,
)
@lightbulb.command(
    "add_complex", description="create a new event (the hard way)", pass_options=True
)
@lightbulb.implements(lightbulb.SlashCommand)
async def addIt(
    ctx: lightbulb.SlashContext,
    title: str,
    start_hour: int,
    start_minute: int,
    start_day: int | None,
    start_month: int | None,
    start_year: int | None,
    timezone: str | None,
    end_hour: int,
    end_minute: int | None,
    end_day: int | None,
    end_month: int | None,
    end_year: int | None,
    reminder_hour: int | None,
    reminder_minute: int | None,
    reminder_day: int | None,
    reminder_month: int | None,
    reminder_year: int | None,
    reminder_number: int,
    reminder_interval: int,
) -> None:
    wcd = ctx.bot.d.world_clock_data  # pyright: ignore[reportAny]
    assert isinstance(wcd, world_clock_data.WorldClockData)
    assert ctx.guild_id is not None
    user_info = wcd.get_member(ctx.guild_id, ctx.user.id)
    if timezone is None and (user_info is None or user_info.tz == ""):
        _ = await ctx.respond("Please set your timezone first")
        return
    now = datetime.datetime.now()
    if timezone is None:
        assert user_info is not None
        now = pytz.timezone(
            user_info.tz  # pyright: ignore[reportArgumentType]
        ).localize(now)
    else:
        now = pytz.timezone(timezone).localize(now)
    if start_day is None:
        start_day = now.day
    if start_month is None:
        start_month = now.month
    if start_year is None:
        start_year = now.year
    start_date = datetime.datetime(
        year=start_year,
        month=start_month,
        day=start_day,
        hour=start_hour,
        minute=start_minute,
    )
    if timezone is None:
        assert user_info is not None
        start_date = pytz.timezone(
            user_info.tz  # pyright: ignore[reportArgumentType]
        ).localize(start_date)
    else:
        start_date = pytz.timezone(timezone).localize(start_date)

    if end_minute is None:
        end_minute = start_minute
    if end_day is None:
        end_day = start_day
    if end_month is None:
        end_month = start_month
    if end_year is None:
        end_year = start_year
    end_date = datetime.datetime(
        year=end_year, month=end_month, day=end_day, hour=end_hour, minute=end_minute
    )
    if timezone is None:
        assert user_info is not None
        end_date = pytz.timezone(
            user_info.tz  # pyright: ignore[reportArgumentType]
        ).localize(end_date)
    else:
        end_date = pytz.timezone(timezone).localize(end_date)

    reminder_hour_was_setup = True
    if reminder_hour is None:
        reminder_hour_was_setup = False
        reminder_hour = start_hour
    if reminder_minute is None:
        reminder_minute = start_minute
    if reminder_day is None:
        reminder_day = start_day
    if reminder_month is None:
        reminder_month = start_month
    if reminder_year is None:
        reminder_year = start_year
    reminder_date = datetime.datetime(
        year=reminder_year,
        month=reminder_month,
        day=reminder_day,
        hour=reminder_hour,
        minute=reminder_minute,
    )
    if not reminder_hour_was_setup:
        reminder_date = reminder_date - datetime.timedelta(hours=1)
    if timezone is None:
        assert user_info is not None
        reminder_date = pytz.timezone(
            user_info.tz  # pyright: ignore[reportArgumentType]
        ).localize(reminder_date)
    else:
        reminder_date = pytz.timezone(timezone).localize(reminder_date)
    if reminder_number == 0:
        reminder_date = None
    cd = ctx.bot.d.calendar_data  # pyright: ignore[reportAny]
    assert isinstance(cd, calendar_data.CalendarData)
    user = cd.get_user(ctx.user.id)
    if user is None:
        user = cd.create_user(ctx.user.id)
    cd.create_event(
        user,
        title,
        start_date,
        end_date,
        reminder_date,
        reminder_number,
        reminder_interval,
    )
    _ = ctx.respond(f"Event `{title}` created")


@addIt.autocomplete("timezone")
async def addIt_autocomplete_timezone(
    opt,  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    inter,  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType, reportUnusedParameter]
):
    return match_timezone(
        opt.value  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
    )


def load(bot: lightbulb.BotApp):
    bot.d.calendar_data = calendar_data.CalendarData()
    bot.load_extensions("extensions.calendar_tasks")
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
