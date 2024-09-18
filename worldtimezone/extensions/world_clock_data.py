import json

import pytz

FILE_INFO = ".data/tz_v2.json"


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


class WorldClockData:
    def __init__(self):
        try:
            with open(FILE_INFO) as f:
                file = json.load(f)
        except FileNotFoundError:
            with open(FILE_INFO, mode="w") as f:
                file = {}
                json.dump(file, f)
        self._data = file

    def get_guilds_list(self) -> list:
        return list(self._data)

    def get_member(self, guild_id, user_id) -> dict:
        guild_id = f"{guild_id}"
        user_id = f"{user_id}"
        if guild_id not in self._data:
            return {}
        if user_id not in self._data[guild_id]["members"]:
            return {}
        member = self._data[guild_id]["members"][user_id]
        return member

    def get_members_list(self, guild_id) -> list:
        guild_id = f"{guild_id}"
        if guild_id not in self._data:
            return []
        if "members" not in self._data[guild_id]:
            return []
        return list(self._data[guild_id]["members"].keys())

    def set_member_tz(self, guild_id, user_id, tz) -> str:
        if tz not in pytz.all_timezones:
            return False
        guild_id = f"{guild_id}"
        user_id = f"{user_id}"
        tz = f"{tz}"
        if guild_id not in self._data:
            self._data[guild_id] = {}
        if "members" not in self._data[guild_id]:
            self._data[guild_id]["members"] = {}
        if user_id not in self._data[guild_id]["members"]:
            self._data[guild_id]["members"][user_id] = {}
        self._data[guild_id]["members"][user_id]["tz"] = tz
        with open(FILE_INFO, mode="w") as f:
            json.dump(self._data, f)
        return True

    def set_world_clock(self, guild_id, channel_id, message_id) -> bool:
        guild_id = f"{guild_id}"
        channel_id = f"{channel_id}"
        message_id = f"{message_id}"
        if guild_id not in self._data:
            self._data[guild_id] = {}
        if "worldclockchannel" not in self._data[guild_id]:
            self._data[guild_id]["worldclockchannel"] = {}
        self._data[guild_id]["worldclockchannel"]["channel_id"] = channel_id
        self._data[guild_id]["worldclockchannel"]["message_id"] = message_id
        with open(FILE_INFO, mode="w") as f:
            json.dump(self._data, f)
        return True

    def get_world_clock(self, guild_id) -> dict:
        guild_id = f"{guild_id}"
        if guild_id not in self._data:
            return {}
        if "worldclockchannel" not in self._data[guild_id]:
            return {}
        return self._data[guild_id]["worldclockchannel"]
