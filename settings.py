import requests
import motor.motor_asyncio
import json
import asyncpraw
import os

from pathlib import Path

directory = os.path.dirname(__file__)
folders = ["Data", "Image", "Logs"]
for folder in folders:
    try:
        if not Path(folder).exists():
            os.makedirs(f"{directory}/{folder}")

    except OSError:
        print(f"unable to create {folder}")

if Path("Data/Config/Config.json").exists():
    with open("Data/Config/Config.json") as setting:
        config = json.load(setting)

    Token = config.get("Token")
    COMMAND_PREFIX = config.get("bot_prefix")
    logchannel = config.get("log_channel")
    supportchannel = config.get("supportchannel")
    mongodb = config.get("connect_mongodb")

client = motor.motor_asyncio.AsyncIOMotorClient(mongodb)
db = client.SINOVA
collectionstatus = db.Status