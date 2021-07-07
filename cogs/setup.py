from cogs.verification import setup_vérification
from discord.ext import commands
import discord
from cogs.level import setup_niveau
from cogs.log import setup_historique


import asyncio

def nombre_en_emojis(nombre: int) -> str:
    chiffre_en_emoji = {0: "0️⃣", 1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5:"5️⃣", 6:"6️⃣", 7:"7️⃣", 8: "8️⃣", 9:"9️⃣"}
    message = "".join(chiffre_en_emoji[int(str(nombre)[i])] for i in range(len(str(nombre))))
    return message
 
async def avoir_réaction(bot: commands.Bot, ctx, content_one: str = "Message par défaut", content_two: str = "\uFEFF", fields: list = list(), reactions: list = list(), name_color: int = 0xF5DF4D, timeout: int = 100) -> tuple:
    """
    Cette fonction envoie un embed contenant les paramètres et attends les réponses
    :param: bot (commands.AuthoSharedBot) :
    :param: ctx (context object) : Utilisé pour envoyer les messages et le reste
    :param: content_one (string) : Le titre de l'embed
    :param: content_two (string) : La description de l'embed
    :param: timeout: (int) Le temps de "wait_for'
    :return: le contenu du message (string) : Si un message est detecté, il retourne le contenu du message
    ou :return: False (bool) : si le "wait_for" n'a aucune réponse
    """
    embed = discord.Embed(
        title=f"{content_one}",
        description=f"{content_two}",
        color=name_color
    )
    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=field[2])
    embed.set_footer(text=f"Veni, vidi, vici | {bot.user.name}", icon_url=bot.user.avatar_url)
    sent = await ctx.send(embed=embed)
    for reaction in reactions:
        await sent.add_reaction(reaction)
    try:
        reaction, user = await bot.wait_for(
            "reaction_add",
            timeout=timeout,
            check=lambda reaction, user: user.id == ctx.author.id
                                  and reaction.message.channel.id == ctx.channel.id,
        )
        if reaction and user:
            return (reaction, user)
    except asyncio.TimeoutError:
        return tuple(None)

class Setup(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.liste_modules = client.liste_modules
        self.base_de_données = self.client.modules_db
    
    @commands.command(
        name="setup",
        description="Permet d'activer ou désactiver les modules du bot",
        usage="setup (desactive|active) (nom_du_module)"
    )
    async def _setup(self, ctx, *args):
        modules_vers_fonctions = {"level": setup_niveau, "log": setup_historique, "vérification": setup_vérification}
        guilde = ctx.guild
        réaction, utilisateur = await avoir_réaction(self.client, ctx, "Que voulez-vous faire ?", "Réagissez en-dessous de ce message !", [["1️⃣ : ", "- Voir le status des extensions", False], ["2️⃣ : ", "- Activer des extensions", False], ["3️⃣ : ", "- Désactiver des extensions",False]], ["1️⃣","2️⃣", "3️⃣"], 0xF5DF4D, 120) 
        if str(réaction) == "1️⃣":
            status_par_extensions = self.base_de_données.avoir_status_extensions(guilde)
            status_embed = discord.Embed(name="Status des extensions", color=0xF5DF4D)
            for nom_extension, status_extension in status_par_extensions.items():
                status_embed.add_field(name=nom_extension.capitalize(), value="✅" if status_extension else "❌", inline=False)
            status_embed.set_footer(text=f"Veni, vidi, vici | {self.client.user.name}", icon_url=self.client.user.avatar_url)
            await ctx.send(embed=status_embed)
        elif str(réaction) == "2️⃣":
            
            extensions_désactivées = self.base_de_données.avoir_liste_extensions_désactivées(guilde)
            if len(extensions_désactivées) > 0:
                champs = []
                emoji_vers_modules = dict()
                for i in range(len(extensions_désactivées)):
                    emoji_vers_modules[nombre_en_emojis(i+1)] = extensions_désactivées[i]                
                    champs.append((f"{nombre_en_emojis(i+1)} : ", f"- {extensions_désactivées[i].capitalize()}", False))
                
                réaction, utilisateur = await avoir_réaction(self.client, ctx, "Quelle extensions voulez-vous activer ?", "Réagissez en-dessous de ce message !", champs, [nombre_en_emojis(i+1) for i in range(len(extensions_désactivées))], 16113485, 120)
                await modules_vers_fonctions[emoji_vers_modules[str(réaction)]](self.client, ctx)
            else:
                await ctx.send(embed=discord.Embed(color=0xF5DF4D).add_field(name="Configuration : ", value="Il y a aucune extension à activer !", inline=False).set_footer(text=f"Veni, vidi, vici | {self.client.user.name}", icon_url=self.client.user.avatar_url))
        elif str(réaction) == "3️⃣":
            extensions_activées = self.base_de_données.avoir_liste_extensions_activées(guilde)
            if len(extensions_activées) > 0:
                fields = []
                emoji_vers_modules = dict()
                for i in range(len(extensions_activées)):
                    emoji_vers_modules[nombre_en_emojis(i+1)] = extensions_activées[i]                
                    fields.append((f"{nombre_en_emojis(i+1)} : ", f"- {extensions_activées[i].capitalize()}", False))
                
                réaction, utilisateur = await avoir_réaction(self.client, ctx, "Quelle extensions voulez-vous désactiver ?", "Réagissez en-dessous de ce message !", fields, [nombre_en_emojis(i+1) for i in range(len(extensions_activées))], 16113485, 120)
                self.base_de_données.modifier_status_extension(guilde, emoji_vers_modules[str(réaction)], False)
                await ctx.send(f"L'extension `{emoji_vers_modules[str(réaction)]}` est bien désactivée !")
            else:
                await ctx.send(embed=discord.Embed(color=0xF5DF4D).add_field(name="Configuration : ", value="Il y a aucune extension à désactiver !", inline=False).set_footer(text=f"Veni, vidi, vici | {self.client.user.name}", icon_url=self.client.user.avatar_url))
            
def setup(client):
    client.add_cog(Setup(client))