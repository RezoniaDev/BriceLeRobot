from discord.ext import commands
import discord
import os
import platform
from utils.util import get_path, get_emoji, get_color


def est_le_propriétaire():
    def predicate(ctx):
        return ctx.author.id ==528157130432315403
    return commands.check(predicate)


def read_changelog(filename, directory):
    """
    Cette fonction lit le fichier `filename.json` et retourne les
    données

    :param filename (str) : Le nom du fichier à ouvrir
    :return: data (dict) : Un dictionnaire avec les données du fichier
    """
    cwd = get_path()
    with open(f"{cwd}\\{directory}\\{filename}.txt", "r", encoding="utf-8") as file:
        return file.read()

class Administration(commands.Cog, name="Administration"):
    
    def __init__(self, client) -> None:
        self.client = client

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.create_annonces(guild)

    @est_le_propriétaire()
    @commands.command(name="get_cogs",aliases=["extensions"], hidden=True)
    async def __get_cogs(self, ctx):
        """
        Envoie un message avec la liste des extensions
        """
        extensions = self.client.cogs
        embed = discord.Embed(title="Noms des extensions", color=discord.Colour(0xF5DF4D))
        for nom_extension, extension in extensions.items():
            embed.add_field(name="Nom de l'extension : ", value=f"{nom_extension}" , inline=True)
        embed.set_footer(text=f"Veni, vidi, vici | {self.client.user.name}", icon_url=self.client.user.avatar_url)
        await ctx.send(embed=embed)

    def __get_cogs_list__(self) -> list[str]:
        """
        Renvoie la liste des extensions
        """
        nom_modules = []
        accès_dossier = get_path()
        if(platform.system() == "Windows"):    
            for nom_fichier in os.listdir(accès_dossier + "\\cogs"):
                if nom_fichier.endswith(".py") and not nom_fichier.startswith("_"):
                    nom_fichier_sans_extension= nom_fichier.rsplit(".py")[0].lower()
                    nom_modules.append(nom_fichier_sans_extension)
        elif platform.system() == "Linux": 
            for nom_fichier in os.listdir(accès_dossier + "/cogs"):
                if nom_fichier.endswith(".py") and not nom_fichier.startswith("_"):
                    nom_fichier_sans_extension= nom_fichier.rsplit(".py")[0].lower()
                    nom_modules.append(nom_fichier_sans_extension)
        return nom_modules
    
    @est_le_propriétaire()
    @commands.command(
        name="restart",
        hidden=True
    )
    async def __restart(self, ctx):
        for id, shards in self.client.shards.items():
            await shards.reconnect()
        await ctx.send("Je me suis redémarrer !")
    
    @est_le_propriétaire()    
    @commands.group(name="reload", hidden=True, invoke_without_command=True)
    async def __reload(self, ctx, *, module):
        """
        Permet de recharger le module `module`
        """
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
    
    @est_le_propriétaire()
    @__reload.command(name="all", hidden=True)
    async def __reload_all(self, ctx):
        """
        Permet de recharger tous les modules
        """
        reload_embed = discord.Embed(color=0xF5DF4D, title="Status du rechargement des extensions : ")
        async with ctx.typing():
            for nom_extension in self.__get_cogs_list__():
                try:
                    self.__reload_or_load_extension(nom_extension)
                except commands.ExtensionError:
                    reload_embed.add_field(name=f"{nom_extension.capitalize()} ", value=str(get_emoji(self.client, "no")), inline=False)
                else:
                    reload_embed.add_field(name=f"{nom_extension.capitalize()} ", value=str(get_emoji(self.client, "yes")), inline=False)
        await ctx.send(embed=reload_embed)

    @est_le_propriétaire()
    @commands.command(
    name="shutdown",
    hidden=True
    )
    async def __stop__(self, ctx):
        await ctx.send("Je me déconnecte")
        for id, shards in self.client.shards.items():
            await shards.disconnect()
    
    @est_le_propriétaire()
    @commands.command(
        name="annonces",
        hidden=True
    )
    async def annonces(self, ctx, *args):
        await ctx.send(embed=await self.__check_annonces__())
        message = " ".join(args)
        liste_keys_valeurs = self.client.annonces_bdd.select_all_annonces_channel()
        print(liste_keys_valeurs)
        for str_guild_id, annonces_channel in liste_keys_valeurs.items():
            channel = await self.client.fetch_channel(annonces_channel)
            await channel.send(message)
  
    @commands.command(
        name="changelog",
        description="Envoie le changelog de la nouvelle version",
        usage="changelog"
    )
    async def changelog(self, ctx):
        f = read_changelog("latest", "changelog")
        await ctx.send(f)


    async def create_annonces(self, guild):
        member_bot_name = [m.name for m in guild.members if m.bot]
        adminstrator_roles = [r for r in guild.roles if r.permissions.administrator and r.name not in member_bot_name]
        adminstrator_roles.append(guild.me)
        overwrites = {k:discord.PermissionOverwrite(read_messages=True, send_messages=True) for k in adminstrator_roles}
        overwrites[guild.default_role] = discord.PermissionOverwrite(read_messages=False)
        catégorie = guild.get_channel(self.client.log_db.avoir_identifiant_catégorie(guild))
        annonces_channel = await guild.create_text_channel(f"annonces-{guild.me.name}",category=catégorie,overwrites=overwrites)
        self.client.annonces_bdd.insert_element(guild.id, annonces_channel.id)
        return annonces_channel.id
    
    async def __check_annonces__(self):
        guild_embed = discord.Embed(
            title="Status des salons annonces :",
            color = get_color()
        )
        txt = ""
        
        yes = get_emoji(self.client, "yes")
        no = get_emoji(self.client, "no")

        for guild in self.client.guilds:
            if not self.client.annonces_bdd.est_dans_la_table(guild.id):
                id = await self.create_annonces(guild)            
                txt += f"**{guild.name}** *({guild.id})* : {yes} *({id})*\n"
            else:
                channel_id = self.client.annonces_bdd.select_one_annonce_channel(guild.id)
                channel = guild.get_channel(channel_id)
                if channel is None:
                    txt += f"**{guild.name}** *({guild.id})* : {no} \n"
                    await guild.owner.send("Il ne faut pas supprimer le salon 'annonces' du bot ! je vais en recréer un")
                    await self.create_annonces(guild)
                else:
                    txt += f"**{guild.name}** *({guild.id})* : {yes} *({channel_id})* \n"
        guild_embed.description = txt
        return guild_embed

    @est_le_propriétaire()
    @commands.command(
        name="check_annonces",
        hidden=True
    )
    async def check_annonces(self, ctx):
        await ctx.send(embed=await self.__check_annonces__())


def setup(client):
    client.add_cog(Administration(client))
    print("L'extension Administration est activée !")