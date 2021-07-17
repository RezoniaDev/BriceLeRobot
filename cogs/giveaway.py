import re
import random
import asyncio
import discord
from utils.util import avoir_réaction, get_color, get_message, get_printable_string, get_emoji, est_activé, avoir_préfixe_guilde, a_un_rôle
from discord.ext import commands


time_regex = re.compile("(?:(\d{1,10000})(a|mo|w|h|s|m|d))+?")
time_dict = {"a": 31536000, "mo": 2592000, "w": 604800, "d": 86400, "h": 3600, "m": 60, "s": 1}



def convert( argument):
    args = argument.lower()
    matches = re.findall(time_regex, args)
    time = 0
    for key, value in matches:
        try:
            time += time_dict[value] * float(key)
        except KeyError:
            raise commands.BadArgument(
                f"{value} n'est pas un type de préfixes de temps ('a': année, 'mo': mois, 'w':semaine, 'd': jour, 'h': heure, 'm': minute, 's': seconde)")
        except ValueError:
            raise commands.BadArgument(f"{key} n'est pas un nombre !")
    return round(time)

class Giveaway(commands.Cog, name="Giveaway"):

    def __init__(self, client):
        self.client = client

    @commands.command(
        name="giveaway",
        description="Permet de créer un giveaway !",
        usage="giveaway"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels=True)
    async def giveaway(self, ctx):
        if est_activé(self.client.modules_db, ctx.guild, "giveaway"):
            await ctx.send("C'est parti pour la création du giveaway !\nJe pose des questions pour créer un giveaway unique !")

            question_list = [
                ["Quel est le salon où je vais lancer le giveaway ?", "Mentionne le salon !"],
                ["Combien de temps durera le giveaway ?", "a => année \n mo|w|h|d|m|s"],
                ["Qu'est que tu vas donner ?", "Pas ton rein, j'espère"]
            ]

            answers = {}

            for i, question in enumerate(question_list):
                answer = await get_message(self.client, ctx, question[0], question[1])

                if not answer:
                    await ctx.send("Vous avez pas répondu dans les temps.\nRépondez plus rapidement la prochaine fois !")
                    return
                answers[i] = answer
            mention_rôle, utilisateur, message = await avoir_réaction(self.client, ctx, "Est-ce que vous mentionnez un rôle ?", "Réagissez en-dessous !", [], [get_emoji(self.client, name="yes"), get_emoji(self.client, name="no")])
            if mention_rôle.emoji == get_emoji(self.client, name="yes"):
                rôle_à_mentionner = await get_message(self.client, ctx, "Quel rôle voulez-vous mentionner ?", "Mentionnez-le en-dessous de ce message !")
                if len(a_un_rôle(rôle_à_mentionner)) == 0:
                    await ctx.send("Vous devez mentionner un rôle !")
                    return
            else:
                rôle_à_mentionner = None

            embed = discord.Embed(title="Contenu du Giveaway", color=get_color())
            for key, value in answers.items():
                embed.add_field(name=f"Question: `{question_list[key][0]}`", value=f"Réponse: `{value}`", inline=False)
            embed.add_field(name="Question : `Est-ce que vous mentionnez un rôle ?`", value=f"""Réponse : `{rôle_à_mentionner if rôle_à_mentionner is not None else "Non"}`""")
            n = await ctx.send("Tout est valide ?", embed=embed)
            await n.add_reaction(get_emoji(self.client, "yes"))
            await n.add_reaction(get_emoji(self.client, "no"))
            liste_emojis = [get_emoji(self.client, "yes"), get_emoji(self.client, "no")]
            try:
                reaction, member = await self.client.wait_for(
                    "reaction_add",
                    timeout=10,
                    check=lambda reaction, user: user == ctx.author
                    and reaction.message.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                await ctx.send("Erreur lors de la confirmation ! Réessayez si vous plaît !")
                return
            if reaction.emoji not in liste_emojis or reaction.emoji == get_emoji(self.client, "no"):
                await ctx.send("Giveaway annulé !")
                return
            channel_id = re.findall(r"[0-9]+", answers[0])[0]
            channel = self.client.get_channel(int(channel_id))

            time = convert(answers[1])

            giveaway_embed = discord.Embed(
                title="🎉 ——**Giveaway**—— 🎉",
                description=f"**Voici ce qui est à gagner : **\n     {answers[2]}",
                color=get_color()
            )
            giveaway_embed.set_footer(text=f"Ce giveaway se terminera dans {await get_printable_string(time)} | {self.client.user.name}", icon_url=self.client.user.avatar)
            giveaway_message = await channel.send(embed=giveaway_embed)
            if rôle_à_mentionner is not None:
                await channel.send(rôle_à_mentionner)

            await giveaway_message.add_reaction("🎉")

            await asyncio.sleep(time)

            message = await channel.fetch_message(giveaway_message.id)
            users = await message.reactions[0].users().flatten()
            users.pop(users.index(ctx.guild.me))
            users.pop(users.index(ctx.author))
            if(len(users) == 0):
                await channel.send("Aucun gagnant a été décidé !")
                return

            winner = random.choice(users)

            await channel.send(f"**Félicitations à {winner.mention} !**\nContactez {ctx.author.mention} pour votre prix !")
        else:
            await ctx.send(f"Le module **Giveaway** n'est pas activé ! Faîtes `{self.client, avoir_préfixe_guilde(ctx.guild)}setup` pour l'activer !")

async def setup_giveaway(client, ctx):
    guilde = ctx.guild
    client.modules_db.modifier_status_extension(guilde, "giveaway", True)
    await ctx.send("L'extension **Giveaway** est bien paramétrée ! :white_check_mark:") 

def setup(client):
    client.add_cog(Giveaway(client))
    print("L'extension Giveaway est activée !")