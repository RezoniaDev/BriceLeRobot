import os
import logging
import platform
from utils.spoil import SpoilDB
from dotenv import load_dotenv
from utils.logs import HistoriqueDB
import discord
from utils.util import get_path
from discord.ext import commands
from utils.vérification import VérificationDB
from utils.modules import ModulesDB
from utils.level import LevelDB
from utils.annonces import AnnoncesDB
from utils.prefix import PrefixDB
from discord.ext.commands import when_mentioned_or
import discord.ext.commands as cmds
import sys
import asyncio


def est_le_propriétaire():
    def predicate(ctx):
        return ctx.author.id ==528157130432315403
    return commands.check(predicate)

if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

load_dotenv()

clé_bot = os.getenv("TOKEN")

système_exploitation_hébergeur = platform.system()

accès_dossier = get_path()

dossier_bases_de_données = accès_dossier + "\\données\\" if système_exploitation_hébergeur == "Windows" else accès_dossier + "/données/"

def charger_les_extensions():
    if(système_exploitation_hébergeur == "Windows"):    
        for nom_fichier in os.listdir(accès_dossier + "\\cogs"):
            if nom_fichier.endswith(".py") and not nom_fichier.startswith("_"):
                nom_fichier_sans_extension= nom_fichier.rsplit(".py")[0].lower()
                client.load_extension(f"cogs.{nom_fichier_sans_extension}")
    elif (système_exploitation_hébergeur == "Linux") : 
        for nom_fichier in os.listdir(accès_dossier + "/cogs"):
            if nom_fichier.endswith(".py") and not nom_fichier.startswith("_"):
                nom_fichier_sans_extension= nom_fichier.rsplit(".py")[0].lower()
                client.load_extension(f"cogs.{nom_fichier_sans_extension}")    
        



def avoir_préfixe_avec_serveur(client, message):
    préfixe = client.prefix_db.get_prefix(message.guild) if message.guild is not None else "?"
    return when_mentioned_or(préfixe)(client, message)


client = cmds.AutoShardedBot(activity=discord.Game("&help"), command_prefix=avoir_préfixe_avec_serveur, help_command=None, intents=discord.Intents.all())


client.liste_modules = ["level", "log", "vérification", "spoil", "quiz", "giveaway"]
client.dossier_données = dossier_bases_de_données

client.version = "1.2"
client.prefix_db = PrefixDB(dossier_bases_de_données)
client.modules_db = ModulesDB(dossier_bases_de_données, client.liste_modules)
client.level_db = LevelDB(dossier_bases_de_données)
client.log_db = HistoriqueDB(dossier_bases_de_données, client, client.modules_db)
client.vérification_bdd = VérificationDB(dossier_bases_de_données, client.modules_db)
client.spoil_bdd = SpoilDB(dossier_bases_de_données, client)
client.annonces_bdd = AnnoncesDB(dossier_bases_de_données)

@client.event
async def on_ready():
    print(f"{client.user.name} est prêt !")
    charger_les_extensions()
    client.id_auteur = os.getenv("OWNER_ID")
    client.auteur = client.get_user(client.id_auteur)

@client.event
async def on_message(message):
    if message.author.bot:
        return       

    await client.process_commands(message)

client.run(clé_bot)


    