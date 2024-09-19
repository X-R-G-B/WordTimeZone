import datetime

import hikari
import lightbulb
import pytz
from lightbulb.ext import tasks

plugin = lightbulb.Plugin("EditWorldClock")


@tasks.task(m=5, auto_start=True, pass_app=True)
async def edit_world_clock(bot: lightbulb.BotApp) -> None:
    await bot.wait_for(hikari.StartedEvent, timeout=None)

    def create_embed(guild_id, member_id, tz):
        print("guild_id", guild_id, "member_id", member_id)
        user_ = bot.cache.get_member(guild_id, int(member_id))
        if user_ is None:
            return None
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

    for guild in bot.d.data.get_guilds_list():
        embeds = []
        channel_world_clock = guild.channel_id
        message_world_clock = guild.message_id

        for u in bot.d.data.get_members_list(guild.discord_id) or []:
            if u.tz != "":
                embed = create_embed(guild.discord_id, u.discord_id, u.tz)
                if embed is not None:
                    embeds.append(embed)
                else:
                    print(f"Failed user: {guild.discord_id} {u.discord_id}")
        if len(embeds) != 0:
            await bot.rest.edit_message(
                channel_world_clock, message_world_clock, None, embeds=embeds
            )


def load(bot: lightbulb.BotApp):
    pass


def unload(bot: lightbulb.BotApp):
    pass
