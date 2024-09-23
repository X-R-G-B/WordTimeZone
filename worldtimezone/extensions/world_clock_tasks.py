import datetime

import hikari
import lightbulb
import pytz
from extensions import world_clock_data
from lightbulb.ext import tasks


@tasks.task(m=5, auto_start=True, pass_app=True)
async def edit_world_clock(bot: lightbulb.BotApp) -> None:
    wcd = bot.d.world_clock_data  # pyright: ignore[reportAny]
    assert isinstance(wcd, world_clock_data.WorldClockData)

    async def create_embed(
        guild_id: int, member_id: str | int, tz: str
    ) -> hikari.Embed:
        user_ = bot.cache.get_member(guild_id, int(member_id))
        if user_ is None:
            user_ = await bot.rest.fetch_member(guild_id, int(member_id))
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
        _ = embed.add_field("Time", f"{new_now}", inline=False)
        return embed

    for guild in wcd.get_guilds_list():
        embeds: list[hikari.Embed] = []
        if guild.channel_id == "" or guild.message_id == "":
            continue
        channel_world_clock = int(f"{guild.channel_id}")
        message_world_clock = int(f"{guild.message_id}")

        for u in (
            wcd.get_members_list(
                guild.discord_id  # pyright: ignore[reportArgumentType]
            )
            or []
        ):
            if u.tz != "":
                embed = await create_embed(
                    guild.discord_id,  # pyright: ignore[reportArgumentType]
                    u.discord_id,  # pyright: ignore[reportArgumentType]
                    u.tz,  # pyright: ignore[reportArgumentType]
                )
                embeds.append(embed)
        if len(embeds) != 0:
            _ = await bot.rest.edit_message(
                channel_world_clock, message_world_clock, None, embeds=embeds
            )
        else:
            print(f"Failed update message: {guild.discord_id}")


def load(bot: lightbulb.BotApp):  # pyright: ignore[reportUnusedParameter]
    pass


def unload(bot: lightbulb.BotApp):  # pyright: ignore[reportUnusedParameter]
    pass
