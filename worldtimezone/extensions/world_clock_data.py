import os
from typing import Optional

import peewee
import pytz

FILE_INFO_V2 = ".data/tz_v2.json"
FILE_SQLITE_DB = ".data/tz_v3.db"

db = peewee.SqliteDatabase(FILE_SQLITE_DB)


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


class DBBaseModel(peewee.Model):
    class Meta:
        database = db


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
        db.connect()
        db.create_tables([DBGuild, DBMember])
        # START Transform old format to new
        if os.path.isfile(FILE_INFO_V2):
            import json

            with open(FILE_INFO_V2) as f:
                data = json.load(f)
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
                    for member_id, member_value in guild_value["members"].items():
                        new_member = DBMember(
                            discord_id=member_id,
                            guild=new_guild,
                        )
                        if "tz" in member_value:
                            new_member.tz = member_value["tz"]
                        new_member.save()
            os.remove(FILE_INFO_V2)
        # END Transform old format to new

    # Guild

    def get_guild(self, guild_id) -> Optional[DBGuild]:
        guild_id = f"{guild_id}"
        try:
            return DBGuild.select().where(DBGuild.discord_id == guild_id).get()
        except DBGuild.DoesNotExist:
            return None

    def get_guilds_list(self) -> list[DBGuild]:
        guilds = DBGuild.select()
        return list(guilds)

    def set_guild_world_clock(self, guild: DBGuild, channel_id, message_id) -> bool:
        channel_id = f"{channel_id}"
        message_id = f"{message_id}"
        guild.channel_id = channel_id
        guild.message_id = message_id
        guild.save()
        return True

    # Member

    def get_member(self, guild_id, user_id) -> Optional[DBMember]:
        guild_id = f"{guild_id}"
        user_id = f"{user_id}"
        try:
            return (
                DBMember.select()
                .join(DBGuild)
                .where(
                    (DBMember.discord_id == user_id)
                    & (DBGuild.discord_id == guild_id)
                )
                .get()
            )
        except DBMember.DoesNotExist:
            return None

    def get_members_list(self, guild_id) -> Optional[list[DBMember]]:
        guild_id = f"{guild_id}"
        try:
            return DBGuild.select().where(DBGuild.discord_id == guild_id).get().members
        except DBGuild.DoesNotExist:
            return None

    def set_member_tz(self, member: DBMember, tz: str) -> str:
        if tz not in pytz.all_timezones:
            return False
        member.tz = tz
        member.save()
        return True
