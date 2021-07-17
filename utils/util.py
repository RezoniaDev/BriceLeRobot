import re
from discord.ext import commands
from utils.modules import ModulesDB
import discord
import asyncio
import sys

if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def get_message(bot, ctx, contenu_titre="Message par défaut", contenu_description="\uFEFF", code_hexadécimal_couleur=0xF5DF4D, durée_maximale_récepteur=100) -> str:
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
        title=f"{contenu_titre}",
        description=f"{contenu_description}",
        color=code_hexadécimal_couleur
    )
    sent = await ctx.send(embed=embed)
    try:
        msg = await bot.wait_for(
            "message",
            timeout=durée_maximale_récepteur,
            check=lambda message: message.author == ctx.author
                                  and message.channel == ctx.channel,
        )
        if msg:
            return msg.content
    except asyncio.TimeoutError:
        return False
    
async def avoir_réaction(bot: commands.Bot, ctx, contenu_titre: str = "Message par défaut", contenu_description: str = "\uFEFF", champs: list = list(), réactions: list = list(), couleur: int = 0xF5DF4D, timeout: int = 100, message=None) -> tuple:
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
        title=f"{contenu_titre}",
        description=f"{contenu_description}",
        color=couleur
    )
    for champ in champs:
        embed.add_field(name=champ[0], value=champ[1], inline=champ[2])
    embed.set_footer(text=f"Veni, vidi, vici | {bot.user.name}", icon_url=bot.user.avatar)
    if message is None:
        message_envoyé = await ctx.send(embed=embed)
        for réaction in réactions:
            await message_envoyé.add_reaction(réaction)
        try:
            réaction, user = await bot.wait_for(
                "reaction_add",
                timeout=timeout,
                check=lambda reaction, user: user.id == ctx.author.id
                                    and reaction.message.channel.id == ctx.channel.id,
            )
            if réaction and user:
                return (réaction, user, message_envoyé)
        except asyncio.TimeoutError:
            return tuple(None)
    else:
        await message.edit(embed=embed)
        for réaction in réactions:
            await message.add_reaction(réaction)
        try:
            réaction, user = await bot.wait_for(
                "reaction_add",
                timeout=timeout,
                check=lambda reaction, user: user.id == ctx.author.id
                                    and reaction.message.channel.id == ctx.channel.id,
            )
            if réaction and user:
                return (réaction, user, message)
        except asyncio.TimeoutError:
            return tuple(None)
    
def a_un_salon(message) -> list:
    return re.findall("<#.+>", message)    
    
def a_un_rôle(message)-> list:
    return re.findall("<@&.+>", message)

def get_color():
    return 0xF5DF4D

def est_activé(bdd: ModulesDB, guilde: discord.Guild, nom_module: str) -> bool:
    return bdd.avoir_status_extension(guilde, nom_module)


def avoir_préfixe_guilde(client, guilde):
    return client.prefix_db.get_prefix(guilde)

from pathlib import Path

def get_path():
    """
    Cette fonction donne le chemin de `bot.py`

    :return: cwd (str) : Le chemin du dossier de `bot.py`
    """
    cwd = Path(__file__).parents[1]
    cwd = str(cwd)
    return cwd


async def get_printable_string(duration: int) -> str:
    """
    Retourne la durée qui est affichable
    :param duration:
    :return:
    """
    secondes = int(duration)
    minutes = 0
    heures = 0
    jours = 0
    semaines = 0
    mois = 0
    année = 0
    # m": 60, "s": 1
    while secondes >= 31536000:
        année += 1
        secondes -= 31536000
    while secondes >= 2592000:
        mois += 1
        secondes -= 2592000
    while secondes >= 604800:
        semaines += 1
        secondes -= 604800
    while secondes >= 86400:
        jours += 1
        secondes -= 86400
    while secondes >= 3600:
        heures += 1
        secondes -= 3600
    while secondes >= 60:
        minutes += 1
        secondes -= 60

    affichage_total = ""

    if année == 0:
        affichage_total += ""
    elif année == 1:
        if affichage_total == "":
            affichage_total += f"{année} année."
        else:
            affichage_total += f"{année} an "
    elif année > 1:
        if affichage_total == "":
            affichage_total += f"{année} années."
        else:
            affichage_total += f"{année} ans "

    if mois == 0:
        affichage_total += ""

    elif affichage_total == "":
        affichage_total += f"{mois} mois."
    else:
        affichage_total += f"{mois} mois "

    if semaines == 0:
        affichage_total += ""
    elif semaines == 1:
        if affichage_total == "":
            affichage_total += f"{semaines} semaine."
        else:
            affichage_total += f"{semaines} semaine "
    elif semaines > 1:
        if affichage_total == "":
            affichage_total += f"{semaines} semaines."
        else:
            affichage_total += f"{semaines} semaines "

    if jours == 0:
        affichage_total += ""
    elif jours == 1:
        if affichage_total == "":
            affichage_total += f"{jours} jour."
        else:
            affichage_total += f"{jours} jour "
    elif jours > 1:
        if affichage_total == "":
            affichage_total += f"{jours} jours."
        else:
            affichage_total += f"{jours} jours "

    if heures == 0:
        affichage_total += ""
    elif heures == 1:
        if affichage_total == "":
            affichage_total += f"{heures} heure."
        else:
            affichage_total += f"{heures} heure "
    elif heures > 1:
        if affichage_total == "":
            affichage_total += f"{heures} heures."
        else:
            affichage_total += f"{heures} heures "

    if minutes == 0:
        affichage_total += ""
    elif minutes == 1:
        if affichage_total == "" and secondes == 0:
            affichage_total += f"{minutes} minute."
        else:
            affichage_total += f"{minutes} minute "
    elif minutes > 1:
        if affichage_total == "" and secondes == 0:
            affichage_total += f"{minutes} minutes."
        else:
            affichage_total += f"{minutes} minutes "

    if secondes == 0:
        affichage_total += ""
    elif secondes == 1:
        affichage_total += f"{secondes} seconde."
    elif secondes > 1:
        affichage_total += f"{secondes} secondes."

    return affichage_total


emojis = {
    "yes": 790866591197560832,
    "no": 790866590953898005,
    "minecraft": 808622821462900747
}


def get_emoji(bot, name):
    return bot.get_emoji(emojis[name.lower()])