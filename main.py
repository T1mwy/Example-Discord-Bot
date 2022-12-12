import subprocess
import datetime
import os
import platform
import logging
import asyncio
import sys
import traceback
import nextcord
import settings

from nextcord.ext import commands, tasks
from datetime import date, timedelta
from itertools import cycle

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="logs/botlog.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)
intent = nextcord.Intents.default()
intent.message_content = True
intent.members = True

PYTHON_VERSION = platform.python_version()
OS = platform.system()

status = cycle(
    [
        f" S          | {settings.COMMAND_PREFIX}help ",
        f" Si         | {settings.COMMAND_PREFIX}help ",
        f" Sin        | {settings.COMMAND_PREFIX}help ",
        f" Sino       | {settings.COMMAND_PREFIX}help ",
        f" Sinova     | {settings.COMMAND_PREFIX}help ",
        f" Sinova b   | {settings.COMMAND_PREFIX}help ",
        f" Sinova bo  | {settings.COMMAND_PREFIX}help ",
        f" Sinova bot | {settings.COMMAND_PREFIX}help ",
    ]
)

UI = """

         ██████╗ ██╗   ██╗███████╗██████╗ ████████╗██╗███╗   ███╗███████╗
        ██╔═══██╗██║   ██║██╔════╝██╔══██╗╚══██╔══╝██║████╗ ████║██╔════╝
        ██║   ██║██║   ██║█████╗  ██████╔╝   ██║   ██║██╔████╔██║█████╗  
        ██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗   ██║   ██║██║╚██╔╝██║██╔══╝  
        ╚██████╔╝ ╚████╔╝ ███████╗██║  ██║   ██║   ██║██║ ╚═╝ ██║███████╗
         ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝"""

async def print_ascii_art():
    name_space = (25 - (len(str(bot.user)))) * (" ")
    server = str(len(bot.guilds))
    server_space = (27 - int(len(server))) * (" ")
    user = str(len(bot.users))
    user_space = (29 - int(len(user))) * (" ")
    print(f"{UI}")
    print(f"""
        ╔══════════════════════════════════════╗
        ║ BOT NAME : {bot.user}{name_space} ║
        ║ BOT ID : {bot.user.id}         ║
        ║ BOT STATUS : ONLINE                  ║
        ║ SERVER : {server}{server_space} ║
        ║ USER : {user}{user_space} ║
        ║                                      ║
        ╚══════════════════════════════════════╝""")

bot = commands.AutoShardedBot(
    command_prefix=settings.COMMAND_PREFIX,
    case_insensitive=True,
    help_command=None,
    intents=intent,
    strip_after_prefix=True,
)

start_time = datetime.datetime.utcnow()

async def clearcmd():
    subprocess.call("cls" if os.name == "nt" else "clear", shell=True)


@tasks.loop(seconds=5)
async def change_status():
    await bot.wait_until_ready()
    await bot.change_presence(
        status=nextcord.Status.idle,
        activity=nextcord.Streaming(
            name=next(status), url="https://www.twitch.tv/Name" #<-- Status twitch steaming
        ),
    )

@tasks.loop(seconds=120)
async def serverstat():
    await bot.wait_until_ready()
    results = settings.collectionstatus.find({"status_system": "YES"})
    for data in await results.to_list(length=10000):
        if data["guild_id"] in bot.guilds:
            guild = bot.get_guild(data["guild_id"])
            print(data["guild_id"])
            memberonly = len([member for member in guild.members if not member.bot])
            botonly = int(guild.member_count) - int(memberonly)
            total_member_channel = bot.get_channel(data["status_total_id"])
            member_channel = bot.get_channel(data["status_members_id"])
            bot_channel = bot.get_channel(data["status_bots_id"])

            if total_member_channel:
                await total_member_channel.edit(name=f"︱👥 Total : {guild.member_count}")
            if member_channel:
                await member_channel.edit(name=f"︱👥 Members : {memberonly}")
            if bot_channel:
                await bot_channel.edit(name=f"︱👥 Bots : {botonly}")

        else:
            pass


async def checkMongo():
    try:
        await settings.client.admin.command("ismaster")
        print("Successfully connected to mongodb")
    except Exception:
        print("Unable to connect to mongodb")


def loadcogs():
    for filename in os.listdir("Cogs"):
        if filename.endswith(".py") and not filename.startswith("!"):
            try:
                bot.load_extension(f"Cogs.{filename[:-3]}")
                print(f"Successfully loaded {filename}")

            except Exception as e:
                print(f"Failed to load {filename}")
                print(e)
                traceback.print_exc()

def reloadallcogs():
    for filename in os.listdir("Cogs"):
        if filename.endswith(".py") and not filename.startswith("!"):
            try:
                bot.reload_extension(f"Cogs.{filename[:-3]}")
                print(f"Successfully reloaded {filename}")

            except Exception as e:
                print(f"Failed to reloaded {filename}")
                print(e)
                traceback.print_exc()

@bot.event
async def on_ready():
    loadcogs()
    # await settings.collectionmusic.delete_many({})
    try:
        change_status.start()
        serverstat.start()
    except RuntimeError:
        pass
    await print_ascii_art()
    try:
        channel = bot.get_channel(int(settings.logchannel))
        embed = nextcord.Embed(title=f"Bot is online", colour=0x56FF2D)
        await channel.send(embed=embed)

    except Exception as e:
        print(e)
        pass

@bot.command(aliases=["reload"])
@commands.is_owner()
async def reloadcogs(ctx: commands.Context):
    reloadallcogs()
    print("Reloaded all cogs!")
    await ctx.send("Reloaded all cogs successfully!")


@bot.command()
async def cleancmd(ctx: commands.Context):
    await clearcmd()
    await checkMongo()
    await print_ascii_art()
    await ctx.send("Cmd cleared")


@bot.event
async def on_connect():
    print("Connected to discord API")
    # os.system("cls")


def main():
    try:
        bot.run(settings.Token, reconnect=True)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()