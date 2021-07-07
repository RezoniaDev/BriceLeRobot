import re
import discord
import asyncio

async def get_message(bot, ctx, contenu_titre="Message par défaut", contenu_description="\uFEFF", code_hexadécimal_couleur=0xF5DF4D, durée_maximale_récepteur=100):
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
    
def a_un_salon(message) -> list:
    return re.findall("<#.+>", message)    

def a_un_rôle(message)-> list:
    return re.findall("<@&.+>", message)
