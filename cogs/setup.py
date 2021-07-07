from discord.ext import commands
import discord


class Setup(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.liste_modules = client.liste_modules
    
    @commands.command(
        name="setup",
        description="Permet d'activer ou désactiver les modules du bot",
        usage="setup (desactive|active) (nom_du_module)"
    )
    async def _setup(self, ctx, *args):
        emoji_activé = "✅"
        emoji_désactivé  = "❌"
        
        if len(args) == 0:
            embed = discord.Embed(title="Status des modules", color=0xF5DF4D)
            status_modules = self.client.modules_db.avoir_status_extensions(ctx.guild)
            for nom_module, status in status_modules.items():  
                embed.add_field(name=f"Status du module {self.client.dico_nom_modules_jolis[nom_module]}", value=emoji_activé if status else emoji_désactivé)
            embed.set_footer(text=f"Veni, vidi, vici | {self.client.user.name}", icon_url=self.client.user.avatar_url)
            await ctx.send(embed=embed)
        elif len(args) == 2:
            action = args[0]
            nom_module = args[1]
            if nom_module.lower() not in self.liste_modules:
                await ctx.send(f"Le module {nom_module} n'existe pas !")
                return
            elif action not in ["desactive", "activate"]:
                await ctx.send("Pour activer un module, faut utiliser le mot `activate`, et au contraire, pour le désactiver, il faut utiliser le mot `desactivate` !")
                return              
            self.client.modules_db.modifier_status_extension(ctx.guild, nom_module.lower(), action == "activate")
            await ctx.send(f"Le module **{self.client.dico_nom_modules_jolis[nom_module.lower()]}** est été bien {'activé' if action == 'activate' else 'désactivé'} !")
        else:
            a = ""
            for nom_module, nom_module_joli in self.client.dico_nom_modules_jolis.items():
                a += f" - {nom_module_joli} : `{nom_module}`\n"            
            await ctx.send(f"Utilisation : `setup (desactive|active) (nom_du_module)` \nNom des modules : \n{a}")
            return
            
def setup(client):
    client.add_cog(Setup(client))