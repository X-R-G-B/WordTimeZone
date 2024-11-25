# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false
import os
from typing import Any, override
import json

import peewee
import pytz
from playhouse.migrate import SqliteMigrator, migrate

FILE_INFO_V2 = ".data/tz_v2.json"
FILE_SQLITE_DB = ".data/tz_v3.db"

db = peewee.SqliteDatabase(FILE_SQLITE_DB)
db_migrator = SqliteMigrator(db)


COMMON_TIMEZONES = [
    "Europe/London",
    "Europe/Paris",
    "Europe/Moscow",
    "Asia/Yekaterinburg",
    "Asia/Bangkok",
    "Asia/Shanghai",
    "Asia/Yakutsk",
    "Australia/Sydney",
    "Asia/Srednekolymsk",
    "Pacific/Fiji",
    "Pacific/Niue",
    "America/Anchorage",
    "America/Vancouver",
    "America/Regina",
    "America/Winnipeg",
    "America/New_York",
    "America/Buenos_Aires",
    "America/Nuuk",
    "Africa/Bamako",
]


def match_timezone(val: str):
    if val == "":
        return COMMON_TIMEZONES
    return [x for x in pytz.all_timezones if val.lower() in x.lower()][:15]


class DBBaseModel(peewee.Model):
    class Meta:
        database = db


class ArrayField(peewee.TextField):
    field_type = "TEXT"

    @override
    def db_value(self, value: list[str]):
        if value:
            return json.dumps(value)
        return "[]"

    @override
    def python_value(self, value: str) -> list[str]:
        if value:
            return json.loads(value)  # pyright: ignore[reportAny]
        return []


class DBGuild(DBBaseModel):
    discord_id = peewee.CharField(unique=True)
    channel_id = peewee.CharField(default="")
    message_id = peewee.CharField(default="")


class DBMember(DBBaseModel):
    discord_id = peewee.CharField()
    tz = peewee.CharField(default="")
    guild = peewee.ForeignKeyField(DBGuild, backref="members")


class WorldClockData:
    def __init__(self):
        _ = db.connect()
        db.create_tables([DBGuild, DBMember])
        message_id_others = ArrayField(default=[])
        migrate(
            db_migrator.add_column(DBGuild._meta.table_name, "message_id_others", message_id_others)
        )
        # START Transform old format to new
        if os.path.isfile(FILE_INFO_V2):
            import json

            with open(FILE_INFO_V2) as f:
                data: dict[str, dict[str, Any]] = json.load(f)
            for guild_id, guild_value in data.items():
                new_guild = DBGuild(discord_id=guild_id)
                if (
                    "worldclockchannel" in guild_value
                    and "channel_id" in guild_value["worldclockchannel"]
                    and "message_id" in guild_value["worldclockchannel"]
                ):
                    new_guild.channel_id = guild_value["worldclockchannel"][
                        "channel_id"
                    ]
                    new_guild.message_id = guild_value["worldclockchannel"][
                        "message_id"
                    ]
                new_guild.save()
                if "members" in guild_value:
                    for (
                        member_id,  # pyright: ignore [reportAny]
                        member_value,  # pyright: ignore [reportAny]
                    ) in guild_value[  # pyright: ignore [reportAny]
                        "members"
                    ].items():
                        new_member = DBMember(
                            discord_id=member_id,  # pyright: ignore [reportAny]
                            guild=new_guild,
                        )
                        if "tz" in member_value:
                            new_member.tz = member_value["tz"]
                        new_member.save()
            os.remove(FILE_INFO_V2)
        # END Transform old format to new

    # Guild

    def create_guild(self, guild_id: str | int) -> DBGuild:
        guild_id = f"{guild_id}"
        guild = DBGuild(discord_id=guild_id)
        guild.save()
        return guild

    def get_guild(self, guild_id: str | int) -> DBGuild | None:
        guild_id = f"{guild_id}"
        try:
            return DBGuild.select().where(DBGuild.discord_id == guild_id).get()
        except DBGuild.DoesNotExist:  # pyright: ignore[reportAttributeAccessIssue]
            return None

    def get_guilds_list(self) -> list[DBGuild]:
        guilds = DBGuild.select()
        return list(guilds)

    def set_guild_world_clock(
        self, guild: DBGuild, channel_id: str | int, message_id: str | int
    ) -> bool:
        channel_id = f"{channel_id}"
        message_id = f"{message_id}"
        guild.channel_id = channel_id  # pyright: ignore [reportAttributeAccessIssue]
        guild.message_id = message_id  # pyright: ignore [reportAttributeAccessIssue]
        guild.save()
        return True

    def add_message_id(self, guild: DBGuild, message_id: str | int) -> bool:
        message_id = f"{message_id}"
        guild.message_id_others.append(message_id)
        guild.save()
        return True

    def remove_message_id(self, guild: DBGuild, messages_id: list[str | int]) -> bool:
        new_list = []
        messages_id_ = [f"{x}" for x in messages_id]
        for elem in guild.message_id_others:
            if elem not in messages_id_:
                new_list.append(elem)
        guild.message_id_others = new_list
        guild.save()

    # Member

    def create_member(self, guild: DBGuild, user_id: str | int) -> DBMember:
        user_id = f"{user_id}"
        member = DBMember(discord_id=user_id, guild=guild)
        member.save()
        return member

    def get_member(self, guild_id: str | int, user_id: str | int) -> DBMember | None:
        guild_id = f"{guild_id}"
        user_id = f"{user_id}"
        try:
            return (
                DBMember.select()
                .join(DBGuild)
                .where(
                    (DBMember.discord_id == user_id) & (DBGuild.discord_id == guild_id)
                )
                .get()
            )
        except DBMember.DoesNotExist:  # pyright: ignore[reportAttributeAccessIssue]
            return None

    def get_members_list(self, guild_id: str | int) -> list[DBMember] | None:
        guild_id = f"{guild_id}"
        try:
            return DBGuild.select().where(DBGuild.discord_id == guild_id).get().members
        except DBGuild.DoesNotExist:  # pyright: ignore[reportAttributeAccessIssue]
            return None

    def set_member_tz(self, member: DBMember, tz: str) -> bool:
        if tz not in pytz.all_timezones:
            return False
        member.tz = tz  # pyright: ignore [reportAttributeAccessIssue]
        member.save()
        return True
