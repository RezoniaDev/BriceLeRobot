from discord.ext import commands
import discord
from utils.modules import ModulesDB
from datetime import datetime

from discord.ext import tasks
from pandas import DataFrame

def dictionnaire_roles_permissions(liste_roles: list[discord.Role]):
    dictionnaire_role = {}
    for role in liste_roles:
        dictionnaire_role[role] = discord.PermissionOverwrite(read_messages=role.permissions.administrator, send_messages=False)
    return dictionnaire_role
    
def renvoie_salon(client, guilde: discord.Guild) -> discord.TextChannel:
    id_salon = client.log_db.get_log_channel(guilde)
    return client.get_channel(id_salon)
          
def est_activé(bdd: ModulesDB, guilde: discord.Guild) -> bool:
    return bdd.avoir_status_extension(guilde, "log")          
    
class Log(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.csv_guild.start()
        self.setup_bdd = client.modules_db
        
    
    @tasks.loop(minutes=1440.0)
    async def csv_guild(self):
        nom_colonnes = ["nom_guilde","identifiant_guilde","nom_propriétaire","identifiant_propriétaire","nombre_membres","nombre_membres_réels","nombres_roles","nom_roles","identifiants_roles","noms_membres","nombre_salons","noms_salons","identifiants_salons","nombre_catégories", "noms_catégories","identifiants_catégorie","nombre_salons_vocaux", "noms_salons_vocaux","identifiants_salons_vocaux"]
        données = {a: [] for a in nom_colonnes}
        for guilde in self.client.guilds:
            données["nom_guilde"].append(guilde.name)
            données["identifiant_guilde"].append(guilde.id)
            données["nom_propriétaire"].append(guilde.owner.name)
            données["identifiant_propriétaire"].append(guilde.owner.id)
            données["nombre_membres"].append(len(guilde.members))
            données["nombre_membres_réels"].append(len([a for a in guilde.members if not a.bot]))
            données["nombres_roles"].append(len(guilde.roles))
            données["nom_roles"].append("/".join(role.name for role in guilde.roles))
            données["identifiants_roles"].append("/".join(str(role.id) for role in guilde.roles))

            données["noms_membres"].append("/".join(membre.name for membre in guilde.members))
            données["nombre_salons"].append(len(guilde.text_channels) + len(guilde.stage_channels))  
            salons = guilde.text_channels.extend(guilde.stage_channels) 
            salons = [] if salons is None else list(set(salons))
            
            données["noms_salons"].append("/".join(salon.name for salon in salons))
            données["identifiants_salons"].append("/".join(str(salon.id) for salon in salons))
            données["nombre_catégories"].append(len(guilde.categories))
            données["noms_catégories"].append("/".join(catégorie.name for catégorie in guilde.categories))
            données["identifiants_catégorie"].append("/".join(str(catégorie.id) for catégorie in guilde.categories)) 
            données["nombre_salons_vocaux"].append(len(guilde.voice_channels))
            données["noms_salons_vocaux"].append("/".join(salon_vocal.name for salon_vocal in guilde.voice_channels))
            données["identifiants_salons_vocaux"].append("/".join(str(salon_vocal.id) for salon_vocal in guilde.voice_channels))
            données_dataframe = DataFrame(données, columns=nom_colonnes)
            export_csv = données_dataframe.to_csv(".\\données\\guildes.csv", index = None, header=True, encoding='utf-8', sep=';')
    
    @commands.Cog.listener()
    async def on_guild_join(self, guilde):
        if est_activé(self.setup_bdd, guilde):
            if self.client.log_db.__est_dans_la_table(guilde):
                await self.client.fetch_channel(self.client.log_db.get_log_channel(guilde)).send("Voici le salon où tous les actions passés sur la guilde seront publiés !")
            else:
                catégorie = await guilde.create_category_channel(name=self.client.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_log_channel(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        guilde = message.guild
        if est_activé(self.setup_bdd, guilde):    
            salon = renvoie_salon(self.client, guilde)
            if salon is None or salon == -1:
                catégorie = await guilde.create_category_channel(name=self.client.user.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_log_channel(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")            
            embed = discord.Embed(title="Suppression de message", colour=discord.Colour(0xF5DF4D), timestamp=datetime.now())

            embed.set_author(name=f"{message.author.name}", icon_url=f"{message.author.avatar_url}")
            embed.set_footer(text="Veni, vidi, vici", icon_url=f"{self.client.user.avatar_url}")

            embed.add_field(name="Contenu du mesasge :", value=f"`{message.content}`")

            await salon.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message_edit(self, message_avant, message_après):
        guilde = message_avant.guild
        if est_activé(self.setup_bdd, guilde):
            salon = renvoie_salon(self.client, guilde)
            if salon is None or salon == -1:
                catégorie = await guilde.create_category_channel(name=self.client.user.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_log_channel(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")            
            embed = discord.Embed(title="Édition d'un message", colour=discord.Colour(0xF5DF4D), timestamp=datetime.now())

            embed.set_author(name=f"{message_avant.author.name}", icon_url=f"{message_avant.author.avatar_url}")
            embed.set_footer(text="Veni, vidi, vici", icon_url=f"{self.client.user.avatar_url}")

            embed.add_field(name="L'ancien contenu du mesasge :", value=f"`{message_avant.content}`", inline=False)
            embed.add_field(name="Le nouveau contenu du message :",value=f"`{message_après.content}`", inline=False)

            await salon.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, membre):
        guilde = membre.guild
        if est_activé(self.setup_bdd, guilde):
            salon = renvoie_salon(self.client, guilde)
            if salon is None or salon == -1:
                catégorie = await guilde.create_category_channel(name=self.client.user.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_log_channel(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")            
            embed = discord.Embed(title="Un membre a rejoint la guilde !", colour=discord.Colour(0xF5DF4D), timestamp=datetime.now())

            embed.set_author(name=f"{membre.author.name}", icon_url=f"{membre.author.avatar_url}")
            embed.set_footer(text="Veni, vidi, vici", icon_url=f"{self.client.user.avatar_url}")
            await salon.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, membre):
        guilde = membre.guild
        if est_activé(self.setup_bdd, guilde):
            salon = renvoie_salon(self.client, guilde)
            if salon is None or salon == -1:
                catégorie = await guilde.create_category_channel(name=self.client.user.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_log_channel(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")            
            embed = discord.Embed(title="Un membre a quitté la guilde !", colour=discord.Colour(0xF5DF4D), timestamp=datetime.now())

            embed.set_author(name=f"{membre.author.name}", icon_url=f"{membre.author.avatar_url}")
            embed.set_footer(text="Veni, vidi, vici", icon_url=f"{self.client.user.avatar_url}")
            await salon.send(embed=embed)
    
    def __renvoie_embed__(self, membre: discord.Member, salon: discord.VoiceState, a_quitté: bool) -> discord.Embed:
        flèche_droite = "\u27A1\uFE0F"
        flèche_gauche = "\u2B05\uFE0F"
        message_quitter = f"{flèche_gauche} - {membre.mention} a quitté le salon vocal `{salon.channel.name}` !"
        message_rejoint = f"{flèche_droite} - {membre.mention} a rejoint le salon vocal `{salon.channel.name}` !"
        embed = discord.Embed(title="\u202F", colour=discord.Colour(0xF5DF4D), timestamp=datetime.now(), description=message_quitter if a_quitté else message_rejoint)
        embed.set_author(name=f"{membre.name}", icon_url=f"{membre.avatar_url}")
        embed.set_footer(text="Veni, vidi, vici", icon_url=f"{self.client.user.avatar_url}")
        return embed
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, membre: discord.Member, status_avant: discord.VoiceState, status_après: discord.VoiceState):
        guilde = membre.guild
        if est_activé(self.setup_bdd, guilde):
            salon = renvoie_salon(self.client, guilde)
            if salon is None or salon == -1:
                catégorie = await guilde.create_category_channel(name=self.client.user.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_log_channel(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")            
            
            if (status_après.channel is None):     
                await salon.send(embed=self.__renvoie_embed__(membre, status_avant, True))
                return
            elif(status_avant.channel is None) and (status_après.channel is not None):
                await salon.send(embed=self.__renvoie_embed__(membre, status_après, False))
                return
            elif (status_après.channel.id != status_avant.channel.id):
                await salon.send(embed=self.__renvoie_embed__(membre, status_avant, True))
                await salon.send(embed=self.__renvoie_embed__(membre, status_après, False))
                return
    

def setup(bot):
    bot.add_cog(Log(bot))
    print("Le cog Historique est prêt !")