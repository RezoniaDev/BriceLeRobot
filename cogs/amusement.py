import discord
from discord.ext import commands
import aiohttp
import platform
import emoji
import requests
from utils.util import get_color, get_emoji

def est_le_propriétaire():
    def predicate(ctx):
        return ctx.author.id ==528157130432315403
    return commands.check(predicate)

class Amusement(commands.Cog):

    def __init__(self, client):
        self.client = client
    @commands.command(
        name="ping",
        description="Affiche la latence du bot"
    )
    async def ping(self, ctx):
        await ctx.send(f"Ma latence est de : {self.client.latency * 1000} ms")

    @commands.command(
        name="stats",
        description=f"Renvoie les statistiques du bot.",
        usage="stats"
    )
    async def stats(self, ctx):
        """
        Renvoie un embed avec les statistiques du bot
        :param ctx: le contexte
        :return: None
        """

        # Cela permet de compter le nombre de membres totals (on utilise un bot avec des shards)
        member_counts = 0

        for guild in self.client.guilds:
            member_counts += guild.member_count

        # Récupération des versions de Python, du bot, discord.py, du nombre de serveurs et le développeur
        python_version = platform.python_version()
        discord_py_version = discord.__version__
        server_counts = len(self.client.guilds)

        # Création de l'embed
        embeds = discord.Embed(color=get_color(), title=f"**Stats de {self.client.user.name}**",
                                description="[Clique pour inviter le bot](https://discord.com/api/oauth2/authorize?client_id=718452593579262012&permissions=8&scope=bot)\n[Clique pour me payer une bière](https://www.buymeacoffee.com/mrtayai)")
        embeds.add_field(name=f"**Version de {self.client.user.name} : ** {emoji.emojize(':robot:')}",
                         value=self.client.version,
                         inline=True)
        embeds.add_field(name=f"**Version de Python : ** {emoji.emojize(':snake:')}", value=python_version, inline=True)
        embeds.add_field(name=f"**Version de discord.py : ** {emoji.emojize(':alien_monster:')}",
                         value=discord_py_version, inline=True)
        embeds.add_field(name=f"**Nombre de guildes totales : ** {emoji.emojize(':bar_chart:')}", value=server_counts,
                         inline=True)
        embeds.add_field(name=f"**Nombre de membres totals : ** {emoji.emojize(':prince:')} ", value=member_counts,
                         inline=True)
        embeds.add_field(name=f"**Le développeur du bot : ** {emoji.emojize(':beer:', use_aliases=True)}",
                         value=f"<@{self.client.id_auteur}>", inline=True)
        embeds.set_footer(text=f"Veni, vidi, vici | {self.client.user.name}", icon_url=self.client.user.avatar)

        # Envoi de l'embed
        await ctx.send(embed=embeds)


    @commands.command(
        name="channel-stats",
        description="Renvoie un joli embed avec les informations du channels",
        aliases=["cs"]
    )
    @commands.has_guild_permissions(manage_channels=True)
    async def channelstats(self, ctx):
        """
        :param ctx:
        :return:
        """
        channel = ctx.channel
        embed = discord.Embed(title=f"Stats de **{channel.name}**",
                              description=f"{'Catégorie : {}'.format(channel.category.name) if channel.category else 'Une catégorie a ce salon !'}",
                              color=get_color())
        embed.add_field(name="La guilde de ce salon : ", value=ctx.guild.name, inline=False)
        embed.add_field(name="L'identifiant de la guilde : ", value=ctx.guild.id, inline=False)
        embed.add_field(name="L'ID du salon : ", value=channel.id, inline=False)
        embed.add_field(name="Le sujet du salon : ", value=f"{channel.topic if channel.topic else 'Pas de sujet'}",
                        inline=False)
        embed.add_field(name="La position du salon : ", value=channel.position, inline=False)
        embed.add_field(name="Le délai du 'slowmode' du salon : ", value=channel.slowmode_delay, inline=False)
        embed.add_field(name="Le salon est-il en mode 'NSFW' ?",
                        value=get_emoji(self.client, "yes") if channel.is_nsfw() else get_emoji(self.client, "no"),
                        inline=False)
        embed.add_field(name="Le salon est-il un salon de 'news' ?",
                        value=get_emoji(self.client, "yes") if channel.is_news() else get_emoji(self.client, "no"),
                        inline=False)
        embed.add_field(name="La date de création du salon : ", value=channel.created_at, inline=False)
        embed.add_field(name="Les permissions du salon sont-elles synchronisées ? : ",
                        value=get_emoji(self.client, "yes") if channel.permissions_synced else get_emoji(self.client, "no"),
                        inline=False)
        embed.add_field(name="Le 'hash' du salon : ", value=hash(channel), inline=False)
        embed.set_footer(text=f"Veni, vidi, vici | {self.client.user.name}", icon_url=self.client.user.avatar)
        await ctx.send(embed=embed)

    @commands.command(
        name="cat",
        aliases=["chat", "chats", "cats"],
        description="Renvoie une image de chat.",
        usage="cat",
    )
    @commands.cooldown(1, 10,commands.BucketType.user)
    async def cat(self, ctx):
        """
        Renvoie une image aléatoire de chat
        :param ctx: Contexte
        :return: None
        """
        # Création d'une session client
        async with aiohttp.ClientSession() as session:
            # On récupère la page web
            async with session.get("http://aws.random.cat/meow") as r:
                # Si le status est 200 (c'est qd on réussit à se connecter)
                if r.status == 200:
                    # On récupère le json contenu dans la page
                    js = await r.json()
                    # On envoie l'image contenue dans la partie "file" du json
                    await ctx.send(js["file"])

    @commands.command(
        name="dog",
        aliases=["chien", "chiens", "dogs"],
        description="Renvoie une image de chien.",
        usage="dog"
    )
    @commands.cooldown(1, 10,commands.BucketType.user)
    async def dog(self, ctx):
        """
        Renvoie une image aléatoire de chat
        :param ctx: Contexte
        :return: None
        """
        # Création d'une session client
        async with aiohttp.ClientSession() as session:
            # On récupère la page web
            async with session.get("https://dog.ceo/api/breeds/image/random") as r:
                # Si le status est 200 (c'est qd on réussit à se connecter)
                if r.status == 200:
                    # On récupère le json contenu dans la page
                    js = await r.json()
                    # On envoie l'image contenue dans la partie "file" du json
                    await ctx.send(js["message"])

    @dog.error
    async def dog_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = f"Vous devez attendre {int(error.retry_after)} secondes avant de réutiliser cette commande !"
            await ctx.send(msg)
        else:
            raise error

    @cat.error
    async def cat_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            msg = f"Vous devez attendre {int(error.retry_after)} secondes avant de réutiliser cette commande !"
            await ctx.send(msg)
        else:
            raise error

def setup(client):
    client.add_cog(Amusement(client))
    print("L'extension Amusement est activée !")