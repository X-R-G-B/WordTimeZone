import lightbulb

plugin = lightbulb.Plugin("Ping")


@plugin.command
@lightbulb.add_cooldown(5, 1, lightbulb.GuildBucket)
@lightbulb.command("ping", description="The bot's ping.")
@lightbulb.implements(lightbulb.SlashCommand)
async def pingIt(ctx: lightbulb.SlashContext) -> None:
    await ctx.respond(f"Pong! Latency: {ctx.bot.heartbeat_latency * 1000:.2f}ms.")


def load(bot: lightbulb.BotApp):
    bot.add_plugin(plugin)


def unload(bot: lightbulb.BotApp):
    bot.remove_plugin(plugin)
