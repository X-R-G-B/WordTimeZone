# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false
import datetime
from typing import override

import peewee

FILE_SQLITE_DB = ".data/calendar.db"

db = peewee.SqliteDatabase(FILE_SQLITE_DB)


class TimestampField(peewee.DateTimeField):
    field_type = "TEXT"

    @override
    def db_value(self, value: datetime.datetime) -> str:
        if value:
            return value.isoformat()

    @override
    def python_value(self, value: str) -> datetime.datetime:
        if value:
            return datetime.datetime.fromisoformat(value)
        raise ValueError("unknow value")


class DBBaseModel(peewee.Model):
    class Meta:
        database = db


class DBUser(DBBaseModel):
    discord_id = peewee.CharField(unique=True)


class DBEvent(DBBaseModel):
    title = peewee.TextField()
    start = TimestampField()
    end = TimestampField()
    user = peewee.ForeignKeyField(DBUser, backref="events")
    reminder = TimestampField(null=True, default=None)
    number_of_reminder = peewee.IntegerField(default=0)
    minutes_between_reminder = peewee.IntegerField(default=5)


class CalendarData:
    def __init__(self):
        _ = db.connect()
        db.create_tables([DBUser, DBEvent])

    # User

    def create_user(self, user_id: str | int) -> DBUser:
        user_id = f"{user_id}"
        user = DBUser(discord_id=user_id)
        user.save()
        return user

    def get_user(self, user_id: str | int) -> DBUser | None:
        user_id = f"{user_id}"
        try:
            return DBUser.select().where(DBUser.discord_id == user_id).get()
        except DBUser.DoesNotExist:  # pyright: ignore[reportAttributeAccessIssue]
            return None

    # Event

    def create_event(
        self,
        user: DBUser,
        title: str,
        start: datetime.datetime,
        end: datetime.datetime,
        reminder: datetime.datetime | None,
        number_of_reminder: int = 0,
        minutes_between_reminder: int = 5,
    ):
        event = DBEvent(
            title=title,
            start=start,
            end=end,
            user=user,
            reminder=reminder,
            number_of_reminder=number_of_reminder,
            minutes_between_reminder=minutes_between_reminder,
        )
        event.save()

    def get_events_list(self, user: DBUser) -> list[DBEvent]:
        return list(user.events)  # pyright: ignore[reportAttributeAccessIssue]

    def get_events_need_reminder(self) -> list[DBEvent]:
        now = datetime.datetime.now().timestamp()
        return list(DBEvent.select().where(now > DBEvent.reminder.to_timestamp()))

    def set_event_done_reminder(self, events: list[DBEvent]):
        for event in events:
            event.number_of_reminder -= 1
            if event.number_of_reminder == 0:
                event.reminder = None  # pyright: ignore[reportAttributeAccessIssue]
            else:
                timedelta = datetime.timedelta(
                    minutes=float(
                        event.minutes_between_reminder  # pyright: ignore[reportArgumentType]
                    )
                )
                event.reminder = (  # pyright: ignore[reportAttributeAccessIssue]
                    event.reminder + timedelta
                )
        DBEvent.bulk_update(
            events, [DBEvent.number_of_reminder, DBEvent.reminder], batch_size=10
        )
