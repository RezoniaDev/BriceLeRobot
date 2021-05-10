from discord.ext import commands
import discord
from random import randint


liste_level_up = []
liste_xp = []

somme = 0
for x in range(1001):
    level_up = 5*(x**2)+(50*x)+100
    somme += level_up
    liste_level_up.append(level_up)
    liste_xp.append(somme)

def envoie_embed_rank(xp, level, user, rang, client):
    embed = discord.Embed(title=user.name, colour=discord.Colour(0xF5DF4D))

    embed.set_thumbnail(url=user.avatar_url)
    embed.set_footer(text=f"Veni, vidi, vici | {client.user.name}", icon_url=client.user.avatar_url)

    embed.add_field(name="Niveau actuel :", value=level, inline=False)
    embed.add_field(name="Rang actuel : ", value=str(rang.index(user.id)+1), inline=False)
    embed.add_field(name="Expérience actuelle :", value=xp, inline=False)
    embed.add_field(name="Expérience restante :", value=str(liste_xp[level]-xp) + " points d'expériences.\n\n"+ retourne_carré(xp, level), inline=False)
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

class Level(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.level = client.level_db
    
    @commands.Cog.listener()
    async def on_message(self, message):
        
        if message.author.bot:
            return
        
        if not self.client.modules_db.get_module_status(message.guild, "level"):
            return
        if (message.content[0] == self.client.prefix_db.get_prefix(message.guild)):
            return
        xp, level = self.level.get_user_informations(message.guild, message.author)
        xp += randint(0, 5)
        
        if xp >= liste_xp[level]:
            await message.channel.send(f"Bravo {message.author}, vous êtes passé au niveau {level+1} !")
            self.level.modifie_experience(message.guild, message.author, xp, level+1)
        else:
            self.level.modifie_experience(message.guild, message.author, xp, level)
    
    
    @commands.Cog.listener()
    async def on_guild_join(self, guilde):
        self.level.ajoute_guilde(guilde)
        
    @commands.Cog.listener()
    async def on_member_remove(self, membre):
        self.level.supprimer_utilisateur(membre.id, membre)

    @commands.Cog.listener()
    async def on_guild_remove(self, guilde):
        self.level.supprimer_guilde(guilde)
        
    @commands.Cog.listener()
    async def on_member_join(self, membre):
        self.level.ajoute_utilisateur(membre.id, membre)

    @commands.command(
        name="rank"
    )
    async def _rank(self, ctx):
        if not self.client.modules_db.get_module_status(ctx.guild, "level"):
            await ctx.send("Le module **Niveau** n'est pas activé !")
            return
        rang = self.level.retourne_liste_rank(ctx.guild)
        xp, level = self.level.get_user_informations(ctx.guild, ctx.author)
        await ctx.send(embed=envoie_embed_rank(xp, level,ctx.author, rang, self.client))
        
    @commands.command(
        name="leaderboard"
    )    
    async def _leaderboard(self, ctx):
        if not self.client.modules_db.get_module_status(ctx.guild, "level"):
            await ctx.send("Le module **Niveau** n'est pas activé !")
            return
        
        level = self.level.retourne_liste_rank(ctx.guild)
        a = 10 if len(level) > 10 else len(level)
        description = ""
        
        for x in range(a):
            user = await self.client.fetch_user(level[x])
            xp, level_user = self.level.get_user_informations(ctx.guild, user)
            description += f"**{x+1}** : {user.mention}\n    ⤇ niveau {level_user} ( {xp} points d'expériences )\n\n"
        
        embed = discord.Embed(title=f"Tableau de bord ({len(level)}) :", colour=discord.Colour(0xF5DF4D), description=description)
        embed.set_footer(text=f"Veni, vidi, vici | {self.client.user.name}", icon_url=self.client.user.avatar_url)

        await ctx.send(embed=embed)
        
        
def setup(client):
    client.add_cog(Level(client))
    print("Le cog Niveau est prêt !")