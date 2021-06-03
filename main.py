import os
import logging

import discord_components
from utils.logs import LogDB

import discord
from utils.modules import ModulesDB
from utils.level import LevelDB
from utils.prefix import PrefixDB
from utils.json import get_path
from discord.ext.commands import when_mentioned_or
import discord.ext.commands as cmds
from discord_components import DiscordComponents

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

directory = get_path()

def load_cogs():
    for filename in os.listdir(directory+"\\cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            filename_strip = filename.rsplit(".py")[0].lower()
            client.load_extension(f"cogs.{filename_strip}")
    
def get_server_prefix(client, message):
    prefix = client.prefix_db.get_prefix(message.guild) if message.guild is not None else "&"
    return when_mentioned_or(prefix)(client, message)

client = cmds.Bot(command_prefix=get_server_prefix, intents=discord.Intents.all())

discord_components_manager = DiscordComponents(client)

client.liste_modules = ["level", "log"]
client.dico_nom_modules_jolis = {"level": "Niveaux", "log": "Historique"}



client.prefix_db = PrefixDB()
client.modules_db = ModulesDB(client.liste_modules)
client.level_db = LevelDB()
client.log_db = LogDB()

@client.event
async def on_ready():
    print(f"{client.user.name} est prêt !")
    load_cogs()
    client.id_auteur = 528157130432315403
    client.auteur = client.get_user(client.id_auteur)
    
@client.event
async def on_message(message):
    if message.author.bot:
        return       

    await client.process_commands(message)

client.run("NzI1NDM0MTU3Nzk4MjYwNzc3.XvOrNQ.J47KiLxA5NHosMl5nJTHSeHBNf4")


    