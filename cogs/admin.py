from discord.ext import commands
import discord
import os
from utils.json import get_path

class Admin(commands.Cog):
    
    def __init__(self, client) -> None:
        self.client = client
        self.nom_extensions_vers_raccourci = {"Niveaux": "level", "Historique": "log", "Préfixe": "prefix", "Configuration": "setup", "Administration": "admin"}
        self.raccourci_vers_nom_extensions = {"level": "Niveaux", "log": "Historique", "prefix": "Préfixe", "setup": "Configuration", "admin": "Administration"}
        
    @commands.command(name="get_cogs",aliases=["extensions"], hidden=True)
    async def __get_cogs(self, ctx):
        """
        Envoie un message avec la liste des extensions
        """
        extensions = self.client.cogs
        embed = discord.Embed(name="Noms des extensions", color=discord.Colour(0xF5DF4D))
        for nom_extension, extension in extensions.items():
            embed.add_field(name="Nom de l'extension : ", value=f"{nom_extension} ({self.nom_extensions_vers_raccourci[nom_extension]})" , inline=True)
        embed.set_footer(text=f"Veni, vidi, vici | {self.client.user.name}", icon_url=self.client.user.avatar_url)
        await ctx.send(embed=embed)
    
    def __get_cogs_list(self):
        """
        Renvoie la liste des extensions
        """
        nom_modules = []
        for filename in os.listdir( get_path() +"\\cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                filename_strip = filename.rsplit(".py")[0].lower()
                nom_modules.append(filename_strip)
        return nom_modules
        
    @commands.group(name="reload", hidden=True, invoke_without_command=True)
    async def __reload(self, ctx, *, module):
        """
        Permet de recharger le module `module`
        """
        if module in self.nom_extensions_vers_raccourci:
            module = self.nom_extensions_vers_raccourci[module]        
        try:
            self.client.reload_extension("cogs." + module)
        except commands.ExtensionError as erreur:
            await ctx.send(f"{erreur.__class__.__name__} : {erreur}")
        else:
            await ctx.send("✅")
    
    def __reload_or_load_extension(self, module):
        try:
            self.client.reload_extension("cogs." + module)
        except commands.ExtensionNotLoaded:
            self.client.load_extension("cogs." + module)
    
    @__reload.command(name="all", hidden=True)
    async def __reload_all(self, ctx):
        """
        Permet de recharger tous les modules
        """
        status = []
        async with ctx.typing():
            for nom_extension in self.__get_cogs_list():
                try:
                    self.__reload_or_load_extension(nom_extension)
                except commands.ExtensionError:
                    status.append(f"{self.raccourci_vers_nom_extensions[nom_extension]} ❌")
                else:
                    status.append(f"{self.raccourci_vers_nom_extensions[nom_extension]} ✅")
        await ctx.send("\n".join(status))

    @commands.command(
        name="refresh_bdd",
        hidden=True
    )
    async def _refresh_bdd(self, ctx):
        if ctx.author.id != self.client.id_auteur:
            return
        self.client.modules_db.__ajouter_extension__("vérification")
        print("a")
        ctx.author.send("L'extension `Vérification` a bien été ajoutée à la base de donnée !")


def setup(client):
    client.add_cog(Admin(client))
    print("Le module Administration est prêt !")