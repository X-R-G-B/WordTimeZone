import datetime

import hikari
import lightbulb
import pytz
from lightbulb.ext import tasks

plugin = lightbulb.Plugin("EditWorldClock")


def load(bot: lightbulb.BotApp):
    @tasks.task(m=5, auto_start=True)
    async def edit_world_clock() -> None:
        def create_embed(guild_id, u, tz):
            user_ = bot.cache.get_member(guild_id, int(u))
            embed = (
                hikari.Embed(
                    title=f"WorldTimeClock - {user_.display_name}",
                    description=f"Timezone: {tz}",
                )
                .set_author(name=f"{user_.display_name}")
                .set_thumbnail(user_.avatar_url)
            )
            now = datetime.datetime.now()
            new_tz = pytz.timezone(tz)
            new_now = now.astimezone(new_tz)
            embed.add_field("Time", f"{new_now}", inline=False)
            return embed

        for guild_id in bot.d.data.get_guilds_list():
            embeds = []
            guild_world_clock = bot.d.data.get_world_clock(guild_id)
            channel_world_clock = guild_world_clock["channel_id"]
            message_world_clock = guild_world_clock["message_id"]

            for u in bot.d.data.get_members_list(guild_id):
                member = bot.d.data.get_member(guild_id, u)
                if "tz" in member:
                    embeds.append(create_embed(guild_id, u, member["tz"]))
            await bot.rest.edit_message(
                channel_world_clock, message_world_clock, None, embeds=embeds
            )


def unload(bot: lightbulb.BotApp):
    pass
