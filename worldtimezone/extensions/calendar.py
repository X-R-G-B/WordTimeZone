import datetime
from typing import override

import dateparser
import lightbulb
import miru
import pytz
from extensions import calendar_data, world_clock_data

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
async def add_complexIt(
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
    _ = await ctx.respond(f"Event `{title}` created")


@add_complexIt.autocomplete("timezone")
async def addIt_autocomplete_timezone(
    opt,  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
    inter,  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType, reportUnusedParameter]
):
    return world_clock_data.match_timezone(
        opt.value  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
    )


class AddEventModal(miru.Modal, title="Add Event"):
    e_title = miru.TextInput(label="Title", placeholder="Event Name", required=True)
    e_start = miru.TextInput(
        label="Start", placeholder="20 september, 10:00", required=True
    )
    e_end = miru.TextInput(label="End", placeholder="2024-09-20 11:00", required=True)
    e_reminder = miru.TextInput(
        label="Reminder", placeholder="2024-09-20 09:50:00", required=False
    )
    e_reminder_number = miru.TextInput(
        label="Number of Reminder", value="1", required=True
    )
    e_reminder_interval = miru.TextInput(
        label="Minute(s) Interval between Reminders", value="5", required=True
    )
    e_timezone = miru.TextInput(
        label="Timezone", placeholder="(your timezone by default)", required=False
    )

    @override
    async def callback(self, ctx: miru.ModalContext) -> None:
        wcd = (  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
            ctx.client.app.d.world_clock_data  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
        )
        assert isinstance(wcd, world_clock_data.WorldClockData)
        assert ctx.guild_id is not None
        user_info = wcd.get_member(ctx.guild_id, ctx.user.id)
        if self.e_timezone.value is None and (user_info is None or user_info.tz == ""):
            _ = await ctx.respond("Please set your timezone first")
            return
        now = datetime.datetime.now()
        if self.e_timezone.value is None:
            assert user_info is not None
            now = pytz.timezone(
                user_info.tz  # pyright: ignore[reportArgumentType]
            ).localize(now)
        else:
            now = pytz.timezone(self.e_timezone.value).localize(now)

        assert self.e_start.value is not None  # Field Required
        start_date = dateparser.parse(self.e_start.value)
        if start_date is None:
            _ = await ctx.respond(f"Can't parse {self.e_start.value} to a date")
            return
        if self.e_timezone.value is None:
            assert user_info is not None
            start_date = pytz.timezone(
                user_info.tz  # pyright: ignore[reportArgumentType]
            ).localize(start_date)
        else:
            start_date = pytz.timezone(self.e_timezone.value).localize(start_date)

        assert self.e_end.value is not None  # Field Required
        end_date = dateparser.parse(self.e_end.value)
        if end_date is None:
            _ = await ctx.respond(f"Can't parse {self.e_end.value} to a date")
            return
        if self.e_timezone.value is None:
            assert user_info is not None
            end_date = pytz.timezone(
                user_info.tz  # pyright: ignore[reportArgumentType]
            ).localize(end_date)
        else:
            end_date = pytz.timezone(self.e_timezone.value).localize(end_date)

        if self.e_reminder.value is None:
            reminder_date = start_date - datetime.timedelta(hours=1)
        else:
            reminder_date = dateparser.parse(self.e_reminder.value)
            if reminder_date is None:
                _ = await ctx.respond(f"Can't parse {self.e_reminder.value} to a date")
                return
            if self.e_timezone.value is None:
                assert user_info is not None
                reminder_date = pytz.timezone(
                    user_info.tz  # pyright: ignore[reportArgumentType]
                ).localize(reminder_date)
            else:
                reminder_date = pytz.timezone(self.e_timezone.value).localize(
                    reminder_date
                )

        reminder_number = 0
        try:
            assert self.e_reminder_number.value is not None  # Field required
            reminder_number = int(self.e_reminder_number.value)
        except ValueError:
            _ = await ctx.respond(
                f"Can't parse {self.e_reminder_number.value} to number"
            )
            return
        if reminder_number == 0:
            reminder_date = None

        reminder_interval = 0
        try:
            assert self.e_reminder_interval.value is not None  # Field required
            reminder_interval = int(self.e_reminder_interval.value)
        except ValueError:
            _ = await ctx.respond(
                f"Can't parse {self.e_reminder_interval.value} to number"
            )
            return

        cd = (  # pyright: ignore [reportUnknownMemberType, reportUnknownVariableType]
            ctx.client.app.d.calendar_data  # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType]
        )
        assert isinstance(cd, calendar_data.CalendarData)
        user = cd.get_user(ctx.user.id)
        if user is None:
            user = cd.create_user(ctx.user.id)
        assert self.e_title.value is not None  # Field required
        cd.create_event(
            user,
            self.e_title.value,
            start_date,
            end_date,
            reminder_date,
            reminder_number,
            reminder_interval,
        )
        _ = await ctx.respond(f"Event `{self.e_title.value}` created")


@lightbulb.add_checks(lightbulb.human_only)
@plugin.command
@lightbulb.command("add", description="create an event with a nice UI")
@lightbulb.implements(lightbulb.SlashCommand)
async def addIt(ctx: lightbulb.SlashContext) -> None:
    modal = AddEventModal()
    miru_client = ctx.bot.d.miru  # pyright: ignore[reportAny]
    assert isinstance(miru_client, miru.Client)
    builder = modal.build_response(miru_client)
    await builder.create_modal_response(ctx.interaction)
    miru_client.start_modal(modal)


def load(bot: lightbulb.BotApp):
    bot.d.calendar_data = calendar_data.CalendarData()
    bot.load_extensions("extensions.calendar_tasks")
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
