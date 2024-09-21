import hikari
import lightbulb
from lightbulb.ext import tasks

from worldtimezone.extensions import calendar_data

@tasks.task(m=1, auto_start=True, pass_app=True)
async def check_events_reminder(bot: lightbulb.BotApp) -> None:
    _ = await bot.wait_for(hikari.StartedEvent, timeout=None)
    cd = bot.d.calendar_data # pyright: ignore[reportAny]
    assert isinstance(cd, calendar_data.CalendarData)

    for event in cd.get_events_need_reminder():
        pass # TODO
