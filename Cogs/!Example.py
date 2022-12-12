import nextcord
import settings
import random
import asyncio

from nextcord.ext import commands

class example(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    

def setup(bot: commands.Bot):
    bot.add_cog(example(bot))