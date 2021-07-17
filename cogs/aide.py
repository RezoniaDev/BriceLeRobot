import discord
import math
import re
import random
from discord.ext import commands

def get_color():
    return 0xF5DF4D

class Help(commands.Cog, name="Aide"):
    

    def __init__(self, client):
        self.client = client
        
    @commands.command(
        name="help",
        aliases=["h", "aide"],
        description="La commande d'aide !"
    )
    async def help(self, ctx, index_extension="1"):
        embed_aide = discord.Embed(
            title="Commande d'aide",
            color = get_color()
        )
        
        # Donne une liste de toutes les cogs et retire le seul sans les commandes
        extensions = [c for c in self.client.cogs.keys()]
        commande = self.client.get_command(index_extension)
        if commande:
            if commande.hidden:
                return

            elif commande.parent != None:
                return

            texte_aide = ""
            texte_aide += f"➳ **__{commande.name.capitalize()}__**\n**{commande.description}**\n"

            if len(commande.aliases) > 0:
                texte_aide += f"**Aliases: ** `{str([alias for alias in commande.aliases])}"
            texte_aide += f'**Format:** `&{commande.usage if commande.usage is not None else ""}`\n'
            embed_aide.set_footer(text=f"<> - Requis et [] - Optionnel | Page n°1", icon_url=self.client.user.avatar)

            embed_aide.description = texte_aide
        
        else:
            total_pages = math.ceil(len(extensions) / 4)

            if re.search(r"\d", str(index_extension)):
                index_extension = int(index_extension)
                if index_extension > total_pages or index_extension < 1:
                    await ctx.send(f"Le numéro de page est invalide : `{index_extension}`. Si vous plaît, choississez dans les {total_pages} pages.\nOu utiliser, tapez juste `&help` pour voir la première page de l'aide !")
                    return
                embed_aide.set_footer(text=f"<> - Requis et [] - Optionnel | Page n°{index_extension} sur {total_pages}", icon_url=self.client.user.avatar)

                extensions_nécessaires = []
                for i in range(6):
                    x = i + (int(index_extension) - 1) * 6
                    try:
                        extension = extensions[x]
                        if len(list(self.client.get_cog(extension).walk_commands())) != 0:
                            if not all([commande.hidden for commande in self.client.get_cog(extension).walk_commands()]):                            
                                extensions_nécessaires.append(extension)
                    except IndexError:
                        pass
                    
                
                for extension in extensions_nécessaires:
                    liste_commandes = ""
                    partie = 1
                    for commande in self.client.get_cog(extension).walk_commands():
                        if commande.hidden:
                            continue
                        elif commande.parent != None:
                            continue
                        
                        liste_commandes += f"**{commande.name}** - *{commande.description}*\n"
                    
                    liste_commandes += "\n" 
                    
                    embed_aide.add_field(name=extension, value=liste_commandes, inline=False)
            
            elif re.search(r"[a-zA-Z]", str(index_extension)):
                lower_cogs = [c.lower() for c in extensions]
                extension = str(index_extension)
                if extension.lower() not in lower_cogs:
                    await ctx.send(f"Arguments invalides : `{extension}`. Si vous plaît, choississez dans les {total_pages} pages.\nOu utiliser, tapez juste `&help` pour voir la première page de l'aide !")
                    return
                embed_aide.set_footer(text=f"<> - Requis et [] - Optionnel | Page n°{extension} sur {total_pages}",icon_url=self.client.user.avatar)

                texte_aide = ""

                for commande in self.client.get_cog(extensions[lower_cogs.index(extension.lower())]).walk_commands():
                    if commande.hidden:
                        continue

                    elif commande.parent != None:
                        continue

                    texte_aide += f"➳ **__{commande.name.capitalize()}__**\n**{commande.description}**\n"

                    if len(commande.aliases) > 0:
                        texte_aide += f'**Aliases: ** `{", ".join(commande.aliases)}`\n'
                    texte_aide += f'**Format:** `&{commande.usage if commande.usage is not None else ""}`\n\n'
                embed_aide.description = texte_aide

            else:
                await ctx.send(f"Arguments invalides: `{index_extension}`\nSi vous plaît, choississez dans les {total_pages} pages.\nSoit vous tapez, simplement `&help` pour avoir la première page de l'aide ou `&help [catégorie]` pour avoir de l'aide sur la catégorie.")
                return

        await ctx.send(embed=embed_aide)
    

def setup(client):
    client.add_cog(Help(client))
    print("L'extension Aide est activée !")