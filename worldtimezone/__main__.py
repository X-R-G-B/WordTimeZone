import os

import hikari
import lightbulb
from data import Data
from hikari import Intents
from lightbulb.ext import tasks

INTENTS = Intents.GUILD_MEMBERS | Intents.GUILDS

bot = lightbulb.BotApp(
    os.environ["BOT_TOKEN"],
    intents=INTENTS,
    banner=None,
)
tasks.load(bot)


@bot.listen(hikari.StartingEvent)
async def on_starting(_: hikari.StartingEvent) -> None:
    bot.d.data = Data()


bot.load_extensions("extensions.ping")
bot.load_extensions("extensions.world_clock")
bot.load_extensions("extensions.edit_world_clock")


if __name__ == "__main__":
    bot.run()
