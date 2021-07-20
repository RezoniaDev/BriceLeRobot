import discord
from discord.ext import commands
import re
from utils.util import get_message, get_color, avoir_préfixe_guilde, est_activé

liste_lettres_emoji = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹",
                       "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"]


class Quiz(commands.Cog, name="Quiz"):

    def __init__(self, client):
        self.client = client

    @commands.command(
        name="quiz",
        description="Permet de créer un quiz",
        usage="quiz"
    )
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def quiz(self, ctx):
        guilde = ctx.guild
        if not est_activé(self.client.modules_db,guilde, "quiz"):
            await ctx.send(f"Le module **Quiz** n'est pas activé ! Si vous voulez l'activer, faîtes `{avoir_préfixe_guilde(self.client, guilde)}setup` !")
            return
        
        await ctx.send("C'est parti pour la création du quiz !\nJe pose des questions pour créer un quizz unique !")

        question_list = [
            ["Quel est le salon où je vais lancer le quiz ?", "Mentionne le salon !"],
            ["Quel rôle dois-je mentionner ?", "Exemple : @Quiz"],
            ["Quelle est la question ?", "Exemple : Quel est le meilleur jeu actuellement ?"],
            ["Combien aura-t-il de réponses ?", "Exemple : 3"]
        ]

        answers = {}

        for i, question in enumerate(question_list):
            answer = await get_message(self.client, ctx, question[0], question[1])

            if not answer:
                await ctx.send("Vous avez pas répondu dans les temps.\nRépondez plus rapidement la prochaine fois !")
                return
            answers[i] = answer

        nombre_réponses = int(answers[len(answers) - 1])
        reponses = {}
        for i in range(nombre_réponses):
            reponse = await get_message(self.client, ctx, f"Quelle sera la réponse {i + 1} ?", "")

            if not reponse:
                await ctx.send("Vous avez pas répondu dans les temps.\nRépondez plus rapidement la prochaine fois !")
                return

            reponses[i] = reponse

        a_embed = discord.Embed(title="Contenu du Quiz", color=get_color())

        str_réponses = ""
        for i in range(nombre_réponses):
            reponse = reponses[i]
            str_réponses += liste_lettres_emoji[i] + " **-** " + reponse + "\n"

        question_list.append(["Quelles seront les réponses ?", "a"])
        answers[len(answers)] = str_réponses

        for key, value in answers.items():
            a_embed.add_field(name=f"Question: `{question_list[key][0]}`", value=f"{value}", inline=False)
        n = await ctx.send("Tout est valide ?", embed=a_embed)

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
        # if reaction.emoji not in liste_emojis or reaction.emoji == get_emoji(self.client, "no"):
        if reaction.emoji not in liste_emojis or reaction.emoji == "❌":
            await ctx.send("Quiz annulé !")
            return
        channel_id = re.findall(r"[0-9]+", answers[0])[0]
        channel = self.client.get_channel(int(channel_id))

        giveaway_embed = discord.Embed(
            title="⁉️ ——** Quiz **—— ⁉️",
            description=f"**Voici la question : **\n     {answers[2]}",
            color=get_color()
        )
        giveaway_embed.add_field(name="Réponses possibles : ", value=str_réponses, inline=False)
        giveaway_embed.set_footer(
            text=f"Veni, vidi, vici | {self.client.user.name}",
            icon_url=self.client.user.avatar)

        await channel.send(answers[1])
        giveaway_message = await channel.send(embed=giveaway_embed)

        for i in range(nombre_réponses):
            await giveaway_message.add_reaction((liste_lettres_emoji[i]))  


async def setup_quiz(client: commands.Bot, ctx: commands.Context):
    guilde = ctx.guild
    client.modules_db.modifier_status_extension(guilde, "quiz", True)
    await ctx.send("L'extension **Quiz** est bien paramétrée ! :white_check_mark:") 


def setup(client):
    client.add_cog(Quiz(client))
    print("L'extension Quiz est activée !")