import discord

from cogs.quiz import setup_quiz
from cogs.spoil import setup_spoil
from cogs.vérification import setup_vérification
from discord.ext import commands
from cogs.giveaway import setup_giveaway

import sys
import asyncio
from utils.util import avoir_réaction
from cogs.niveau import setup_niveau
from cogs.historique import setup_historique

def nombre_en_emojis(nombre: int) -> str:
    chiffre_en_emoji = {0: "0️⃣", 1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5:"5️⃣", 6:"6️⃣", 7:"7️⃣", 8: "8️⃣", 9:"9️⃣"}
    return "".join(chiffre_en_emoji[int(str(nombre)[i])] for i in range(len(str(nombre))))

class Configuration(commands.Cog, name="Configuration"):
    
    modules_vers_fonctions = {"level": setup_niveau, "log": setup_historique, "vérification": setup_vérification, "spoil": setup_spoil, "quiz": setup_quiz, "giveaway": setup_giveaway}
    
    
    def __init__(self, client):
        self.client = client
        self.liste_modules = client.liste_modules
        self.base_de_données = self.client.modules_db
    
    async def début(self, guilde, ctx, message=None):
        réaction, utilisateur, message = await avoir_réaction(self.client, ctx, "Que voulez-vous faire ?", "Réagissez en-dessous de ce message !", [["1️⃣ : ", "- Voir le status des extensions", False], ["2️⃣ : ", "- Activer des extensions", False], ["3️⃣ : ", "- Désactiver des extensions",False]], ["1️⃣","2️⃣", "3️⃣"], 0xF5DF4D, 120, message) 
        await message.clear_reactions()
        if str(réaction) == "1️⃣":
            await self.fonction_réaction_1(guilde, ctx, message)
        elif str(réaction) == "2️⃣":
            await self.fonction_réaction_2(guilde, ctx, message)
        elif str(réaction) == "3️⃣":
            await self.fonction_réaction_3(guilde, ctx, message)
            
    async def fonction_réaction_1(self, guilde, ctx: commands.Context, message: discord.Message):
        status_par_extensions = self.base_de_données.avoir_status_extensions(guilde)
        status_embed = discord.Embed(title="Status des extensions", color=0xF5DF4D)
        for nom_extension, status_extension in status_par_extensions.items():
            status_embed.add_field(name=nom_extension.capitalize(), value="✅" if status_extension else "❌", inline=False)
        status_embed.add_field(name=f"{nombre_en_emojis(1)} - ", value="Retour en arrière", inline=False)
        
        status_embed.set_footer(text=f"Veni, vidi, vici | {self.client.user.name}", icon_url=self.client.user.avatar)
        await message.edit(embed=status_embed)
        await message.add_reaction(nombre_en_emojis(1))
        try:
            réaction, user = await self.client.wait_for(
                "reaction_add",
                timeout=100,
                check=lambda reaction, user: user.id == ctx.author.id
                                    and reaction.message.channel.id == ctx.channel.id,
            )
            if réaction.emoji == nombre_en_emojis(1):
                await message.clear_reactions()
                await self.début(guilde, ctx, message)
                
        except asyncio.TimeoutError:
            return tuple(None)
        
        
        return message
        
    async def fonction_réaction_2(self, guilde: discord.Guild, ctx: commands.Context, message:discord.Message):

        extensions_désactivées = self.base_de_données.avoir_liste_extensions_désactivées(guilde)
        if len(extensions_désactivées) > 0:
            champs = []
            emoji_vers_modules = {}
            emoji_retour = None
            for i in range(len(extensions_désactivées) + 1):
                if i == len(extensions_désactivées):
                    emoji_retour = nombre_en_emojis(i + 1)
                    champs.append((f"{nombre_en_emojis(i+1)} : ", f"- Retour en arrière", False))
                else:
                    emoji_vers_modules[nombre_en_emojis(i+1)] = extensions_désactivées[i]                
                    champs.append((f"{nombre_en_emojis(i+1)} : ", f"- {extensions_désactivées[i].capitalize()}", False))
                
            réaction, utilisateur, message = await avoir_réaction(self.client, ctx, "Quelle extensions voulez-vous activer ?", "Réagissez en-dessous de ce message !", champs, [nombre_en_emojis(i+1) for i in range(len(extensions_désactivées) + 1)], 16113485, 120, message)
            if réaction.emoji == emoji_retour:
                await message.clear_reactions()
                await self.début(guilde, ctx, message)
                return
            await self.modules_vers_fonctions[emoji_vers_modules[str(réaction)]](self.client, ctx)
        else:
            champs = [("Configuration : ", "Il y a aucune extension à activer !", False), (f"{nombre_en_emojis(1)} - ", "Retour en arrière", False)]
            réaction, utilisateur, message = await avoir_réaction(self.client, ctx, " ", " ", champs, [nombre_en_emojis(1)], 16113485, 120, message)
            if réaction:
                await message.clear_reactions()
                await self.début(guilde, ctx, message)
                return
    
    async def fonction_réaction_3(self, guilde: discord.Guild, ctx: commands.Context, message: discord.Message):
        extensions_activées = self.base_de_données.avoir_liste_extensions_activées(guilde)
        if len(extensions_activées) > 0:
            fields = []
            emoji_vers_modules = {}
            emoji_retour = None
            for i in range(len(extensions_activées) + 1):
                if i == len(extensions_activées):
                    emoji_retour = nombre_en_emojis(i + 1)
                    fields.append((f"{nombre_en_emojis(i+1)} : ", f"- Retour en arrière", False))
                else:
                    emoji_vers_modules[nombre_en_emojis(i+1)] = extensions_activées[i]                
                    fields.append((f"{nombre_en_emojis(i+1)} : ", f"- {extensions_activées[i].capitalize()}", False))
                
            réaction, utilisateur, message = await avoir_réaction(self.client, ctx, "Quelle extensions voulez-vous désactiver ?", "Réagissez en-dessous de ce message !", fields, [nombre_en_emojis(i+1) for i in range(len(extensions_activées) + 1)], 16113485, 120, message)
            if réaction.emoji == emoji_retour:
                await message.clear_reactions()
                await self.début(guilde, ctx, message)
            self.base_de_données.modifier_status_extension(guilde, emoji_vers_modules[str(réaction)], False)
            await ctx.send(f"L'extension `{emoji_vers_modules[str(réaction)]}` est bien désactivée !")
        else:
            champs = [["Configuration : ", "Il y a aucune extension à désactiver !", False], [f"{nombre_en_emojis(1)} - ", "Retour en arrière", False]]
            réaction, utilisateur, message = await avoir_réaction(self.client, ctx, " ", " ", champs, [nombre_en_emojis(1)], 16113485, 120, message)
            if réaction:
                await message.clear_reactions()
                await self.début(guilde, ctx, message)
                return
    
    @commands.command(
        name="setup",
        description="Permet d'activer ou désactiver les modules du bot",
        usage="setup"
    )
    async def _setup(self, ctx, *args):
        guilde = ctx.guild
        await self.début(guilde, ctx)
            
def setup(client):
    client.add_cog(Configuration(client))
    print("L'extension Configuration est activée !")