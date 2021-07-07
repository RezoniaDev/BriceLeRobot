import os
import logging
from dotenv import load_dotenv
import discord_components
from utils.logs import HistoriqueDB
import discord
from utils.vérification import VérificationDB
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

load_dotenv()

clé_bot = os.getenv("TOKEN")

accès_dossier = get_path()

def charger_les_extensions():
    for nom_fichier in os.listdir(accès_dossier + "\\cogs"):
        if nom_fichier.endswith(".py") and not nom_fichier.startswith("_"):
            nom_fichier_sans_extension= nom_fichier.rsplit(".py")[0].lower()
            client.load_extension(f"cogs.{nom_fichier_sans_extension}")
    
def avoir_préfixe_avec_serveur(client, message):
    préfixe = client.prefix_db.get_prefix(message.guild) if message.guild is not None else "?"
    return when_mentioned_or(préfixe)(client, message)

client = cmds.Bot(command_prefix=avoir_préfixe_avec_serveur, intents=discord.Intents.all())

discord_components_manager = DiscordComponents(client)

client.liste_modules = ["level", "log", "vérification"]
client.dico_nom_modules_jolis = {"level": "Niveau", "log": "Historique"}



client.prefix_db = PrefixDB()
client.modules_db = ModulesDB(client.liste_modules)
client.level_db = LevelDB()
client.log_db = HistoriqueDB(client, client.modules_db)
client.vérification_bdd = VérificationDB(client.modules_db)

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


    