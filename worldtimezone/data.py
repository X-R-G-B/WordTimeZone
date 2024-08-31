import json

import pytz

FILE_INFO = ".data/tz_v2.json"


class Data:
    def __init__(self):
        try:
            with open(FILE_INFO) as f:
                file = json.load(f)
        except FileNotFoundError:
            with open(FILE_INFO, mode="w") as f:
                json.dump({}, f)
                file = {}
        self._data = file

    def get_member(self, guild_id, user_id) -> dict:
        guild_id = f"{guild_id}"
        user_id = f"{user_id}"
        if guild_id not in self._data:
            return {}
        if user_id not in self._data[guild_id]:
            return {}
        member = self._data[guild_id][user_id]
        return member

    def get_members_list(self, guild_id) -> list:
        guild_id = f"{guild_id}"
        if guild_id not in self._data:
            return []
        return list(self._data[guild_id].keys())

    def set_member_tz(self, guild_id, user_id, tz) -> str:
        if tz not in pytz.all_timezones:
            return False
        guild_id = f"{guild_id}"
        user_id = f"{user_id}"
        tz = f"{tz}"
        if guild_id not in self._data:
            self._data[guild_id] = {}
        if user_id not in self._data[guild_id]:
            self._data[guild_id][user_id] = {}
        self._data[guild_id][user_id]["tz"] = tz
        return True
