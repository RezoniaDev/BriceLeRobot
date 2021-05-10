import os
from utils.modules import ModulesDB
from utils.level import LevelDB
from utils.prefix import PrefixDB
from utils.json import get_path
from discord.ext.commands import when_mentioned_or
import discord.ext.commands as cmds

directory = get_path()

def load_cogs():
    for filename in os.listdir(directory+"\\cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            filename_strip = filename.rsplit(".py")[0]
            client.load_extension(f"cogs.{filename_strip}")
    
def get_server_prefix(client, message):
        prefix = client.prefix_db.get_prefix(message.guild)
        return when_mentioned_or(prefix)(client, message)

client = cmds.Bot(command_prefix=get_server_prefix)

client.prefix_db = PrefixDB()
client.modules_db = ModulesDB()
client.level_db = LevelDB()

@client.event
async def on_ready():
    print(f"{client.user.name} est prêt !")
    load_cogs()
    
@client.event
async def on_message(message):
    
    if message.author.bot:
        return       

    await client.process_commands(message)

client.run("NzI1NDM0MTU3Nzk4MjYwNzc3.XvOrNQ.J47KiLxA5NHosMl5nJTHSeHBNf4")


    