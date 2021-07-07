from discord.ext import commands
import discord
from utils.modules import ModulesDB
from datetime import datetime

from discord.ext import tasks
from pandas import DataFrame

from discord.ext import tasks
from pandas import DataFrame

def est_activé(bdd: ModulesDB, guilde: discord.Guild) -> bool:
    return bdd.avoir_status_extension(guilde, "vérification")

def dictionnaire_roles_permissions(liste_roles: list[discord.Role]):
    dictionnaire_role = {}
    for role in liste_roles:
        dictionnaire_role[role] = discord.PermissionOverwrite(read_messages=role.permissions.administrator, send_messages=False)
    return dictionnaire_role
    
def renvoie_salon(client, guilde: discord.Guild) -> discord.TextChannel:
    id_salon = client.log_db.avoir_identifiant_salon(guilde)
    return guilde.get_channel(id_salon)

def renvoie_catégorie(client, guilde):
    id_catégorie = client.log_db.avoir_identifiant_catégorie(guilde)
    return guilde.get_channel(id_catégorie)

class Historique(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.log_db = client.log_db
        self.csv_guild.start()
        
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
    async def on_guild_join(self, guilde: discord.Guild) -> None:
        
        if est_activé(self.log_db.avoir_bdd_setup(), guilde):
            if self.client.log_db.est_dans_la_table(guilde):
                await self.client.fetch_channel(self.client.log_db.get_log_channel(guilde)).send("Voici le salon où tous les actions passés sur la guilde seront publiés !")
            else:
                catégorie = await guilde.create_category_channel(name=self.client.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        guilde = message.author.guild
        if est_activé(self.log_db.avoir_bdd_setup(), guilde):
            salon = renvoie_salon(self.client, guilde)
            catégorie = renvoie_catégorie(self.client, guilde)
            if catégorie is None or catégorie == -1:
                catégorie = await guilde.create_category_channel(name=self.client.user.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")            
            elif salon is None or salon == -1:
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")            
            embed = discord.Embed(title="Suppression de message", colour=discord.Colour(0xF5DF4D), timestamp=datetime.now())

            embed.set_author(name=f"{message.author.name}", icon_url=f"{message.author.avatar_url}")
            embed.set_footer(text="Veni, vidi, vici", icon_url=f"{self.client.user.avatar_url}")

            embed.add_field(name="Contenu du mesasge :", value=f"`{message.content}`")

            await salon.send(embed=embed)
        
    @commands.Cog.listener()
    async def on_message_edit(self, message_avant: discord.Message, message_après: discord.Message) -> None:
        guilde = message_avant.guild
        if est_activé(self.log_db.avoir_bdd_setup(), guilde):
            salon = renvoie_salon(self.client, guilde)
            salon = renvoie_salon(self.client, guilde)
            catégorie = renvoie_catégorie(self.client, guilde)
            if catégorie is None or catégorie == -1:
                catégorie = await guilde.create_category_channel(name=self.client.user.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")            
            elif salon is None or salon == -1:
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")                      
            embed = discord.Embed(title="Édition d'un message", colour=discord.Colour(0xF5DF4D), timestamp=datetime.now())

            embed.set_author(name=f"{message_avant.author.name}", icon_url=f"{message_avant.author.avatar_url}")
            embed.set_footer(text="Veni, vidi, vici", icon_url=f"{self.client.user.avatar_url}")

            embed.add_field(name="L'ancien contenu du mesasge :", value=f"`{message_avant.content}`", inline=False)
            embed.add_field(name="Le nouveau contenu du message :",value=f"`{message_après.content}`", inline=False)

            await salon.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, membre: discord.Member) -> None:
        if est_activé(self.log_db.avoir_bdd_setup(), guilde):
            guilde = membre.guild
            salon = renvoie_salon(self.client, guilde)
            catégorie = renvoie_catégorie(self.client, guilde)
            if catégorie is None or catégorie == -1:
                catégorie = await guilde.create_category_channel(name=self.client.user.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")            
            elif salon is None or salon == -1:
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")                        
            embed = discord.Embed(title="Un membre a rejoint la guilde !", colour=discord.Colour(0xF5DF4D), timestamp=datetime.now())

            embed.set_author(name=f"{membre.author.name}", icon_url=f"{membre.author.avatar_url}")
            embed.set_footer(text="Veni, vidi, vici", icon_url=f"{self.client.user.avatar_url}")
            await salon.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, membre: discord.Member) -> None:
        guilde = membre.guild
        if est_activé(self.log_db.avoir_bdd_setup(), guilde):
            salon = renvoie_salon(self.client, guilde)
            catégorie = renvoie_catégorie(self.client, guilde)
            if catégorie is None or catégorie == -1:
                catégorie = await guilde.create_category_channel(name=self.client.user.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")            
            elif salon is None or salon == -1:
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon)
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
        if est_activé(self.log_db.avoir_bdd_setup(), guilde):
            salon = renvoie_salon(self.client, guilde)
            catégorie = renvoie_catégorie(self.client, guilde)
            if catégorie is None or catégorie == -1:
                catégorie = await guilde.create_category_channel(name=self.client.user.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")            
            elif salon is None or salon == -1:
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon)
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
        
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, salon: discord.abc.GuildChannel) -> None:
        guilde = salon.guild
        if est_activé(self.log_db.avoir_bdd_setup(), guilde):
            salon = renvoie_salon(self.client, guilde)
            catégorie = renvoie_catégorie(self.client, guilde)
            if catégorie is None or catégorie == -1:
                catégorie = await guilde.create_category_channel(name=self.client.user.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")            
            elif salon is None or salon == -1:
                salon = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")                        
            embed = discord.Embed(title=f"Le salon `{salon.name}` a été supprimé !", colour=discord.Colour(0xF5DF4D), timestamp=datetime.now())

            embed.set_footer(text="Veni, vidi, vici", icon_url=f"{self.client.user.avatar_url}")
            await salon.send(embed=embed)
    
    def __renvoie_embed_informations_salon_textuel__(self, embed, salon, guilde):
        oui = "✅"
        non = "❌"
        embed.add_field(name="Le nom du salon :", value=f"{salon.name}", inline=False)
        embed.add_field(name="L'identifiant du salon :", value=f"{salon.id}", inline=False)
        embed.add_field(name="Le sujet du salon : ", value=f"""{salon.topic if salon.topic is not None else "Pas de sujet !"}`""", inline=False)
        embed.add_field(name="La position du salon :", value=f"{salon.position}", inline=False)
        embed.add_field(name="Le délai du salon :", value=f"{salon.slowmode_delay}", inline=False)
        embed.add_field(name="Le salon est-il sûr ?", value=f"{oui if salon.is_nsfw else non}", inline=False)
        embed.add_field(name="Le salon est-il un salon d'annonce ?", value=f"{oui if salon.is_news else non}", inline=False)
        embed.add_field(name="La date de création du salon :", value=f"{salon.created_at}", inline=False)
        embed.add_field(name="Le salon a-t-il ses permissions synchronisées ? ; ", value=f"{oui if salon.permissions_synced else non}", inline=False)
        embed.add_field(name="Le hachage du salon : ", value=f"{hash(salon)}", inline=False)
        embed.set_footer(text="Veni, vidi, vici", icon_url=f"{self.client.user.avatar_url}")
        return embed
    
    def __renvoie_embed_informations_salon_vocal(self, embed,salon):
        oui = "✅"
        non = "❌"
        embed.add_field(name="Le nom du salon :", value=f"{salon.name}", inline=False)
        embed.add_field(name="L'identifiant du salon :", value=f"{salon.id}", inline=False)
        embed.add_field(name="Le débit binaire du salon : ", value=f"""{salon.bitrate}`""", inline=False)
        embed.add_field(name="La position du salon :", value=f"{salon.position}", inline=False)
        embed.add_field(name="La limite d'utilsateur du salon :", value=f"{salon.user_limit}", inline=False)
        embed.add_field(name="La date de création du salon :", value=f"{salon.created_at}", inline=False)
        embed.add_field(name="Le salon a-t-il ses permissions synchronisées ? ; ", value=f"{oui if salon.permissions_synced else non}", inline=False)     
        embed.add_field(name="La région du salon : ", value=f"{str(salon.rtc_region)}", inline=False)
        embed.add_field(name="Le hachage du salon :", value=f"{hash(salon)}", inline=False)
        embed.set_footer(text="Veni, vidi, vici", icon_url=f"{self.client.user.avatar_url}")
        return embed
    
    def __renvoie_embed_informations_catégorie__(self, embed, salon):
        oui = "✅"
        non = "❌"
        embed.add_field(name="Le nom de la catégorie :", value=f"{salon.name}", inline=False)
        embed.add_field(name="L'identifiant de la catégorie :", value=f"{salon.id}", inline=False)
        embed.add_field(name="La position de la catégorie :", value=f"{salon.position}", inline=False)
        embed.add_field(name="Le nombre de salons textuels :", value=f"{len(salon.text_channels)}", inline=False)
        embed.add_field(name="Le nombre de salons vocaux :", value=f"{len(salon.voice_channels)}", inline=False)
        embed.add_field(name="Le nombre de salons de présentation :", value=f"{len(salon.stage_channels)}", inline=False)
        embed.add_field(name="La date de création de la catégorie :", value=f"{salon.created_at}", inline=False)
        embed.add_field(name="La catégorie a-t-il ses permissions synchronisées ? ; ", value=f"{oui if salon.permissions_synced else non}", inline=False)
        embed.add_field(name="La catégorie est-elle sûre ?", value=f"{oui if salon.is_nsfw else non}", inline=False)
        embed.set_footer(text="Veni, vidi, vici", icon_url=f"{self.client.user.avatar_url}")
        return embed
        
        
    @commands.Cog.listener()
    async def on_guild_channel_create(self, salon: discord.abc.GuildChannel) -> None:
        salon = self.client.get_channel(salon.id)
        guilde = salon.guild
        if est_activé(self.log_db.avoir_bdd_setup(), guilde):
            salon_historique = renvoie_salon(self.client, guilde)
            catégorie = renvoie_catégorie(self.client, guilde)
            if catégorie is None or catégorie == -1:
                catégorie = await guilde.create_category_channel(name=self.client.user.name, overwrites=dictionnaire_roles_permissions(guilde.roles))
                salon_historique = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon_historique)
                await salon_historique.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")            
            elif salon is None or salon == -1:
                salon_historique = await guilde.create_text_channel(name="log-administration", category=catégorie)
                self.client.log_db.ajouter_une_guilde(guilde, catégorie, salon_historique)
                await salon.send("Voici le salon où tous les actions passés sur la guilde seront publiés !")                        
            embed = discord.Embed(title=f"Le salon `{salon.name}` a été crée !", colour=discord.Colour(0xF5DF4D), timestamp=datetime.now())

            oui = "✅"
            non = "❌"
            
            if salon.type == discord.ChannelType.text or salon.type == discord.ChannelType.news or salon.type == discord.ChannelType.store:    
                await salon_historique.send(embed=self.__renvoie_embed_informations_salon_textuel__(embed, salon, guilde))
            elif salon.type == discord.ChannelType.stage_voice or salon.type == discord.ChannelType.voice:
                await salon_historique.send(embed=self.__renvoie_embed_informations_salon_vocal(embed, salon))
            elif salon.type == discord.ChannelType.category:
                embed = discord.Embed(title=f"La catégorie `{salon.name}` a été crée !", colour=discord.Colour(0xF5DF4D), timestamp=datetime.now())
                await salon_historique.send(embed=self.__renvoie_embed_informations_catégorie__(embed, salon))
async def setup_historique(client: commands.Bot, ctx):
    guilde = ctx.guild
    client.modules_db.modifier_status_extension(guilde, "log", True)
    await ctx.send("L'extension Historique est bien paramétrée ! :white_check_mark:") 


def setup(bot):
    bot.add_cog(Historique(bot))
    print("Le cog Historique est prêt !")