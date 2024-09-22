import hikari
import lightbulb
from lightbulb.ext import tasks
from extensions import calendar_data


@tasks.task(m=1, auto_start=True, pass_app=True)
async def check_events_reminder(bot: lightbulb.BotApp) -> None:
    _ = await bot.wait_for(hikari.StartedEvent, timeout=None)
    cd = bot.d.calendar_data  # pyright: ignore[reportAny]
    assert isinstance(cd, calendar_data.CalendarData)

    async def send_event(event: calendar_data.DBEvent) -> bool:
        user_ = bot.cache.get_user(
            event.user.discord_id  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        )
        if user_ is None:
            user_ = await bot.rest.fetch_user(
                event.user.discord_id  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
            )
        embed = (
            hikari.Embed(
                title=f"{event.title}", description=f"{event.start} - {event.end}"
            )
            .set_author(name=f"{user_.display_name}")
            .set_thumbnail(user_.avatar_url)
        )
        _ = await user_.send(embed)
        return True

    sent_events: list[calendar_data.DBEvent] = []
    for event in cd.get_events_need_reminder():
        res = await send_event(event)
        if res is True:
            sent_events.append(event)

    cd.set_event_done_reminder(sent_events)


def load(bot: lightbulb.BotApp):  # pyright: ignore[reportUnusedParameter]
    pass


def unload(bot: lightbulb.BotApp):  # pyright: ignore[reportUnusedParameter]
    pass
