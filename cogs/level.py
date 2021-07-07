from turtle import pd
from utils.modules import ModulesDB
from discord.ext import commands
import discord
from discord_components import Button, ButtonStyle, component
from random import randint


liste_level_up = []
liste_xp = []

somme = 0
for x in range(1001):
    level_up = 5*(x**2)+(50*x)+100
    somme += level_up
    liste_level_up.append(level_up)
    liste_xp.append(somme)

def est_activé(bdd: ModulesDB, guilde: discord.Guild) -> bool:
    return bdd.avoir_status_extension(guilde, "level")

def envoie_embed_rang(expérience, niveau, utilisateur: discord.User, rang: list, client) -> discord.Embed:
    
    embed = discord.Embed(title = utilisateur.name, colour=discord.Colour(0xF5DF4D))

    embed.set_thumbnail(url = utilisateur.avatar_url)
    embed.set_footer(text = f"Veni, vidi, vici | {client.user.name}", icon_url = client.user.avatar_url)

    embed.add_field(name = "Niveau actuel :", value = niveau, inline=False)
    embed.add_field(name = "Rang actuel : ", value = str ( rang.index( utilisateur.id ) + 1), inline=False)
    embed.add_field(name = "Expérience actuelle :", value=expérience, inline=False)
    embed.add_field(name = "Expérience restante :", value=str(liste_xp[niveau]- expérience) + " points d'expériences.\n\n"+ retourne_carré(expérience, niveau), inline=False)
    return embed                    

def retourne_carré(xp, level):
    ratio = ((xp)/(liste_xp[level]))
    cases_vides = 10 - int(ratio*10)
    a = ""
    for x in range(int(ratio*10)):
        a += "🟩"
    for x in range(cases_vides):
        a+= "⬜"
    return a +f" **( {int(ratio*100)} % )**"

class Level(commands.Cog, name="Niveau"):
    
    def __init__(self, client: commands.Bot):
        self.client = client
        self.niveau_bdd = client.level_db
        self.setup_bdd = client.modules_db 
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        
        if est_activé(self.setup_bdd, message.author.guild):
            if message.author.bot:
                return
            
            if (message.content[0] == "?"):
                return
            expérience, niveau = self.niveau_bdd.avoir_informations_utilisateur(message.guild, message.author)
            expérience += randint(0, 5)
            
            if expérience >= liste_xp[niveau]:
                await message.channel.send(f"Bravo {message.author}, vous êtes passé au niveau {niveau + 1} !")
                self.niveau_bdd.modifier_expérience(message.guild, message.author, expérience, niveau + 1)
            else:
                self.niveau_bdd.modifier_expérience(message.guild, message.author, expérience, niveau) 
    
    
    @commands.Cog.listener()
    async def on_guild_join(self, guilde: discord.Guild):
        self.niveau_bdd.ajouter_guilde(guilde)
        
    @commands.Cog.listener()
    async def on_member_remove(self, membre: discord.Member):
        self.niveau_bdd.supprimer_utilisateur(membre.id, membre)

    @commands.Cog.listener()
    async def on_guild_remove(self, guilde: discord.Guild):
        self.niveau_bdd.supprimer_guilde(guilde)
        
    @commands.Cog.listener()
    async def on_member_join(self, membre: discord.Member):
        self.niveau_bdd.ajouter_utilisateur(membre.guild, membre)

    @commands.command(
        name="rank"
    )
    async def _rank(self, ctx):
        
        if est_activé(self.setup_bdd, ctx.guild):
            rang_utilisateurs = self.niveau_bdd.retourne_liste_rangs(ctx.guild)
            expérience, niveau = self.niveau_bdd.get_user_informations(ctx.guild, ctx.author)
            await ctx.send(embed=envoie_embed_rang(expérience, niveau, ctx.author , rang_utilisateurs, self.client))
        else:
            await ctx.send("L'extension **Niveau** n'est pas activé !")        
        
    @commands.command(
        name="leaderboard"
    )    
    async def _leaderboard(self, ctx):
        
        if est_activé(self.setup_bdd, ctx.guild):
        
            podium_utilisateurs = self.niveau_bdd.retourne_liste_rangs(ctx.guild)
            longueur_podium = 10 if len(podium_utilisateurs) > 10 else len(podium_utilisateurs)
            description = ""
            
            for x in range(longueur_podium):
                user = await self.client.fetch_user(podium_utilisateurs[x])
                expérience, niveau_utilisateur = self.niveau_bdd.avoir_informations_utilisateur(ctx.guild, user)
                description += f"**{x + 1}** : {user.mention}\n    ⤇ niveau {niveau_utilisateur} ( {expérience} points d'expériences )\n\n"
            
            embed = discord.Embed(title=f"Tableau de bord ({len(podium_utilisateurs)}) :", colour=discord.Colour(0xF5DF4D), description=description)
            embed.set_footer(text=f"Veni, vidi, vici | {self.client.user.name}", icon_url=self.client.user.avatar_url)
        
        
def setup(client):
    
    client.add_cog(Level(client))
    print("Le cog Niveau est prêt !")
    
