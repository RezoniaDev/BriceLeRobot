import discord
from datetime import datetime
from discord.ext import commands

def get_color():
    return 0xF5DF4D

def dictionnaire_roles_permissions(liste_roles: list[discord.Role]):
    dictionnaire_role = {}
    for role in liste_roles:
        dictionnaire_role[role] = discord.PermissionOverwrite(read_messages=role.permissions.administrator, send_messages=False)
    return dictionnaire_role

class Error(commands.Cog, name="Erreur"):

    def __init__(self, client):
        self.client = client

    @commands.command(
        name="error",
        aliases=["erreur", "report-bug"],
        description="Envoie le lien du discord de RezoniaDev pour le rejoindre",
        usage="error <description>"
    )
    async def _error(self, ctx, *args):
        if len(args) == 0:
            await ctx.send("Vous devez marquer la description du message !")
        else:
            description = " ".join(args)
            date = datetime.now()
            guilde = ctx.guild
            envoyeur = ctx.author
            erreur = self.client.errors_class.ajouter_une_erreur(envoyeur, guilde, description, date)
            salon = self.client.get_channel(824702585562857504)
            await salon.send(embed=erreur.avoir_embed())
            await ctx.send(f"Rejoignez notre Discord : https://discord.gg/T5euTWuKHD pour savoir la suite de votre rapport ! *(Son identifiant : {erreur.avoir_identifiant()})*")
                
def setup(client):
    client.add_cog(Error(client))
    print("L'extension Erreur est activée !")